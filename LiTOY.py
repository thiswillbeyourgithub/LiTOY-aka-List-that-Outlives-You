#!/usr/bin/env python3.9

import argparse
import time
import random
from statistics import mean, stdev, median
import readline
import platform
import subprocess
import sys
import os
from itertools import chain
from pathlib import Path
from other_functions import get_terminal_size
from pprint import pprint
from tqdm import tqdm

import get_wayback_machine
import json
import pandas as pd
import pdftotext
import requests
import youtube_dl
from bs4 import BeautifulSoup
from moviepy.editor import VideoFileClip

import logging
from logging.handlers import RotatingFileHandler
import pdb
import signal
from contextlib import suppress
from youtube_dl.utils import ExtractorError, DownloadError

###############################################################################
# Summary of each section
# 0. Banner and license
# 1. User settings
# 2. Fonctions, Classes, etc :
#          def debug_signal_handler(signal, frame):
#          def log_(string, onlyLogging=True):
#          def DB_file_check(path):
#          def importation(path):
#          def wrong_arguments_(args):
#          def add_new_entry(df, content):
#          def pick_entries(df):
#          def print_memento_mori(): # remember you will die
#          def print_2_entries(id_left, id_right, mode, all_fields="no"):
#              def side_by_side(rowname, a, b, space=2, col=""):
#          def show_podium(df):
#          def show_stats(df, printing=True):
#          def rlinput(prompt, prefill=''):
#          def shortcut_and_action(id_left, id_right, mode, progress):
#              def fetch_action(input):
#              def star(entry):
#              def disable(entry):
#              def edit(entry):
#          def get_tags_from_content(string):
#          def get_meta_from_content(string):
#          def extract_youtube(url):
#          def extract_local_video(link):
#          def extract_pdf_url(url):
#          def extract_pdf_local(path):
#          def extract_txt(path):
#          def extract_webpage(url):
#          def expected_elo(elo_A, elo_B, Rp=100):
#          def update_elo(elo, exp_score, real_score, K):
#          def adjust_K(K0):
#          def compute_global_score(iELO, tELO):
#          def json_periodic_save():
#              def __init__(self, db_path):
#              def _reload_df(self):
#              def save_to_file(self, df):
#              def create_database(self):
#              def entry_duplicate_check(self, df, new):
#              def get_tags(self, df):
# 3. Main routine

###############################################################################
# 0. Banner and license

###################################################################
#     __    _ ____________  __                                    #
#    / /   (_)_  __/ __ \ \/ /                                    #
#   / /   / / / / / / / /\  /                                     #
#  / /___/ / / / / /_/ / / /                                      #
# /_____/_/ /_/  \____/ /_/                                       #
#   ________            __    _      __     ________          __  #
#  /_  __/ /_  ___     / /   (_)____/ /_   /_  __/ /_  ____ _/ /_ #
#   / / / __ \/ _ \   / /   / / ___/ __/    / / / __ \/ __ `/ __/ #
#  / / / / / /  __/  / /___/ (__  ) /_     / / / / / / /_/ / /_   #
# /_/ /_/ /_/\___/  /_____/_/____/\__/    /_/ /_/ /_/\__,_/\__/   #
#    ____        __  ___                    __  __                #
#   / __ \__  __/ /_/ (_)   _____  _____    \ \/ /___  __  __     #
#  / / / / / / / __/ / / | / / _ \/ ___/     \  / __ \/ / / /     #
# / /_/ / /_/ / /_/ / /| |/ /  __(__  )      / / /_/ / /_/ /      #
# \____/\__,_/\__/_/_/ |___/\___/____/      /_/\____/\__,_(_)     #
#                                                                 #
###################################################################

###############################################################################
# Released under the GNU Lesser General Public License v2.                    #
# Copyright (C) - 2021 - user "thiswillbeyourgithub" of the website "github". #
# This file is part of LiTOY : a tool to help organiser various goals over    #
# time.                                                                       #
#                                                                             #
# LiTOY is free software: you can redistribute it and/or modify               #
# it under the terms of the GNU Lesser General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# LiTOY is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU Lesser General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the GNU Lesser General Public License    #
# along with LiTOY.  If not, see <https://www.gnu.org/licenses/>.             #
#                                                                             #
# for more information or to get the latest version go to :                   #
# https://github.com/thiswillbeyourgithub/LiTOY                               #
###############################################################################


###############################################################################
# 1. User settings

# lifebar arguments :
disable_lifebar     = "no"
useless_first_years = 13
user_age            = 24
user_life_expected  = 90
useless_last_years  = 20

# save very often a copy of the whole database as a json file
json_auto_save = True

# number of entries to pick for review at each launch (default=10)
n_to_review = 10

# for reading time estimation :
wpm = 200
average_word_length = 6

# used when reviewing
questions = {
        "importance": "What steps will make you likely to achieve your goals?",
#        "importance": "What steps will make you likely to achieve your goals?\
#\n* Which is more important?\n* If you had one hour to spend,\
#which would bring you more in your life?",
        "time": "Which task takes the less time to complete?",
        }

shortcuts = {"skip_review"      : ["s", "-"],
             "answer_level"     : ["1", "2", "3", "4", "5",
                                   "a", "z", "e", "r", "t"],
             "edit_left"        : ["el"],
             "edit_right"       : ["er"],
             "reload_media"     : ["re"],
             "undo"             : ["u"],
             "show_all_fields"  : ["m"],
             "star_left"        : ["xl"],
             "star_right"       : ["xr"],
             "disable_left"     : ["dl"],
             "disable_right"    : ["dr"],
             "open_media"       : ["o"],
             "repick"           : ["repick"],
             "show_help"        : ["h", "H", "?"],
             "quit"             : ["q"] }

