#!/usr/bin/env python3.9
from user_settings import (disable_lifebar,
                           useless_first_years,
                           useless_last_years,
                           user_age,
                           user_life_expected,
                           json_auto_save,
                           n_session,
                           n_to_review,
                           average_word_length,
                           wpm,
                           default_dir,
                           questions,
                           shortcuts,
                           K_values,
                           default_score,
                           global_weights,
                           headers,
                           col_red,
                           col_blu,
                           col_yel,
                           col_gre,
                           #col_cya,
                           col_mgt_fg,
                           col_blink,
                           col_bold,
                           col_uline,
                           col_rst,
                           spacer)
from other_functions import get_terminal_size

from glob import glob
import argparse
import code
import time
import random
from statistics import mean, stdev, median, StatisticsError
import platform
import requests
import subprocess
import sys
import os
import json
import pandas as pd
from itertools import chain
from pathlib import Path
from pprint import pprint
from tqdm import tqdm
from prettytable import PrettyTable
import threading
import webbrowser

import pdb
import signal
import logging
from logging.handlers import RotatingFileHandler
from contextlib import suppress
import prompt_toolkit
from pygments.lexers import JavascriptLexer

def import_media():
    """
    import some media library, put aside because I want people to be able to 
    install and use litoy even if they can't install those libraries (ex raspi)
    """
    if "get_wayback_machine" not in sys.modules:
        try:
            global get_wayback_machine, pdftotext, requests, youtube_dl, ExtractorError, DownloadError, BeautifulSoup, VideoFileClip
            import get_wayback_machine
            import pdftotext
            import youtube_dl
            from youtube_dl.utils import ExtractorError, DownloadError
            from bs4 import BeautifulSoup
            from moviepy.editor import VideoFileClip
        except Exception as e:
            print(col_red + f"Import failed: {e}\nThis means litoy might \
crash when trying to load media. Use 'pip install -r requirements.txt' to fix this." + col_rst)

###############################################################################
# Summary of each section
#-1. Import statements
# 0. Banner and license
# 1. Fonctions, Classes, etc :
#          def debug_signal_handler(signal, frame):
#          def log_(string, onlyLogging=True):
#          def DB_file_check(path):
#          def importation(path):
#          def wrong_arguments_(args):
#          def add_new_entry(df, content):
#          def pick_entries():
#          def print_memento_mori(): # remember you will die
#          def print_2_entries(id_left, id_right, mode, all_fields="no"):
#              def side_by_side(rowname, a, b, space=2, col=""):
#          def show_podium(df):
#          def show_stats(df, printing=True):
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
#          def compute_global_score(iELO, tELO, status):
#          def json_periodic_save():
#              def __init__(self, db_path):
#              def _reload_df(self):
#              def save_to_file(self, df):
#              def create_database(self):
#              def entry_duplicate_check(self, df, new):
#              def get_tags(self, df):
# 2. Main routine

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
# 1. Functions, classes, etc

def debug_signal_handler(signal, frame):
    """
    Make the whole script interruptible using ctrl+c,
    you can then resume using 'c'
    """
    pdb.set_trace()


def prompt_we(*args, **kargs):
    """
    wrapper for prompt_toolkit.prompt to catch Keyboard interruption cleanly
    """
    style = prompt_toolkit.styles.Style.from_dict({"": "ansibrightyellow"})
    try:
        return prompt_toolkit.prompt(*args, **kargs, style=style)
    except (KeyboardInterrupt, EOFError):
        log_("Exiting.", False)
        raise SystemExit()


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
    if onlyLogging is False or args["verbose"] is True:
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
            return False
    else:
        answer = input(f"No database file found at {path}, do you want me to\
 create it?\ny/n?")
        if answer in ["y", "yes"]:
            db_location.touch()
            return False
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
    import_thread.join()
    for line in tqdm(lines, desc="Processing line by line", unit="line",
                     ascii=False, dynamic_ncols=True, mininterval=0):
        line = line.strip()
        line = line.replace("\n", "")
        metacontent = get_meta_from_content(line)
        if not litoy.entry_duplicate_check(litoy.df, line, metacontent):
            add_new_entry(litoy.df, line, metacontent)


def wrong_arguments_(args):
    "Print user arguments then exit"
    print("Exiting because called with wrong arguments \nYour arguments:")
    pprint(args)
    raise SystemExit()


def add_new_entry(df, content, metacontent, gui_litoy=None, gui_log=None):
    "Add a new entry to the pandas dataframe"
    tags = get_tags_from_content(content)
    if gui_litoy is None:
        global litoy
    else:
        litoy = gui_litoy
    if gui_log is None:
        global log_
    else:
        log_ = gui_log

    # in case metacontent doesn't contain those keys, ignore exceptions:
    with suppress(KeyError, TypeError):
        # if url not working, reload it after 5 seconds :
        if "forbidden" in str(metacontent['title']).lower() or \
                "404" in str(metacontent['title']).lower() or\
                "403" in str(metacontent['title']).lower():
            log_(f"Waiting 5 seconds because apparent webpage loading limit \
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
               "gELO": compute_global_score(),
               "review_time": 0,
               "n_review": 0,
               "K": sorted(K_values)[-1],
               "starred": 0,
               "disabled": 0,
               }
    log_(f"Adding new entry # {newID} : {new_dic}")
    for k, v in new_dic.items():
        df.loc[newID, k] = v
    litoy.save_to_file(df)
    return newID


