#!/usr/bin/env python3

##################################################################################
# Released under the GNU Lesser General Public License v2.
# Copyright (C) - 2020 - user "thiswillbeyourgithub" of the website "github".
# This file is part of LiTOY : a tool to help organiser various goals over time.
# Anki card template helping user to retain knowledge.
# 
# LiTOY is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# LiTOY is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with LiTOY.  If not, see <https://www.gnu.org/licenses/>.
# 
# for more information or to get the latest version go to :
# https://github.com/thiswillbeyourgithub/LiTOY
##################################################################################

import time
import logging
import random
import webbrowser
import sys
import sqlite3
import pprint
import readline
import re
import bs4
import requests
import pdftotext
import math

from    itertools      import chain
import urltitle
#from requests_html import HTMLSession

from   .settings        import *
from   .elo             import *
from   .media_retriever import *

# to get the terminal size on all OS :
import os
import shlex
import struct
import platform
import subprocess
 

# This file contains general functions used in the main loop :


# color codes :
col_red = "\033[91m"
col_blu = "\033[94m"
col_yel = "\033[93m"
col_rst = "\033[0m"
col_gre = "\033[92m"
spacer  = "    "  # nicer print message


def print_memento_mori(): # remember you will die
    if disable_lifebar == "no" :
        logging.info("Memento mori : begin")
        seg1 = useless_first_years
        seg2 = user_age - useless_first_years
        seg3 = user_life_expected - user_age - useless_last_years
        seg4 = useless_last_years
        resize = 1/user_life_expected*(sizex-17)
        print("Your life ("+ col_red + str(int((seg2)/(seg2 + seg3)*100)) + "%" + col_rst + ") : " + col_red + "x"*int(seg1*resize) + col_red + "X"*(int(seg2*resize)) + col_gre + "-"*(int(seg3*resize)) + col_yel + "_"*int(seg4*resize) + col_rst)
        logging.info("Memento mori : done")
    else : 
        logging.info("Memento mori : disabled")

def print_2_entries(fighters, deck, mode, all_fields="no"): # used when fighting
    logging.info("Printing fighters : "+ str(fighters[0]["ID"]) + " and " + str(fighters[1]["ID"]))
    print(col_blu + "#"*sizex + col_rst)
    print("Deck " + str(mode) + " delta = " + str(get_deck_delta(deck, mode)))
    print_memento_mori()
    print(col_blu + "#"*sizex + col_rst)
    def side_by_side(rowname, a, b, space=2, col=""):
        #https://stackoverflow.com/questions/53401383/how-to-print-two-strings-large-text-side-by-side-in-python
        rowname = rowname.ljust(30)
        col_width=int((int(sizex)-len(rowname))/2-int(space)*2)
        inc = 0
        while a or b:
            inc+=1
            if inc == 1:
                print(str(col) + str(rowname) + " "*space + "|" + a[:col_width].ljust(col_width) + " "*space + "|" + b[:col_width] + col_rst)
            else :
                print(str(col) + " "*(len(rowname)+space) + "|" + a[:col_width].ljust(col_width) + " "*space + "|" + b[:col_width] + col_rst)
            a = a[col_width:]
            b = b[col_width:]

    random.shuffle(fighters) # otherwise they can be ordered by ID
    if all_fields != "all":
        ids = ["IDs : ", str(fighters[0]["ID"]), str(fighters[1]["ID"])]
        side_by_side(ids[0], ids[1], ids[2])
        print("."*sizex)

        if str(fighters[0]['tags']) not in ["None",""] or str(fighters[1]['tags']) not in ["None", ""] :
            tags = ["Tags :", str(fighters[0]['tags']), str(fighters[1]['tags'])]
            side_by_side(tags[0], tags[1], tags[2])
            print("."*sizex)
        if str(fighters[0]['progress']) not in ["None", ""] or str(fighters[1]['progress']) not in ["None", ""] :
            progress = ["Progress :", str(fighters[0]['progress']), str(fighters[1]['progress'])]
            side_by_side(progress[0], progress[1], progress[2])
            print("."*sizex)
        if str(fighters[0]['starred']) != "0" or str(fighters[1]['starred']) != "0" :
            starred = ["Starred :", str(fighters[0]['starred']), str(fighters[1]['starred'])]
            side_by_side(starred[0], starred[1], starred[2], col = col_yel)
            print("."*sizex)

        content = ["Entry :", str(fighters[0]['entry']), str(fighters[1]['entry'])]
        side_by_side(content[0], content[1], content[2])
        print("."*sizex)

        # removed as I don't think it should be displayed all the time
        #deck = ["Deck :", str(fighters[0]['deck']), str(fighters[1]['deck'])]
        #side_by_side(deck[0], deck[1], deck[2])
        #print("."*sizex)
        #importance = ["Importance :", str(fighters[0]['importance_elo']).split("_")[-1], str(fighters[1]['importance_elo']).split("_")[-1]]
        #side_by_side(importance[0], importance[1], importance[2])
        #time = ["Time (high is short) :", str(fighters[0]['time_elo']).split("_")[-1], str(fighters[1]['time_elo']).split("_")[-1]]
        #side_by_side(time[0], time[1], time[2])
        #if str(fighters[0]['metadata']) != "None" or str(fighters[1]['metadata']) != "None" :
            #metadata = ["metadata :", str(fighters[0]['metadata']), str(fighters[1]['metadata'])]
            #side_by_side(metadata[0], metadata[1], metadata[2])

    if all_fields=="all": # print all fields, used more for debugging
       for i in get_field_names():
           side_by_side(str(i), str(fighters[0][i]), str(fighters[1][i]))
           print("."*sizex)

    # metadata :
    mediaTitle     = {0:"", 1:""}
    readingtime = {0:"", 1:""}
    vidlen      = {0:"", 1:""}
    for n,i in enumerate(fighters) :
        meta = i["metadata"]
        if "urlTabTitle" in meta:
            tabtitle = str(re.search("urlTabTitle=__.+?__", meta).group())[14:-2]
            mediaTitle[n] = tabtitle
        if "fileTitle" in meta:
            filetitle = str(re.search("fileTitle=__.+?__", meta).group())[11:-2]
            mediaTitle[n] = filetitle
        if "estimatedReadingTime" in meta:
            estimate = str(re.search("estimatedReadingTime=__.+?__", meta).group())[23:-2]
            readingtime[n] = estimate
        if "fileEstimatedReadingTime" in meta:
            estimate = str(re.search("fileEstimatedReadingTime=__.+?__", meta).group())[27:-2]
            readingtime[n] = estimate
        if "videoLength" in meta:
            length = str(re.search("videoLength=__.+?__", meta).group())[14:-2]
            vidlen[n] = str(length)
    if mediaTitle != {0:"", 1:""} :
        side_by_side("Media title :", str(mediaTitle[0]), str(mediaTitle[1]))
        print("."*sizex)
    if readingtime != {0:"", 1:""} :
        side_by_side("Reading time in minute :", str(readingtime[0]), str(readingtime[1]))
        print("."*sizex)
    if vidlen != {0:"", 1:""}:
        side_by_side("Watch time in minute :", str(vidlen[0]), str(vidlen[1]))
        print("."*sizex)

    print(col_blu + "#"*sizex + col_rst)