# ELO :
K_values           =  [100, 80, 60, 40, 25, 17, 15, 12, 10]
# if you decide to change the setting, be careful : each new term has to be
# different and lower than the last one
default_score      =  1000  # default 1000
global_weights     =  (2, 1)  # gELO = 1st number*iELO + 2nd*tELO

# to avoid getting flagged for abusive web scraping
headers = {"User-Agent": "Mozilla/5.0"}

# color codes :
col_red = "\033[91m"
col_blu = "\033[94m"
col_yel = "\033[93m"
col_rst = "\033[0m"
col_gre = "\033[92m"
spacer = "    "  # nicer print message

###############################################################################
# 2. Functions, classes, etc

global cols
cols = ["ID", "date", "content", "metacontent", "tags",
        "starred", "iELO", "tELO", "DiELO", "DtELO", "gELO",
        "review_time", "n_review", "K", "disabled"]
# TODO : mention that in the README
# iELO stands for "importance ELO", DiELO for "delta iELO",
# gELO for "global ELO", etc


def debug_signal_handler(signal, frame):
    """
    Make the whole script interruptible using ctrl+c,
    you can then resume using 'c'
    """
    pdb.set_trace()


# misc functions
def log_(string, onlyLogging=True):
    """
    Append string to the logging file, if onlyLogging=False then
    will also print to user using tqdm.write
    """
    caller_name = str(sys._getframe().f_back.f_code.co_name)
    if not caller_name.startswith("<"):
        prefix = f"{caller_name}: "
    else:
        prefix = ""
    log.info(f"{time.asctime()}: {prefix}{string}")
    if onlyLogging is False or args["verbose"] is not False:
        tqdm.write(string)


def DB_file_check(path):
    "Check if the file and database already exists, if not create the file"
    db_location = Path(path)
    if db_location.exists():
        log_(f"Database file found at {path}")
        try:
            return True
        except ValueError as e:
            log_(f"ERROR: Litoy database not found in file at {path} :\
{e}", False)
            return None
    else:
        answer = input(f"No database file found at {path}, do you want me to\
create it?\ny/n?")
        if answer in "yes":
            db_location.touch()
            return None
        else:
            print("Exiting")
            raise SystemExit()


def importation(path):
    "Check if text file exists then import it into LiTOY"
    import_file = Path(path)
    if not import_file.exists():
        log_(f"ERROR: Import file not found at {path}, exiting", False)
        raise SystemExit()
    log_(f"Importing from file {path}", False)
    with import_file.open() as f:
        lines = f.readlines()
    lines = [li for li in lines if not str(li).startswith("#") and
             str(li) != "" and str(li) != "\n"]
    for line in tqdm(lines, desc="Processing line by line", unit="line",
                     ascii=False, dynamic_ncols=True, mininterval=0):
        line.strip()
        line = line.replace("\n", "")
        if not litoy.entry_duplicate_check(litoy.df, line):
            add_new_entry(litoy.df, line)


def wrong_arguments_(args):
    "Print user arguments then exit"
    print("Exiting because called with wrong arguments \nYour arguments:")
    pprint(args)
    raise SystemExit()


def add_new_entry(df, content):
    "Add a new entry to the pandas dataframe"
    tags = get_tags_from_content(content)
    metacontent = get_meta_from_content(content)

    # in case metacontent doesn't contain those keys, ignore exceptions:
    with suppress(KeyError, TypeError):
        # if url not working, reload it after 5 seconds :
        if "forbidden" in str(metacontent['title']).lower() or \
                "404" in str(metacontent['title']).lower() or\
                "403" in str(metacontent['title']).lower():
            log_(f"Waiting 5 seconds because apparent webpage loading limit\
                was reached while inspecting line : {content}", False)
            time.sleep(5)
            metacontent = get_meta_from_content(content)
        # if wayback machine was used : mention it in the tags
        if metacontent['wayback_used'] == "1":
            tags.append("wayback_machine")
        elif metacontent['wayback_machine'] == "wayback url not found":
            tags.append("url_not_found")
        metacontent.pop("wayback_used")

    try:
        newID = max(df.index)+1
    except ValueError:  # first card
        newID = 1
    new_dic = {
               "date": str(int(time.time())),
               "content": content,
               "metacontent": json.dumps(metacontent),
               "tags": json.dumps(sorted(tags)),
               "iELO": default_score,
               "tELO": default_score,
               "DiELO": default_score,
               "DtELO": default_score,
               "gELO": compute_global_score(default_score, default_score),
               "review_time": 0,
               "n_review": 0,
               "K": sorted(K_values)[-1],
               "starred": 0,
               "disabled": 0,
               }
    log_(f"Adding new entry : {new_dic}")
    for k, v in new_dic.items():
        df.loc[newID, k] = v
    litoy.save_to_file(df)


