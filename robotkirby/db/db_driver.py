import datetime
import os
from typing import Any, Optional

import hikari
from pymongo import TEXT, MongoClient
from pymongo.collection import Collection
from pymongo.database import Database as PyMongoDatabase


class Database:
    def __init__(self):
        self.client: MongoClient[dict[str, Any]] = MongoClient(
            os.environ.get("MONGO_URI")
        )
        self.db: PyMongoDatabase[dict[str, Any]] = self.client.kirby
        self.messages: Collection[dict[str, Any]] = self.db.messages
        self.permissions: Collection[dict[str, Any]] = self.db.permissions

        # create compound index with `guild` as the prefix since we will always include this
        # efficient for [guild], [guild, author], [guild, author, channel]
        # less efficient at [guild, channel]
        self.messages.create_index([("guild", 1), ("author", 1), ("channel", 1)])

        # create index for [guild, channel] to address the previously mentioned limitation
        # the optimizer doesn't use this one I think, IDK why
        self.messages.create_index([("guild", 1), ("channel", 1)])

        # cursed
        self.messages.create_index([("content", TEXT)], default_language="english")

    def log_message(self, event: hikari.GuildMessageCreateEvent) -> None:
        message = {
            "_id": event.message_id,
            "author": event.author_id,
            "time": datetime.datetime.utcnow(),
            "channel": event.channel_id,
            "guild": event.guild_id,
            "content": event.content,
        }

        self.messages.insert_one(message)

    def delete_message(self, event: hikari.GuildMessageDeleteEvent) -> None:
        self.messages.delete_one({"_id": event.message_id})

    def update_message(self, event: hikari.GuildMessageUpdateEvent) -> None:
        self.messages.update_one(
            {"_id": event.message_id},
            {"$set": {"content": event.content}},
        )

    @staticmethod
    def _get_filter_dict(
        since: Optional[datetime.datetime] = None,
        before: Optional[datetime.datetime] = None,
        member: Optional[hikari.User | int] = None,
        guild: Optional[int] = None,
        channel: Optional[hikari.InteractionChannel] = None,
        text: Optional[str] = None,
    ) -> dict[str, Any]:
        filter_dict: dict[str, Any] = {}
        if member is not None:
            if isinstance(member, hikari.User):
                filter_dict["author"] = member.id
            if isinstance(member, int):
                filter_dict["author"] = member

        if guild is not None:
            filter_dict["guild"] = guild

        if channel is not None:
            filter_dict["channel"] = channel.id

        if text is not None:
            filter_dict["$text"] = {"$search": text}

        time_filter: dict[str, Any] = {}
        if since is not None:
            time_filter["$gte"] = since
        if before is not None:
            time_filter["$lt"] = before
        if time_filter:
            filter_dict["time"] = time_filter

        return filter_dict

    def get_messages(
        self,
        since: Optional[datetime.datetime] = None,
        before: Optional[datetime.datetime] = None,
        member: Optional[hikari.User | int] = None,
        guild: Optional[int] = None,
        channel: Optional[hikari.InteractionChannel] = None,
        text: Optional[str] = None,
    ) -> list[str]:
        filter_dict = self._get_filter_dict(
            member=member,
            guild=guild,
            channel=channel,
            text=text,
            since=since,
            before=before,
        )

        return [
            msg["content"]
            for msg in self.messages.find(filter_dict, {"_id": 0, "content": 1})
        ]

    def get_channels(
        self,
        since: Optional[datetime.datetime] = None,
        before: Optional[datetime.datetime] = None,
        member: Optional[hikari.User | int] = None,
        guild: Optional[int] = None,
        channel: Optional[hikari.InteractionChannel] = None,
        text: Optional[str] = None,
    ) -> list[int]:
        filter_dict = self._get_filter_dict(
            member=member,
            guild=guild,
            channel=channel,
            text=text,
            since=since,
            before=before,
        )

        return [
            msg["channel"]
            for msg in self.messages.find(filter_dict, {"_id": 0, "channel": 1})
        ]

    def get_timestamps(
        self,
        since: Optional[datetime.datetime] = None,
        before: Optional[datetime.datetime] = None,
        member: Optional[hikari.User | int] = None,
        guild: Optional[int] = None,
        channel: Optional[hikari.InteractionChannel] = None,
        text: Optional[str] = None,
    ) -> list[datetime.datetime]:
        filter_dict = self._get_filter_dict(
            member=member,
            guild=guild,
            channel=channel,
            text=text,
            since=since,
            before=before,
        )

        return [
            msg["time"]
            for msg in self.messages.find(filter_dict, {"_id": 0, "time": 1})
        ]

    def update_permissions(self, member: hikari.User, read_messages: bool) -> None:
        self.permissions.update_one(
            {"_id": member.id}, {"$set": {"read_messages": read_messages}}, upsert=True
        )

    def check_read_permission(self, member: hikari.User) -> bool:
        read_permission = self.permissions.find_one({"_id": member.id})
        if read_permission is not None:
            return read_permission["read_messages"]
        else:
            return False

    def get_all_opted_in_user_ids(self, guild: Optional[int] = None) -> list[int]:
        return [
            int(user["_id"])
            for user in self.permissions.find(
                {"read_messages": True}, {"_id": 1, "read_messages": 0}
            )
        ]

    def get_unique_user_ids(
        self,
        guild: Optional[int] = None,
        channel: Optional[hikari.InteractionChannel] = None,
        since: Optional[datetime.datetime] = None,
        before: Optional[datetime.datetime] = None,
    ) -> list[int]:
        filter_dict = self._get_filter_dict(
            guild=guild,
            channel=channel,
            since=since,
            before=before,
        )

        vals = list(self.messages.distinct("author", filter_dict))
        return [int(v) for v in vals]

    def delete_many(
        self,
        member: Optional[hikari.User] = None,
        guild: Optional[int] = None,
        channel: Optional[hikari.InteractionChannel] = None,
        text: Optional[str] = None,
    ) -> int:
        filter_dict = self._get_filter_dict(
            member=member, guild=guild, channel=channel, text=text
        )

        deletion = self.messages.delete_many(filter_dict)
        return deletion.deleted_count
