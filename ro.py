import json
import keyboard
import os
import platform
import subprocess
import sys
import time
import tkinter as tk

from queue import Empty, Queue
from roku import Roku
from threading import Thread


def load_settings():
    if os.path.isfile('settings.json'):
        with open('settings.json', 'r') as settings_file:
            settings = json.load(settings_file)
    else:
        settings = {
            'font': 'Roboto',
            'colors': {
                'text': '#ebe2f3',
                'light': '#5a3382',
                'dark': '#352552',
                'power': '#ba2323',
                'app': '#2c345c'
            },
            'win_w': 420,
            'win_h': 462
        }
    return settings


def save_settings(settings):
    with open('settings.json', 'w+') as  settings_file:
        json.dump(settings, settings_file)


def config_grids(widget, rows=[1], columns=[1]):
    [widget.rowconfigure(i, weight=weight) for i, weight in enumerate(rows)]
    [widget.columnconfigure(i, weight=weight)
        for i, weight in enumerate(columns)]


def click_button(button):
    button.config()
    button.invoke()


def check_queue(master):
    try:
        item = master.queue.get(block=False)
    except Empty:
        pass # nothing in the queue


def close_window(root):
    w = root.winfo_width()
    h = root.winfo_height() + 20
    x = root.winfo_x()
    y = root.winfo_y()
    root.settings.update({
        'win_w': w,
        'win_h': h,
        'win_x': x,
        'win_y': y
    })
    save_settings(root.settings)
    root.destroy()


class Worker(Thread):
    def __init__(self, url):
        super().__init__()

        self.running = True

        self.queue = Queue()


    def run(self):
        while self.running:
            check_queue(self)
            time.sleep(0.5)


class Menubar(tk.Menu):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.main_menu = tk.Menu(self, tearoff=0)
        self.main_menu.add_command(label='Restart', command=self.restart)
        self.main_menu.add_command(label='Quit', command=self.quit)

        self.devices_menu = tk.Menu(self, tearoff=0)
        self.devices_menu.add_command(
            label='Add device', command=self.scan_devices
        )

        self.add_cascade(label='Main', menu=self.main_menu)
        self.add_cascade(label='Devices', menu=self.devices_menu)


    def quit(self):
        self.master.cont = False
        close_window(self.master.master)


    def restart(self):
        self.quit()
        self.master.restart_flag = True


    def scan_devices(self):
        print(Roku.discover(timeout=30))


def get_geometry(settings):
    if all([(key in settings) for key in ['win_x', 'win_y']]):
        geometry = '{}x{}+{}+{}'.format(
            settings['win_w'], settings['win_h'],
            settings['win_x'], settings['win_y']
        )
    else:
        geometry = '{}x{}'.format(settings['win_w'], settings['win_h'])
    return geometry


