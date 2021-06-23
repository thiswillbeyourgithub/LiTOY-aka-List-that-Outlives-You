#!/usr/bin/env python3

###############################################################################
# Summary of each section
# 0. Banner and license
# 1. User defined settings
# 2. fonctions etc
# 3. Main routine


###############################################################################
# 0. Banner and license

###################################################################
#                                                                 #
#     __    _ ____________  __                                    #
#    / /   (_)_  __/ __ \ \/ /                                    #
#   / /   / / / / / / / /\  /                                     #
#  / /___/ / / / / /_/ / / /                                      #
# /_____/_/ /_/  \____/ /_/                                       #
#                                                                 #
#                                                                 #
#   ________            __    _      __     ________          __  #
#  /_  __/ /_  ___     / /   (_)____/ /_   /_  __/ /_  ____ _/ /_ #
#   / / / __ \/ _ \   / /   / / ___/ __/    / / / __ \/ __ `/ __/ #
#  / / / / / /  __/  / /___/ (__  ) /_     / / / / / / /_/ / /_   #
# /_/ /_/ /_/\___/  /_____/_/____/\__/    /_/ /_/ /_/\__,_/\__/   #
#                                                                 #
#    ____        __  ___                    __  __                #
#   / __ \__  __/ /_/ (_)   _____  _____    \ \/ /___  __  __     #
#  / / / / / / / __/ / / | / / _ \/ ___/     \  / __ \/ / / /     #
# / /_/ / /_/ / /_/ / /| |/ /  __(__  )      / / /_/ / /_/ /      #
# \____/\__,_/\__/_/_/ |___/\___/____/      /_/\____/\__,_(_)     #
#                                                                 #
#                                                                 #
#                                                                 #
###################################################################

###############################################################################
# Released under the GNU Lesser General Public License v2.                    #
# Copyright (C) - 2020 - user "thiswillbeyourgithub" of the website "github". #
# This file is part of LiTOY : a tool to help organiser various goals over    #
# time.                                                                       #
# Anki card template helping user to retain knowledge.                        #
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
# 1. User defined settings

# lifebar arguments :
disable_lifebar     = "no"
useless_first_years = 13
user_age            = 24
user_life_expected  = 90
useless_last_years  = 20


# for reading time estimation :
wpm = 200
average_word_length = 6

# used when comparing
questions = {
        "importance": "What steps will make you likely to achieve your goals?\
\n* Which is more important?\n* If you had one hour to spend,\
which would bring you more in your life?",
        "time": "Which task takes the less time to complete?",
        }

shortcuts = {
        "skip_fight"                 :  ["s","-"],
        "answer_level"               :  ["1","2","3","4","5","a","z","e","r","r","t"],
        "edit"                       :  ["E"],
        "undo"                       :  ["u"],
        "show_more_fields"           :  ["M"],
        "star"                       :  ["x"],
        "disable"                    :  ["d"],
        "open_media"                 :  ["o"],
        "show_help"                  :  ["h","?"],
        "quit"                       :  ["q"]
        }

# ELO :
K_values           =  [100, 50, 25, 15, 10]  # default [100, 50, 25, 15, 10]
default_score      =  1000  # default 1000


###############################################################################
# 2. Initialization, definitions etc

import pandas as pd
import argparse
import logging as lg
import argparse
import random
import requests
from Pathlib import Path
from pprint import pprint
from tqdm import tqdm
import logging
from logging.handlers import RotatingFileHandler
from Levenshtein import distance as lev
import pdftotext
from urltitle import URLtitleReader


def log_(string, onlyLogging=True):
    "appends string to the logging file and sometimes also print it"
    lg.info(f"{time.asctime()}: {string}")
    if onlyLogging is False:
        print(string)


def checkIfFileAndDB(path):
    "checks if the file and database already exists, if not create the file"
    db_location = Path(path)
    if db_location.exists():
        log_(f"Database file found at {path}", False)
        try:
            return pd.read_excel(db_location)
        except ValueError:
            log_(f"Litoy database not found in file at {path}")
            return None
    else:
        answer = input(f"No database file found at {path}, create it? (y/n)")
        if answer in "yes":
            db_location.touch()
            return None
        else:
            print("Exiting then")
            raise SystemExit()