def pick_2_entries(mode, condition=""):  # used to choose who will fight who
    logging.info("Picking : begin")
    col = fetch_entry('ID >= 0 AND DISABLED IS 0 ' + condition)
    random.shuffle(col)  # helps when all entries are the same, ie when begining to use litoy
    if mode == "importance" : 
        col.sort(reverse=True, key=lambda x : int(x['delta_importance']))
        col_deltas_dates = col
    if mode == "time" :
        col.sort(reverse=True, key=lambda x : int(x['delta_time']))
        col_deltas_dates = col
    highest_5_deltas = col_deltas_dates[0:5]
    choice1 = random.choice(highest_5_deltas) # first opponent

    # a fraction of the time, the card that was used the farther away in time will be picked,
    # else it will be the one with the highest delta
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

def print_syntax_examples():  # used when an error is thrown
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
    print("   * python3 __main__.py --edit 'CONDITION' FIELD NEWVALUE")

    print("Changing a setting :")

    print("List tags, decks and number of cards :")
    print("   * python3 __main__.py --state")

    print("Compare entries :")
    print("   * python3 __main__.pay --fight imp -n 10 --deck DECK")

    print("Example of formula in settings.py :")
    print('   * formula_list = { "deckname" : "formula_name", "Toread" : "sum_elo", "DIY" : "sum_elo" }"')

    print("Current shortcuts in fight mode :")
    pprint.pprint(shortcuts)
    print("Meaning of the score :")
    print("          pressing 1 means you strongly favor the entry on the left on the question")
    print("          pressing 5 means you strongly favor the entry on the right")
    print("          pressing 3 means you think the 2 entries are of equal value")
    print("#"*sizex)

    logging.info("Printing syntax example : done")

