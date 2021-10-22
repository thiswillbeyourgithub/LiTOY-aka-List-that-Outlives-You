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
import re
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
from contextlib import suppress
import prompt_toolkit
from pygments.lexers import JavascriptLexer


from src.backend.backend import DB_file_check, importation, import_media, move_flags_at_end, add_new_entry, pick_entries, shortcut_and_action, get_tags_from_content, get_meta_from_content
from src.backend.media import extract_youtube, extract_local_video, extract_pdf_url, extract_pdf_local, extract_txt, extract_webpage
from src.backend.scoring import expected_elo, update_elo, adjust_K, compute_global_score
from src.backend.util import log_, debug_signal_handler, prompt_we, wrong_arguments_, format_length, json_periodic_save
from src.cli.cli import side_by_side, format_length, show_podium, show_stats, print_2_entries
from src.cli.get_terminal_size import get_terminal_size
from src.gui.gui import launch_gui

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


class LiTOYClass:
    "Class that interacts with the database using panda etc"
    def __init__(self, db_path):
        if db_path is None:
            db_path = args['db']
            self.path = db_path
            self.create_database()
        else:
            self.path = db_path
            self.df = pd.read_excel(db_path).set_index("ID").sort_index()
        self.log_ = log_
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
    # init misc :
    (sizex, sizey) = get_terminal_size()
    args = parser.parse_args().__dict__
    signal.signal(signal.SIGINT, debug_signal_handler)
    log_("\n\nSTARTUP")

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

    # initialize litoy class:
    if DB_file_check(args['db']) is False:
        litoy = LiTOYClass(None)
    else:
        litoy = LiTOYClass(args['db'])

    if args['import_path'] is not None or args["add_entries"] is not None or args["review_mode"] is True:
        # asynchronous loading
        litoy.import_thread = threading.Thread(target=import_media)
        litoy.import_thread.start()

    if args['verbose'] is True:
        pprint(args)

    # automatic backup at startup
    json_periodic_save(litoy)

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
        launch_gui(args, litoy)
        raise SystemExit()

    if args['import_path'] is not None:
        importation(args['import_path'])
        log_("Done importing from file, exiting", False)
        raise SystemExit()

    if args["add_entries"] is True:
        log_("Adding entries.")
        cur_tags = litoy.get_tags(litoy.df)
        autocomplete_list = ["tags:"+tags for tags in cur_tags] + ["set_length:"]

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
        litoy.import_thread.join()
        while True:
            new_content = prompt_we(input_prompt,
                                  completer=auto_complete,
                                  complete_while_typing=False,
                                  complete_in_thread=True)
            new_content = new_content.replace("tags:tags:", "tags:")
            new_content = move_flags_at_end(new_content)
            
            if new_content in ["n", "no", "q", "quit", ""]:
                log_("Exiting without adding more entries.", False)
                raise SystemExit()
            log_(f'Adding entry {new_content}')
            metacontent = get_meta_from_content(new_content)
            if not litoy.entry_duplicate_check(litoy.df,
                                               new_content,
                                               metacontent):
                newID = add_new_entry(litoy, new_content, metacontent)
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
                    if chosenfield == "content":
                        new_value = move_flags_at_end(new_value)
                        df.loc[entry_id, "metacontent"] = json.dumps(get_meta_from_content(new_value))
                        df.loc[entry_id, "tags"] = json.dumps(sorted(get_tags_from_content(new_value)))
                    df.loc[entry_id, chosenfield] = new_value
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
                picked_ids = pick_entries(litoy.df)
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
                                        litoy=litoy,
                                        mode=m,
                                        all_fields=disp_flds)
                        state = ""
                        state = shortcut_and_action(picked_ids[0],
                                                    i,
                                                    mode=m,
                                                    progress=progress +
                                                    session_nb*n_to_review,
                                                    litoy=litoy,
                                                    shortcut_auto_completer=shortcut_auto_completer,
                                                    available_shortcut=available_shortcut)
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
                rlvt_index += [x for x in df.index if tag.lower() in str(
                    df.loc[x, "tags"]).lower()]
            rlvt_index = sorted(list(set(rlvt_index)))
            df = df.loc[rlvt_index, ["media_title", "content", "gELO"]]
            if len(rlvt_index) != 0:
                pprint(df)
                print(f"Number of corresponding entries: {len(rlvt_index)}")
            else:
                print("No corresponding entries found.\nList of tags currently \
in your db:")
                pprint(litoy.get_tags(litoy.df))
            raise SystemExit()
        else:
            query = query[0][0]

        if query == "stats":
            log_("Showing statistics")
            show_stats(df)
            raise SystemExit()

        if query in ["podium", "global", "global_tasks"]:
            log_("Showing podium")
            show_podium(df, sizex, args)
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
            log_file = "logs/rotating_log"
            with open(log_file) as lf:
                print(lf.read())
            raise SystemExit()

    log_("ERROR: Reached last line of code, insufficient arguments?", False)
    wrong_arguments_(args)
