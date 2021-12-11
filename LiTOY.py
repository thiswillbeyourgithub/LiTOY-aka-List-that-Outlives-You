#!/usr/bin/env python3.9
from glob import glob
import argparse
import signal

import code
import threading

from pathlib import Path
import json
import pandas as pd
from pprint import pprint
import prompt_toolkit

from user_settings import (default_dir)
from src.backend.backend import (importation,
                                 move_flags_at_end, add_new_entry,
                                 get_meta_from_content)
from src.backend.scoring import compute_global_score
from src.backend.util import (log_, debug_signal_handler, prompt_we,
                              wrong_arguments_, json_periodic_save)
from src.cli.cli import (print_podium, print_stats,
                         print_specific_entries, action_edit_entry,
                         review_mode_cli)

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
        self.path = db_path
        if not Path(self.path).exists():
            answer = input(f"No database found at {self.path}, do you want me to\
 create it? (y/n)\n>")
            if answer in ["y", "yes"]:
                self.create_database()
            else:
                log_("Exiting.", False)
                raise SystemExit()
        else:
            log_(f"Database found at {self.path}")
            self.df = pd.read_json(self.path).sort_index()
        self.log_ = log_
        self.gui_log = lambda x, y=False: self.log_(f"GUI: {x}", y)

    def save_to_file(self, df):
        "used to save the dataframe to a json file"
        df.to_json(f"{args['db']}.temp.json")
        Path(args['db']).unlink()
        Path(f"{args['db']}.temp.json").rename(args['db'])
        self.df = df

    def create_database(self):
        "used to create the json database"
        cols = ["ID", "date", "content", "metacontent", "tags",
                "starred", "iELO", "tELO", "DiELO", "DtELO", "gELO",
                "review_time", "n_review", "K", "disabled"]
        df = pd.DataFrame(columns=cols).set_index("ID")
        if Path(args['db']).exists():
            log_(f"ERROR: cannot create database : \
it already exist: {args['db']}", False)
            raise SystemExit()
        else:
            Path(args['db']).touch()
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
            if newm == metacontent and "url" in metacontent:
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
                    action="extend",
                    nargs="*",
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
parser.add_argument("--convert_to_excel", 
                    dest='convert_to_excel',
                    required=False,
                    action="store_true",
                    help="convert json database to excel spreadsheet")
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
    if not args['db'].endswith(".json"):
        log_(f"ERROR: Not a valid json filename : {args['db']}\n\
                Please add '.json' at the end of the filename")
        wrong_arguments_(args)

    if (args['import_path'] is None and args['db'] is None) or (args['review_mode'] is True and args['import_path'] is not None):
        wrong_arguments_(args)

    # initialize litoy class:
    litoy = LiTOYClass(args['db'])

    if args['verbose'] is True:
        pprint(args)

    # automatic backup at startup
    json_periodic_save(litoy)

    # finally the actual code:


    # gELO is now set to -1 if the entry has never been reviewed
    # I coded it that way to avoir breaking changes
    try: 
        df = litoy.df
        if len(df.index) > 0 and -1 not in list(df.loc[:, "gELO"]):
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
        importation(args['import_path'], litoy)
        log_("Done importing from file, exiting", False)
        raise SystemExit()

    if args["add_entries"] is not None:
        log_("Adding entries.")
        if args["add_entries"] not in [[], [None]]:
            default_prompt = args["add_entries"][0]
        else:
            default_prompt = ""
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
        while True:
            new_content = prompt_we(input_prompt,
                                    default=default_prompt,
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
                if default_prompt in args["add_entries"]:
                    ind = args["add_entries"].index(default_prompt) + 1
                    if len(args["add_entries"]) >= ind + 1:
                        default_prompt = args["add_entries"][ind]
                    else:
                        default_prompt = ""
            else:
                print("Database already contains this entry, not added.")
            input_prompt = second_prompt

    if args['search_query'] is not None:
        log_("Searching entries")
        query = args['search_query'][0]
        df = litoy.df
        while True:
            query = query.lower()
            match = [x for x in df.index
                    if query in str(df.loc[x, "content"]).lower()
                    or query in str(df.loc[x, "metacontent"]).lower()]
            if len(match) == 0:
                log_("No matching entries found.", False)
                query = prompt_we("New search query > ")
                continue

            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', None)
            pd.set_option('display.max_colwidth', None)
            if args["verbose"] is False:
                print(df.loc[match, "content"])
            else:
                print(df.loc[match, :])
            pd.reset_option('display.max_rows')
            pd.reset_option('display.max_columns')
            pd.reset_option('display.width')
            pd.reset_option('display.max_colwidth')

            complete_list = ["quit", "exit", "search_again"]
            complete_list += [f'{x}: {df.loc[x, "content"]}' for x in match]
            auto_completer = prompt_toolkit.completion.WordCompleter(complete_list,
                                                                    match_middle=True,
                                                                    ignore_case=True,
                                                                    sentence=True)
            ans = prompt_we("Which entry do you want to edit?\n",
                            completer = auto_completer)
            if ans in ["q", "quit", "exit"]:
                raise SystemExit()
            elif ans == "search_again":
                query = prompt_we("New search query > ")
                continue
            else:  # either a new query or a match
                test = ans.split(":")[0]
                if test in [str(x) for x in match]:
                    args["edit_entries"] = [ans.split(":")[0]]
                    break
                else:
                    query = ans
                    continue


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
                log_(f"Entry with ID {entry_id} was removed. \
Content was {entry['content']}", False)
            else:
                log_(f"Entry with ID {entry_id} was NOT removed.", False)
        raise SystemExit()

    if args['edit_entries'] is not None:
        log_("Editing entries.")
        df = litoy.df.copy()

        # tags completion
        cur_tags = litoy.get_tags(litoy.df)
        autocomplete_list = ["tags:"+tags for tags in cur_tags] + ["set_length:"]
        auto_complete = prompt_toolkit.completion.WordCompleter(autocomplete_list,
                              match_middle=True,
                              ignore_case=True,
                              sentence=False)

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
                raise SystemExit()
            action_edit_entry(entry_id, litoy, field_list, field_auto_completer, auto_complete)
        raise SystemExit()

    if args['review_mode'] is True:
        log_("Entering review mode.")
        print_stats(litoy.df, printing=False)
        n = len(litoy.df.index)
        if n < 10:
            log_(f"ERROR: you only have {n} entries in your database, add 10 \
to start using LiTOY!", False)
            raise SystemExit()
        review_mode_cli(litoy)

    if args["convert_to_excel"] is True:
        log_("Converting to excel spreadsheet format", False)
        Excelwriter = pd.ExcelWriter(f"{str(args['db']).replace('.json', '')}_converted.xlsx",
                                     engine="xlsxwriter")
        litoy.df.to_excel(Excelwriter, sheet_name="LiTOY", index=True)
        Excelwriter.save()
        log_(f"Finished converting file to excel: {args['db']}_converted.xlsx", False)
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
                               if "title" in json.loads(x)
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

        if query == "logs":
            log_("Showing logs")
            log_file = "logs/rotating_log"
            with open(log_file) as lf:
                lines = lf.read()
            print(lines)
            raise SystemExit()


        df["tags"] = [", ".join(json.loads(x)) for x in df.loc[:, "tags"]]

        if query == "stats":
            log_("Showing statistics")
            print_stats(df)
            raise SystemExit()

        if query in ["podium", "global", "global_tasks"]:
            log_("Showing podium")
            print_podium(df, sizex, args)
            raise SystemExit()

        else:
            print_specific_entries(query, args, litoy.df)
        raise SystemExit()

    log_("ERROR: Reached last line of code, insufficient arguments?", False)
    wrong_arguments_(args)
