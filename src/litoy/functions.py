#!/usr/bin/env python3

import time
import logging
import random
import webbrowser
from itertools import chain
import pprint
from   .sql         import *
from   .settings    import *
from   .elo    import *

# to get the terminal size on all OS :
import os
import shlex
import struct
import platform
import subprocess
 

# This file contains general functions used in the main loop :

def print_memento_mori():
    seg1 = useless_first_years
    seg2 = user_age - useless_first_years
    seg3 = user_life_expected - user_age - useless_last_years
    seg4 = useless_last_years
    resize = 1/user_life_expected*(sizex-17)
    print("Your life ("+ col_red + str(int((seg2)/(seg2 + seg3)*100)) + "%" + col_rst + ") : " + col_yel + "x"*int(seg1*resize) + col_red + "X"*(int(seg2*resize)) + "_"*(int(seg3*resize)) + col_yel + "_"*int(seg4*resize) + col_rst)

def print_2_entries(fighters, deck, mode, all_fields="no"):
    logging.info("Printing fighters : "+ str(fighters[0]["ID"]) + " and " + str(fighters[1]["ID"]))
    print(col_blu + "#"*sizex + col_rst)
    print("Deck " + str(mode) + " delta = " + str(get_deck_delta(deck, mode)))
    print_memento_mori()
    print(col_blu + "#"*sizex + col_rst)
    def side_by_side(rowname, a, b, space=4, col=""):
        #https://stackoverflow.com/questions/53401383/how-to-print-two-strings-large-text-side-by-side-in-python
        rowname = rowname.ljust(30)
        sizex = get_terminal_size()
        width=int((int(sizex)-len(rowname))/2-int(space)*2)
        inc = 0
        while a or b:
            inc+=1
            if inc == 1:
                print(str(col) + str(rowname) + " "*space + a[:width].ljust(width) + " "*space + b[:width] + col_rst)
            else :
                print(str(col) + " "*(len(rowname)+space) + a[:width].ljust(width) + " "*space + b[:width] + col_rst)
            a = a[width:]
            b = b[width:]

    random.shuffle(fighters)
    if all_fields != "all":
        ids = ["IDs : ", str(fighters[0]["ID"]), str(fighters[1]["ID"])]
        side_by_side(ids[0], ids[1], ids[2])
        deck = ["Deck :", str(fighters[0]['deck']), str(fighters[1]['deck'])]
        side_by_side(deck[0], deck[1], deck[2])
        if str(fighters[0]['tags']) != "None" or str(fighters[1]['tags']) != "None" :
            tags = ["Tags :", str(fighters[0]['tags']), str(fighters[1]['tags'])]
            side_by_side(tags[0], tags[1], tags[2])
        if str(fighters[0]['metadata']) != "None" or str(fighters[1]['metadata']) != "None" :
            metadata = ["metadata :", str(fighters[0]['metadata']), str(fighters[1]['metadata'])]
            side_by_side(metadata[0], metadata[1], metadata[2])
        if str(fighters[0]['progress']) != "None" or str(fighters[1]['progress']) != "None" :
            progress = ["Progress :", str(fighters[0]['progress']), str(fighters[1]['progress'])]
            side_by_side(progress[0], progress[1], progress[2])
        if str(fighters[0]['starred']) != "0" or str(fighters[1]['starred']) != "0" :
            starred = ["Starred :", str(fighters[0]['starred']), str(fighters[1]['starred'])]
            side_by_side(starred[0], starred[1], starred[2], col = col_yel)
        content = ["Entry :", str(fighters[0]['entry']), str(fighters[1]['entry'])]
        side_by_side(content[0], content[1], content[2])
        #importance = ["Importance :", str(fighters[0]['importance_elo']).split("_")[-1], str(fighters[1]['importance_elo']).split("_")[-1]]
        #side_by_side(importance[0], importance[1], importance[2])
        #time = ["Time (high is short) :", str(fighters[0]['time_elo']).split("_")[-1], str(fighters[1]['time_elo']).split("_")[-1]]
        #side_by_side(time[0], time[1], time[2])

    if all_fields=="all":
       for i in get_field_names():
           side_by_side(str(i), str(fighters[0][i]), str(fighters[1][i]))
    print(col_blu + "#"*sizex + col_rst)