def compute_Global_score():  # comptes the score that will be used for final ranking
    # this function is triggered just before displaying the ranks
    logging.info("Compute global : all cards")

    # check if the formulas declared in the dictionnary in  settings.py 
    # correspond to function that have been defined
    decks = list(get_decks())
    formulas = list(deck_and_formula_table.keys())
    needed_formula = deck_and_formula_table.values()
    defined_function = globals()
    if decks != formulas :
        print(col_red + "WARNING : deck list and formula list don't correspond in the settings" + col_rst)
        logging.info("Compute global : deck list and formula list don't correspond in the settings")
    for i in needed_formula :  # check only if formula is missing, as the program has to stop otherwise
        if i not in defined_function :
            print("Compute global : Missing formula declaration : " + i)
            logging.info("Compute global : Missing formula declaration : " + i)
            sys.exit()

    def get_formula(deck): 
        found = ""
        for key, formula in deck_and_formula_table.items(): 
            if str(deck) in key: 
                if found != "" :
                    print("Several corresponding formulas found!")
                    logging.info("Several corresponding formulas found!")
                    sys.exit()
                found = formula
        return found 

    all_cards = fetch_entry("ID >=0")
    for n,i in enumerate(all_cards):
        try : 
            formula = deck_and_formula_table[i["deck"]]
        except TypeError:
            print(col_red + "Type error, are you sure the deck name has been put in formula_dict in settings.py?")
            logging.info("Compute global score : type error, probably deck name has not been added to formula_dict")
            sys.exit()
        except KeyError:
            print(col_red + "Key error, are you sure the deck name has been put in formula_dict in settings.py?")
            logging.info("Compute global score : Key error, probably deck name has not been added to formula_dict")
            sys.exit()

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
    # shortcuts are stored in settings.py
    def get_action(input):   # get action from the keypress pressed
        found = ""
        for action, keypress in shortcuts.items(): 
            if str(input) in keypress: 
                if found != "" :
                    print("Several corresponding shortcuts found!")
                    logging.info("Several corresponding shortcuts found!")
                    sys.exit()
                found = action
        if action == "":
            logging.info("No shortcut found, key = " + str(input))
            action = "show_help"

        return found 

    action = ""
    while True:
        start_time = time.time() # to get time elapsed

        if action=="exit_outerloop" :  # not a shortcut, but used as a way to exit the while loop
            # not to be confused with "quit"
            break
        action = ""

        logging.info("Shortcut : asking question, mode = " + str(mode))
        keypress = input(col_gre + questions[mode] + "  (h or ? for help)\n" + col_rst + "=>")
        logging.info("Shortcut : User typed : " + keypress)

        if keypress not in list(chain.from_iterable(shortcuts.values())) :
            print("Shortcut : Error : keypress not found : " + keypress)
            logging.info("Shortcut : Error : keypress not found : " + keypress)
            action = "show_help"
        else :
            action = str(get_action(keypress))
            logging.info("Shortcut : Action="+action)

        if action == "answer_level" : # where the actual fight takes place
            if keypress=="a": keypress="1"
            if keypress=="z": keypress="2"
            if keypress=="e": keypress="3"
            if keypress=="r": keypress="4"
            if keypress=="t": keypress="5"

            if mode=="mixed":
                mode=random.choice(["importance","time"])
                loggin.info("Shortcut : randomly chosed mode "+str(mode))

            f1new = f1old = fighters[0]
            f2new = f2old = fighters[1]

            date = int(time.time())
            field=str(mode)+"_elo"
            elo1=int(str(f1old[field]).split(sep="_")[-1])
            elo2=int(str(f2old[field]).split(sep="_")[-1])
            f1new[field] = str(f1old[field])+"_"+str(update_elo(elo1, expected(elo1, elo2), int(keypress), f1old['K_value']))
            f2new[field] = str(f1old[field])+"_"+str(update_elo(elo2, expected(elo2, elo1), int(keypress), f2old['K_value']))
            logging.info("Shortcut : elo : old new => 1 : " + str(elo1) + ", " + str(f1new[field]) + " ; 2 : " + str(elo2) + ", " + str(f2new[field]))

            f1new['nb_of_fight'] += 1
            f2new['nb_of_fight'] += 1
            f1new['K_value'] = adjust_K(f1old['K_value'])
            f2new['K_value'] = adjust_K(f2old['K_value'])
            if mode=="importance":
                f1new["delta_importance"] = abs(int(str(f1new["importance_elo"]).split("_")[-1]) - int(str(f1new["importance_elo"]).split("_")[-2]))*math.log(int(f1new["K_value"]))
                f2new["delta_importance"] = abs(int(str(f2new["importance_elo"]).split("_")[-1]) - int(str(f2new["importance_elo"]).split("_")[-2]))*math.log(int(f2new["K_value"]))
                f1new["date_importance_elo"] = str(date)
                f2new["date_importance_elo"] = str(date)
            if mode=="time":
                f1new["delta_time"] = abs(int(str(f1new["time_elo"]).split("_")[-1]) - int(str(f1new["time_elo"]).split("_")[-2]))*math.log(int(f1new["K_value"]))
                f2new["delta_time"] = abs(int(str(f2new["time_elo"]).split("_")[-1]) - int(str(f2new["time_elo"]).split("_")[-2]))*math.log(int(f2new["K_value"]))
                f1new["date_time_elo"] = str(date)
                f2new["date_time_elo"] = str(date)
            elapsed = int((time.time() - start_time)*1000) # in milliseconds
            f1new['ms_spent_comparing'] = int(f1new['ms_spent_comparing'] + elapsed)
            f2new['ms_spent_comparing'] = int(f2new['ms_spent_comparing'] + elapsed)



            logging.info("Shortcut : fight, done")
            push_dico(f1new, "UPDATE")
            push_dico(f2new, "UPDATE")

            push_persist_data(f1new["deck"], mode, date, str(f1new["ID"]), str(f2new["ID"]), str(keypress)) 

            action="exit_outerloop"
            continue


        if action == "skip_fight":
            logging.info("Shortcut : Skipped fight")
            print("Shortcut : skipped fight")
            break

        if action == "show_more_fields":  # display all the fields from a card
            logging.info("Shortcut : displaying the entries in full")
            print("\n"*(sizey-10))
            print_2_entries(fighters, fighters[0]["deck"], mode, "all")
            continue

        if action == "edit":  # edit field of one of the current fighters
            logging.info("Shortcut : edit : begin")
            ans = "no"
            while True :
                if ans in "undo" or ans in "exit_innerloop" :
                    break
                ans = input("Which card do you want to edit?\n (left/right/u)=>")
                if ans in "left" or ans in "right" :
                    if ans in "left" :
                        entry = fighters[0]
                        logging.info("Shortcut : edit : editing left card, id = " + str(entry["ID"]))
                    else :
                        entry = fighters[1]
                        logging.info("Shortcut : edit : editing right card, id = " + str(entry["ID"]))

                    print("Field currently in the db : " + col_blu + str(get_field_names()) + col_rst)
                    chosenfield = str(input("What field do you want to edit?\n"))
                    logging.info("Shortcut : edit : user wants to edit field " + chosenfield)
                    try :
                        old_value = str(entry[chosenfield])
                    except KeyError:
                        print("Wrong field name")
                        logging.info("Shortcut : edit : wrong field name")
                        continue
                    if platform.system is not "Windows" :
                        new_value = str(rlinput("Enter the desired new value for field '" + chosenfield +"'\n", prefill=old_value))
                    else :
                        logging.info("Shortcut : edit : Windows user, no prefilled input")
                        new_value = str(input("Enter the desired new value for field '" + chosenfield +"'\n"))
                    logging.info("Shortcut : edit : field=" + chosenfield + ", old_value='" + old_value + "', new_value='" + new_value + "'")
                    entry[chosenfield] = new_value
                    push_dico(entry, "UPDATE")
                    ans = "exit_innerloop"
                    logging.info("Shortcut : edit : done")
                else :
                    print("Incorrect answer, Please choose left or right or undo")
                    logging.info("Shortcut : edit : wrong answer")
                    logging.info("Shortcut : edit : done")
                    continue
            print_2_entries(fighters, fighters[0]["deck"], mode)
            continue







        if action == "undo":
            print("The undo function has not been implemented yet!")
            logging.info("Shortcut : called for undo")
            continue

        if action == "open_media":  # if links are found in the entry, open them
            logging.info("Shortcut : openning media")
            print("Shortcut : openning media")
            status = []
            status = status + find_media(fighters[0], "auto-open") + find_media(fighters[1], "auto-open")
            if status == []:
                print("No media found!")
                logging.info("Shortcut : no media found")
                continue
            else :
                print("Done openning media")
                continue

        if action == "star":  # useful to get back to it to edit etc after a fight
            logging.info("Shortcut : star : begin")
            ans = "no"
            while True :
                if ans in "undo" or ans in "exit_innerloop" :
                    break
                ans = input("Which card do you want to star?\n (left/right/u)=>")
                if ans in "left" or ans in "right" :
                    if ans in "left" :
                        entry = fighters[0]
                        logging.info("Shortcut : star : starring left card, id = " + str(entry["ID"]))
                    else :
                        entry = fighters[1]
                        logging.info("Shortcut : star : starring right card, id = " + str(entry["ID"]))
                    entry["starred"] = 1
                    push_dico(entry, "UPDATE")
                    logging.info("Shortcut : star : done")
                    ans = "exit_innerloop"
                    action = "exit_outerloop"
                else :
                    print("Incorrect answer, Please choose left or right or undo")
                    logging.info("Shortcut : star : wrong answer")
                    continue

            logging.info("Shortcut : star : done")
            continue

        if action == "disable":  # disable an entry
            logging.info("Shortcut : disable : begin")
            ans = "no"
            while True :
                if ans in "undo" or ans in "exit_innerloop" :
                    break
                ans = input("Which card do you want to disable?\n (left/right/both/undo)=>")
                if ans in "undo":
                    logging.info("Shortcut : disable : input = " + ans)
                    print("Undone.")
                    continue
                if ans not in "both" and ans not in "left" and ans not in "right" and ans not in "undo" :
                    print("Incorrect answer, Please choose left or right or undo")
                    logging.info("Shortcut : disable : wrong answer")
                    continue
                if ans in "both" :
                    logging.info("Shortcut : disable : disabling both cards, id = " + str(fighters[0]["ID"]) + " and " + str(fighters[1]["ID"]))
                    fighters[0]["disabled"] = 1
                    fighters[1]["disabled"] = 1
                    fighters[0]["metadata"] = str(fighters[0]["metadata"]) + " dateWhenDisabled="+str(int(time.time()))
                    fighters[1]["metadata"] = str(fighters[1]["metadata"]) + " dateWhenDisabled="+str(int(time.time()))
                    push_dico(fighters[0], "UPDATE")
                    push_dico(fighters[1], "UPDATE")
                    logging.info("Shortcut : disable : done")
                    ans = "exit_innerloop"
                    action = "exit_outerloop"
                    continue
                elif ans in "left" or ans in "right" :
                    if ans in "left" :
                        entry = fighters[0]
                        logging.info("Shortcut : disable : disabling left card, id = " + str(entry["ID"]))
                    elif ans in "right" :
                        entry = fighters[1]
                        logging.info("Shortcut : disable : disabling right card, id = " + str(entry["ID"]))
                    entry["disabled"] = 1
                    entry["metadata"] = str(entry["metadata"]) + " dateWhenDisabled="+str(int(time.time()))
                    push_dico(entry, "UPDATE")
                    logging.info("Shortcut : disable : done")
                    ans = "exit_innerloop"
                    action = "exit_outerloop"
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



