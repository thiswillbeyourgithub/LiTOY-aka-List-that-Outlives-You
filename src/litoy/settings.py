#!/usr/bin/env python3

# This file contains the user settings :

# used for the life bar
disable_lifebar = "no" #default no
useless_first_years = 13
user_age = 23
user_life_expected = 90
useless_last_years = 20

questions = {
        "importance" : "What steps will make you likely to achieve your goals?\n* Which is more important?\n* If you had one hour to spend, which would bring you more in your life?",
        "time" : "Which task takes the less time to complete?",
        "ranking" : "Which task should be done first?",
        "filesize" : "What file is bigger ?",
        "duration" : "What movie is longer?",
        }

sqlitebrowser_path = "/usr/bin/sqlitebrowser"
browser_path = "/usr/bin/firefox" # only on linux, otherwise it uses the webbbrowser package

# a few notes :
# * if you add a one letter shortcut, be sure it's in a list and not just 
# a str like so ["D"]
# * if you add or change a letter to the answer level shortcuts, modify
# it also in the shortcut_and_action function to translate it to the correct number
# this function is in the file function.py
shortcuts = {
        "skip_fight"                 :  ["s","-"],
        "answer_level"               :  ["1","2","3","4","5","a","z","e","r","r","t"],
        #"toggle_display_options"     :  ["D"],
        "edit"                       :  ["E"],
        "undo"                       :  ["u"],
        "show_more_fields"           :  ["M"],
        "star"                       :  ["x"],
        "disable"                    :  ["d"],
        "open_links"                 :  ["o"],
        "show_help"                  :  ["h","?"],
        "quit"                       :  ["q"]
        }

deck_mode_correspondance = {
        "toread" : ["importance", "time"],
        "movies" : ["importance", "duration", "file_size"]
        }

# ELO :
K_values           =  [100, 50, 25, 15, 10]  # default [100, 50, 25, 15, 10]
default_score      =  1000  # default 1000
choice_threshold   =  0.10  # default 0.10, means that 10% of the time the card used the least recently  will  be  picked

formula_dict = {
        "IA&work" : "sum_elo",
        "toread" : "sum_elo",
        "t"       : "sum_elo",
        "movies" : "sum_elo"
        }
# syntax :
#"deckname" : "formula_name"

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
