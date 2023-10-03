import json.decoder

import PySimpleGUI as sg
import pyperclip
from robotkirby.db.local_db_driver import Database
from robotkirby.plugins import sentient

if __name__ == '__main__':
    my_database = Database()
    message_count = my_database.messages.count_documents({})
    database_initialized = False if message_count == 0 else True
    print(f'database initialized: {database_initialized}')

    guilds = []
    guild_names = []
    members = []
    member_names = []
    channels = []
    channel_names = []

    guild_list = []
    member_list = ['None']
    channel_list = ['None']

    # get combo options
    if database_initialized:
        members, member_ids, member_names = my_database.get_members()
        member_list.extend(member_names)
        member_list = list(dict.fromkeys(member_list))

        guilds, guild_ids, guild_names = my_database.get_guilds()
        guild_list.extend(guild_names)
        guild_list = list(dict.fromkeys(guild_list))

        channels, channel_ids, channel_names = my_database.get_channels()
        channel_list.extend(channel_names)
        channel_list = list(dict.fromkeys(channel_list))

    sg.theme('DarkAmber')
    layout = [[sg.Text('Robot Kirby Local')],
              [sg.Text('Guild:'), sg.Combo(key='-GUILD-', values=guild_list, default_value=guild_list[0])],
              [sg.Text('Member:'), sg.Combo(key='-MEMBER-', values=member_list, default_value=member_list[0])],
              [sg.Text('Channel:'), sg.Combo(key='-CHANNEL-', values=channel_list, default_value=channel_list[0])],
              [sg.Button(key='Opinion', button_text='Opinion'), sg.Input(key='-OPINION-')],
              [sg.Button(key='Sentient', button_text='Sentient'), sg.Text(key='-SENTIENT-', text='')],
              [sg.Button(key='Time Density', button_text='Time Density')],
              [sg.Button(key='Word Cloud', button_text='Word Cloud')],
              [sg.FileBrowse(button_text='Open Discord JSON', target='filebrowse_field'),
               sg.Input(key='filebrowse_field', default_text=''), sg.Button(key='load_db', button_text='LOAD')],
              [sg.Button(key='Clear', button_text='Clear Database'), sg.Text(text="Loaded: "), sg.Text(key='-N-ENTRIES-', text=message_count)]]

    window = sg.Window('Window Title', layout)

    last_folder = ''
    while True:
        event, values = window.read()

        guild = None if values['-GUILD-'] == 'None' else guilds[guild_names.index(values['-GUILD-'])]
        member = None if values['-MEMBER-'] == 'None' else members[member_names.index(values['-MEMBER-'])]
        channel = None if values['-CHANNEL-'] == 'None' else channels[channel_names.index(values['-CHANNEL-'])]

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
                member_ids, member_names = my_database.get_members()
                member_list.extend(member_names)
                member_list = list(set(member_list))
                window['-MEMBER-'].update(values=member_list, value=member_list[0])

            except json.decoder.JSONDecodeError:
                print('NOT VALID JSON FILE')
                # otherwise
                # window['Folder'].update('FAILED to load this as a database')
        if not database_initialized:
            continue  # nothing past this works without a database initialized
        if event == 'Clear':
            my_database.clear_database()
            message_count = my_database.messages.count_documents({})
            database_initialized = False if message_count == 0 else True
            window['-N-ENTRIES-'].update(message_count)
        if event == 'Opinion':
            print('good')
        elif event == 'Sentient':
            # generate output
            output = sentient.sentient(guild, member, channel, my_database)
            print(output)
            try:
                pyperclip.copy(output)  # try to put output on clipboard
            except:
                pass
            window['-SENTIENT-'].update(output)  # show in GUI
        elif event == 'Time Density':
            # generate time density graph
            # show graph
            print('___,,.--.,_,.,--.,,__')
            # put image on clipboard
            # give option to save
        elif event == 'Word Cloud':
            # generate word cloud
            # show word cloud
            print('oOOoo oOOOo')
            # put image on clipboard
            # give option to save

    window.close()