def rlinput(prompt, prefill=''):  # prompt with prefilled text
    # https://stackoverflow.com/questions/2533120/show-default-value-for-editing-on-python-input-possible
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    readline.parse_and_bind("tab: complete")
    try:
       return input(prompt)  # or raw_input in Python 2
    finally:
      readline.set_startup_hook()


#### SQL functions :
def init_table():  # used to create the table if none is found, but launched everytime just in case
    # the main table is used to store each entry
    # the persistent table is used to store data related to litoy

    logging.info("Init table")
    query_create_table = '\
            CREATE TABLE IF NOT EXISTS LiTOY(\
            ID INTEGER,\
            date_added INTEGER,\
            entry TEXT,\
            deck TEXT,\
            tags TEXT,\
            metadata TEXT,\
            starred INTEGER,\
            progress TEXT,\
            importance_elo TEXT,\
            date_importance_elo TEXT,\
            time_elo TEXT,\
            date_time_elo TEXT,\
            delta_importance INTEGER,\
            delta_time INTEGER,\
            global_score,\
            ms_spent_comparing INTEGER,\
            nb_of_fight INTEGER,\
            K_value INTEGER,\
            disabled INTEGER\
            )'
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute(query_create_table)

    # persistent settings and data :
    query_create_pers_sett_table = '\
            CREATE TABLE IF NOT EXISTS PERS_SETT(\
            date TEXT,\
            deck TEXT,\
            mode TEXT,\
            seq_delta TEXT,\
            who_fought_who TEXT\
            )'
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute(query_create_pers_sett_table)
    db.commit(); db.close()
    logging.info("Done init table")



