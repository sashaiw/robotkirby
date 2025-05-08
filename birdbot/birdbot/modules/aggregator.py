import hikari
import tanjun
import asyncio
import datetime
import os

from birdbot.database import Database

import pandas as pd
from pandas.api.types import CategoricalDtype


component = tanjun.Component()

def get_time_of_day(hour: int) -> str:
    if 5 <= hour < 10:
        return "Morning"
    elif 10 <= hour < 14:
        return "Mid-day"
    elif 14 <= hour < 18:
        return "Afternoon"
    elif 18 <= hour < 21:
        return "Evening"
    else:
        return "Night"

def get_am_pm(hour: int) -> str:
    if hour < 12:
        return "AM"
    else:
        return "PM"

def split_message(message: str, max_length: int = 2000) -> list[str]:
    lines = message.splitlines(keepends=True)
    chunks = []
    current_chunk = ""

    for line in lines:
        if len(current_chunk) + len(line) > max_length:
            chunks.append(current_chunk)
            current_chunk = ""
        current_chunk += line

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

@component.with_listener(hikari.StartedEvent)
async def on_startup(event: hikari.StartedEvent, db: Database = tanjun.inject(type=Database)) -> None:
    async def send_daily_aggregate():
        min_observations = 5
        min_confidence = 0.6

        df = db.get_recent_observations()

        df = df[df['confidence'] >= min_confidence]


        df['time_of_day'] = df['begin_time'].dt.hour.map(get_time_of_day)
        time_order = ['Morning', 'Mid-day', 'Afternoon', 'Evening', 'Night']
        cat_type = CategoricalDtype(categories=time_order, ordered=True)
        df['time_of_day'] = df['time_of_day'].astype(cat_type)

        # df['am_pm'] = df['begin_time'].dt.hour.map(get_am_pm)
        # am_pm_order = ['AM', 'PM']
        # cat_type = CategoricalDtype(categories=am_pm_order, ordered=True)
        # df['am_pm'] = df['am_pm'].astype(cat_type)

        grouped = df.groupby(['source_node', 'common_name', 'scientific_name']).agg(
            observations=('id', 'count'),
            avg_confidence=('confidence', 'mean'),
            times_seen = ('time_of_day', lambda x: sorted(set(x.dropna()), key=time_order.index))
        ).reset_index()

        grouped = grouped[grouped['observations'] >= min_observations]

        grouped = grouped.sort_values(
            by=['source_node', 'observations'],
            ascending=[False, False]
        )

        # await event.app.rest.create_message(channel=int(os.environ.get("UPDATE_CHANNEL_ID")), content=str(grouped)[0:1999])

        lines = ['>>> # 🐦 Daily BirdNET report']

        for source_node in grouped['source_node'].unique():
            lines.append(f"## Node: `{source_node}`")
            source_data = grouped[grouped['source_node'] == source_node]

            for _, row in source_data.iterrows():
                lines.append(
                    # f"**{row['common_name']}** (*{row['scientific_name']}*)\n"
                    # f"    Observations: {row['observations']}\n"
                    # f"    Average confidence: {round(row['avg_confidence'] * 100):d}%\n"
                    # f"    Seen: {', '.join(row['times_seen'])}"
                    f"**{row['common_name']}** (*{row['scientific_name']}*)\n"
                    f"-#\t`n={row['observations']}` `conf={round(row['avg_confidence'] * 100):d}%`"
                    f" `seen: {', '.join(row['times_seen'])}`\n"
                )

            # embed.add_field(name=f"Node: {source_node}", value='\n'.join(lines), inline=True)

        # print('\n'.join(lines))

        message = '\n'.join(lines)

        chunks = split_message(message)
        for chunk in chunks:
            await event.app.rest.create_message(
                channel=int(os.environ.get("UPDATE_CHANNEL_ID")),
                content=chunk)

    async def aggregate_scheduler():
        while True:
            now = datetime.datetime.now()
            target = now.replace(hour=22, minute=0, second=0, microsecond=0)
            if now >= target:
                target += datetime.timedelta(days=1)
            await asyncio.sleep((target - now).total_seconds())

            await send_daily_aggregate()

    asyncio.create_task(aggregate_scheduler())
    # await send_daily_aggregate()

@tanjun.as_loader
def load_component(client: tanjun.Client) -> None:
    client.add_component(component)