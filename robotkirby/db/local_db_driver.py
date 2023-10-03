import bson
import hikari
import pymongo.errors
from pymongo import MongoClient, TEXT
import datetime
import json
import logging
import os


class Database:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['kirby']  # create our database
        self.messages = self.db.messages
        # self.permissions = self.db.permissions

        # create compound index with `guild` as the prefix since we will always include this
        # efficient for [guild], [guild, author], [guild, author, channel]
        # less efficient at [guild, channel]
        self.messages.create_index([('guild', 1), ('author', 1), ('channel', 1)])

        # create index for [guild, channel] to address the previously mentioned limitation
        # the optimizer doesn't use this one I think, IDK why
        self.messages.create_index([('guild', 1), ('channel', 1)])

        # cursed
        self.messages.create_index([('content', TEXT)], default_language='english')

    def clear_database(self):
        self.client.drop_database('kirby')

    def load_json(self, json_data):
        n = 0
        with open(json_data, 'r') as jsonfile:
            data = json.load(jsonfile)
            guild_id = int(data['guild']['id'])
            guild_name = data['guild']['name']
            channel_id = int(data['channel']['id'])
            channel_name = data['channel']['name']
            print('loading messages...')
            for message in data['messages']:
                _id = int(message['id'])
                author_id = int(message['author']['id'])
                author_nick = message['author']['nickname']
                try:
                    time = datetime.datetime.strptime(message['timestamp'], '%Y-%m-%dT%H:%M:%S.%f%z')
                except ValueError:
                    time = datetime.datetime.strptime(message['timestamp'], '%Y-%m-%dT%H:%M:%S%z')
                content = message['content']
                if isinstance(author_id, str):
                    print("????")
                my_message = {'_id': _id, 'author': {'id': author_id, 'name': author_nick}, 'time': time,
                              'channel': {'id': channel_id, 'name': channel_name},
                              'guild': {'id': guild_id, 'name': guild_name}, 'content': content}
                try:
                    self.messages.insert_one(my_message)
                except pymongo.errors.DuplicateKeyError:
                    continue
                    # n += 1
                    # print()
                    # print(f"Duplicate Key Instance #{n}")
                    # print(self.messages.find_one({'_id': _id}))
                    # print(my_message)
                    pass
            print(f'done loading {self.messages.count_documents({})} messages!')

    @staticmethod
    def _get_filter_dict(member, guild, channel, text) -> dict:
        filter_dict = {}
        if member is not None:
            filter_dict['author'] = member

        if guild is not None:
            filter_dict['guild'] = guild

        if channel is not None:
            filter_dict['channel'] = channel

        if text is not None:
            filter_dict['$text'] = {'$search': text}

        return filter_dict

    def get_messages(self, member, guild, channel, text) -> list[str]:
        filter_dict = self._get_filter_dict(member=member, guild=guild, channel=channel, text=text)

        return [msg['content'] for msg in self.messages.find(
            filter_dict,
            {'_id': 0, 'content': 1}
        )]

    def get_timestamps(self, member, guild, channel, text) -> list[datetime.datetime]:
        filter_dict = self._get_filter_dict(member, guild, channel, text)

        return [msg['time'] for msg in self.messages.find(
            filter_dict,
            {'_id': 0, 'time': 1}
        )]

    def get_guilds(self):
        guilds = self.messages.distinct('guild')

        guild_id_list = []
        guild_name_list = []
        for guild in guilds:
            guild_id = guild['id']
            guild_name = guild['name']
            if guild_id not in guild_id_list:
                guild_id_list.append(guild_id)
                guild_name_list.append(guild_name)
        return guilds, guild_id_list, guild_name_list

    def get_members(self):
        members = self.messages.distinct('author')

        member_id_list = []
        member_name_list = []
        for member in members:
            member_id = member['id']
            member_name = member['name']
            if member_id not in member_id_list:
                member_id_list.append(member_id)
                member_name_list.append(member_name)
        return members, member_id_list, member_name_list

    def get_channels(self):
        channels = self.messages.distinct('channel')

        channel_id_list = []
        channel_name_list = []
        for channel in channels:
            channel_id = channel['id']
            channel_name = channel['name']
            if channel_id not in channel_id_list:
                channel_id_list.append(channel_id)
                channel_name_list.append(channel_name)
        return channels, channel_id_list, channel_name_list