def add_entry_todb(args):
        logging.info("Addentry : begin")
        newentry = {} 
        if args["deck"] == None :
            print("No deckname supplied")
            logging.info("Addentry : No deckname supplied")
            print_syntax_examples()
            print("Here are the decks that are already in your db :")
            print(get_decks())
            sys.exit()
        try :
            if args["tags"]==None:
                logging.info("No tags supplied")
                rep = input("are you sure you don't want to add tags? They are really useful!\n(Yes/tags)=>")
                if rep in "yes" :
                    logging.info("Import : Won't use tags")
                    newentry['tags'] = ""
                else :
                    newentry['tags']=str(rep)
        except KeyError :  # tags contains a list and is not Nonetype when called using --import
            pass
        else :
            newentry["tags"] = str(" ".join(args["tags"]))[0:]

        newentry['entry'] = str(args['addentry'][0])
        newentry['deck'] = str(args["deck"][0])
        if args["metadata"] is not None:
            newentry["metadata"] = args['metadata']
        else : newentry["metadata"] = ""

        cur_time = str(int(time.time()))
        newID = str(int(get_max_ID())+1)
        newentry['ID'] = newID
        newentry['date_added'] = cur_time
        newentry['starred'] = "0"
        newentry['progress'] = ""
        newentry['importance_elo'] = "0_" + str(default_score)
        newentry['time_elo'] = "0_" + str(default_score)
        newentry['global_score'] = ""
        newentry['date_importance_elo'] = cur_time
        newentry['date_time_elo'] = cur_time
        newentry['delta_importance'] = str(default_score)
        newentry['delta_time'] = str(default_score)
        newentry['ms_spent_comparing'] = "0"
        newentry['nb_of_fight'] = "0"
        newentry['disabled'] = 0
        newentry['K_value'] = K_values[0]

        logging.info("Addentry : Pushing entry to db, ID = " + newID)
        print(col_gre + "Addentry : Pushing entry to db, ID = " + newID + col_rst)
        print("")
        push_dico(newentry, "INSERT")


def get_decks():  # get list of decks
    logging.info("Getting deck list : begin")
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    all_entries = fetch_entry("ID >= 0")
    cat_list = []
    for i in range(len(all_entries)):
        cat_list.append(all_entries[i]['deck'])
    cat_list = list(set(cat_list))
    cat_list.sort()
    db.commit() ;   db.close()
    logging.info("Getting deck list : done")
    return cat_list

def get_tags() :  # get list of tags that are currently being used
    logging.info("Getting tag list : begin")
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    all_entries = fetch_entry("ID >= 0")
    tag_list = []
    for i in range(len(all_entries)):
        toadd = str(all_entries[i]['tags']).split(" ")
        tag_list += list(toadd)
        if tag_list[-1] == None:
            tag_list[-1] = ""
    tag_list = list(set(tag_list))
    tag_list.sort()
    try :
        tag_list.remove("")
    except ValueError:
        pass
    db.commit() ;   db.close()
    logging.info("Getting tag list : done")
    return tag_list

def get_deck_delta(deck, mode):  # get the delta of one specific deck
    logging.info("Getting delta : begin")
    all_cards = fetch_entry("ID >=0 AND disabled = 0 AND deck is '" + str(deck) + "'")
    wholedelta = 0
    for i in all_cards:
        wholedelta += int(i["delta_"+str(mode)])
    return wholedelta
    logging.info("Getting delta : done")