def pick_entries(df):
    """
    Pick entries for the reviews : the left one is chosen randomly
    among the 5 with the highest pick_factor, then n_to_review other entries
    are selected at random among the half with the highest pick factor.
    Note: the pick_score goes down fast.
    """
    picked_ids = []
    df = df.loc[df.disabled == 0].copy()
    valid_id = df.index  # to be sure not to pick disabled cards
    df["pick_score"] = df.K + df.DiELO*0.1 + df.DtELO*0.1
    df.sort_values(by="pick_score", axis=0, ascending=False, inplace=True)
    choiceL = int(df.iloc[0:5].sample(1).index[0])
    id_pick_list = [x for x in list(range(1, int((len(df.index)-1)/2)))
                    if x in valid_id and x != choiceL]
    choiceR = df.loc[id_pick_list, :].sample(
            min(n_to_review, len(id_pick_list)-1))
    picked_ids.append(choiceL)
    picked_ids.extend(choiceR.index)

    while picked_ids[0] in picked_ids[1:]:
        # this was a former test that should not be necessary  anymore
        # but I chose to keep it as failsafe
        log_("Picking entries one more time to avoid reviewing to itself",
                False)
        picked_ids = pick_entries(df)
    return picked_ids


def print_memento_mori():
    """
    Print a reminder to the user that life is short and times
    is always passing by faster as time goes on
    """
    if disable_lifebar == "no":
        seg1 = useless_first_years
        seg2 = user_age - useless_first_years
        seg3 = user_life_expected - user_age - useless_last_years
        seg4 = useless_last_years
        resize = 1/user_life_expected*(sizex-17)
        if random.random() > 0.99:
            string = "REMEMBER THAT TIME IS RUNNING OUT"
            for i in range(5):
                print(f"{col_red}{string}     {string}{col_rst}")
        print("Your life (" + col_red + str(int((seg2)/(seg2 + seg3)*100)) +
              "%" + col_rst + ") : " + col_red + "x"*int(seg1*resize) +
              col_red + "X"*(int(seg2*resize)) + col_gre +
              "-"*(int(seg3*resize)) + col_yel + "_"*int(seg4*resize) +
              col_rst)


def print_2_entries(id_left, id_right, mode, all_fields="no"):
    "Show the two entries to review side by side"
    print(col_blu + "#"*sizex + col_rst)
    print_memento_mori()
    print(col_blu + "#"*sizex + col_rst)

    def side_by_side(rowname, a, b, space=2, col=""):
        """
        from https://stackoverflow.com/questions/53401383/how-to-print-two-strings-large-text-side-by-side-in-python
        """
        rowname = rowname.ljust(15)
        a = str(a)
        b = str(b)
        col_width = int((int(sizex)-len(rowname))/2-int(space)*2)
        inc = 0
        while a or b:
            inc += 1
            if inc == 1:
                print(str(col) + str(rowname) + " "*space + "|" +
                      a[:col_width].ljust(col_width) + " "*space +
                      "|" + b[:col_width] + col_rst)
            else:
                print(str(col) + " "*(len(rowname)+space) + "|" +
                      a[:col_width].ljust(col_width) + " "*space +
                      "|" + b[:col_width] + col_rst)
            a = a[col_width:]
            b = b[col_width:]

    entry_left = litoy.df.loc[id_left, :].copy()
    entry_right = litoy.df.loc[id_right, :].copy()

    if all_fields != "all":
        side_by_side("ID", id_left, id_right)
        print("."*sizex)

        if "".join(entry_left.tags + entry_right.tags) != "":
            side_by_side("Tags", entry_left.tags, entry_right.tags)
            print("."*sizex)
        if int(entry_left.starred) + int(entry_right.starred) != 0:
            side_by_side("Starred", entry_left.starred, entry_right.starred,
                         col=col_yel)
            print("."*sizex)

        side_by_side("Entry", entry_left.content, entry_right.content)
        print("."*sizex)
        if mode == "importance":
            side_by_side("iELO", entry_left.iELO, entry_right.iELO)
            print("."*sizex)
        else:
            side_by_side("tELO",
                         entry_left.tELO, entry_right.tELO)
            print("."*sizex)
        side_by_side("K factor", entry_left.K, entry_right.K)

    # print all fields, used more for debugging
    if all_fields == "all":
        for c in litoy.df.columns:
            side_by_side(str(c), str(entry_left[c]), str(entry_right[c]))

    # metadata :
    js = []
    js.append(json.loads(entry_left.metacontent))
    js.append(json.loads(entry_right.metacontent))
    for x in [0, 1]:
        for y in ["type", "title", "length", "url"]:
            if y not in js[x].keys():
                js[x][y] = ""
    side_by_side("Length", js[0]["length"], js[1]["length"])
    side_by_side("Title", js[0]["title"], js[1]["title"])
    print("."*sizex)
    side_by_side("Path", js[0]["url"], js[1]["url"])
    side_by_side("Media type", js[0]["type"], js[1]["type"])

    print(col_blu + "#"*sizex + col_rst)


def show_podium(df):
    "Show the highest ranked things to do in LiTOY "
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', sizex)
    pd.set_option('display.max_colwidth', int(3*sizex/4))
    if args["verbose"] is True:  # print all fields
        pprint(df.sort_values(by="gELO", ascending=False)[0:10])
    else:
        df2 = df.loc[:, ["content", "gELO", "iELO", "tELO", "tags"]]
        pprint(df2.sort_values(by="gELO", ascending=False)[0:10])