def pick_entries(gui_litoy=None):
    """
    Pick entries for the reviews : the left one is chosen randomly
    among the 5 with the highest pick_factor, then n_to_review other entries
    are selected at random among the half with the highest pick factor.
    Note: the pick_score goes down fast.
    """
    if gui_litoy is None:
        df = litoy.df.loc[litoy.df.disabled == 0].copy()
    else:
        df = gui_litoy.df.loc[gui_litoy.df.disabled == 0].copy()

    df["pick_score"] = df.loc[:, "DiELO"].values + df.loc[:, "DtELO"]
    df.sort_values(by="pick_score", axis=0, ascending=False, inplace=True)
    left_choice_id = df.iloc[0:10].sample(1).index[0]

    df_h = df.iloc[0: int(len(df.index)/2), :]
    right_choice_id = df_h.sample(min(n_to_review, len(df_h.index))).index

    picked_ids = [int(left_choice_id)]
    picked_ids.extend(right_choice_id)

    cnt = 0
    while picked_ids[0] in picked_ids[1:]:
        cnt += 1
        if cnt > 50:
            log_("Seem to be stuck in an endless loop. Openning debugger", False)
            pdb.set_trace()
        log_("Picking entries one more time to avoid reviewing to itself",
             False)
        picked_ids = pick_entries()
    return picked_ids


def print_memento_mori():
    """
    Print a reminder to the user that life is short and times
    is always passing by faster as time goes on
    """
    if disable_lifebar is False:
        seg1 = useless_first_years
        seg2 = user_age - useless_first_years
        seg3 = user_life_expected - user_age - useless_last_years
        seg4 = useless_last_years
        resize = 1/user_life_expected*(sizex-17)
        if random.random() > 0.99:
            string = "REMEMBER THAT TIME IS RUNNING OUT"
            for i in range(5):
                color_set = [col_red, col_yel]*3
                random.shuffle(color_set)
                col_rdm = (col for col in color_set)
                print(f"{col_mgt_fg}{col_blink}{col_bold}{col_uline}", end="")
                print(f"{next(col_rdm)}{string}", end=spacer*2)
                print(f"{next(col_rdm)}{string}", end=spacer*2)
                print(f"{next(col_rdm)}{string}", end="")
                print(col_rst, end="\n")
        print("Your life (" + col_red + str(int((seg2)/(seg2 + seg3)*100)) +
              "%" + col_rst + ") : " + col_red + "x"*int(seg1*resize) +
              col_red + "X"*(int(seg2*resize)) + col_gre +
              "-"*(int(seg3*resize)) + col_yel + "_"*int(seg4*resize) +
              col_rst)


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

def formats_length(minutes):
    "displays 120 minutes as 2h0m etc"
    if minutes == "":
        return ""
    minutes = float(minutes)
    hours = minutes // 60
    days = hours // 24
    if days == 0:
        days = ""
    else:
        hours = hours-days*24
        days = str(int(days))+"d"
    if hours == 0 :
        hours = ""
    else:
        minutes = minutes-hours*60
        hours = str(int(hours))+"h"
    minutes = str(int(minutes))+"min"
    length = days+hours+minutes
    return length


def print_2_entries(id_left, id_right, mode, all_fields="no"):
    "Show the two entries to review side by side"
    (sizex, sizey) = get_terminal_size()  # dynamic sizing
    print(col_blu + "#"*sizex + col_rst)
    print_memento_mori()
    print(col_blu + "#"*sizex + col_rst)

    entry_left = litoy.df.loc[id_left, :].copy()
    entry_right = litoy.df.loc[id_right, :].copy()

    if all_fields != "all":
        side_by_side("ID", id_left, id_right)
        print("."*sizex)

        if "".join(entry_left.tags + entry_right.tags) != "":
            tag_left = ', '.join(json.loads(entry_left.tags))
            tag_right = ', '.join(json.loads(entry_right.tags))
            side_by_side("Tags", tag_left, tag_right)
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

    # print all fields, useful for debugging
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
    side_by_side("Length", formats_length(js[0]["length"]),
            formats_length(js[1]["length"]))
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
    pd.set_option('display.max_colwidth', int(sizex/2.6))
    if args["verbose"] is True:  # print all fields
        pprint(df.sort_values(by="gELO", ascending=False)[0:10])
    else:
        dfp = df.loc[:, ["content", "gELO", "iELO", "tELO",
                         "tags", "disabled", "metacontent"]
                     ][df["disabled"] == 0]
        dfp["media_title"] = [(lambda x: json.loads(x)["title"]
                               if "title" in json.loads(x).keys()
                               else "")(x)
                              for x in dfp.loc[:, "metacontent"]]
        pprint(dfp.loc[:,
                       ["media_title", "content",
                        "gELO", "iELO", "tELO", "tags"]
                       ].sort_values(by="gELO", ascending=False)[0:10])


