#!/usr/bin/env python3

# This file contains the user settings

user_age = "23"
user_life_expected = "75"

#question_importance = "What steps will actually make you likely to achieve your goals?\n* Which is more important?\n* If you had one hour to spend, which would bring you more in your life?"
#question_time = "Which task takes the less time to complete?"
#question_ranking = "Which task should be done first?"
questions = {
        "importance" : "What steps will make you likely to achieve your goals?\n* Which is more important?\n* If you had one hour to spend, which would bring you more in your life?",
        "time" : "Which task takes the less time to complete?",
        "ranking" : "Which task should be done first?"
        }

shortcut = {
        "skip_fight"                 :  ["s","-"],
        "answer_level"               :  ["1","2","3","4","5","a","z","e","r","r","t"],
        "cycle_display_options"      :  "q",
        "edit_entry"                 :  "s",
        "edit_details"               :  "d",
        "undo_fight"                 :  "f",
        "mark_left"                  :  "w",
        "mark_right"                 :  "x",
        "disable_card_because_done"  :  "C",
        "disable_card_because_else"  :  "c",
        "show_help"                  :  ["h","?"]
        }

K_values           =  [100,50,25,15,10]
default_score      =  "1000"
adjustment_factor  =  "1"                #  used  in  the  global  score  formula
#choice_threshold   =  0.25               #  X%    of  the  time    :      the      card  used  the  least  recently  will  be  picked
choice_threshold   =  0.5               #debug