def show_stats(df, printing=True):
    """
    shows statistics on the litoy database, but is also used to write at each
    launch the state of the database for later analysis
    """
    df = litoy.df.copy()
    df_nd = df[df['disabled'] == 0]
    df_virg = df[df['n_review'] == 0]
    if printing is True:
        action = print
    else:
        action = log_
    action(f"Number of entries in LiTOY : {len(df)}, and of non disabled entries \
only : {len(df_nd)}")
    action(f"Number of entries that have never been reviewed : {len(df_virg)}")
    action(f"Total number of review : {round(df_nd.n_review.sum(), 1)} \
average : {round(df_nd['n_review'].mean(), 2)}")
    action("")
    action("Average / standard deviation / median :")
    action(f"Importance score : {round(df_nd.iELO.mean(),1)} / \
{round(df_nd.iELO.std(), 2)}")
    action(f"Time score : {round(df_nd.tELO.mean(), 1)} / \
{round(df_nd.tELO.std() , 2)}")
    action(f"Global score : {round(df_nd.gELO.mean(), 1)} / \
{round(df_nd.gELO.std(), 2)}")
    pooled = list(df_nd.DiELO + df_nd.DtELO)
    action(f"Delta scores : {round(mean(pooled),1)} / {round(stdev(pooled),2)}\
/ {round(median(pooled), 2)}")
    action(f"K value : {round(df_nd.K.mean(), 1)} / {round(df_nd.K.std(), 2)} / {round(df_nd.K.median())}")
    action(f"Time spent reviewing : {round(df_nd.review_time.sum(), 1)} / \
{round(df_nd.review_time.std(), 2)}")


def rlinput(prompt, prefill=''):
    """
    prompt the user using prefilled text, but doesn't work on windows
    """
    # https://stackoverflow.com/questions/2533120/show-default-value-for-editing-on-python-input-possible
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    readline.parse_and_bind("tab: complete")
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()


def shortcut_and_action(id_left, id_right, mode, progress):
    """
    makes the link between keypresses and actions
    shortcuts are stored at the top of the file
    """
    entry_left = litoy.df.loc[id_left, :].copy()
    entry_right = litoy.df.loc[id_right, :].copy()
    log_(f"Waiting for shortcut for {id_left} vs {id_right} for {mode}")

    def fetch_action(input):
        "deduce action from user keypress"
        found = ""
        for action, keypress in shortcuts.items():
            if str(input) in keypress:
                if found != "":
                    log_("ERROR: Several corresponding shortcuts found!\
Quitting.", False)
                    raise SystemExit()
                found = action
        if action == "":
            log_(f"ERROR: No {str(input)} shortcut found")
            action = "show_help"
        return found

    def star(entry_id):
        "stars an entry_id during review"
        df = litoy.df.copy()
        df.loc[entry_id, "starred"] = 1
        litoy.save_to_file(df)
        log_(f"Starred entry_id {entry}", False)

    def disable(entry_id):
        "disables an entry during review"
        df = litoy.df.copy()
        assert df.loc[entry_id, "disabled"] == 0
        df.loc[entry_id, "disabled"] = 1
        litoy.save_to_file(df)
        log_(f"Disabled entry {entry_id}", False)

    def edit(entry_id):
        "edit an entry during review"
        log_(f"Editing entry {entry_id}")
        while True:
            df = litoy.df.copy()
            entry = df.loc[entry_id, :]
            print(f"Current fields available for edition : {list(df.columns)}")
            chosenfield = str(input("What field do you want to edit?\
(q to exit)\n>"))
            if chosenfield == "q" or chosenfield == "quit":
                break
            try:
                old_value = str(entry[chosenfield])
            except KeyError:
                log_("ERROR: Shortcut : edit : wrong field name", False)
                continue
            if platform.system() == "Windows":
                new_value = str(input("Enter the desired new value for field\
'" + chosenfield + "'\n"))
            else:
                new_value = str(rlinput("Enter the desired new value for\
field '" + chosenfield + "'\n", prefill=old_value))
            df.loc[entry_id, chosenfield] = new_value
            litoy.save_to_file(df)
            log_(f'Edited field "{chosenfield}", {old_value} => {new_value}',
                 False)
            break

    action = ""
    start_time = time.time()
    while True:
        action = ""
        log_(f"Asking question, mode : {mode}")
        print(f"{col_gre}{progress}/{n_to_review} {questions[mode]}\
(h or ? for help){col_rst}")
        keypress = input(">")

        if keypress not in list(chain.from_iterable(shortcuts.values())):
            log_(f"ERROR: keypress not found : {keypress}")
            action = "show_help"
        else:
            action = str(fetch_action(keypress))
            log_(f"Shortcut found : Action={action}")

        if action == "answer_level":  # where the actual review takes place
            if keypress == "a":
                keypress = 1
            if keypress == "z":
                keypress = 2
            if keypress == "e":
                keypress = 3
            if keypress == "r":
                keypress = 4
            if keypress == "t":
                keypress = 5
            keypress = int(keypress)-0.5
            date = time.time()
            assert entry_left["disabled"] == 0 and entry_right["disabled"] == 0

            eL_old = entry_left
            eR_old = entry_right
            eL_new = eL_old.copy()
            eR_new = eR_old.copy()

            if mode == "importance":
                elo_fld = "iELO"
                Delo_fld = "DiELO"
            else:
                elo_fld = "tELO"
                Delo_fld = "DtELO"
            eloL = int(eL_old[elo_fld])
            eloR = int(eR_old[elo_fld])

            eL_new[elo_fld] = update_elo(eloL, expected_elo(eloL, eloR),
                                         5-keypress, eL_old.K)
            eR_new[elo_fld] = update_elo(eloR, expected_elo(eloL, eloR),
                                         keypress, eR_old.K)
            log_(f"Elo: L: {eloL}=>{eL_new[elo_fld]} R:\
{eloR}=>{eR_new[elo_fld]}")

            eL_new["K"] = adjust_K(eL_old.K)
            eR_new["K"] = adjust_K(eR_old.K)
            eL_new[Delo_fld] = abs(eL_new[elo_fld] - eL_old[elo_fld])
            eR_new[Delo_fld] = abs(eR_new[elo_fld] - eR_old[elo_fld])
            eL_new["gELO"] = compute_global_score(eL_new.iELO, eL_new.tELO)
            eR_new["gELO"] = compute_global_score(eR_new.iELO, eR_new.tELO)
            eL_new["review_time"] = round(eL_new["review_time"] + date
                                          - start_time, 3)
            eR_new["review_time"] = round(eR_new["review_time"] + date
                                          - start_time, 3)
            eL_new["n_review"] += 1
            eR_new["n_review"] += 1

            df = litoy.df.copy()
            df.loc[id_left, :] = eL_new
            df.loc[id_right, :] = eR_new
            litoy.save_to_file(df)
            log_(f"Done reviewing {id_left} and {id_right}")
            break

        if action == "skip_review":
            log_("Skipped review", False)
            break

        if action == "show_all_fields":
            log_("Displaying the entries in full")
            print("\n"*10)
            print_2_entries(int(id_left), int(id_right), mode, "all")
            continue

        if action == "open_media":
            log_("Openning media")
            for ent_id in [id_left, id_right]:
                ent = litoy.df.loc[ent_id, :]
                js = json.loads(ent.metacontent)
                try:
                    path = str(js["url"])
                    if platform.system() == "Linux":
                        if platform.system() == "Windows":
                            os.startfile(path)
                        elif platform.system() == "Darwin":
                            subprocess.Popen(["open", path])
                        else:
                            subprocess.Popen(["xdg-open", path],
                                             stdout=open(os.devnull, 'wb'))
                except KeyError as e:
                    log_(f"url not found in entry {ent_id} : {e}")
            time.sleep(1.5)  # better display
            print("\n"*10)
            print_2_entries(int(id_left),
                            int(id_right),
                            mode=mode)
            continue

        if action == "reload_media":
            log_("Reloading media")
            for ent_id in [id_left, id_right]:
                df = litoy.df.copy()
                ent = df.loc[ent_id, :]
                content = ent["content"]

                old = args["verbose"]
                args["verbose"] = True
                metacontent = get_meta_from_content(content)
                args["verbose"] = old

                entry_left["metacontent"] = json.dumps(metacontent)
                df.loc[ent_id, "metacontent"] = json.dumps(metacontent)
                litoy.save_to_file(df)
                log_(f"New metacontent value for {ent_id} : {metacontent}")
            print_2_entries(int(id_left),
                            int(id_right),
                            mode=mode)
            print("\n"*10)
            continue

        if action == "edit_left":
            edit(id_left)
            continue
        if action == "edit_right":
            edit(id_right)
            continue
        if action == "star_left":
            star(id_left)
            continue
        if action == "star_right":
            star(id_right)
            continue
        if action == "disable_left":
            disable(id_left)
            return(action)
        if action == "disable_right":
            disable(id_right)
            return(action)

        if action == "undo":
            print("Undo function is not yet implemented,\
  manually correct the database using libreoffice calc after looking at\
  the logs. Or take a look at the saved json files")
            input("(press enter to resume reviewing session)")
            continue

        if action == "show_help":
            log_("Printing help :", False)
            pprint(shortcuts)
            continue

        if action == "repick":
            log_("Repicking entries", False)
            return "repick"

        if action == "quit":
            log_("Shortcut : quitting")
            print("Quitting.")
            raise SystemExit()


