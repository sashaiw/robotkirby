import PySimpleGUI as sg
import pyperclip

member_list = ['all', 'amelia', 'sammy']
channel_list = ['all', 'general', ]

sg.theme('DarkAmber')
layout = [[sg.Text('Robot Kirby Local')],
            [sg.Text('Member:'), sg.Combo(key='-MEMBER-', values=member_list, default_value=member_list[0])],
            [sg.Text('Channel:'), sg.Combo(key='-CHANNEL-', values=channel_list, default_value=channel_list[0])],
            [sg.Button(key='Opinion', button_text='Opinion'), sg.Input(key='-OPINION-')],
            [sg.Button(key='Sentient', button_text='Sentient'), sg.Text(key='-SENTIENT-', text='')],
            [sg.Button(key='Time Density', button_text='Time Density')],
            [sg.Button(key='Word Cloud', button_text='Word Cloud')],
            [sg.FolderBrowse(button_text='Open Folder with Discord Messages', key='-FOLDER-'), sg.Text(key='Folder', text='')]]

window = sg.Window('Window Title', layout)

if __name__ == '__main__':
    database_initialized = False
    last_folder = ''
    while True:
        event, values = window.read()
        member = values['-MEMBER-']
        channel = values['-CHANNEL-']

        if member == 'all':
            member = None
        if channel == 'all':
            channel = None

        if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
            break
        if values['-FOLDER-'] != last_folder:  # if new database selected
            folder_filepath = values['-FOLDER-']
            # try to initialize a db from folder given
            # initialize_db()  # converts folder of discord msgs into mongodb
            # if successful
            window['Folder'].update(values['-FOLDER-'])  # show file path
            database_initialized = True
            # otherwise
            # window['Folder'].update('FAILED to load this as a database')
        if not database_initialized:
            continue  # nothing past this works without a database initialized
        if event == 'Opinion':
            print('good')
        elif event == 'Sentient':
            # generate output
            output = 'sample sentence'
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
