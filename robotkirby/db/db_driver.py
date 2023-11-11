import hikari
from pymongo import MongoClient, TEXT
import datetime
import logging
import os


class Database:
    def __init__(self):
        self.client = MongoClient(os.environ.get('MONGO_URI'))
        self.db = self.client.kirby
        self.messages = self.db.messages
        self.permissions = self.db.permissions

        # create compound index with `guild` as the prefix since we will always include this
        # efficient for [guild], [guild, author], [guild, author, channel]
        # less efficient at [guild, channel]
        self.messages.create_index([('guild', 1), ('author', 1), ('channel', 1)])

        # create index for [guild, channel] to address the previously mentioned limitation
        # the optimizer doesn't use this one I think, IDK why
        self.messages.create_index([('guild', 1), ('channel', 1)])

        # cursed
        self.messages.create_index([('content', TEXT)], default_language='english')

    def log_message(self, event: hikari.GuildMessageCreateEvent) -> None:
        message = {
            '_id': event.message_id,
            'author': event.author_id,
            'time': datetime.datetime.utcnow(),
            'channel': event.channel_id,
            'guild': event.guild_id,
            'content': event.content,
        }

        self.messages.insert_one(message)

    def delete_message(self, event: hikari.GuildMessageDeleteEvent) -> None:
        self.messages.delete_one(
            {'_id': event.message_id}
        )

    def update_message(self, event: hikari.GuildMessageUpdateEvent) -> None:
        self.messages.update_one(
            {'_id': event.message_id},
            {'$set': {'content': event.content}},
        )

    @staticmethod
    def _get_filter_dict(
            member: hikari.User = None,
            guild: int = None,
            channel: hikari.InteractionChannel = None,
            text: str = None
    ) -> dict:
        filter_dict = {}
        if member is not None:
            filter_dict['author'] = member.id

        if guild is not None:
            filter_dict['guild'] = guild

        if channel is not None:
            filter_dict['channel'] = channel.id

        if text is not None:
            filter_dict['$text'] = {'$search': text}

        return filter_dict

    def get_messages(
            self,
            since: datetime.datetime = None,
            before: datetime.datetime = None,
            member: hikari.User = None,
            guild: int = None,
            channel: hikari.InteractionChannel = None,
            text: str = None
    ) -> list[str]:
        filter_dict = self._get_filter_dict(member=member, guild=guild, channel=channel, text=text)
        if since is not None:
            filter_dict['time'] = {"$gte": since}

        if before is not None:
            filter_dict['time'] = {"$lt": since}

        return [msg['content'] for msg in self.messages.find(
            filter_dict,
            {'_id': 0, 'content': 1}
        )]

    def get_channels(
            self,
            since: datetime.datetime = None,
            before: datetime.datetime = None,
            member: hikari.User = None,
            guild: int = None,
            channel: hikari.InteractionChannel = None,
            text: str = None
    ) -> list[str]:
        filter_dict = self._get_filter_dict(member=member, guild=guild, channel=channel, text=text)
        if since is not None:
            filter_dict['time'] = {"$gte": since}

        if before is not None:
            filter_dict['time'] = {"$lt": since}

        return [msg['channel'] for msg in self.messages.find(
            filter_dict,
            {'_id': 0, 'channel': 1}
        )]

    def get_timestamps(
            self,
            since: datetime.datetime = None,
            before: datetime.datetime = None,
            member: hikari.User = None,
            guild: int = None,
            channel: hikari.InteractionChannel = None,
            text: str = None
    ) -> list[datetime.datetime]:
        filter_dict = self._get_filter_dict(member, guild, channel, text)

        if since is not None:
            filter_dict['time'] = {"$gte": since}

        if before is not None:
            filter_dict['time'] = {"$lt": since}

        return [msg['time'] for msg in self.messages.find(
            filter_dict,
            {'_id': 0, 'time': 1}
        )]

    def update_permissions(self, member: hikari.User, read_messages: bool) -> None:
        self.permissions.update_one(
            {'_id': member.id},
            {'$set': {'read_messages': read_messages}},
            upsert=True
        )

    def check_read_permission(self, member: hikari.User) -> bool:
        read_permission = self.permissions.find_one({'_id': member.id})
        if read_permission is not None:
            return read_permission['read_messages']
        else:
            return False

    def get_active_user_ids(self) -> list[str]:
        return [user['_id'] for user in self.permissions.find(
            {'read_messages': True},
            {'_id': 1, 'read_messages': 0}
        )]

    def delete_many(
        self,
        member: hikari.User = None,
        guild: int = None,
        channel: hikari.InteractionChannel = None,
        text: str = None
    ) -> int:
        filter_dict = self._get_filter_dict(member=member, guild=guild, channel=channel, text=text)

        deletion = self.messages.delete_many(filter_dict)
        return deletion.deleted_count
