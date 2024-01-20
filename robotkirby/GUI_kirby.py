import json.decoder

import PySimpleGUI as sg
import pyperclip
from robotkirby.db.local_db_driver import Database
from robotkirby.local_plugins import sentient, timedensity, opinion, my_wordcloud

import emoji

if __name__ == '__main__':
    my_database = Database()
    message_count = my_database.messages.count_documents({})
    database_initialized = False if message_count == 0 else True
    print(f'database initialized: {database_initialized}')

    guilds = []
    guild_names = []

    channels = []
    channel_names = []

    members = []
    member_names = []

    guild_list = ['None']
    member_list = ['None']
    channel_list = ['None']

    # get combo options
    if database_initialized:
        guilds, guild_ids, guild_names = my_database.get_guilds()
        guild_list = guild_names

        channels, channel_ids, channel_names = my_database.get_channels(guild=guilds[0])
        channel_list = channel_names

        members, member_ids, member_names = my_database.get_members(guild=guilds[0], channel=None)
        member_list = member_names

    sg.theme('DarkAmber')
    layout = [[sg.Text('Robot Kirby Local')],
              [sg.Text('Guild:'), sg.Combo(key='-GUILD-', size=(35, 10), enable_events=True, values=guild_list, default_value=guild_list[0])],
              [sg.Text('Channel:'), sg.Combo(key='-CHANNEL-', size=(35, 10), enable_events=True, values=channel_list, default_value=channel_list[0])],
              [sg.Text('Member:'), sg.Combo(key='-MEMBER-', size=(35, 10), values=member_list, default_value=member_list[0])],
              [sg.Text('Topic:'), sg.Input(key='-TOPIC-')],
              [sg.Button(key='Opinion', button_text='Opinion'), sg.Text(key='-OPINION-', text='', font=())],
              [sg.Button(key='Sentient', button_text='Sentient'), sg.Text(key='-SENTIENT-', text='', font=())],
              [sg.Button(key='Time Density', button_text='Time Density'), sg.Text(key='-TIMEDENSITY-', text='', font=())],
              [sg.Button(key='Word Cloud', button_text='Word Cloud'), sg.Text(key='-WORDCLOUD-', text='', font=())],
              [sg.FileBrowse(button_text='Open Discord JSON', target='filebrowse_field'),
               sg.Input(key='filebrowse_field', default_text=''), sg.Button(key='load_db', button_text='LOAD')],
              [sg.Button(key='Clear', button_text='Clear Database'), sg.Text(text="Loaded: "), sg.Text(key='-N-ENTRIES-', text=message_count)]]

    window = sg.Window('Window Title', layout)

    last_folder = ''
    while True:
        event, values = window.read()

        guild = None if values['-GUILD-'] == 'None' else guilds[guild_names.index(values['-GUILD-'])]
        channel = None if values['-CHANNEL-'] == 'None' else channels[channel_names.index(values['-CHANNEL-'])]
        member = None if values['-MEMBER-'] == 'None' else members[member_names.index(values['-MEMBER-'])]
        topic = None if values['-TOPIC-'] == '' else values['-TOPIC-']

        if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
            break
        if event == 'load_db':
            folder_filepath = values['filebrowse_field']
            # try to initialize a db from JSON file given
            try:
                my_database.load_json(folder_filepath)
                # if successful
                message_count = my_database.messages.count_documents({})
                database_initialized = False if message_count == 0 else True
                window['-N-ENTRIES-'].update(message_count)

                # update possible guild, member, and channel values
                guilds, guild_ids, guild_names = my_database.get_guilds()
                guild_list = guild_names
                window['-GUILD-'].update(values=guild_list, value=guild_list[0])

                guild = guilds[guild_names.index(guild_list[0])]

                channels, channel_ids, channel_names = my_database.get_channels(guild=guild)
                channel_list = channel_names
                window['-CHANNEL-'].update(values=channel_list, value=channel_list[0])

                channel = channels[channel_names.index(channel_list[0])]

                members, member_ids, member_names = my_database.get_members(guild, channel)
                member_list = member_names
                window['-MEMBER-'].update(values=member_list, value=member_list[0])

            except json.decoder.JSONDecodeError:
                print('NOT VALID JSON FILE')
                # otherwise
                # window['Folder'].update('FAILED to load this as a database')
        if not database_initialized:
            continue  # nothing past this works without a database initialized
        if event == '-GUILD-':  # change guild
            guild = None if values['-GUILD-'] == 'None' else guilds[guild_names.index(values['-GUILD-'])]

            # update channel list
            channels, channel_ids, channel_names = my_database.get_channels(guild=guild)
            channel_list = channel_names
            window['-CHANNEL-'].update(values=channel_list, value=channel_list[0])

            channel = channels[channel_names.index(channel_list[0])]

            # update member list
            members, member_ids, member_names = my_database.get_members(guild=guild, channel=channel)
            member_list = member_names
            window['-MEMBER-'].update(values=member_list, value=member_list[0])
        elif event == '-CHANNEL-':  # change channel
            channel = None if values['-CHANNEL-'] == 'None' else channels[channel_names.index(values['-CHANNEL-'])]

            # update member list
            members, member_ids, member_names = my_database.get_members(guild=guild, channel=channel)
            member_list = member_names
            window['-MEMBER-'].update(values=member_list, value=member_list[0])
        elif event == 'Clear':
            my_database.clear_database()
            message_count = my_database.messages.count_documents({})
            database_initialized = False if message_count == 0 else True
            window['-N-ENTRIES-'].update(message_count)
            window['-GUILD-'].update(values=['None'], value='None')
            window['-CHANNEL-'].update(values=['None'], value='None')
            window['-MEMBER-'].update(values=['None'], value='None')
        elif event == 'Opinion':
            output = opinion.opinion(guild, topic, member, channel, db=my_database)
            output = emoji.demojize(output)
            window['-OPINION-'].update(output)
        elif event == 'Sentient':
            # generate output
            output = sentient.sentient(guild, member, channel, my_database)
            print(output)
            output = "" if output is None else output
            output = emoji.demojize(output)
            try:
                pyperclip.copy(output)  # try to put output on clipboard
            except:
                pass
            window['-SENTIENT-'].update(output)  # show in GUI
        elif event == 'Time Density':
            # generate time density graph
            output = timedensity.timedensity(guild, topic, member, channel, timezone='EST', db=my_database)
            print(output)
            output = "" if output is None else output
            output = emoji.demojize(output)
            window['-TIMEDENSITY-'].update(output)
            # put image on clipboard
            # give option to save
        elif event == 'Word Cloud':
            # generate word cloud
            output = my_wordcloud.wordcloud(guild, member, channel, db=my_database)
            # output= "aw mann"
            print(output)
            output = "" if output is None else output
            output = emoji.demojize(output)
            window['-WORDCLOUD-'].update(output)
            # show word cloud
            print('oOOoo oOOOo')
            # put image on clipboard
            # give option to save

    window.close()