# functions related to one entry
def get_tags_from_content(string):
    "extracts tags from a line in the import file"
    splitted = string.split(" ")
    result = []
    for word in splitted:
        if word.startswith("tags:"):
            temp = str(word[5:])
            # removes non letter from tags, usually ,
            while not temp.isalnum():
                temp = temp[:-1]
            result.append(temp)
    return list(set(result))


def get_meta_from_content(string):
    """
    extracts all metadata from a line in the import file
    this does not include tags, which are indicated using tags:sometag in the
    line. Instead it's for example the length of a youtube video which link
    appears in the content.
    If several links are supplied, only the first one will be used
    """
    with suppress(UnboundLocalError):
        since = time.time() - last
        last = time.time()
        if since < 2:
            log_(f"Sleeping for {2-since} seconds", False)
            time.sleep(2-since)

    splitted = string.split(" ")
    for word in splitted:
        if word == "type:video":  # this forces to analyse as a video
            for word in splitted:
                if word.startswith("http") or word.startswith("www."):
                    log_(f"Extracting info from video {word}")
                    return extract_youtube(word)

        if word == "type:local_video":  # fetch local video files
            for part in string.split("\""):
                if "/" in part:
                    log_(f"Extracting info from local video {part}")
                    return extract_local_video(part)

        if word.startswith("http") or word.startswith("www."):
            if "ytb" in word or "youtube" in word:
                log_(f"Extracting info from video {word}")
                return extract_youtube(word)

            if word.endswith(".pdf"):
                log_(f"Extracting pdf from {word}")
                return extract_pdf_url(word)

            # if here then is probably just an html
            # and should be treated as text
            log_(f"Extracting text from webpage {word}")
            return extract_webpage(word)

    if "/" in string:  # might be a link to a file
        for part in string.split("\""):
            if ".mp4" in part or ".mov" in part or ".avi" in part:
                if "/" in part:
                    log_(f"Extracting info from local video {part}")
                    return extract_local_video(part)

            if ".pdf" in part:
                log_(f"Extracting pdf from {part}")
                return extract_pdf_local(part)

            if ".md" in part or ".txt" in part:
                log_(f"Extracting text data from {part}")
                return extract_txt(part)
    log_(f"No metadata were extracted for {string}")
    return {}


