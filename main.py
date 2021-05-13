""" === MOSQUITOES TIMER === """

# imports
import tkinter as tk
import pandas as pd
from winsound import Beep
from time import perf_counter, strftime, gmtime
from datetime import datetime

# general settings
up_time = 1_000  # ms

# GUI style
font = 'verdana'
size = 16
pad = size // 2
c0 = '#2d3436'
c1 = '#636e72'
c2 = '#b2bec3'
c3 = '#dfe6e9'


# functions
def sound(n):
    for _ in range(n):
        Beep(1500, 200)


def format_n(n):
    return float(f'{n:.2f}')


def format_m(m):
    return strftime('%M:%S', gmtime(m))


def update_info(t_stamp, event):
    # global variables
    global data
    
    # get all information
    end_t = perf_counter() - info['main'].t
    start_t = end_t - t_stamp
    ev_info = {'event': event,
               'start time': format_n(start_t),
               'start time (m)': format_m(start_t),
               'end time': format_n(end_t),
               'end time (m)': format_m(end_t),
               'duration': format_n(t_stamp)}
    # check if first landing
    if event == 'Landing' and 'Landing' not in data['event'].values:
        ev_info['first land'] = 'yes'
    # update data
    data = data.append([ev_info])
    
    # update event log
    log_info = f'{ev_info["event"]} - {ev_info["duration"]}'
    info['log'].txt = log_info if info['log'].txt == '' else f'{info["log"].txt}\n{log_info}'
    info['log'].lbl.configure(text=info['log'].txt)


def export_data():
    # global variables
    global data
    
    # get experiment time
    current_t = datetime.now().strftime('%Y-%m-%d_%H-%M')
    
    # get counters info
    for c in [info['probe'], info['sensing']]:
        for t in c.timestamps:
            c_info = {'event': c.txt,
                      'start time': t,
                      'start time (m)': format_m(t)}
            data = data.append([c_info])
    
    # export to excel
    file_name = f'test_{current_t}.xlsx'
    data.to_excel(file_name, index=False)


def reset_data():
    # clear data
    global data
    data.drop(data.index, inplace=True)
    
    # clear log, reset timers and counters
    for name, element in info.items():
        element.reset_t()