def show_stats(df, printing=True):
    """
    shows statistics on the litoy database, but is also used to write at each
    launch the state of the database for later analysis
    """
    df = litoy.df.copy()
    df_nd = df[df['disabled'] == 0]
    df_virg = df[df['n_review'] == 0]
    df_nvirg = df[df['n_review'] != 0]
    try:
        table = PrettyTable()
        table.field_names = ["", "value"]
        table.align[""] = "l"
        table.align["value"] = "r"
        table.add_row(["Number of entries in LiTOY:", len(df)])
        table.add_row(["Number of non disabled entries in LiTOY:", len(df_nd)])
        table.add_row(["Number of entries that have never been reviewed:",
                       len(df_virg)])
        table.add_row(["Total number of review:",
                       round(df_nd.n_review.sum(), 1)])
        table.add_row(["Average number of review:",
                       round(df_nd['n_review'].mean(), 2)])

        table2 = PrettyTable()
        table2.field_names = ["", "average", "sd", "median"]
        table2.align[""] = "l"
        table2.align["average"] = "r"
        table2.align["sd"] = "r"
        table2.align["median"] = "r"
        table2.add_row(["Importance score:",
                       round(df_nd.iELO.mean(), 1),
                       round(df_nd.iELO.std(), 2),
                       round(median(df_nd.iELO), 2)])
        table2.add_row(["Time score:", round(df_nd.tELO.mean(), 1),
                       round(df_nd.tELO.std(), 2),
                       round(median(df_nd.tELO), 2)])
        table2.add_row(["Global score:", round(df_nvirg.gELO.mean(), 1),
                       round(df_nvirg.gELO.std(), 2),
                       round(median(df_nvirg.gELO), 2)])

        pooled = list(df_nd.DiELO + df_nd.DtELO)
        table2.add_row(["Delta scores:", round(mean(pooled), 1),
                       round(stdev(pooled), 2), round(median(pooled), 2)])
        table2.add_row(["K value:", round(df_nd.K.mean(), 1),
                       round(df_nd.K.std(), 2), round(df_nd.K.median())])
        table2.add_row(["Time spent reviewing:",
                        round(df_nd.review_time.sum(), 1),
                        round(df_nd.review_time.std(), 2),
                        round(median(df_nd.review_time), 2)])

        completion_score = round(mean([
                                       mean(pooled),
                                       median(pooled)
                                      ]
                                      ) / len(df_nd.index), 4)
        if printing is True:
            print(table)
            print("")
            print(table2)
            print(f"Progress score: {round(completion_score, 3):>20}")
            print("(lower is better)")
        else:
            table.border = False
            table2.border = False
            log_(str(table))
            log_(str(table2))
            log_(f"Progress score: {round(completion_score, 3):>20}")
    except StatisticsError as e:
        log_(f"Not enough data points! {e}", False)
        raise SystemExit()