def get_sequential_deltas(deck, mode):  # get the delta of each deck over time 
    logging.info("Getting sequential deltas : begin")
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    cursor.execute("SELECT date, seq_delta FROM PERS_SETT WHERE mode IS '"+ mode +"' AND deck IS '" + deck + "'")
    delta_x_dates_raw = cursor.fetchall()
    columns = cursor.description
    db.commit() ; db.close()
    delta_x_dates = turn_into_dict(delta_x_dates_raw, columns)
    logging.info("Getting sequential deltas : delta")
    return delta_x_dates


def get_field_names():  # get the list of all the fields used in the entry db
    logging.info("Getting field names : begin")
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    entry = fetch_entry("ID = 1")
    db.commit() ; db.close()
    try :
        result = list(entry[0].keys())
    except :
        logging.info("No deck found")
        result = "None"
    logging.info("Getting field names : done")
    return result

def get_max_ID():  # used to get the maximum ID number attributed to a card currently in the db, to ensure ID's are unambiguous
    logging.info("Getting maxID : begin")
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    cursor.execute('''SELECT MAX(ID) FROM LiTOY''')
    maxID = cursor.fetchone()[0]
    db.commit() ; db.close()
    try : # if None
        maxID = int(maxID)
    except : # then 0
        maxID = 0 
    logging.info("MaxID = " + str(maxID))
    logging.info("Getting maxIS : done")
    return maxID

def check_db_consistency():  # used to make basic tests to know if some incoherent values are found
    logging.info("Checking database consistency")
    #compute_Global_score()  # commented to avoid circular importation
        # https://stackoverflow.com/questions/1556387/circular-import-dependency-in-python
    def print_check(id, fieldname, value, error) :
        msg = "CONSISTENCY ERROR : ID="+str(id) + ", "+str(fieldname) + "='"+str(value)+"' <= " + error
        print(msg)
        logging.info(msg)
    all_entries = fetch_entry("ID >=0")
    for i,content in enumerate(all_entries) :
        one_entry = all_entries[i]
#        try : int(one_entry['importance_elo'])
#        except : print_check(i, "importance_elo", one_entry['importance_elo'], "Not an int")
#        try : int(one_entry['time_elo'])
#        except : print_check(i, "time_elo", one_entry['time_elo'], "Not an int")
#        try : int(one_entry['date_importance_elo'])
#        except : print_check(i, "date_importance_elo", one_entry['date_importance_elo'], "Not an int")
#        try : int(one_entry['date_time_elo'])
#        except : print_check(i, "date_time_elo", one_entry['date_time_elo'], "Not an int")

        if one_entry['entry'] == "" :
            print_check(i, "entry", one_entry['entry'], "Empty entry")

#        try : int(one_entry['date_time_elo'])
#        except : print_check(i, "date_time_elo", one_entry['date_time_elo'], "Not an int")

        process_all_metadata(one_entry, "UPDATE") 

        ##TODO
        # check if doublon id ou doublon entry
        # check delta imp et time
        # check if starred pas 0 ou 1
        # check if date added int
        # check if number of dates correspond to fighting number
        # check if empty deck
        # check if global score not int
        # check time comparing
        # check nb of fight is int
        # check K value part of the setting
    logging.info("Done checking consistency")

def fetch_entry(condition):  # used to query all fields from an entry
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    logging.info("Fetching  : whole entry on condition : "+condition)
    queryFetch = 'SELECT * FROM LiTOY WHERE ' + str(condition)
    logging.info("Fetching : SQL : " + queryFetch)
    cursor.execute(queryFetch)
    fetched_raw = cursor.fetchall()
    columns = cursor.description
    db.commit() ;   db.close()
    dictio = turn_into_dict(fetched_raw, columns)
    logging.info("Fetching : Done")
    return dictio

def turn_into_dict(fetched_raw, columns=""):  # used to turn the sql result to a python friendly dictionnary
    # https://stackoverflow.com/questions/28755505/how-to-convert-sql-query-results-into-a-python-dictionary
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    col_name = [col[0] for col in columns]
    fetch_clean = [dict(zip(col_name, row)) for row in fetched_raw]
    db.commit() ;   db.close()
    return fetch_clean

def push_dico(dico, mode):  # used to turn a python friendly dictionnary back into the sql db
    # https://blog.softhints.com/python-3-convert-dictionary-to-sql-insert/
    logging.info('Pushing dictionnary : ' + str(dico) + " ; mode = " + str(mode))
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    if mode == "INSERT" :
#        columns = ', '.join("`" + str(x).replace('/', '_') + "`" for x in dico.keys())
#        values = ', '.join("'" + str(x).replace('/', '_') + "'" for x in dico.values())
        columns = ', '.join("'" + str(x).replace("'","`") + "'" for x in dico.keys())
        values = ', '.join("'" + str(x).replace("'","`") + "'" for x in dico.values())
        query = "INSERT INTO LiTOY ( %s ) VALUES ( %s );" % (columns, values)
    if mode == "UPDATE" :
        query = "UPDATE LiTOY SET "
        entry_id = dico['ID']
        for a,b in dico.items():
            query = query + str(a) + " = \'" + str(b) + "\', "
        query = query[0:len(query)-2] + " WHERE ID = " + str(entry_id) + " ;"
    logging.info("Pushing dictionnary : SQL : " + query)
    cursor.execute(query)
    db.commit() ;   db.close()
    logging.info('Pushing dictionnary : Done')

