import hikari
from pymongo import MongoClient
import datetime


class Database:
    def __init__(self):
        self.client = MongoClient('mongodb://root:kirby@kirby_db:27017/')
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

    def log_message(
            self,
            event: hikari.GuildMessageCreateEvent
    ) -> None:
        message = {
            '_id': event.message_id,
            'author': event.author_id,
            'time': datetime.datetime.utcnow(),
            'channel': event.channel_id,
            'guild': event.guild_id,
            'content': event.content,
        }

        self.messages.insert_one(message)

    def get_messages(
            self,
            member: hikari.User = None,
            guild: int = None,
            channel: hikari.InteractionChannel = None,
    ) -> list:
        filter_dict = {}
        if member is not None:
            filter_dict['author'] = member.id

        if channel is not None:
            filter_dict['channel'] = channel.id

        if guild is not None:
            filter_dict['guild'] = guild

        return [msg['content'] for msg in self.messages.find(
            filter_dict,
            {'_id': 0, 'content': 1}
        )]

    def update_permissions(self, member: hikari.User, read_messages: bool):
        self.permissions.update_one(
            {'_id': member.id},
            {'$set': {'read_messages': read_messages}},
            upsert=True
        )

    def check_read_permission(self, member: hikari.User):
        read_permission = self.permissions.find_one({'_id': member.id})
        if read_permission is not None:
            return read_permission['read_messages']
        else:
            return False

    def delete_by_user(self, member: hikari.User):
        deletion = self.messages.delete_many({'author': member.id})
        return deletion.deleted_count