def shortcut_and_action(id_left, id_right, mode, progress):
    """
    makes the link between keypresses and actions
    shortcuts are stored at the top of the file
    """
    entry_left = litoy.df.loc[id_left, :]
    entry_right = litoy.df.loc[id_right, :]
    log_(f"Waiting for shortcut for {id_left} vs {id_right} for {mode}")

    def fetch_action(user_input):
        "deduce action from user keypress"
        found = ""
        for action, keypress in shortcuts.items():
            if str(user_input) in keypress:
                if found != "":
                    log_("ERROR: Several corresponding shortcuts found! \
Quitting.", False)
                    raise SystemExit()
                found = action
        if action == "":
            log_(f"ERROR: No {str(user_input)} shortcut found", False)
            action = "show_help"
        return found

    def star(entry_id):
        "stars an entry_id during review"
        df = litoy.df.copy()
        df.loc[entry_id, "starred"] = 1
        litoy.save_to_file(df)
        log_(f"Starred entry_id {entry_id}", False)

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
        df = litoy.df.copy()
        field_list = list(df.columns)
        field_auto_completer = prompt_toolkit.completion.WordCompleter(field_list, sentence=True)
        while True:
            entry = df.loc[entry_id, :]
            print(f"Fields available for edition : {field_list}")
            chosenfield = prompt_we("What field do you want to edit? \
(q to exit)\n>", completer = field_auto_completer)
            if chosenfield == "q" or chosenfield == "quit":
                break
            if chosenfield == "metacontent" or chosenfield == "tags":
                additional_args = {"lexer": prompt_toolkit.lexers.PygmentsLexer(JavascriptLexer)}
            else:
                additional_args = {}
            try:
                old_value = str(entry[chosenfield])
            except KeyError:
                log_("ERROR: Shortcut : edit : wrong field name", False)
                continue
            new_value = str(prompt_we("Enter the desired new value \
for  field '" + chosenfield +"'\n>",
                                       default=old_value,
                                       **additional_args))
            df.loc[entry_id, chosenfield] = new_value
            if chosenfield == "content":
                df.loc[entry_id, "metacontent"] = json.dumps(get_meta_from_content(new_value))
                df.loc[entry_id, "tags"] = json.dumps(sorted(get_tags_from_content(new_value)))
            litoy.save_to_file(df)
            log_(f'Edited field "{chosenfield}":\n* {old_value}\nbecame:\n* {new_value}',
                 False)
            break

    action = ""
    while True:
        start_time = time.time()
        action = ""
        log_(f"Asking question, mode : {mode}")
        prompt_text = f"{progress}/{n_to_review*n_session} {questions[mode]} \
(h or ? for help)\n>"

        keypress = prompt_we(prompt_text, completer = shortcut_auto_completer)

        if keypress not in available_shortcut:
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
            keypress = round(int(keypress)/6*5, 2)  # resize value from 1-5 to 0-5
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
                                         round(5-keypress, 2), eL_old.K)
            eR_new[elo_fld] = update_elo(eloR, expected_elo(eloL, eloR),
                                         keypress, eR_old.K)
            log_(f"Elo: L: {eloL}=>{eL_new[elo_fld]} R: \
{eloR}=>{eR_new[elo_fld]}")

            eL_new["K"] = adjust_K(eL_old.K)
            eR_new["K"] = adjust_K(eR_old.K)
            eL_new[Delo_fld] = abs(eL_new[elo_fld] - eL_old[elo_fld])
            eR_new[Delo_fld] = abs(eR_new[elo_fld] - eR_old[elo_fld])
            eL_new["gELO"] = compute_global_score(eL_new.iELO, eL_new.tELO, 1)
            eR_new["gELO"] = compute_global_score(eR_new.iELO, eR_new.tELO, 1)
            eL_new["review_time"] = round(eL_new["review_time"] + min(date
                                          - start_time, 30), 3)
            eR_new["review_time"] = round(eR_new["review_time"] + min(date
                                          - start_time, 30), 3)
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

        if action == "show_few_fields":
            log_("Displaying only most important fields of entries")
            print("\n"*10)
            print_2_entries(int(id_left), int(id_right), mode)
            continue

        if action == "open_media":
            log_("Openning media")
            for ent_id in [id_left, id_right]:
                ent = litoy.df.loc[ent_id, :]
                try:
                    path = str(json.loads(ent.metacontent)["url"])
                    if "http" in path:
                        webbrowser.open(path)
                    else:
                        if platform.system() == "Linux":
                            subprocess.Popen(["xdg-open", path],
                                             stdout=open(os.devnull, 'wb'))
                        elif platform.system() == "Windows":
                            os.startfile(path)
                        elif platform.system() == "Darwin":
                            subprocess.Popen(["open", path])
                        else:
                            log_("Platform system not found.", False)
                except (KeyError, AttributeError) as e:
                    log_(f"url not found in entry {ent_id} : {e}")
            time.sleep(1.5)  # better display
            print("\n"*10)
            print_2_entries(int(id_left),
                            int(id_right),
                            mode=mode)
            continue

        if action == "reload_media" or action == "reload_media_fallback_text_extractor":
            log_("Reloading media")
            import_thread.join()
            additional_args = {}
            if action == "reload_media_fallback_text_extractor":
                additional_args.update({"fallback_text_extractor": True})
            for ent_id in [id_left, id_right]:
                df = litoy.df.copy()
                old_cont = df.loc[ent_id, :]["content"]
                new_meta = get_meta_from_content(old_cont, additional_args)
                df.loc[ent_id, "metacontent"] = json.dumps(new_meta)
                entry_left = df.loc[id_left, :]
                entry_right = df.loc[id_right, :]
                litoy.save_to_file(df)
                log_(f"New metacontent value for {ent_id} : {new_meta}")
            print("\n"*10)
            print_2_entries(int(id_left),
                            int(id_right),
                            mode=mode)
            continue

        if action == "open debugger":
            log_("Openning debugger", False)
            print("To open a python console within the debugger, type in \
'interact'. You can load the database as a pandas DataFrame using df=litoy.df")
            pdb.set_trace()
            continue

        if action == "edit_left":
            edit(id_left)
            print_2_entries(id_left, id_right, mode)
            continue
        if action == "edit_right":
            edit(id_right)
            print_2_entries(id_left, id_right, mode)
            continue
        if action == "star_left":
            star(id_left)
            continue
        if action == "star_right":
            star(id_right)
            continue
        if action == "disable_left":
            disable(id_left)
            return action
        if action == "disable_both":
            disable(id_right)
            disable(id_left)
            return action
        if action == "disable_right":
            disable(id_right)
            return action

        if action == "undo":
            print("Undo function is not yet implemented, \
  manually correct the database using libreoffice calc after looking at \
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
            while not temp.replace("_", "").replace("-","").isalnum():
                temp = temp[:-1]
            result.append(temp)
    return list(set(result))


def get_meta_from_content(string, additional_args=None, gui_log=None):
    """
    extracts all metadata from a line in the import file
    this does not include tags, which are indicated using tags:sometag in the
    line. Instead it's for example the length of a youtube video which link
    appears in the content.
    If several links are supplied, only the first one will be used
    """
    if additional_args is None:
        additional_args = {}
    if gui_log is None:
        global log_
    else:
        log_ = gui_log
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
            return extract_webpage(word, **additional_args)

    if "/" in string:  # might be a link to a file
        for part in string.split("\""):
            if ".mp4" in part or\
                    ".mov" in part or\
                    ".avi" in part or\
                    ".webm" in part:
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
        except (KeyError, DownloadError, ExtractorError) as e:
            log_(f"ERROR: Video link skipped because : error during information \
extraction from {url} : {e}", False)
            res.update({"type": "video not found", "url": url})
            return res

        title = video['title'].strip()
        res = {"type": "video",
               "title": title.replace("\n", ""),
               "url": url}
        if "uploader" in video.keys():
            res.update({"channel": video["uploader"]})
            print(video["uploader"])
        try:
            length = str(round(video['duration']/60, 1))
            res.update({"length": length})
        except Exception as e:
            log_("Youtube link looks like it's a playlist, using fallbackmethod:", False)
            length = 0
            for ent in video["entries"]:
                length += ent["duration"]
            length = str(round(length/60, 1))
            res.update({"length": length})
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
        log_(f"ERROR : Thought this was a local video but file was not found! \
: {link}", False)
        return {"type": "local video not found",
                "url": link}
    clip = VideoFileClip(link)
    duration = round(clip.duration/60, 1)
    title = clip.filename.strip()
    dic = {"type": "local video",
           "title": title.replace("\n", ""),
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

    title = path.split(sep="/")[-1].strip()
    res = {"type": "local pdf",
           "length": estimatedReadingTime,
           "title": title.replace("\n", ""),
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

        title = path.split(sep="/")[-1].strip()
        res = {"type": "text",
               "length": estimatedReadingTime,
               "url": path,
               "title": title.replace("\n", "")}
        return res

    except ValueError as e:
        log_(f"ERROR: Cannot find {path} : {e}", False)
        res = {"type": "txt file not found",
               "url": path}
        return res


def extract_webpage(url, fallback_text_extractor=False):
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
            log_(f"ERROR: url could not be found even using wayback machine : \
{url} : {e}", False)
            res = {"title": "web page not found",
                   "url": url,
                   "length": "-1",
                   "used_wayback_machine": "wayback url not found"}
            return res
        res = requests.get(url, headers=headers)
    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')

    # the smallest text find is usually the best
    if fallback_text_extractor is False:
        text_content = " ".join(
                        " ".join(
                            [x.text.replace("\n", " ")
                             for x in soup.find_all('p')]
                            ).split())
    else:
        log_("Using fallback text extractor")
        parsed_text_trial = []
        parsed_text_trial.append(' '.join([x.text.replace("\n", " ")
                                           for x in soup.find_all("div")]))
        parsed_text_trial.append(soup.get_text().replace("\n", " "))
        parsed_text_trial.append(" ".join([x.text.replace("\n", " ")
                                           for x in soup.find_all('p')]))
        parsed_text_trial = [" ".join(x.split()) for x in parsed_text_trial]
        parsed_text_trial.sort(key=lambda x: len(x))
        text_content = parsed_text_trial[0]

    titles = soup.find_all('title')
    if len(titles) != 0:
        title = soup.find_all('title')[0].get_text()
    else:
        title = "No title found"

    total_words = len(text_content)/average_word_length
    estimatedReadingTime = str(round(total_words/wpm, 1))
    title = title.replace("\n", "").replace("\\n", "").strip()
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
    Calculate expected score of A in a best of 5 match against B
    Expected score of B in a best of 5 match against A is given by
    1-expected(A,B,Rp). For each Rp rating points of advantage over the
    opponent, the expected score is magnified ten times in comparison to
    the opponent's expected score
    '''
    result = 5 / (1 + 10 ** ((elo_B - elo_A) / Rp))
    log_(f"Expected_elo: A={str(elo_A)} B={str(elo_B)} Rp={str(Rp)}, expected \
score : {str(result)}")
    return round(result, 2)


def update_elo(elo, exp_score, real_score, K):
    "computes the ELO score"
    result = round(elo + K*(real_score - exp_score), 2)
    log_(f"Update_elo: current elo={str(elo)} ; expected score={str(exp_score)} \
; real score={str(real_score)} ; K={str(K)} ; resulting score={str(result)}")
    return int(result)


def adjust_K(K0):
    """
    lowers the K factor of the card after at each review
    until lowest value is reached
    """
    K0 = int(K0)
    if K0 == K_values[-1]:
        log_(f"Adjust_K : K already at last specified value : \
{str(K0)}={str(K_values[-1])}")
        return str(K0)
    for i in range(len(K_values)-1):
        if int(K_values[i]) == int(K0):
            log_(f"Adjust K: {K0} => {K_values[i+1]}")
            return K_values[i+1]
    if K0 not in K_values:
        log_(f"ERROR: K not part of K_values : {str(K0)}, reset to \
{str(K_values[-1])}")
        return str(K_values[-1])
    log_("ERROR: This should never print", False)
    raise SystemExit()


def compute_global_score(iELO=default_score, tELO=default_score, status=0):
    """
    returns weight adjusted sum of importance score and time score
    status is used to know if the card has never been reviewed, in which 
    case gELO is set to -1
    """
    status = int(status)
    if status != 0:
        gELO = float(global_weights[0])*int(iELO) + float(global_weights[1])*int(tELO)
    else:
        gELO = -1
    return int(gELO)


def json_periodic_save():
    """
    If json_auto_save is set to True, this function will save the whole litoy
    database in a new json file at startup. The idea is to avoid data loss
    by corrupting the xlsx file
    """
    if json_auto_save is True and len(litoy.df.index) > 5:
        json_dir = f'{str(Path(".").absolute())}/logs/json_backups/'
        json_name = "json_backup_" + str(int(time.time())) + ".json"
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
    def __init__(self, db_path, log_, handler):
        if db_path is None:
            db_path = args['db']
            self.path = db_path
            self.create_database()
        else:
            self.path = db_path
            self.df = pd.read_excel(db_path).set_index("ID").sort_index()
        self.log_ = log_
        self.handler = handler
        self.gui_log = lambda x, y=False: self.log_(f"GUI: {x}", y)

    def _reload_df(self):
        "used to reload the df from the file"
        self.df = pd.read_excel(self.path).set_index("ID").sort_index()

    def save_to_file(self, df):
        "used to save the dataframe to an excel file"
        Excelwriter = pd.ExcelWriter(f"{args['db']}.temp.xlsx",
                                     engine="xlsxwriter")
        df.to_excel(Excelwriter, sheet_name="LiTOY", index=True)
        Excelwriter.save()

        # this way, interruption of LiTOY are less likely to corrupt the db
        to_rename = Path(f"{args['db']}.temp.xlsx")
        to_remove = Path(args['db'])
        to_remove.unlink()
        to_rename.rename(args['db'])
        self._reload_df()

    def create_database(self):
        "used to create the excel database"
        cols = ["ID", "date", "content", "metacontent", "tags",
                "starred", "iELO", "tELO", "DiELO", "DtELO", "gELO",
                "review_time", "n_review", "K", "disabled"]
        df = pd.DataFrame(columns=cols).set_index("ID")
        self.save_to_file(df)

    def entry_duplicate_check(self, df, newc, newm):
        "checks if an entry already exists before adding it"
        # strangely, this was faster than using lapply
        for i in list(df.index):
            content = str(df.loc[i, "content"]).strip()
            content = content.replace("\n", "")
            metacontent = json.loads(df.loc[i, "metacontent"])
            if newc == content:
                log_(f"Content is the same as entry with ID {i}: '\
{content}'", False)
                return True
            if newm == metacontent and newm != {}:
                log_(f"Metacontent is the same as entry with ID {i}: new\
content was '{newc}'", False)
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
parser.add_argument("--db",
                    nargs=1,
                    metavar="PATH",
                    dest='db',
                    type=str,
                    required=False,
                    help="path to the litoy database")
parser.add_argument("--graphical", "-g",
                    dest='gui',
                    action="store_true",
                    required=False,
                    help="enable GUI")
parser.add_argument("--gui-darkmode",
                    dest='darkmode',
                    action="store_true",
                    default=False,
                    help="toggle GUI darkmode")
parser.add_argument("--import_from_file", "-i",
                    nargs="?",
                    metavar="PATH",
                    dest='import_path',
                    type=str,
                    required=False,
                    help="path of a text file containing entries to import")
parser.add_argument("--add_entries", "-a",
                    action="store_true",
                    dest='add_entries',
                    required=False,
                    help="open prompt to add entries to litoy. Local filepaths \
have to be between quotation \" marks. Autocompletion for filepaths can \
be configured in the settings.")
parser.add_argument("--remove_entries", "-R",
                    action="extend",
                    nargs='+',
                    metavar="ID",
                    dest='remove_entries',
                    required=False,
                    help="removes entries according to their ID. \
'last' can be used as placeholder for the last added entry")
parser.add_argument("--edit_entries", "-e",
                    action="extend",
                    nargs='+',
                    dest='edit_entries',
                    metavar="ID",
                    required=False,
                    help="edit entries according to their ID. \
'last' can be used as placeholder for the last added entry")
parser.add_argument("--review", "-r",
                    dest='review_mode',
                    required=False,
                    action="store_true",
                    help="began review session")
parser.add_argument("--show", "-s",
                    dest='show',
                    required=False,
                    metavar="QUERY",
                    action="append",
                    nargs='+',
                    help="query can be 'podium', 'quick_tasks', \
'important_tasks', 'global_tasks', 'stats', 'by_tags todo work', \
'starred_tasks', 'disabled_tasks', 'logs'. Those cannot be combined yet.")
parser.add_argument("--search_content", "-S",
                    nargs=1,
                    metavar="STRING",
                    dest='search_query',
                    type=str,
                    required=False,
                    help="show entries that match the content")
parser.add_argument("--external", "-x",
                    dest='external_open',
                    required=False,
                    action="store_true",
                    help="ask default external app to open the database. As \
the extension is .xlsx, libreoffice is usually preferred")
parser.add_argument("--python", "-P",
                    dest='python',
                    required=False,
                    action="store_true",
                    help="launches a python console, useful to access \
the pandas dataframe")
parser.add_argument("--verbose", "-v",
                    dest='verbose',
                    required=False,
                    action="store_true",
                    help="prints debug logs during runtime")

###############################################################################
# 2. Main routine


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
    log.info("\n\n")
    log_("STARTUP")

    # checks if the arguments are sane
    if args['db'] is None:
        wrong_arguments_(args)
    args['db'] = args['db'][0]
    if not args['db'].endswith(".xlsx"):
        log_(f"ERROR: Not a valid xlsx filename : {args['db']}\n\
                Please add '.xlsx' at the end of the filename")
        wrong_arguments_(args)

    if (args['import_path'] is None and args['db'] is None) or (args['review_mode'] is True and args['import_path'] is not None):
        wrong_arguments_(args)

    if args['import_path'] is not None or args["add_entries"] is not None or args["review_mode"] is True:
        # asynchronous loading
        import_thread = threading.Thread(target=import_media)
        import_thread.start()

    if args['verbose'] is True:
        pprint(args)

    # initialize litoy class:
    if DB_file_check(args['db']) is False:
        litoy = LiTOYClass(None, log_, handler)
    else:
        litoy = LiTOYClass(args['db'], log_, handler)

    # automatic backup at startup
    json_periodic_save()

    # finally the actual code:


    # gELO is now set to -1 if the entry has never been reviewed
    # I coded it that way to avoir breaking changes
    try: 
        df = litoy.df
        if -1 not in list(df.loc[:, "gELO"]):
            log_("Recomputing global scores according to the new format \
(-1 is now assigned to new entries, this message should appear only once for \
a given database):", False)
            print(df["gELO"])
            df["gELO"] = [compute_global_score(
                            *list(df.loc[x, ["iELO", "tELO", "n_review"]])
                            ) for x in df.index]
            print(df["gELO"])
            litoy.save_to_file(df)
    except Exception as e:
        print(f"Error recomputing global scores: {e}")

    # launches python console
    if args["python"] is not False:
        log_("Openning console")
        df = litoy.df
        banner = "LiTOY database has been loaded to variable 'df'.\n\
Type q() to quit.\n\
To save dataframe to the database use litoy.save_to_file(df)\n\
Press enter twice between lines to solve buggy display."
        pp = pprint
        q = exit
        try:
            code.interact(banner=banner,
                          local=locals())
        except RuntimeError as e:
            print(f"Exiting: {e}")
        raise SystemExit()

    if args["gui"] is True:
        log_("Launching GUI")
        from gui import launch_gui
        launch_gui(args, litoy)
        raise SystemExit()

    if args['import_path'] is not None:
        importation(args['import_path'])
        log_("Done importing from file, exiting", False)
        raise SystemExit()

    if args["add_entries"] is True:
        log_("Adding entries.")
        cur_tags = litoy.get_tags(litoy.df)
        autocomplete_list = ["tags:"+tags for tags in cur_tags]

        if default_dir is not None:
            def load_autocomplete_list():
                "asynchronous loading of paths for autocompletion"
                file_list = []
                for ext in ["pdf", "md", "mp4", "mov", "avi", "webm"]:
                    file_list.extend(glob(f"/{default_dir}/**/*.{ext}", recursive=True))
                for i in range(len(file_list)):  # local paths have to be between "
                    file_list[i] = "\"" + file_list[i].replace("//", "/") + "\""
                autocomplete_list.extend(file_list)
            autocomplete_thread = threading.Thread(target=load_autocomplete_list)
            autocomplete_thread.start()

        auto_complete = prompt_toolkit.completion.WordCompleter(autocomplete_list,
                                      match_middle=True,
                                      ignore_case=True,
                                      sentence=False) # I would prefer 
# setting sentence to True but it seems to only autocomplete once

        input_prompt = f"Current tags: {cur_tags}\n\
Put local links between \"\" quotation signs!\n\
Use <TAB> to autocomplete paths or tags\n\
Text content of the entry?\n>"
        second_prompt = "\nEnter content of the next entry:  (n/no/q/'' to exit, <TAB> to autocomplete)\n>"
        import_thread.join()
        while True:
            new_entry_content = prompt_we(input_prompt,
                                  completer=auto_complete,
                                  complete_while_typing=False,
                                  complete_in_thread=True)
            new_entry_content = new_entry_content.replace("tags:tags:", "tags:")
            new_entry_content = new_entry_content.strip()
            if new_entry_content in ["n", "no", "q", "quit", ""]:
                log_("Exiting without adding more entries.", False)
                raise SystemExit()
            log_(f'Adding entry {new_entry_content}')
            metacontent = get_meta_from_content(new_entry_content)
            if not litoy.entry_duplicate_check(litoy.df,
                                               new_entry_content,
                                               metacontent):
                newID = add_new_entry(litoy.df, new_entry_content, metacontent)
                print(f"New entry has ID {newID}")
                input_prompt = second_prompt
                pass
            else:
                print("Database already contains this entry, not added.")
                input_prompt = second_prompt
                continue

    if args['search_query'] is not None:
        log_("Searching entries")
        query = args['search_query'][0]
        df = litoy.df
        query = query.lower()
        match = [x for x in df.index if query in str(df.loc[x, "content"]).lower()
                or query in str(df.loc[x, "metacontent"]).lower()]
        if len(match) == 0:
            log_("No matching entries found.", False)
            raise SystemExit()
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        if args["verbose"] is False:
            print(df.loc[match, "content"])
        else:
            print(df.loc[match, :])
        raise SystemExit()

    if args['remove_entries'] is not None:
        log_("Removing entries.")
        df = litoy.df.copy()
        id_list = args['remove_entries']
        if "last" in id_list:
            n_max = max(litoy.df.index)
            id_list.remove("last")
            id_list.append(n_max)
        for entry_id in id_list:
            try:
                entry_id = int(entry_id)
            except Exception as e:
                print(f"ID {entry_id}: {e}")
                wrong_arguments_(args)

            try:
                entry = df.loc[entry_id, :]
            except KeyError as e:
                print(f"Couldn't find entry with ID: {e}")
                continue
            log_("Entry to remove:", False)
            log_(str(entry), False)
            ans = prompt_we("Do you confirm that you want to remove this entry? (y/n)\n>")
            if ans in ["y", "yes"]:
                df = df.drop(entry_id)
                litoy.save_to_file(df)
                log_(f"Entry with ID {entry_id} was removed.", False)
            else:
                log_(f"Entry with ID {entry_id} was NOT removed.", False)
        raise SystemExit()

    if args['edit_entries'] is not None:
        log_("Editing entries.")
        df = litoy.df.copy()
        field_list = list(df.columns)
        field_auto_completer = prompt_toolkit.completion.WordCompleter(field_list, sentence=True)
        id_list = args['edit_entries']
        if "last" in id_list:
            n_max = max(df.index)
            id_list.remove("last")
            id_list.append(n_max)
        for entry_id in id_list:
            try:
                entry_id = int(entry_id)
                entry = df.loc[entry_id, :]
            except KeyError as e:
                print(f"Couldn't find entry with ID: {e}")
                continue
            except ValueError as e:
                print(f"ID {entry_id}: {e}")
                wrong_arguments_(args)

            log_("Entry to edit:", False)
            log_(str(entry), False)
            ans = prompt_we("Do you confirm that you want to edit this entry? (y/n)\n>")
            if ans in ["y", "yes", ""]:
                log_(f"Editing entry {entry_id}")
                while True:
                    print(f"Fields available for edition : {field_list}")
                    chosenfield = prompt_we("What field do you want to edit? \
(q to exit)\n>", completer = field_auto_completer)
                    if chosenfield == "q" or chosenfield == "quit":
                        break
                    if chosenfield == "metacontent" or chosenfield == "tags":
                        additional_args = {"lexer": prompt_toolkit.lexers.PygmentsLexer(JavascriptLexer)}
                    else:
                        additional_args = {}
                    try:
                        old_value = str(entry[chosenfield])
                    except KeyError:
                        log_("ERROR: Shortcut : edit : wrong field name", False)
                        continue
                    new_value = str(prompt_we("Enter the desired new value \
for field '" + chosenfield +"'\n>",
                                               default=old_value,
                                               **additional_args))
                    df.loc[entry_id, chosenfield] = new_value
                    if chosenfield == "content":
                        df.loc[entry_id, "metacontent"] = json.dumps(get_meta_from_content(new_value))
                        df.loc[entry_id, "tags"] = json.dumps(sorted(get_tags_from_content(new_value)))
                    litoy.save_to_file(df)
                    log_(f'Edited entry with ID {entry_id}, field "{chosenfield}", {old_value} => {new_value}',
                         False)
                    break
            else:
                log_(f"Entry with ID {entry_id} was NOT edited.", False)
        raise SystemExit()

    if args['review_mode'] is True:
        log_("Entering review mode.")
        show_stats(litoy.df, printing=False)
        n = len(litoy.df.index)
        if n < 10:
            log_(f"ERROR: you only have {n} entries in your database, add 10 \
to start using LiTOY!", False)
            raise SystemExit()
        available_shortcut = list(chain.from_iterable(shortcuts.values()))
        shortcut_auto_completer = prompt_toolkit.completion.WordCompleter(available_shortcut,
                                                sentence=False,
                                                match_middle=True,
                                                ignore_case=True)
        for session_nb in range(n_session):
            state = "repick"  # this while loop is used to repick if the
            # user wants to use another "left entry" when reviewing
            while state == "repick":
                state = "don't repick"
                picked_ids = pick_entries()
                log_(f"Picked the following entries : {picked_ids}")
                disp_flds = "no"
                for (progress, i) in enumerate(picked_ids[1:]):
                    progress += 1
                    if state == "repick":
                        break
                    for m in ["importance", "time"]:
                        if state == "repick":
                            break
                        print("\n"*10)
                        print_2_entries(int(picked_ids[0]),
                                        int(i),
                                        mode=m,
                                        all_fields=disp_flds)
                        state = ""
                        state = shortcut_and_action(picked_ids[0],
                                                    i,
                                                    mode=m,
                                                    progress=progress +
                                                    session_nb*n_to_review)
                        if state == "repick":
                            break
                        if state == "disable_right":
                            break
                        if state == "disable_left":
                            log_("Repicking because you suspended left entry.",
                                 False)
                            state = "repick"
                            break
                if state == "repick":
                    continue  # is finally telling the loop to repick
        log_("Finished all reviewing session. Quitting.", False)
        raise SystemExit()

    if args["external_open"] is True:
        log_("Openning external app", False)
        path = args['db']
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

    if args["show"] is not None:
        query = args["show"]

        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', sizex)
        pd.set_option('display.max_colwidth', int(sizex/2.6))
        df = litoy.df
        if len(df.index) == 0:
            log_("Empty db, add more entries before calling 'show'", False)
            raise SystemExit()
        df["media_title"] = [(lambda x: json.loads(x)["title"]
                               if "title" in json.loads(x).keys()
                               else "")(x)
                              for x in df.loc[:, "metacontent"]]
        if len(query[0]) != 1 and query[0][0] == "by_tags":
            log_(f"Showing tags {query}")
            tag_list = query[0][1:]
            rlvt_index = []
            for tag in tag_list:
                rlvt_index += [x for x in df.index if tag in df.loc[x, "tags"]]
            rlvt_index = sorted(list(set(rlvt_index)))
            df = df.loc[rlvt_index, ["media_title", "content", "gELO"]]
            pprint(df)
            print(f"Number of corresponding entries: {len(rlvt_index)}")
            raise SystemExit()
        else:
            query = query[0][0]

        if query == "stats":
            log_("Showing statistics")
            show_stats(df)
            raise SystemExit()

        if query in ["podium", "global", "global_tasks"]:
            log_("Showing podium")
            show_podium(df)
            raise SystemExit()

        if query in ["quick", "quick_tasks"]:
            log_("Showing quick entries", False)
            if args["verbose"] is True:  # print all fields
                pprint(df.sort_values(by="tELO", ascending=False)[0:10])
            else:
                df = df.loc[df["disabled"] == 0]
                pprint(df.loc[:,
                               ["media_title", "content",
                                "tELO", "tags"]
                               ].sort_values(by="tELO", ascending=False)[0:10])
            raise SystemExit()

        if query in ["important", "important_tasks"]:
            log_("Showing important entries", False)
            if args["verbose"] is True:  # print all fields
                pprint(df.sort_values(by="iELO", ascending=False)[0:10])
            else:
                df = df.loc[df["disabled"] == 0]
                pprint(df.loc[:,
                               ["media_title", "content",
                                "iELO", "tags"]
                               ].sort_values(by="iELO", ascending=False)[0:10])
            raise SystemExit()

        if query in ["starred", "starred_tasks"]:
            log_("Showing starred entries", False)
            df = df.loc[df.starred == 1].sort_values(by="gELO", ascending=False)[0:10]
            if len(df.index) == 0:
                log_("No starred entries.", False)
                raise SystemExit()

            if args["verbose"] is True:  # print all fields
                pprint(df)
            else:
                pprint(df.loc[:,
                               ["media_title", "content",
                                "gELO", "tags"]
                               ].sort_values(by="gELO", ascending=False)[0:10])
            raise SystemExit()

        if query in ["disabled", "disabled_tasks"]:
            log_("Showing disabled entries", False)
            df = df.loc[df.disabled == 1].sort_values(by="gELO", ascending=False)[0:10]
            if len(df.index) == 0:
                log_("No disabled entries.", False)
                raise SystemExit()

            if args["verbose"] is True:  # print all fields
                pprint(df)
            else:
                pprint(df.loc[:,
                               ["media_title", "content",
                                "gELO", "tags"]
                               ].sort_values(by="gELO", ascending=False)[0:10])
            raise SystemExit()

        if query == "logs":
            log_("Showing logs")
            log_file = str(handler).split(" ")[1]
            with open(log_file) as lf:
                print(lf.read())
            raise SystemExit()

    log_("ERROR: Reached last line of code, insufficient arguments?", False)
    wrong_arguments_(args)