def extract_youtube(url):
    "extracts video duration in minutes from youtube link, title etc"
    res = {}
    with youtube_dl.YoutubeDL({"quiet": True}) as ydl:
        try:
            video = ydl.extract_info(url, download=False)
            res = {"type": "video",
                   "length": str(round(video['duration']/60, 1)),
                   "title": video['title'],
                   "url": url}
        except (KeyError, DownloadError, ExtractorError) as e:
            log_(f"ERROR: Video link skipped because : error during information\
                    extraction from {url} : {e}", False)
            res.update({"type": "video not found", "url": url})
    return res


def extract_local_video(link):
    """
    extracts video duration in minutes from local files
    https://stackoverflow.com/questions/3844430/how-to-get-the-duration-of-a-video-in-python
    """
    vid = Path(link)
    if not vid.exists():
        link = link.replace("\\", "")
        vid = Path(link)
    if not vid.exists():
        log_(f"ERROR : Thought this was a local video but file was not found!\
                : {link}", False)
        return {"type": "local video not found",
                "url": link}
    clip = VideoFileClip(link)
    duration = round(clip.duration/60, 1)
    dic = {"type": "local video",
           "title": clip.filename,
           "length": duration,
           "url": link}
    return dic


def extract_pdf_url(url):
    "extracts reading time from an online pdf"
    downloaded = requests.get(url, headers=headers)
    open("./.temporary.pdf", "wb").write(downloaded.content)
    temp_dic = extract_pdf_local("./.temporary.pdf")
    temp_dic["type"] = "online pdf"
    temp_dic["url"] = url
    Path("./.temporary.pdf").unlink()
    return temp_dic


def extract_pdf_local(path):
    "extracts reading time from a local pdf file"
    if not Path(path).exists():
        path = path.replace(" ", "\\ ")
    try:
        with open(path, "rb") as f:
            text_content = pdftotext.PDF(f)
            text_content = " ".join(text_content).replace("\n", " ")
    except FileNotFoundError:
        log_(f"ERROR: Cannot find {path}, I thought it was a PDF", False)
        return {"type": "pdf not found",
                "url": path}

    total_words = len(text_content)/average_word_length
    estimatedReadingTime = str(round(total_words/wpm, 1))

    title = path.split(sep="/")[-1]
    res = {"type": "local pdf",
           "length": estimatedReadingTime,
           "title": title,
           "url": path}
    return res


def extract_txt(path):
    "extracts reading time from a text file"
    try:
        txt_file = Path(path)
        with txt_file.open() as f:
            lines = f.readlines()
        text_content = ' '.join(lines).replace("\n", " ")

        total_words = len(text_content)/average_word_length
        estimatedReadingTime = str(round(total_words/wpm, 1))

        title = path.split(sep="/")[-1]
        res = {"type": "text",
               "length": estimatedReadingTime,
               "url": path,
               "title": title}
        return res

    except ValueError as e:
        log_(f"ERROR: Cannot find {path} : {e}", False)
        res = {"type": "txt file not found",
               "url": path}
        return res


def extract_webpage(url):
    """
    extracts reading time from a webpage, output is a tupple containing
    estimation of the reading time ; title of the page ; if the wayback
    machine was used
    """
    try:
        wayback_used = 0
        res = requests.get(url, headers=headers)
    except requests.exceptions.ConnectionError:
        # if url is dead : use wayback machine
        tqdm.write(f"Using the wayback machine for {url}")
        wayback_used = 1
        wb = get_wayback_machine.get(url)
        try:  # if url was never saved
            url = wb.links['last memento']['url']
        except (requests.exceptions.ConnectionError, AttributeError) as e:
            log_(f"ERROR: url could not be found even using wayback machine :\
{url} : {e}", False)
            res = {"title": "web page not found",
                   "url": url,
                   "length": "-1",
                   "used_wayback_machine": "wayback url no found"}
            return res
        res = requests.get(url, headers=headers)
    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')
    text_content = ' '.join(soup.find_all(text=True)).replace("\n", " ")

    title = "No title"
    for t in soup.find_all('title'):
        title = t.get_text()

    total_words = len(text_content)/average_word_length
    estimatedReadingTime = str(round(total_words/wpm, 1))
    res = {"title": title,
           "type": "webpage",
           "length": estimatedReadingTime,
           "used_wayback_machine": wayback_used,
           "url": url}
    if res['length'] == "-1":
        res.pop("length")
        res.pop("title")
        res["type"] = "webpage not found"
    return res


# functions related to elo scores:
def expected_elo(elo_A, elo_B, Rp=100):
    '''
    Calculate expected score of A in a best of 3 match against B
    Expected score of B in a best of 5 match against A is given by
    1-expected(A,B,Rp). For each Rp rating points of advantage over the
    opponent, the expected score is magnified ten times in comparison to
    the opponent's expected score
    '''
    result = 5 / (1 + 10 ** ((elo_B - elo_A) / Rp))
    log_(f"Expected : A={str(elo_A)} B={str(elo_B)} Rp={str(Rp)}, expected\
score : {str(result)}")
    return int(result)


