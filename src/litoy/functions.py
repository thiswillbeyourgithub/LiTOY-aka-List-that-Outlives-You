#!/usr/bin/env python3

import logging
import random
from   .sql         import *
from   .settings    import *

# to get the terminal size on all OS :
import os
import shlex
import struct
import platform
import subprocess
 

# This file contains general functions used in the main loop :

def print_2_entries(entry_id, all_fields="no"):
    logging.info("Printing entries : "+ str(entry_id[0]) + " and " + str(entry_id[1]))
    print("#"*sizex)
    def side_by_side(rowname, a, b, space=4):
        #https://stackoverflow.com/questions/53401383/how-to-print-two-strings-large-text-side-by-side-in-python
        rowname = rowname.ljust(30)
        sizex = get_terminal_size()
        width=int((sizex-len(rowname))/2-space*2)
        inc = 0
        while a or b:
            inc+=1
            if inc == 1:
                print(rowname + " "*space + a[:width].ljust(width) + " "*space + b[:width])
            else :
                print(" "*(len(rowname)+space) + a[:width].ljust(width) + " "*space + b[:width])
            a = a[width:]
            b = b[width:]

    entries = fetch_entry("ID = " + str(entry_id[0]) + " OR ID = " + str(entry_id[1]))
    random.shuffle(entries)
    if all_fields != "all":
        cat = ["Category :", str(entries[0]['category']), str(entries[1]['category'])]
        content = ["Entry :", str(entries[0]['entry']), str(entries[1]['entry'])]
        side_by_side(content[0], content[1], content[2])
        if str(entries[0]['details']) != "None" or str(entries[1]['details']) != "None" :
            details = ["Details :", str(entries[0]['details']), str(entries[1]['details'])]
            side_by_side(details[0], details[1], details[2])
        if str(entries[0]['progress']) != "None" or str(entries[1]['progress']) != "None" :
            progress = ["Progress :", str(entries[0]['progress']), str(entries[1]['progress'])]
            side_by_side(progress[0], progress[1], progress[2])
        importance = ["Importance :", str(entries[0]['importance_elo']).split("_")[-1], str(entries[1]['importance_elo']).split("_")[-1]]
        side_by_side(importance[0], importance[1], importance[2])
        time = ["Time (high is short) :", str(entries[0]['time_elo']).split("_")[-1], str(entries[1]['time_elo']).split("_")[-1]]
        side_by_side(time[0], time[1], time[2])

    if all_fields=="all":
       for i in get_field_names():
           side_by_side(str(i), str(entries[0][i]), str(entries[1][i]))
    print("#"*sizex)

def pick_2_entries(mode, condition=""): # tested seems OK
    col = fetch_entry('ID >= 0 AND DISABLED IS 0' + condition)
    random.shuffle(col)  # helps when all entries are the same
    if mode == "i" : 
        col.sort(reverse=True, key=lambda x : int(x['delta_imp']))
        col_deltas_dates = col
    if mode == "t" :
        col.sort(reverse=True, key=lambda x : int(x['delta_time']))
        col_deltas_dates = col
    highest_5_deltas = col_deltas_dates[0:5]
    choice1 = random.choice(highest_5_deltas) # first opponent

    randomness = random.random()
    if randomness > choice_threshold :
        while 1==1 :
            choice2 = random.choice(col_deltas_dates)
            if choice2['ID'] == choice1['ID']:
                print("Re choosing : selected the same entry")
                continue
            break
    else :
        print("Choosing the oldest seen entry")
        logging.info("Choosing the oldest seen entry")
        while 1==1 :
            #col_deltas_dates.sort(reverse=False, key=lambda x : str(x[mode+2]).split(sep="_")[-1])
            if mode == "i":
                col_deltas_dates.sort(reverse=False, key=lambda x : str(x['delta_imp']).split(sep="_")[-1])
            if mode == "t":
                col_deltas_dates.sort(reverse=False, key=lambda x : str(x['delta_time']).split(sep="_")[-1])
            choice2 = col_deltas_dates[0]
            print("\n\n\n")
            while choice2['ID'] == choice1['ID']:
                print("Re choosing : selected the same entry")
                choice1 = random.choice(highest_5_deltas)
            break
    logging.info("Chose those fighters : " + str(choice1['ID']) + " and " + str(choice2['ID']))
    result = [choice1['ID'], choice2['ID']]
    return result

def shortcut_reaction(key, mode, fighters):
    def get_key(val): 
        for key, value in my_dict.items(): 
             if val == value: 
                 return key 

    while 1==1 :
        logging.info("User types =>" + key)
        pass
        if key not in shortcut.values() :
            print("Error : key not found : " + key)
            logging.info("Error : key not found : " + key)
            continue
        action = get_key(key)
        if action == "answer_level" :
            cur_elo1 = get_sql_value("importance_elo, date_importance_elo, time_elo, date_time_elo", "id = "+fighters[0])
            cur_elo2 = get_sql_value("importance_elo, date_importance_elo, time_elo, date_time_elo", "id = "+fighters[1])
            cur_K_1 = get_sql_value("K", "id = "+fighters[0])
            cur_K_2 = get_sql_value("K", "id = "+fighters[1])


            new_elo1 = update_elo(cur_elo1, expected(cur_elo1, cur_elo2), int(key), cur_K_1)
            new_elo2 = update_elo(cur_elo2, expected(cur_elo2, cur_elo1), int(key), cur_K_2)
        break





# from here : https://gist.github.com/jtriley/1108174
# used to get terminal size
def get_terminal_size():
    """ getTerminalSize()
     - get width and height of console
     - works on linux,os x,windows,cygwin(windows)
     originally retrieved from:
     http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
    """
    current_os = platform.system()
    tuple_xy = None
    if current_os == 'Windows':
        tuple_xy = _get_terminal_size_windows()
        if tuple_xy is None:
            tuple_xy = _get_terminal_size_tput()
            # needed for window's python in cygwin's xterm!
    if current_os in ['Linux', 'Darwin'] or current_os.startswith('CYGWIN'):
        tuple_xy = _get_terminal_size_linux()
    if tuple_xy is None:
        print("default")
        tuple_xy = (80, 25)      # default value
    return tuple_xy[0]
def _get_terminal_size_windows():
    try:
        from ctypes import windll, create_string_buffer
        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            (bufx, bufy, curx, cury, wattr,
             left, top, right, bottom,
             maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            sizex = right - left + 1
            sizey = bottom - top + 1
            return sizex, sizey
    except:
        pass
def _get_terminal_size_tput():
    # get terminal width
    # src: http://stackoverflow.com/questions/263890/how-do-i-find-the-width-height-of-a-terminal-window
    try:
        cols = int(subprocess.check_call(shlex.split('tput cols')))
        rows = int(subprocess.check_call(shlex.split('tput lines')))
        return (cols, rows)
    except:
        pass
def _get_terminal_size_linux():
    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            cr = struct.unpack('hh',
                               fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
            return cr
        except:
            pass
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (os.environ['LINES'], os.environ['COLUMNS'])
        except:
            return None
    return int(cr[1]), int(cr[0])
 
sizex = get_terminal_size()
