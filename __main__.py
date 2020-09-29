#!/usr/bin/env python3

import time
import random
import sqlite3
import logging
import os
import sys
import argparse

from   src.litoy.sql        import *
from   src.litoy.settings   import *
import src.litoy.elo
import src.litoy.functions



###################################################################
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
###################################################################





###################### initialization :

def main() :
    if os.path.exists('database.db'):
        logging.info("\n## db found\n")
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
    else:
        logging.info("\n## db NOT found\n")
        sys.exit()

    logging.info("\n ## Openning db \n")
    logging.info("\n ## Creating table if not found \n")
    query_create_table = '\
            CREATE TABLE IF NOT EXISTS LiTOY(\
            ID INTEGER,\
            date_added INTEGER,\
            entry TEXT,\
            details TEXT,\
            category TEXT,\
            starred INTEGER,\
            progress TEXT,\
            importance_elo TEXT,\
            date_importance_elo TEXT,\
            time_elo TEXT,\
            date_time_elo TEXT,\
            delta_imp INTEGER,\
            delta_time INTEGER,\
            global_score,\
            time_spent_comparing INTEGER,\
            number_of_comparison INTEGER,\
            disabled INTEGER,\
            done INTEGER,\
            K_value INTEGER\
            )'
    logging.info("SQL CREATE REQUEST : " + query_create_table)
    cursor.execute(query_create_table)


#    while True :
#        import_bool =  input("\nDo you want to import new entries from a file? (y/n)\n=> ")
#        if import_bool == "y":
#            category_list = get_category()
#            cat_choice = input("Specify category for the new entries? (default is 'None')\nCategories already found in db : " + category_list + "\n=> ")
#            if cat_choice == "" :
#                cat_choice = "None"
#            filename = input("\nWhat is the name of the file containing the new entries? Press Enter to use default file (new_entry.txt)\n(remember to put it in the same folder!)\n=> ")
#            if filename == "" :
#                filename = "new_entry.txt"
#            print("\n ## Importing from " + filename + "...\n")
#            logging.info("\n ## Importing from " + filename + "...\n")
#            import_from_txt(filename, cat_choice)
#        else :
#            print("\n ## No importation to do\n")
#            logging.info("\n ## No importation to do\n")
#            break

    set_db_defaults_value()

    # sets all deltas just in case
    #all_ids = get_sql_value("id")
    logging.info("Updating all deltas")
    all_IDs = fetch_entry("ID >=0")
    for i in range(len(all_IDs)):
        update_delta(str(all_IDs[i]["ID"]))
    logging.info("Done batch updating all deltas\n")

    logging.info(" ## End of initialization\n\n")


###################### main loop :


#    while 1==1:
#        type_of_fight = input("Select mode:\nt = Compare time\ni = Compare importance\n\n\nYour choice => ")
#        if type_of_fight !="i" and type_of_fight != "t" :
#            print("Incorrect choice\n\n")
#            continue
#        fighters = choose_fighting_entries(type_of_fight)
#        print("\n")
#        print("#######################")
#        print_entry(fighters[0])
#        print("#######################")
#        print_entry(fighters[1])
#        print("\n\n")
#        if type_of_fight == "t":
#            user_input = input(question_time + "\n=>")
#        if type_of_fight == "i":
#            user_input = input(question_importance + "\n=>")
#        shortcut_reaction(user_input,type_of_fight, fighters)
#        break


###################### script arguments :
# links I used :
# https://docs.python.org/3/howto/argparse.html
# https://cmsdk.com/python/how-to-add-multiple-argument-options-in-python-using-argparse.html
# https://docs.python.org/3/library/argparse.html
parser = argparse.ArgumentParser()
# mutually exclusive arguments :
group_exclusive = parser.add_mutually_exclusive_group()
group_exclusive.add_argument("--add",
        nargs = "*",
        type = str,
        help = "directly add an entry by putting it inside quotation mark like so : python3 ./__main__.py add \"do x\"")
group_exclusive.add_argument("--import_from_txt",
        nargs = "*",
        type = str,
        help = "import from a textfile")
group_exclusive.add_argument("--rank",
        nargs = "*",
        type = str,
        help = "display ranked entries according to the right formulae")
group_exclusive.add_argument("--settings",
        nargs = "?",
        type = str,
        help = "set user settings")
# actually useful arguments :
#parser.add_argument(dest="import_from_txt", help="import from txt file that has to be specified", type=str)
# parse the arguments :
args = parser.parse_args()

#print(args.add)
#print(args.import_from_txt)



if __name__ == "__main__" :
    logging.basicConfig(level=logging.INFO, filename = 'debug.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    main()




################################################################# CODE GRAVEYARD
'''


#query_create = "IF NOT EXISTS (SELECT 1 FROM LiTOY WHERE entry = \"" + entry + "\") BEGIN (INSERT INTO LiTOY(ID, date_added, entry, time_spent_comparing, number_of_comparison, starred, delta) VALUES (" + newID + ", " + unixtime + ", \'" + entry + "\', 0, 0, 0, " + delta_0 + ")) END"
#query_create = "INSERT OR IGNORE INTO LiTOY(ID, date_added, entry, time_spent_comparing, number_of_comparison, starred, category) VALUES (" + newID + ", " + unixtime + ", \'" + entry + "\', 0, 0, 0, 'None' )"
#query_create = str("INSERT INTO LiTOY(ID, date_added, entry, time_spent_comparing, number_of_comparison, starred, delta) VALUES (") + newID + ", " + unixtime + ", \'" + str(entry) + "\', 0, 0, 0, " + delta_0 + ")) END"
#query_create = "'INSERT INTO LiTOY (entry) VALUES ('" + entry + "') EXCEPT (SELECT 1 FROM LiTOY WHERE entry = '" + entry + "')' "
#query_create = "INSERT INTO LiTOY(entry) VALUES ('" + entry + "')"



#real_score =
#3 si rep positive +
#2 si rep positive
#1.5 si match nul
#1 si rep negative
#0 si rep negative +




#cursor.execute('CREATE TABLE IF NOT EXISTS LiTOY(ID INTEGER, date_added INTEGER, entry TEXT, details TEXT, category TEXT, starred INTEGER, progress TEXT, importance_elo TEXT, date_importance_elo TEXT, time_elo TEXT, date_time_elo TEXT, delta_imp INTEGER, delta_time INTEGER, global_score, time_spent_comparing INTEGER, number_of_comparison INTEGER, disabled INTEGER, done INTEGER, UNIQUE(ID, entry))')
# "unique" doesn't seem to work well so I added the workaround to check wether an entry exists



'''
