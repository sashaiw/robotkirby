import hikari
from pymongo import MongoClient
import datetime


class Database:
    def __init__(self):
        self.client = MongoClient('mongodb://root:kirby@kirby_db:27017/')
        self.db = self.client.kirby
        self.messages = self.db.messages
        self.permissions = self.db.permissions

    def log_message(
            self,
            event: hikari.GuildMessageCreateEvent
    ) -> None:
        message = {
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
        return self.permissions.find_one({'_id': member.id})['read_messages']

    def delete_by_user(self, member: hikari.User):
        deletion = self.messages.delete_many({'author': member.id})
        return deletion.deleted_count