# GUI elements
class Frame:
    """frame to contain other objects"""
    
    def __init__(self, root, row, col):
        # get info
        self.root = root
        self.row = row
        self.col = col
        
        # create frame
        self.frame = tk.Frame(self.root)
        self.frame.configure(bg=c0)
        self.frame.grid(row=self.row, column=self.col, padx=pad // 2, pady=pad // 2, sticky='nsew')


class LblFrame:
    """frame to contain other objects with a label"""
    
    def __init__(self, root, txt, row, col):
        # get info
        self.root = root
        self.txt = f' {txt} '
        self.row = row
        self.col = col
        
        # create label frame
        self.lblframe = tk.LabelFrame(self.root, text=self.txt, font=(font, size // 2))
        self.lblframe.configure(bg=c0, fg=c2, labelanchor='n', relief='ridge')
        self.lblframe.grid(row=self.row, column=self.col, padx=pad // 2, pady=pad // 2, sticky='nsew')


class Lbl:
    """simple text in a label"""
    
    def __init__(self, root, txt, row, col):
        # get info
        self.root = root
        self.txt = txt
        self.row = row
        self.col = col
        
        # create label
        self.lbl = tk.Label(self.root, text=self.txt, font=(font, size))
        self.lbl.configure(bg=c0, fg=c2)
        self.lbl.grid(row=self.row, column=self.col, padx=pad, pady=pad)
    
    def timer(self):
        self.lbl.configure(font=(font, size * 2))
        self.lbl.grid(columnspan=2, padx=0, pady=0)
    
    def log(self):
        self.lbl.configure(font=(font, size, 'italic'), width=25)
        self.lbl.grid(columnspan=2, sticky='n')
        info['log'] = self
    
    def reset_t(self):
        self.txt = ''
        self.lbl.configure(text='')


class Btn:
    """button linked to a function"""
    
    def __init__(self, root, txt, func, row, col):
        # get info
        self.root = root
        self.txt = txt
        self.func = func
        self.row = row
        self.col = col
        
        # create button
        self.btn = tk.Button(self.root, text=self.txt, font=(font, size), command=self.func)
        self.btn.configure(bg=c0, fg=c2, activebackground=c0, activeforeground=c2, relief='flat')
        self.btn.grid(row=self.row, column=self.col, padx=pad, pady=pad)
        
        # bind to function to change color when the mouse is hovering
        self.btn.bind('<Enter>', lambda e: self.over(e))
        self.btn.bind('<Leave>', lambda e: self.over(e))
    
    def over(self, event):
        """change the background of the button when the mouse is over it"""
        
        # check event type
        enter = True if int(event.type) == 7 else False
        
        # configure button
        if enter:
            self.btn.configure(bg=c2, fg=c0)
        else:
            self.btn.configure(bg=c0, fg=c2)
    
    def counter_main(self):
        self.btn.configure(font=(font, size * 2, 'bold'))
        self.btn.grid(padx=0, pady=0)
    
    def counter_small(self):
        self.btn.configure(font=(font, size // 2))
        self.btn.grid(padx=0, pady=0, sticky='s')
    
    def timer(self):
        self.btn.configure(width=10)
        self.btn.grid(padx=0, pady=0)


# timer elements
class Timer:
    """timestamp label with start/stop buttons and auto-update"""
    
    def __init__(self, root, txt, row, col):
        # get info
        self.root = root
        self.txt = txt
        self.row = row
        self.col = col
        self.stop = True
        self.t = 0
        self.key = ''
        self.update_info()
        
        # frame
        self.frame = LblFrame(self.root, self.txt, self.row, self.col).lblframe
        self.root.columnconfigure(self.col, weight=1)
        self.frame.columnconfigure(0, weight=1)
        
        # timestamp label
        self.timestamp = Lbl(self.frame, '00:00', 0, 0)
        self.timestamp.timer()
        
        # buttons
        self.start_stop = Btn(self.frame, 'Start', self.start_t, 1, 0)
        self.start_stop.timer()
    
    def update_t(self):
        if not self.stop:
            stamp = strftime('%M:%S', gmtime(perf_counter() - self.t))
            self.timestamp.lbl.configure(text=stamp)
            self.root.after(up_time, self.update_t)
    
    def start_t(self):
        self.stop = False
        self.t = perf_counter() - self.t
        self.update_t()
        self.start_stop.btn.configure(text='Stop', command=self.stop_t)
        self.start_stop.btn.bind_all(self.key, lambda _: self.stop_t())
    
    def stop_t(self):
        t = perf_counter() - self.t
        update_info(t, self.txt)
        self.reset_t()
    
    def reset_t(self):
        # reset timer
        self.stop = True
        self.t = 0
        self.timestamp.lbl.configure(text='00:00')
        self.start_stop.btn.configure(text='Start', command=self.start_t)
        self.start_stop.btn.bind_all(self.key, lambda _: self.start_t())
    
    def bind_key(self, k):
        self.key = k
        self.start_stop.btn.bind_all(self.key, lambda _: self.start_t())
    
    def update_info(self):
        if self.txt == 'Landing':
            info['landing'] = self
        if self.txt == 'Walking':
            info['walking'] = self
        if self.txt == 'Feeding':
            info['feeding'] = self
        if self.txt == 'Probe & Sensing':
            info['probe_sensing'] = self


class Countdown:
    """countdown label with start/pause/resume buttons and auto-update"""
    
    def __init__(self, root, txt, start_t, row, col):
        # get info
        self.root = root
        self.txt = txt
        self.row = row
        self.col = col
        self.pause = True
        self.t = 0
        self.tot = int(start_t)
        self.update_info()
        
        # frame
        fr = LblFrame(self.root, self.txt, self.row, self.col).lblframe
        self.root.columnconfigure(self.col, weight=1)
        for i in range(2):
            fr.rowconfigure(i, weight=1)
            fr.columnconfigure(i, weight=1)
        
        # timestamp label
        stamp = strftime('%M:%S', gmtime(self.tot))
        self.timestamp = Lbl(fr, stamp, 0, 0)
        self.timestamp.timer()
        if self.tot != 120:
            self.timestamp.lbl.configure(font=(font, size * 4))
        
        # buttons
        self.start_pause = Btn(fr, 'Start', self.start_t, 1, 0)
        self.start_pause.timer()
        self.reset = Btn(fr, 'Reset', self.reset_t, 1, 1)
        self.reset.timer()
    
    def update_t(self):
        # beeps at the end and half time
        if self.tot - (perf_counter() - self.t) <= 0:
            sound(4)
            return
        if self.tot != 120 and self.tot // 2 - 1 <= self.tot - (perf_counter() - self.t) <= self.tot // 2 + 1:
            sound(1)
        
        # update timestamp
        if not self.pause:
            t = strftime('%M:%S', gmtime(self.tot - (perf_counter() - self.t)))
            self.timestamp.lbl.configure(text=t)
            self.root.after(up_time, self.update_t)
    
    def start_t(self):
        self.pause = False
        self.t = perf_counter() - self.t
        self.update_t()
        self.start_pause.btn.configure(text='Pause', command=self.pause_t)
    
    def pause_t(self):
        self.pause = True
        self.t = perf_counter() - self.t
        self.start_pause.btn.configure(text='Start', command=self.start_t)
    
    def reset_t(self):
        self.pause = True
        self.t = 0
        stamp = strftime('%M:%S', gmtime(self.tot))
        self.timestamp.lbl.configure(text=stamp)
        self.start_pause.btn.configure(text='Start', command=self.start_t)
    
    def setup_time(self):
        self.start_pause.btn.configure(width=5)
        self.reset.btn.configure(width=5)
    
    def update_info(self):
        if self.txt == 'Setup':
            info['setup'] = self
        if self.txt == 'Observation':
            info['main'] = self


class Counter:
    def __init__(self, root, txt, key, row, col):
        """counter with plus/minus and reset buttons"""
        
        # get info
        self.root = root
        self.txt = txt
        self.key = key
        self.row = row
        self.col = col
        self.val = 0
        self.timestamps = []
        self.update_info()
        
        # frame
        fr = LblFrame(self.root, self.txt, self.row, self.col).lblframe
        
        # value button
        self.val_btn = Btn(fr, self.val, lambda: self.change_val('+'), 0, 1)
        self.val_btn.btn.bind_all(self.key, lambda _: self.change_val('+'))
        self.val_btn.counter_main()
        
        # buttons
        Btn(fr, 'R', lambda: self.change_val('r'), 0, 0).counter_small()
        Btn(fr, '-', lambda: self.change_val('-'), 0, 2).counter_small()
    
    def change_val(self, op):
        if op == '+':
            self.val += 1
            t = perf_counter() - info['main'].t
            self.timestamps.append(format_n(t))
        if op == '-':
            if self.val != 0:
                self.val -= 1
                self.timestamps.pop()
        if op == 'r':
            self.reset_t()
        self.val_btn.btn.configure(text=self.val)
    
    def reset_t(self):
        self.val = 0
        self.val_btn.btn.configure(text=self.val)
        self.timestamps = []
    
    def update_info(self):
        if self.txt == 'Probe':
            info['probe'] = self
        if self.txt == 'Sensing':
            info['sensing'] = self


# App
class App:
    def __init__(self):
        """initialize application"""
        
        self.root = tk.Tk()
        self.root.withdraw()
        self.content()
        self.setup()
        self.root.deiconify()
        self.root.mainloop()
    
    def content(self):
        """set window content"""
        
        # main and setup countdown
        main_fr = Frame(self.root, 0, 0).frame
        Countdown(main_fr, 'Setup', 60 * 2, 0, 0).setup_time()
        Countdown(main_fr, 'Observation', 60 * 10, 0, 1)
        
        # setup time, landing and walking
        land_frame = Frame(self.root, 1, 0).frame
        Timer(land_frame, 'Landing', 0, 0).bind_key('<Return>')
        Timer(land_frame, 'Walking', 0, 1).bind_key('w')
        Timer(land_frame, 'Feeding', 0, 2).bind_key('o')
        
        # probe and sensing
        prob_frame = Frame(self.root, 2, 0).frame
        Counter(prob_frame, 'Probe', '<space>', 0, 0)
        Timer(prob_frame, 'Probe & Sensing', 0, 1).bind_key('d')
        Counter(prob_frame, 'Sensing', 's', 0, 2)
        
        # event log
        log_frame = LblFrame(self.root, 'Events Log', 0, 2).lblframe
        log_frame.grid(rowspan=3)
        log_frame.rowconfigure(0, weight=1)
        log_lbl = Lbl(log_frame, '', 0, 0)
        log_lbl.log()
        
        # buttons
        Btn(log_frame, 'Export', export_data, 1, 0).timer()
        Btn(log_frame, 'Reset', reset_data, 1, 1).timer()
    
    def setup(self):
        """root settings"""
        
        def closing():
            """what to do when closing the program"""
            
            self.root.destroy()
        
        def position():
            """set the dimension and position the window at the center of the screen"""
            
            self.root.update()
            root_w = self.root.winfo_reqwidth()
            root_h = self.root.winfo_reqheight()
            disp_w = self.root.winfo_screenwidth()
            disp_h = self.root.winfo_screenheight()
            pos = f'+{(disp_w - root_w) // 2}+{(disp_h - root_h) // 2}'
            self.root.geometry(f'{root_w}x{root_h}')
            self.root.geometry(pos)
        
        self.root.title('Mosquitoes Timer')
        self.root.iconbitmap(r'data/msq_1.ico')
        self.root.resizable(False, False)
        self.root.configure(bg=c0)
        self.root.protocol('WM_DELETE_WINDOW', closing)
        position()


""" main start """
if __name__ == '__main__':
    # create dataframe
    columns = ['event', 'start time', 'start time (m)', 'end time', 'end time (m)', 'duration']
    data = pd.DataFrame(columns=columns)
    info = {}
    
    # launch app
    App()