def update_elo(elo, exp_score, real_score, K):
    "computes the ELO score"
    result = elo + K*(real_score - exp_score)
    log_(f"Update_elo : elo={str(elo)} expected={str(exp_score)}\
            real_score={str(real_score)} K={str(K)} ; result={str(result)}")
    return int(result)


def adjust_K(K0):
    """
    lowers the K factor of the card after at each review
    until lowest value is reached
    """
    K0 = int(K0)
    log_(f"Adjust_K : K0={str(K0)}")
    if K0 == K_values[-1]:
        log_(f"Adjust_K : K already at last specified value :\
                {str(K0)}={str(K_values[-1])}")
        return str(K0)
    for i in range(len(K_values)-1):
        if int(K_values[i]) == int(K0):
            log_(f"New K_value : {str(K_values[i+1])}")
            return K_values[i+1]
    if K0 not in K_values:
        log_(f"ERROR: K not part of K_values : {str(K0)}, reset to\
                {str(K_values[-1])}")
        return str(K_values[-1])
    log_("ERROR: This should never print", False)
    raise SystemExit()


def compute_global_score(iELO, tELO):
    "returns weight adjusted sum of importance score and time score"
    return int(global_weights[0]*int(iELO) + global_weights[1]*int(tELO))


def json_periodic_save():
    """
    If json_auto_save is set to True, this function will save the whole litoy
    database in a new json file at startup. The idea is to avoid data loss
    by corrupting the xlsx file
    """
    if json_auto_save is True and len(litoy.df.index) > 5:
        json_dir = f'{str(Path(".").absolute())}/logs/json_backups/'
        json_name = str(int(time.time())) + ".json"
        Path(json_dir).mkdir(parents=True, exist_ok=True)
        jfile = Path(f"{json_dir}{json_name}")
        if jfile.exists():
            print("json file already exists!")
            raise SystemExit()
        jfile.touch()
        log_(f"automatically saving database as json file {json_name}")
        litoy.df.to_json(jfile, compression="bz2", index=True)


# class
class LiTOYClass:
    "Class that interacts with the database using panda etc"
    def __init__(self, db_path):
        if db_path is None:
            db_path = args['litoy_db']
            self.path = db_path
            self.create_database()
        else:
            self.path = db_path
            self.df = pd.read_excel(db_path).set_index("ID").sort_index()

    def _reload_df(self):
        "used to reload the df from the file"
        self.df = pd.read_excel(self.path).set_index("ID").sort_index()

    def save_to_file(self, df):
        "used to save the dataframe to an excel file"
        Excelwriter = pd.ExcelWriter(f"{args['litoy_db']}.temp.xlsx",
                                     engine="xlsxwriter")
        df.to_excel(Excelwriter, sheet_name="LiTOY", index=True)
        Excelwriter.save()

        # this way, interruption of LiTOY are less likely to corrupt the db
        to_rename = Path(f"{args['litoy_db']}.temp.xlsx")
        to_remove = Path(args['litoy_db'])
        to_remove.unlink()
        to_rename.rename(args['litoy_db'])
        self._reload_df()

    def create_database(self):
        "used to create the excel database"
        df = pd.DataFrame(columns=cols).set_index("ID")
        self.save_to_file(df)

    def entry_duplicate_check(self, df, new):
        "checks if an entry already exists before adding it"
        # strangely, this was faster than using lapply
        for current in list(df['content']):
            current.strip()
            current = current.replace("\n", "")
            if current == new:
                log_(f"Entry already in database : {current}", False)
                return True
        return False

    def get_tags(self, df):
        "gets the list of tags already present in the db"
        tags_list = list(df["tags"])
        tags_list = [json.loads(t) for t in tags_list]
        found_at_least_one = 1
        while found_at_least_one != 0:
            found_at_least_one = 0
            for item in tags_list:
                if isinstance(item, list):
                    found_at_least_one += 1
                    tags_list.extend([*item])
                    tags_list.remove(item)
        tags_list = sorted(list(set(tags_list)))
        return tags_list


# arguments
parser = argparse.ArgumentParser()
parser.add_argument("--import-from-file", "-i",
                    nargs="?",
                    metavar="import_path",
                    dest='import_ff_arg',
                    type=str,
                    required=False,
                    help="path of the text file to import to litoy database")
parser.add_argument("--litoy-db", "-l",
                    nargs="?",
                    metavar="litoy_db",
                    dest='litoy_db',
                    type=str,
                    required=False,
                    help="path to the litoy database")
parser.add_argument("--disable", "-d",
                    nargs=1,
                    metavar="id_to_disable",
                    dest='id_to_disable',
                    type=int,
                    required=False,
                    help="supply an ID of an entry to disable it (useful \
                         when you have finished a task")
parser.add_argument("--add", "-a",
                    action="store_true",
                    dest='entry_to_add',
                    required=False,
                    help="directly add an entry by putting it inside quotation\
                    mark like so : python3 ./__main__.py -a \"do this thing\
                    tags:DIY, I really need to do it that way\"")
parser.add_argument("--verbose", "-v",
                    dest='verbose',
                    required=False,
                    action="store_true",
                    help="debug flag : prints more information during runtime")
parser.add_argument("--external", "-x",
                    dest='external_open',
                    required=False,
                    action="store_true",
                    help="triggers openning of libreoffice on the database")