def wrong_arguments_(args):
    "used to exit while printing arguments"
    print("Exiting because called with wrong arguments :")
    pprint(args)
    raise SystemExit()


def importFromFile(path):
    "checks if text file exists then import it into LiTOY"
    import_file = Path(path)
    if not import_file.exists():
        log_(f"Import file not found at {path}, exiting")
        raise SystemExit()
    log_(f"Importing from file {path}"
    with import_file.open() as f:
        lines = f.readlines()
    for line in tqdm(lines):
        if not litoy.checksIfEntryExists(line):
            add_new_entry(litoy.db, line)
        else:
            log_(f"Line already exists in the litoy database : {line}")
def add_new_entry(df, content):
    "add a new entry to the pandas dataframe"
    metacontent = get_meta_from_content(content)
    tags = get_tags_from_content(content)
    df.append({
        "ID": str(max(df['ID'])+1),
        "date_added": int(time.time()),
        "content": content,
        "metacontent": metacontent,
        "tags": tags,
        "starred": "No",
        "iELO": default_score,
        "tELO": default_score,
        "DiELO": default_score,
        "DtELO": default_score,
        "gELO": 2*default_score,
        "ms_spent_comparing":0,
        "K": sorted(K_values[-1]),
        "is_disabled":"No"
        })

def get_tags_from_content(string):
    "extracts tags from a line in the import file"
    splitted = string.split(" ")
    result = []
    for word in splitted:
        if word.startswith("tags:"):
            result.append(word[5:])
    return sorted(list(set(result)))

def get_meta_from_content(string):
    """
    extracts all metadata from a line in the import file
    this does not include tags, which are indicated using tags:sometag in the
    line. Instead it's for example the length of a youtube video which link
    appears in the content.
    If several links are supplied, only the first one will be used
    """
    splitted = string.split(" ")
    res_dic = {}
    for word in splitted:
        if word == "type:video": # this forces to analyse as a video
            for word in splitted:
            if word.startswith("http://") or word.startswith("www."):
                temp = extract_youtube(word)
                res_dic.update({"type":"video",
                    "length": temp[0],
                    "title": temp[1]})
                return res_dic

        if word.startswith("http://") or word.startswith("www."):
            if "yt" in word or "youtube" in word:
                temp = extract_youtube(word)
                res_dic.update({"type":"video",
                    "length": temp[0],
                    "title": temp[1]})
                return res_dic
            if word.endswith(".pdf"):
                temp = extract_pdf_url(word)
                res_dic.update({"type":"pdf",
                    "length": temp[0],
                    "title": temp[1]})
                return res_dic
        else if "/" in word:  # might be a link to a file
            if word.endswith(".pdf"):
                temp = extract_pdf_local(word)
                res_dic.update({"type":"pdf",
                    "length": temp[0],
                    "title": temp[1]})
                return res_dic
            if word.endswith(".md") or word.endswith(".txt")
                temp = extract_txt(word)
                res_dic.update({"type":"text",
                    "length": temp[0],
                    "title": temp[1]})
                return res_dic


def extract_youtube(word):
    "extracts video duration in seconds from youtube link, title etc"
    url = word
    title = URLTitleReader(verify_ssl=True).title(url)
    html = requests.get(link).text
    soup = bs4.BeautifulSoup(html, "html.parser")
    relevant_line = re.search("length_seconds.+: \d+\.\d+", str(soup)).group()
    video_length = str(round(int(re.search("\d+", line).group())/60,1))
    return (video_length, title)


def extract_pdf_url(word):
    "extracts reading time from an online pdf"
    url = word
    downloaded = requests.get(url)
    open("./.temporary.pdf", "wb").write(downloaded.content)
    (a, b) = extract_pdf_local("./.temporary.pdf")
    Path("./.temporary.pdf").unlink()
    return (a, b)

def extract_pdf_local(word):
    "extracts reading time from a local pdf file"
    try:
        with open(word, "rb") as f:
            text_content = pdftotext.PDF(f)
            text_content = str("\n").join(text_content)
    except FileNotFoundError:
        log_(f"Cannot find {word}, I thought it was a PDF")
        return (None, None)

    total_words = len(text_content)/average_word_length
    estimatedReadingTime = round(total_words/wpm,1)

    title = item.split(sep="/")[-1]
    return (estimatedReadingTime, title)


def extract_txt(word):
    "extracts reading time from a text file"
    try:
        txt_file = Path(word)
        with txt_file.open() as f:
            lines = f.readlines()
        text_content = ' '.join(lines)

        total_words = len(text_content)/average_word_length
        estimatedReadingTime = round(total_words/wpm,1)

        title = item.split(sep="/")[-1]
        return (estimatedReadingTime, title)

    Except ValueError:
        log_(f"Cannot find {word}, I thought it was a text file")
        return (None, None)

class LiTOYClass:
    "Class that interacts with the database using panda etc"
    def __init__(self, db_path):
        self.path = db_path
        self.save_to_file = save_to_file
        self.create_database(
        self.checksIfEntryExists = checksIfEntryExists
        self.get_tags = get_tags

    def save_to_file(self, df_entries):
        Excelwriter = pd.ExcelWriter(db_path, engine="xlsxwriter")
        df.to_excel(Excelwriter, sheet_name="LiTOY", index=False)
        Excelwriter.save()

    def create_database(self):
        cols = ["ID", "date_added", "content", "metacontent", "tags",
            "starred", "iELO", "tELO", "DiELO", "DtELO", "gELO",
            "ms_spent_comparing", "K", "is_disabled"]
        # iELO stands for "importance ELO", DiELO for "delta iELO",
        # gELO for "global ELO", etc
        df = pd.DataFrame(columns=cols)
        save_to_file(df_entries)

    def checksIfEntryExists(self, text, df):
        text.strip()
        for c in df['content']:
            if lev(text, c) <= max(0.2 * len(text), 10):
                return True
            else:
                return False

    def get_tags(self, df):
        tag_list = []
        for i in df.index:
            tag_list.append(i['tags'])
        return sorted(list(set(tag_list)))


    def print_all_entries(self, df, pretty=True):
        for i in df.index
            if pretty is True:
                pprint(df.iloc[i])
            else:
                print(df.iloc[i])


parser = argparse.ArgumentParser()
parser.add_argument("--import-from-file", "-i",
        nargs="?",
        metavar = "import_path",
        dest='to_import_loc',
        type = str,
        required=False,
        help = "path of the text file to import to litoy database")
parser.add_argument("--litoy-db", "-l",
        nargs = "?",
        metavar = "litoy_db_path",
        dest='litoy_db',
        type = str,
        required=False,
        help = "path to the litoy database")
parser.add_argument("--mode", "-m",
        nargs = "?",
        metavar = "mode",
        dest='mode',
        type = str,
        required=False,
        help = "comparison mode, can be either \'importance\' or \'time\'")

###############################################################################
# 3. Main routine


if __name__ == "__main__":
    args = parser.parse_args().__dict__

    # checks if the arguments are sane
    if args['to_import_loc'] is None and args['litoy_db_path'] is None:
        wrong_arguments_(args)
    if args['mode'] is not in "importance" or args['mode'] is not in "time":
        wrong_arguments_(args)

    if args['to_import_loc') is not None:
        importFromFile(args['to_import_loc'])
        log_("Done importing from file, exiting")
        raise SystemExit()

    if args['litoy_db_path'] is not None:
        db = checkIfFileAndDB(args['litoy_db_path'])
        if db is None:
            litoy = LiTOYClass()
            litoy.create_database()
        else:
            litoy = LiTOYClass(db)


# TODOS :
# * respect pep8
# * use type hints from the beginning
# * use docstrings everywhere
# * use mypy
