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

# This file contains the user settings :

# lifebar arguments :
disable_lifebar = "no" #default no
useless_first_years = 13
user_age            = 23
user_life_expected  = 90
useless_last_years  = 20





questions = {
        "importance"        : "What steps will make you likely to achieve your goals?\n* Which is more important?\n* If you had one hour to spend, which would bring you more in your life?",
        "time"              : "Which task takes the less time to complete?",
        "ranking"           : "Which task should be done first?",
        "filesize"          : "What file is bigger ?",
        "duration"          : "What movie is longer?",
        "order"             : "What task should be done before the other?"
        }

sqlitebrowser_path = "/usr/bin/sqlitebrowser"
browser_path = "/usr/bin/firefox" # only on linux, otherwise it uses the webbbrowser package
default_path = "/home/"  # when a file beginning like that is found in an entry, it is recognized as a media 




# a few notes :
# * if you add a one letter shortcut, be sure it's in a list and not just 
# a str like so ["D"]
# * if you add or change a letter to the answer level shortcuts, modify
# it also in the shortcut_and_action function to translate it to the correct number
# this function is in the file function.py
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

deck_mode_correspondance = {
        "toread" : ["importance", "time"],
        "movies" : ["importance", "duration", "file_size"],
        "simple_order" : ["order"]
        }





# ELO :
K_values           =  [100, 50, 25, 15, 10]  # default [100, 50, 25, 15, 10]
default_score      =  1000  # default 1000
choice_threshold   =  0.10  # default 0.10, means that 10% of the time the card used the least recently  will  be  picked

formula_dict = {
        "IA&work"   : "sum_elo",
        "toread"    : "sum_elo",
        "t"         : "sum_elo",
        "movies"    : "sum_elo",
        "order"     : "simple_order_score"
        }
# syntax : "deckname" : "formula_name"






# Elo functions :
def sum_elo(elo1, elo2, elo3=0, elo4=0, elo5=0):
    # here, elo1 and elo2 can be importance_elo and time_elo for example
    result = int(elo1) + int(elo2) + int(elo3) + int(elo4) + int(elo5)
    return result

def example_formula(elo1,elo2,elo3,elo4,elo5):
    # do computation here
    result = ""
    sys.exit()
    return result


def simple_order_score(elo1, elo2, elo3, elo4, elo5):  # used to sort in what order task should be done
    result = int(elo1)
    return result