def push_persist_data(deck, mode, time, id1, id2, score):  # used to push the data to the persistent db
    logging.info("Pushing persistent data  : begin")
    db = sqlite3.connect('database.db') ; cursor = db.cursor()

    delta_to_add = str(get_deck_delta(deck, mode))
    query_delta = "INSERT INTO PERS_SETT ( date, mode, deck, seq_delta, who_fought_who ) VALUES ( " + str(time) + ", '" + mode + "', '" + deck + "', " + delta_to_add + ", '" + id1+"_"+id2+":"+score + "')"
    #logging.info("SQL PUSH PERSI DATA : " + query_delta)
    cursor.execute(query_delta)
    db.commit() ; db.close()
    logging.info("Pushing persistent data : latest delta = " + delta_to_add)
    logging.info("Pushing persistent data : done")















# This file contains functions used to retrieve reading time from pdf or URL, 

def process_all_metadata(entry, action):  # used to store information related links found etc in the entry
    logging.info("Process all metadata : begin")
    if action not in ["UPDATE", "RETURN"]:
        logging.info("Process all metadata : invalid call")
        print("Process all metadata : invalid call")
        sys.exit()
    found = find_media(entry, "return")
    if len(found)==0:
        logging.info("Processing all metadata : none in entry with ID " + str(entry["ID"]))
    else:
        if entry["metadata"] is None: entry["metadata"] = ""
        print("Processing metadata for entry with ID " + str(entry["ID"]))
        for item in found:
            if default_path in item :
                print("        found path : " + item)
                logging.info("Processing all metadata : identified as path")
                if item[-3:] == "pdf" or item[-3:] == "txt" or item[-2:]=="md":
                    print("            path links to a text file (pdf, txt or md)")
                    logging.info("Processing all metadata : path links to a text file")
                    if item[-3:]=="pdf":
                        # estimating time to read
                        try :
                            with open(item, "rb") as f:
                                text_content = pdftotext.PDF(f)
                                text_content = str("\n").join(text_content)
                        except FileNotFoundError:
                            print(col_red + "FILE NOT FOUND : " + item)
                    else : 
                        f = open(item)
                        text_content = f.read()
                        f.close()
                    text_content = text_content.replace(" ","")
                    text_content = text_content.replace("\r","")
                    text_content = text_content.replace("\n","")
                    total_words = 0
                    for current_text in text_content:
                            total_words += len(current_text)/average_word_length
                    estimatedReadingTime = round(total_words/wpm,1)
                    entry["metadata"] = entry["metadata"] + "fileEstimatedReadingTime=__" + str(estimatedReadingTime) + "__"

                    # getting title
                    title = item.split(sep="/")[-1]
                    title.replace("__","_ _") # to make sure it doesn't interfere with the formatting
                    entry["metadata"] = entry["metadata"] + "fileTitle=__" + str(title) + "__"

            elif "http" in item :
                if "pdf" in item : # if the webpage links to a pdf
                    print(spacer*1 + "found weblink to a pdf : " + item)
                    logging.info("Processing all metadata : identified as link to a pdf")
                    pass
                else :
                    print(spacer*1 + "found webpage : " + item)

                    print(spacer*2 + "Getting page title...")
                    logging.info("Processing all metadata : identified as link to an article")
                    useWB=0
                    title=""
                    try :
                        reader = urltitle.URLTitleReader(verify_ssl=True)
                        title = reader.title(item)
                    except urltitle.urltitle.URLTitleError as err :
                        logging.info("Processing all metadata : error, probably 404 : " + str(err))
                        useWB=1
                    if "not found" in title or "404" in title or "error" in title or useWB == 1 or "forbidden" in title or "403" in title :
                        print(col_yel + spacer*2 + "Needs to use the Wayback Machine!" + col_rst)
                        logging.info("Processing all metadata : dead url, using the wayback machine")
                        itemBackup = item
                        item = item.replace("https:/","http:/")
                        item = item.replace("http:/","")
                        item = "https://web.archive.org/web/2/" + item
                        reader = urltitle.URLTitleReader(verify_ssl=True)
                        title = reader.title(item)
                        entry["metadata"] = entry["metadata"] + "neededToUseWaybackmachine=__1__"
                    title.replace("'","`")
                    title.replace(",",".")
                    entry["metadata"] = entry["metadata"] + "urlTabTitle=__" + title + "__"

                    print(spacer*3 + "Title : " + title)
                    print(spacer*4 + "Estimating reading time...")
                    # http://www.assafelovic.com/blog/2017/6/27/estimating-an-articles-reading-time
                    # https://github.com/assafelovic/reading_time_estimator/blame/master/reading_time_estimator.py
                    html = ""
                    while html == "":
                        try :
                            html = requests.get(item).text
                        except requests.exceptions.ConnectionError as err :
                            logging.info("Processing all metadata : error found : " + str(err))
                            print(spacer*4 + "Connection reset, retrying using the wayback machine...")
                            if "https://web.archive.org" not in item:
                                itemWB = item.replace("https:/","http:/")
                                itemWB = itemWB.replace("http:/","")
                                itemWB = "https://web.archive.org/web/2/" + itemWB
                                html = requests.get(itemWB).text
                                logging.info("Processing all metadata : wayback machine URL : " + itemWB)
                                entry["metadata"] = entry["metadata"] + "neededToUseWaybackmachine=__1__"
                            else :
                                logging.info("Processing all metadata : error, already using wayback machine!")
                                print("HUGE ERROR")
                                sys.exit()

                    soup = bs4.BeautifulSoup(html, 'html5lib')
                    texts = soup.findAll(text=True)
                    if "403" in " ".join(texts) or "forbidden" in " ".join(texts):
                        logging.info("Processing all metadata : forbidden url, using wayback machine")
                        itemWB = item.replace("https:/","http:/")
                        itemWB = itemWB.replace("http:/","")
                        itemWB = "https://web.archive.org/web/2/" + itemWB
                        html = requests.get(itemWB).text
                        soup = bs4.BeautifulSoup(html, 'html5lib')
                        texts = soup.findAll(text=True)
                    def is_visible(element):
                        if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
                            return False
                        elif isinstance(element, bs4.element.Comment):
                            return False
                        elif element.string == "\n":
                            return False
                        return True
                    def filter_visible_text(page_texts):
                            return filter(is_visible, page_texts)
                    def count_words_in_text(text_list, word_length):
                            total_words = 0
                            for current_text in text_list:
                                    total_words += len(current_text)/average_word_length
                            return total_words
                    def estimate_reading_time(url):
                            filtered_text = filter_visible_text(texts)
                            total_words = count_words_in_text(filtered_text, average_word_length)
                            return round(total_words/wpm,1)
                    est = estimate_reading_time("http://www.assafelovic.com/blog/2017/6/27/estimating-an-articles-reading-time")
                    entry["metadata"] = entry["metadata"] + "estimatedReadingTime=__" + str(est) + "__"
                    print(spacer*5 + str(est) + "m")  # printing estimation


                    if "tube" in item or "ytb" in item :
                        if "watch" in item :  # failsafe
                            print(spacer*2 + "Getting youtube video duration...")
                            try :
                                replacement_link = yt_instance + str(re.search("watch.+", item).group())
                            except AttributeError:
                                logging.info("Processing all metadata : needs to use the other youtube instance!")
                                replacement_link = yt_instance2 + str(re.search("watch.+", item).group())
                            html = requests.get(replacement_link).text
                            soup = bs4.BeautifulSoup(html, "html.parser")
                            line = re.search("length_seconds.+: \d+\.\d+", str(soup)).group()
                            vidlen = str(round(int(re.search("\d+", line).group())/60,1))
                            entry["metadata"] = entry["metadata"] + "videoLength=__" + str(vidlen) + "__"
                            print(spacer*3 + vidlen + "m")

    if action == "UPDATE" :
        push_dico(entry, action)
    if action == "RETURN":
        return entry
    logging.info("Process all metadata : done")