def pick_2_entries(mode, condition=""): # tested seems OK
    logging.info("Picking : begin")
    col = fetch_entry('ID >= 0 AND DISABLED IS 0 ' + condition)
    random.shuffle(col)  # helps when all entries are the same
    if mode == "importance" : 
        col.sort(reverse=True, key=lambda x : int(x['delta_importance']))
        col_deltas_dates = col
    if mode == "time" :
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
        print(col_yel + "Choosing the oldest seen entry" + col_rst)
        logging.info("Choosing the oldest seen entry")
        while 1==1 :
            #col_deltas_dates.sort(reverse=False, key=lambda x : str(x[mode+2]).split(sep="_")[-1])
            if mode == "i":
                col_deltas_dates.sort(reverse=False, key=lambda x : str(x['delta_importance']).split(sep="_")[-1])
            if mode == "t":
                col_deltas_dates.sort(reverse=False, key=lambda x : str(x['delta_time']).split(sep="_")[-1])
            choice2 = col_deltas_dates[0]
            while choice2['ID'] == choice1['ID']:
                print("Re choosing : selected the same entry")
                choice1 = random.choice(highest_5_deltas)
            break
    logging.info("Chose those fighters : " + str(choice1['ID']) + " and " + str(choice2['ID']))
    result = [choice1, choice2]
    logging.info("Picking : Done")
    return result

def print_syntax_examples():
    logging.info("Printing syntax example : begin")
    print("#"*sizex)
    print("Syntax examples :")
    print("Adding entries :")
    print("   * python3 __main__.py --add ENTRY --deck DECK  --tags TAGS --metadata metadata")

    print("Importing from file :")
    print("   * python3 __main__.py --import FILENAME  --deck DECK --tags TAG")

    print("Showing ranks and listing entries : ")
    print("   * python3 __main__.py --rank FIELD r(everse) -n 50 --deck DECK")

    print("Editing an entry :")
    print("   * python3 __main__.py --edit ID FIELD NEWVALUE")

    print("Changing a setting :")

    print("List tags, decks and number of cards :")
    print("   * python3 __main__.py --state")

    print("Compare entries :")
    print("   * python3 __main__.pay --fight imp -n 10 --deck DECK")

    print("Example of formula in settings.py :")
    print('   * formula_list = { "deckname" : "formula_name", "Toread" : "sum_elo", "DIY" : "sum_elo" }"')

    print("Current shortcuts in fight mode :")
    pprint.pprint(shortcuts)
    print("#"*sizex)

    logging.info("Printing syntax example : done")

def compute_Global_score():
    logging.info("Compute global : all cards")

    # check if the formulas declared in the dictionnary in  settings.py 
    # correspond to function that have been defined
    decks = list(get_decks()[0]).sort()
    formulas = formula_dict.keys()
    needed_formula = formula_dict.values()
    defined_function = globals()
    if decks != formulas :
        print(col_red + "WARNING : Not all formulas have been found in the settings" + col_rst)
        logging.info("Not all formulas have been found in the settings")
    for i in needed_formula :
        if i not in defined_function :
            print("Compute global : Missing formula declaration : " + i)
            logging.info("Compute global : Missing formula declaration : " + i)
            sys.exit()

    def get_formula(deck): 
        found = ""
        for key, formula in formula_dict.items(): 
            if str(deck) in key: 
                if found != "" :
                    print("Several corresponding formulas found!")
                    logging.info("Several corresponding formulas found!")
                    sys.exit()
                found = formula
        return found 

    all_cards = fetch_entry("ID >=0")
    for n,i in enumerate(all_cards):
        formula = formula_dict[i["deck"]]
        elo1=str(i["importance_elo"]).split(sep="_")[-1]
        elo2=str(i["time_elo"]).split(sep="_")[-1]
