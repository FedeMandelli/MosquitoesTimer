""" === MOSQUITOES TIMER === """

# imports
import tkinter as tk
import pandas as pd
from tkinter.messagebox import showinfo
from winsound import Beep
from time import perf_counter, strftime, gmtime
from datetime import datetime
from os import path

# general settings
up_time = 1_000  # ms
temperature = 0
# save_path = 'C:/Users/mc9241x/Desktop/Timer Data'
save_path = 'C:/Users/Federico/Desktop/test'

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


def confirm_sound():
    Beep(2200, 200)


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
               'duration (s)': format_n(t_stamp)}
    # check if first landing
    if event == 'Landing' and 'Landing' not in data['event'].values:
        ev_info['first land'] = 'yes'
    # update data
    data = data.append([ev_info])
    
    # update event log
    log_update()


def export_data():
    # global variables
    global data
    
    # get experiment time
    current_t = datetime.now().strftime('%Y-%m-%d_%H-%M')
    
    # get counters info
    for c in info.values():
        if isinstance(c, Counter):
            for t in c.timestamps:
                c_info = {'event': c.txt,
                          'start time': t,
                          'start time (m)': format_m(t)}
                data = data.append([c_info])
    
    # export to excel
    file_name = f'timer_{current_t}_{temperature}.xlsx'
    dest = path.join(save_path, file_name)
    data.to_excel(dest, index=False)
    
    # confirmation messagebox
    showinfo('Confirm Save', f'Experiment exported in {save_path}')
    reset_data()


def reset_data():
    # clear data
    global data
    data.drop(data.index, inplace=True)
    
    # clear log, reset timers and counters
    for name, element in info.items():
        element.reset_t()


def remove_last():
    global data
    
    # remove last row and update label
    data = data[:-1]
    log_update()


def log_update():
    info['log'].txt = '\n'.join([f'{a} - {b}' for a, b in zip(data['event'].values, data['duration (s)'].values)])
    info['log'].lbl.configure(text=info['log'].txt)