class MainWindow(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master

        settings = self.master.settings
        font = settings['font']

        text = settings['colors']['text']
        light = settings['colors']['light']
        dark = settings['colors']['dark']
        power = settings['colors']['power']
        app = settings['colors']['app']

        size = 20

        flat = {
            'relief': 'solid', 'bd': 1,
            'activebackground': '#ffffff', 'activeforeground': '#ffffff'
        }
        font = {**flat, 'font': [font, size], 'fg': text, 'bg': dark}
        arrow = {**flat, 'font': [font, size], 'fg': text, 'bg': light}
        app = {**flat, 'font': [font, size], 'fg': text, 'bg': app}
        power = {**flat, 'font': [font, 30], 'fg': text, 'bg': power}

        def set_active_bg(f):
            f['activebackground'] = f['bg']

        [set_active_bg(f) for f in [font, arrow, app, power]]

        self.roku = Roku('192.168.1.144')

        self.master.title('Roku Remote')

        self.pack(fill=tk.BOTH, expand=True)

        config_grids(self, rows=[1, 1, 1, 1, 1, 1], columns=[1, 1, 1, 1])

        self.restart_flag = False

        self.back_button = tk.Button(
            self, **font, text=u'\u2B60', command=self.roku.back
        )
        self.back_button.grid(row=0, column=1, sticky='nsew')

        self.up_button = tk.Button(
            self, **arrow, text=u'\u2B9D', command=self.roku.up
        )
        self.up_button.grid(row=0, column=2, sticky='nsew')

        self.home_button = tk.Button(
            self, **font, text=u'\u2302', command=self.roku.home
        )
        self.home_button.grid(row=0, column=3, sticky='nsew')

        self.left_button = tk.Button(
            self, **arrow, text=u'\u2B9C', command=self.roku.left
        )
        self.left_button.grid(row=1, column=1, sticky='nsew')

        self.select_button = tk.Button(
            self, **arrow, text='OK', command=self.roku.select
        )
        self.select_button.grid(row=1, column=2, sticky='nsew')

        self.right_button = tk.Button(
            self, **arrow, text=u'\u2B9E', command=self.roku.right
        )
        self.right_button.grid(row=1, column=3, sticky='nsew')

        self.replay_button = tk.Button(
            self, **font, text=u'\u27F2', command=self.roku.replay
        )
        self.replay_button.grid(row=2, column=1, sticky='nsew')

        self.down_button = tk.Button(
            self, **arrow, text=u'\u2B9F', command=self.roku.down
        )
        self.down_button.grid(row=2, column=2, sticky='nsew')

        self.options_button = tk.Button(
            self, **font, text=u'\u273C', command=self.roku.info
        )
        self.options_button.grid(row=2, column=3, sticky='nsew')

        self.rewind_button = tk.Button(
            self, **font, text=u'\u23EA', command=self.roku.reverse
        )
        self.rewind_button.grid(row=3, column=1, sticky='nsew')

        self.pause_play_button = tk.Button(
            self, **font, text=u'\u25B6\u2758\u2758',
            command=self.roku.play
        )
        self.pause_play_button.grid(row=3, column=2, sticky='nsew')

        self.fast_forward_button = tk.Button(
            self, **font, text=u'\u23E9', command=self.roku.forward
        )
        self.fast_forward_button.grid(row=3, column=3, sticky='nsew')

        self.volume_mute_button = tk.Button(
            self, **font, text='MUTE', command=self.roku.volume_mute, width=20
        )
        self.volume_mute_button.grid(row=4, column=1, sticky='nsew')

        self.volume_down_button = tk.Button(
            self, **font, text='VOL-', command=self.roku.volume_down, width=20
        )
        self.volume_down_button.grid(row=4, column=2, sticky='nsew')

        self.volume_up_button = tk.Button(
            self, **font, text='VOL+', command=self.roku.volume_up, width=20
        )
        self.volume_up_button.grid(row=4, column=3, sticky='nsew')

        self.search_button = tk.Button(
            self, **font, text=u'\u2315', command=self.roku.search, width=20
        )
        self.search_button.grid(row=5, column=0, sticky='nsew')

        self.search_var = tk.StringVar()
        self.previous_text = ''
        self.search_var.trace('w', self.send_text)

        self.search_frame = tk.Frame(self, bg='#000000', bd=1)
        #self.search_frame.grid(row=5, column=1, columnspan=2, sticky='nsew')
        config_grids(self.search_frame)

        self.build_search_input()

        self.backspace_button = tk.Button(
            self, **font, text='DEL', command=self.roku.backspace
        )
        self.backspace_button.grid(row=5, column=3, sticky='nsew')

        self.power_button = tk.Button(
            self, **power, text=u'\u23FB', command=self.roku.power
        )
        self.power_button.grid(row=0, column=0, rowspan=2, sticky='nsew')

        self.computer_button = tk.Button(
            self, **app, text='PC', command=lambda: self.launch_app('computer')
        )
        self.computer_button.grid(row=2, column=0, sticky='nsew')

        self.plex_button = tk.Button(
            self, **app, text='PLEX', command=lambda: self.launch_app('plex')
        )
        self.plex_button.grid(row=3, column=0, sticky='nsew')

        self.ps4_button = tk.Button(
            self, **app, text='PS4', command=lambda: self.launch_app('playstation')
        )
        self.ps4_button.grid(row=4, column=0, sticky='nsew')

        self.menu_bar = Menubar(self)
        self.master.config(menu=self.menu_bar)

        self.bindings = [
            ('<KeyPress>', self.key_press),
            ('<Left>', self.roku.left),
            ('<Right>', self.roku.right),
            ('<Up>', self.roku.up),
            ('<Down>', lambda *args: click_button(self.down_button)),
            ('<Return>', self.roku.select),
            ('-', self.roku.volume_down),
            ('+', self.roku.volume_up),
            ('=', self.roku.volume_up),
            ('<space>', self.roku.play),
            ('<BackSpace>', self.roku.back),
        ]

        self.bound = False
        
        self.master.bind('<FocusIn>', self.set_bindings)
        self.master.bind('<FocusOut>', self.set_bindings)

        self.master.geometry(get_geometry(settings))


    def get_geometry(self):
        if all([(key in self.master.settings) for key in ['win_x', 'win_y']]):
            self.master.geometry(
                '{}x{}+{}+{}'.format(
                    self.master.settings['win_w'],
                    self.master.settings['win_h'],
                    self.master.settings['win_x'],
                    self.master.settings['win_y']
                )
            )
        else:
            self.master.geometry(
                '{}x{}'.format(settings['win_w'], settings['win_h'])
            )


    def send_text(self, *args):
        text = self.search_var.get()
        diff = len(self.previous_text) - len(text)
        if diff < 0:
            new_text = text[diff]
            self.roku.literal(new_text)
        if diff > 0:
            for i in range(diff):
                self.roku.backspace()
        self.previous_text = text


    def build_search_input(self, *args):
        font = self.master.settings['font']
        ENTRY = {'font': [font, 14], 'fg': '#201d3d', 'bg': '#fcfbfd'}
        if hasattr(self, 'search_input'):
            self.search_input.destroy()

        self.search_input = tk.Entry(
            self, **ENTRY, bd=10, relief='flat', textvariable=self.search_var
        )
        self.search_input.grid(
            row=5, column=1, columnspan=2, padx=1, pady=1, sticky='nsew'
        )

        self.search_input.bind('<Escape>', self.build_search_input)


    def launch_app(self, ident):
        app = next((a for a in self.roku.apps if ident in a.name.lower()), None)
        if app:
            app.launch()


    def key_press(self, *args):
        print(args)


    def set_bindings(self, event):
        if not self.bound:
            self.bind_keys(event)
        else:
            self.unbind_keys(event)


    def bind_keys(self, event):
        for key, func in self.bindings:
            self.master.bind(key, func)
        self.bound = True


    def unbind_keys(self, event):
        if str(event.widget) == '.!mainwindow.!entry' and self.bound:
            for key, func in self.bindings:
                self.master.unbind(key)
            self.bound = False


if __name__ == '__main__':
    root = tk.Tk()
    root.settings = load_settings()
    root.protocol('WM_DELETE_WINDOW', lambda: close_window(root))
    ico = tk.PhotoImage(file = './iconfinder_tv_172609.png')
    root.iconphoto(False, ico)
    window = MainWindow(root, bg='#000000')
    root.mainloop()

    if window.restart_flag:
        system = platform.system()
        if system == 'Windows':
            os.system('py ' + __file__)
        if system == 'Linux':
            os.system('python3 ' + __file__)
