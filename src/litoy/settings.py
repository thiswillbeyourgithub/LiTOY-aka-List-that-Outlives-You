#!/usr/bin/env python3

# This file contains the user settings

user_age = 23
user_life_expected = 75

questions = {
        "importance" : "What steps will make you likely to achieve your goals?\n* Which is more important?\n* If you had one hour to spend, which would bring you more in your life?",
        "time" : "Which task takes the less time to complete?",
        "ranking" : "Which task should be done first?"
        }

shortcuts = {
        "skip_fight"                 :  ["s","-"],
        "answer_level"               :  ["1","2","3","4","5","a","z","e","r","r","t"],
        "toggle_display_options"     :  ["D"],
        "edit"                       :  ["E"],
        "undo"                       :  ["u"],
        "star"                       :  ["x"],
        "disable"                    :  ["d"],
        "show_help"                  :  ["h","?"],
        "quit"                       :  ["q"]
        }

K_values           =  [100,50,25,15,10]
default_score      =  "1000"
choice_threshold   =  0.25               #  X%    of  the  time    :      the      card  used  the  least  recently  will  be  picked

formula_dict = {
        #"deckname" : "formula_name"
        "IA&work" : "sum_elo",
        "toread" : "sum_elo",
        "movies" : "sum_elo"
        }

def sum_elo(elo1, elo2, elo3=0, elo4=0, elo5=0):
    # here, elo1 and elo2 can be importance_elo and time_elo for example
    result = int(elo1) + int(elo2) + int(elo3) + int(elo4) + int(elo5)
    return result

def example_formule(elo1,elo2,elo3,elo4,elo5):
    # do computation here
    result = ""
    sys.exit()
    return result