parser.add_argument("--review", "-r",
                    dest='review_mode',
                    required=False,
                    action="store_true",
                    help="use this to enable review mode instead of\
importation etc")
parser.add_argument("--podium", "-p",
                    dest='podium',
                    required=False,
                    action="store_true",
                    help="use this to show the current podium")
parser.add_argument("--show-stats", "-s",
                    dest='show_stats',
                    required=False,
                    action="store_true",
                    help="use this to show show current database statistics")

###############################################################################
# 3. Main routine


if __name__ == "__main__":
    # init logging :
    # https://stackoverflow.com/questions/24505145/how-to-limit-log-file-size-in-python
    Path("./logs").mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO,
                        filename='logs/rotating_log',
                        filemode='a',
                        format='')
    handler = RotatingFileHandler("logs/rotating_log",
                                  maxBytes=20*1024*1024,
                                  backupCount=20)
    log = logging.getLogger()
    log.handlers.pop()  # otherwise all lines are duplicated
    log.addHandler(handler)

    # init misc :
    (sizex, sizey) = get_terminal_size()
    args = parser.parse_args().__dict__
    signal.signal(signal.SIGINT, debug_signal_handler)
    log_("\n"*10 + "##################### STARTUP")

    # checks if the arguments are sane
    if args['litoy_db'] is None:
        wrong_arguments_(args)
    if not args['litoy_db'].endswith(".xlsx"):
        log_(f"ERROR: Not a valid xlsx filename : {args['litoy_db']}\n\
                Please add '.xlsx' at the end of the filename")
    if args['import_ff_arg'] is None and args['litoy_db'] is None:
        wrong_arguments_(args)
    if args['review_mode'] is True and args['import_ff_arg'] is not None:
        wrong_arguments_(args)

    # initialize litoy class:
    if DB_file_check(args['litoy_db']) is None:
        litoy = LiTOYClass(None)
    else:
        litoy = LiTOYClass(args['litoy_db'])

    # finally the actual code:
    if args['import_ff_arg'] is not None:
        importation(args['import_ff_arg'])
        log_("Done importing from file, exiting", False)
        json_periodic_save()
        raise SystemExit()

    if args["entry_to_add"] is True:
        cur_tags = litoy.get_tags(litoy.df)
        entry_to_add = input(f"Current tags: {cur_tags}\n\
Text content of the entry?\n>")
        log_(f'Adding entry {entry_to_add}')
        if len(entry_to_add.split(sep=" ")) == 1:  # avoids bugs
            print("There is no point in adding single word entries. Quitting")
            raise SystemExit()
        if not litoy.entry_duplicate_check(litoy.df, entry_to_add):
            add_new_entry(litoy.df, entry_to_add)
        else:
            raise SystemExit()
        log_("Done adding entry.", False)
        raise SystemExit()

    if args['review_mode'] is True:
        show_stats(litoy.df, printing=False)
        n = len(litoy.df.index)
        if n < 10:
            log_(f"ERROR: you only have {n} entries in your database, add 10 \
to start using LiTOY!", False)
            raise SystemExit()
        state = "repick"  # this while loop is used to repick if the user wants
        # to use another "left entry" when reviewing
        while state == "repick":
            state = "don't repick"
            picked_ids = pick_entries(litoy.df.copy())
            log_(f"Picked the following entries : {picked_ids}")
            if args["verbose"] is True:
                disp_flds = "all"
            else:
                disp_flds = "no"
            for (progress, i) in enumerate(picked_ids[1:]):
                if state == "repick":
                    break
                for m in ["importance", "time"]:
                    if state == "repick":
                        break
                    (sizex, sizey) = get_terminal_size()  # dynamic sizing
                    print("\n"*10)
                    print_2_entries(int(picked_ids[0]),
                                    int(i),
                                    mode=m,
                                    all_fields=disp_flds)
                    state = ""
                    state = shortcut_and_action(picked_ids[0], i, mode=m,
                                                progress=progress)
                    if state == "repick":
                        break
                    if state == "disable_right":
                        pass
                    if state == "disable_left":
                        log_("Repicking because you suspended left entry.",
                             False)
                        state = "repick"
                        break
            if state == "repick":
                continue  # is finally telling the loop to repick
        log_("Finished reviewing session.\nQuitting.", False)
        json_periodic_save()  # periodic save
        raise SystemExit()

    if args['id_to_disable'] is not None:
        "disables an entry at launch, use this when the task has been\
accomplished"
        idtd = int(args['id_to_disable'][0])
        df = litoy.df.copy()
        if int(df.loc[idtd, "disabled"]) != 0:
            log_(f"Entry with ID {idtd} is already disabled", False)
            raise SystemExit()
        df.loc[int(idtd), "disabled"] = 1
        litoy.save_to_file(df)
        log_(f'Disabled entry {idtd}: {df.loc[idtd, "content"]}', False)
        raise SystemExit()

    if args["external_open"] is True:
            log_("Openning libreoffice", False)
            path = args['litoy_db']
            if platform.system() == "Linux":
                if platform.system() == "Windows":
                    print("Not implemented on windows, contributions are \
welcome!")
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", path])
                else:
                    subprocess.Popen(["xdg-open", path],
                                     stdout=open(os.devnull, 'wb'))
            raise SystemExit()



    if args["podium"] is True:
        log_("Showing podium")
        show_podium(litoy.df)
        raise SystemExit()

    if args["show_stats"] is True:
        log_("Showing statistics :")
        show_stats(litoy.df)
        raise SystemExit()

    log_("ERROR: Insufficient arguments?", False)
    wrong_arguments_(args)