def end_main_reset():
    for i in info.values():
        if isinstance(i, Timer):
            if not i.stop:
                i.stop_t()


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
    
    def legend(self):
        self.lbl.configure(font=(font, size // 2, 'italic'), fg=c1)
        self.lbl.grid(padx=0, pady=0, columnspan=2)


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


class Radio:
    def __init__(self, root, val, row, col):
        # get info
        self.root = root
        self.val = val
        self.row = row
        self.col = col
        
        # create radio button
        self.rad = tk.Radiobutton(self.root, text=self.val, variable=1, value=self.val, font=(font, size // 2))
        self.rad.configure(bg=c2, fg=c0, activebackground=c2, activeforeground=c0, command=self.sel)
        self.rad.grid(row=self.row, column=self.col, padx=pad, pady=pad)
    
    def sel(self):
        global temperature
        temperature = self.val


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
        confirm_sound()
        self.stop = False
        self.t = perf_counter() - self.t
        self.update_t()
        self.start_stop.btn.configure(text='Stop', command=self.stop_t)
        self.start_stop.btn.bind_all(self.key, lambda _: self.stop_t())
        self.start_cond()
    
    def stop_t(self):
        confirm_sound()
        t = perf_counter() - self.t
        update_info(t, self.txt)
        self.reset_t()
        self.stop_cond()
    
    def reset_t(self):
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
        if self.txt == 'Still':
            info['still'] = self
        if self.txt == 'Feeding':
            info['feeding'] = self
        if self.txt == 'Probe & Sensing':
            info['probe_sensing'] = self
    
    def start_cond(self):
        if self.txt == 'Feeding':
            for i in [info['still'], info['probe_sensing']]:
                if not i.stop:
                    i.stop_t()
        if self.txt == 'Probe & Sensing':
            if info['landing'].stop:
                info['landing'].start_t()
    
    def stop_cond(self):
        if self.txt == 'Landing':
            for i in [info['probe_sensing'], info['feeding']]:
                if not i.stop:
                    i.stop_t()


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
        self.fr = LblFrame(self.root, self.txt, self.row, self.col).lblframe
        self.root.columnconfigure(self.col, weight=1)
        for i in range(2):
            self.fr.rowconfigure(i, weight=1)
            self.fr.columnconfigure(i, weight=1)
        
        # timestamp label
        stamp = strftime('%M:%S', gmtime(self.tot))
        self.timestamp = Lbl(self.fr, stamp, 0, 0)
        self.timestamp.timer()
        if self.tot != 120:
            self.timestamp.lbl.configure(font=(font, size * 4))
        
        # buttons
        self.start_pause = Btn(self.fr, 'Start', self.start_t, 1, 0)
        self.start_pause.timer()
        self.reset = Btn(self.fr, 'Reset', self.reset_t, 1, 1)
        self.reset.timer()
    
    def update_t(self):
        # end of countdown
        if self.tot - (perf_counter() - self.t) <= 0:
            sound(4)
            if self.tot != 120:
                end_main_reset()
                export_data()
            self.reset_t()
            return
        
        # beep at half time
        if self.tot != 120 and self.tot // 2 - 1 <= self.tot - (perf_counter() - self.t) <= self.tot // 2 + 1:
            sound(1)
        
        # update timestamp
        if not self.pause:
            t = strftime('%M:%S', gmtime(self.tot - (perf_counter() - self.t)))
            self.timestamp.lbl.configure(text=t)
            self.root.after(up_time, self.update_t)
    
    def start_t(self):
        confirm_sound()
        self.pause = False
        self.t = perf_counter() - self.t
        self.update_t()
        self.start_pause.btn.configure(text='Pause', command=self.pause_t)
    
    def pause_t(self):
        confirm_sound()
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
    
    def main_time(self):
        self.fr.grid(rowspan=2)


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
        confirm_sound()
        if op == '+':
            self.val += 1
            t = perf_counter() - info['main'].t
            self.timestamps.append(format_n(t))
            if info['probe_sensing'].stop:
                info['probe_sensing'].start_t()
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
        Countdown(main_fr, 'Setup', 60 * 2, 1, 0).setup_time()
        Countdown(main_fr, 'Observation', 60 * 10, 0, 1).main_time()
        
        # temperature
        temp_frame = LblFrame(main_fr, 'Temperature', 0, 0).lblframe
        Radio(temp_frame, 30, 0, 0)
        Radio(temp_frame, 36, 0, 1)
        Radio(temp_frame, 42, 0, 2)
        Radio(temp_frame, 48, 0, 3)
        
        # setup time, landing and still
        land_frame = Frame(self.root, 1, 0).frame
        Timer(land_frame, 'Landing', 0, 0).bind_key('<space>')
        Timer(land_frame, 'Still', 0, 1).bind_key('w')
        Timer(land_frame, 'Feeding', 0, 2).bind_key('n')
        
        # probe and sensing
        prob_frame = Frame(self.root, 2, 0).frame
        Counter(prob_frame, 'Probe', 'p', 0, 0)
        Timer(prob_frame, 'Probe & Sensing', 0, 1).bind_key('<Return>')
        Counter(prob_frame, 'Sensing', 'l', 0, 2)
        
        # event log
        log_frame = LblFrame(self.root, 'Events Log', 0, 1).lblframe
        log_frame.grid(rowspan=3)
        log_frame.rowconfigure(1, weight=1)
        log_lbl = Lbl(log_frame, '', 1, 0)
        log_lbl.log()
        log_lbl.lbl.bind_all('<BackSpace>', lambda _: remove_last())
        
        # buttons
        Btn(log_frame, 'Export', export_data, 0, 0).timer()
        Btn(log_frame, 'Reset', reset_data, 0, 1).timer()
        
        # legend
        leg = []
        for i in info.values():
            if i.txt not in ['Setup', 'Observation', '']:
                a = f'{i.txt}({i.key})'
                leg.append(a)
        leg = ' - '.join(leg)
        Lbl(self.root, leg, 3, 0).legend()
    
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
        # self.root.resizable(False, False)
        self.root.configure(bg=c0)
        self.root.protocol('WM_DELETE_WINDOW', closing)
        position()


""" main start """
if __name__ == '__main__':
    # create dataframe
    columns = ['event', 'start time (m)', 'end time (m)', 'duration (s)', 'start time', 'end time']
    data = pd.DataFrame(columns=columns)
    info = {}
    
    # launch app
    App()