def find_media(entry, action=""):  # finds media in the entry, action can be "auto-open" or "return"
    logging.info("Finding media : begin")
    relevant_fields = ["entry","metadata"]
    found=[]
    for field in relevant_fields :
        temp_entry = str(entry[field]).replace("['","").replace("']","")
        words = str(temp_entry).split(" ")
        for word in words:
            if default_path in word:  # extract path from the whole string
                wholepath=""
                string = str(temp_entry).split("__")
                for section in string :
                    if str(default_path) in str(section):
                       wholepath=section
                if wholepath=="":
                    print("Path could not be extracted!")
                    sys.exit()
                if action == "auto-open" :
                    logging.info("Finding media : Openning folder : " + wholepath)
                    if platform.system() == "Linux" :
                        if platform.system() == "Windows":
                            os.startfile(wholepath)
                        elif platform.system() == "Darwin":
                            subprocess.Popen(["open", wholepath])
                        else:
                            subprocess.Popen(["xdg-open", wholepath])
                elif action == "return" :
                    logging.info("Finding media : returning folder : " + wholepath)
                    found.append(wholepath)

            if "http://" in word or "https://" in word or "www" in word:
                url=word
                if action == "auto-open" :
                    logging.info("Finding media : Openning link : "+url) 
                    if platform.system() == "Linux" :
                        subprocess.run([browser_path, url])
                    else :
                        webbrowser.open_new_tab(url)
                elif action == "return" :
                    logging.info("Finding media : returning link : "+url)
                    found.append(url)
    logging.info("Finding media : done")
    return found














def get_terminal_size():
    """
    only used to get terminal size, to adjust the width when printing lines
    - get width and height of console
    - works on linux,os x,windows,cygwin(windows)
    originally retrieved from:
    http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
    then from here : https://gist.github.com/jtriley/1108174
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
    return [tuple_xy[0], tuple_xy[1]]
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
both_size = get_terminal_size()
sizex = int(both_size[0])
sizey = int(both_size[1])