#        elo3=str(i["importance_elo"]).split(sep="_")[-1]
#        elo4=str(i["importance_elo"]).split(sep="_")[-1]
#        elo5=str(i["importance_elo"]).split(sep="_")[-1]

        global_score = globals()[get_formula(i["deck"])](elo1,elo2)
        i["global_score"] = global_score
        push_dico(i, "UPDATE")
    logging.info("Compute global : done")

def shortcut_and_action(mode, fighters):
    def get_action(input): 
        found = ""
        for action, key in shortcuts.items(): 
            if str(input) in key: 
                if found != "" :
                    print("Several corresponding shortcuts found!")
                    logging.info("Several corresponding shortcuts found!")
                    sys.exit()
                found = action
        return found 

    action = ""
    while True:
        if action=="exit" :
            break
        logging.info("Shortcut : asking question")
        key = input(col_gre + questions[mode] + "  (h or ? for help)\n" + col_rst + "=>")
        logging.info("Shortcut : User typed : " + key)
        action = ""
        if key not in list(chain.from_iterable(shortcuts.values())) :
            print("Shortcut : Error : key not found : " + key)
            logging.info("Shortcut : Error : key not found : " + key)
            action = "show_help"
        else :
            action = str(get_action(key))
            logging.info("Shortcut : Action="+action)

        if action == "answer_level" :
            if key=="a": key="1"
            if key=="z": key="2"
            if key=="e": key="3"
            if key=="r": key="4"
            if key=="t": key="5"

            #f1old = fetch_entry("ID = " + str(fighters[0]))[0]
            f1new = f1old = fighters[0]
            #f2old = fetch_entry("ID = " + str(fighters[1]))[0]
            f2new = f2old = fighters[1]

            if mode=="mixed":
                mode=random.choice(["importance","time"])
                loggin.info("Shortcut : randomly chosed mode "+str(mode))

            date = int(time.time())
            field=str(mode)+"_elo"
            elo1=int(str(f1old[field]).split(sep="_")[-1])
            elo2=int(str(f2old[field]).split(sep="_")[-1])
            f1new[field] = str(f1old[field])+"_"+str(update_elo(elo1, expected(elo1, elo2), int(key), f1old['K_value']))
            f2new[field] = str(f1old[field])+"_"+str(update_elo(elo2, expected(elo2, elo1), int(key), f2old['K_value']))
            logging.info("Shortcut : elo : old new => 1 : " + str(elo1) + ", " + str(f1new[field]) + " ; 2 : " + str(elo2) + ", " + str(f2new[field]))

            f1new['nb_of_fight'] += 1
            f2new['nb_of_fight'] += 1
            if mode=="importance":
                f1new["delta_importance"] = abs(elo1-elo2)
                f2new["delta_importance"] = abs(elo1-elo2)
                f1new["date_importance_elo"] = str(date)
                f2new["date_importance_elo"] = str(date)
            if mode=="time":
                f1new['delta_time'] = abs(elo1-elo2)
                f2new['delta_time'] = abs(elo1-elo2)
                f1new["date_time_elo"] = str(date)
                f2new["date_time_elo"] = str(date)

            f1new['K_value'] = adjust_K(f1old['K_value'])
            f2new['K_value'] = adjust_K(f2old['K_value'])


            logging.info("Shortcut : fight, done")
            push_dico(f1new, "UPDATE")
            push_dico(f2new, "UPDATE")

            push_persist_data(f1new["deck"], mode, date, str(f1new["ID"]), str(f2new["ID"]), str(key)) 

            action="exit"
            continue


        if action == "skip_fight":
            logging.info("Shortcut : Skipped fight")
            print("Shortcut : skipped fight")
            break

        if action == "show_more_fields":
            logging.info("Shortcut : displaying the entries in full")
            print_2_entries(fighters, fighters[0]["deck"], mode, "all")
            continue



        if action == "edit":
            logging.info("Shortcut : edit : begin")
            ans = "no"
            while True :
                if ans in "undo" or ans in "exit" :
                    break
                ans = input("Which card do you want to edit?\n (left/right/u)=>")
                if ans in "left" or ans in "right" :
                    if ans in "left" :
                        entry = fighters[0]
                        logging.info("Shortcut : edit : editing left card, id = " + str(entry["ID"]))
                    else :
                        entry = fighters[1]
                        logging.info("Shortcut : edit : editing right card, id = " + str(entry["ID"]))

                    ## MAIN


                    logging.info("Shortcut : edit : done")
                    ans = "exit"
                    action = "exit"
                else :
                    print("Incorrect answer, Please choose left or right or undo")
                    logging.info("Shortcut : edit : wrong answer")
                    continue

            logging.info("Shortcut : edit : done")
            continue







        if action == "undo":
            # todo
            continue
        if action == "open_links":
            logging.info("Shortcut : openning links")
            print("Shortcut : openning links")
            relevant_fields = ["entry","metadata"]
            link=""
            for f in fighters :
                for fi in relevant_fields :
                    potential_links = str(f[fi]).split(sep=" ")
                    for l in potential_links:
                        if "http://" in l or "https://" in l:
                            links=l
                            logging.info("Shortcut : Openning link : " + l) 
                            if platform.system() == "Linux" :
                                subprocess.run([browser_path, l])
                            else :
                                webbrowser.open_new_tab(l)
            if links == "" :
                print("No links found!")
                logging.info("Shortcut : no links found")
                continue
            else :
                continue

        if action == "star":
            logging.info("Shortcut : star : begin")
            ans = "no"
            while True :
                if ans in "undo" or ans in "exit" :
                    break
                ans = input("Which card do you want to star?\n (left/right/u)=>")
                if ans in "left" or ans in "right" :
                    if ans in "left" :
                        #entry = fetch_entry("ID = " + str(fighters[0]))[0]
                        entry = fighters[0]
                        logging.info("Shortcut : star : starring left card, id = " + str(entry["ID"]))
                    else :
                        #entry = fetch_entry("ID = " + str(fighters[1]))
                        entry = fighters[1]
                        logging.info("Shortcut : star : starring right card, id = " + str(entry["ID"]))
                    entry["starred"] = 1
                    push_dico(entry, "UPDATE")
                    logging.info("Shortcut : star : done")
                    ans = "exit"
                    action = "exit"
                else :
                    print("Incorrect answer, Please choose left or right or undo")
                    logging.info("Shortcut : star : wrong answer")
                    continue

            logging.info("Shortcut : star : done")
            continue

        if action == "disable":
            logging.info("Shortcut : disable : begin")
            ans = "no"
            while True :
                if ans in "undo" or ans in "exit" :
                    break
                ans = input("Which card do you want to disable?\n (left/right/u)=>")
                if ans in "left" or ans in "right" :
                    if ans in "left" :
                        entry = fetch_entry("ID = " + str(fighters[0]))[0]
                        logging.info("Shortcut : disable : disabling left card, id = " + str(entry["ID"]))
                    else :
                        entry = fetch_entry("ID = " + str(fighters[1]))
                        logging.info("Shortcut : disable : disabling right card, id = " + str(entry["ID"]))
                    entry["disabled"] = 1
                    push_dico(entry, "UPDATE")
                    logging.info("Shortcut : disable : done")
                    ans = "exit"
                    action = "exit"
                else :
                    print("Incorrect answer, Please choose left or right or undo")
                    logging.info("Shortcut : disable : wrong answer")
                    continue

            continue
        if action == "show_help":
            logging.info("Shortcut : showing help")
            pprint.pprint(shortcuts)
            continue
        if action == "quit":
            logging.info("Shortcut : quitting")
            print("Quitting.")
            sys.exit()

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
