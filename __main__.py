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
from   src.litoy.elo        import *
from   src.litoy.functions  import *



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
    else:
        logging.info("\n## db NOT found\n")
        print("NO DB FOUND (database.db), creating one...")
        sys.exit()

    create_table_in_db()

    # sets all deltas just in case
    logging.info("Updating all deltas")
    all_IDs = fetch_entry("ID >=0")
    for i in range(len(all_IDs)):
        update_delta(str(all_IDs[i]["ID"]))
    logging.info("Done batch updating all deltas\n")
    logging.info(" ## End of initialization\n\n")

    set_db_defaults_value()




###################### main loop :



#    while 1==1:
#        type_of_fight = input("\nSelect mode:    t = Compare time     i = Compare importance\nYour choice => ")
#        if type_of_fight !="i" and type_of_fight != "t" :
#            print("Incorrect choice\n\n")
#            continue
#        fighters = pick_2_entries(type_of_fight)
#        print_2_entries(fighters, "all")
#        print("\n")
#        if type_of_fight == "i":
#            user_input = input(questions['importance'] + "\n=>")
#        if type_of_fight == "t":
#            user_input = input(questions['time'] + "\n=>")
#        shortcut_reaction(user_input,type_of_fight, fighters)
#        break


    ###################### script arguments :

    parser = argparse.ArgumentParser()
    parser.add_argument("--fight", "-f",
            nargs = "*",
            metavar = "mode number_of_fights",
            dest='fight',
            type = str,
            required=False,
            help = "pick entries at random and make them fight")
    parser.add_argument("--add", "-a",
            nargs = "*",
            type = str,
            metavar='formated_entry category',
            dest='addentry',
            required=False,
            help = "directly add an entry by putting it inside quotation mark like so : python3 ./__main__.py -a \"do this thing\" \"DIY\"")
    parser.add_argument("--import_from_txt", "-i",
            nargs = "*",
            type = str,
            metavar='database_path category',
            dest='import',
            #default='new_entry.txt',
            required=False,
            help = "import from a textfile")
    parser.add_argument("--settings", "-s",
            nargs = 2,
            type = str,
            metavar="variable new_value",
            dest='settings',
            required=False,
            help = "set user settings")
    parser.add_argument("--rank", "-r",
            nargs = 1,
            type = str,
            metavar = "SQL_condition",
            dest="rank",
            required=False,
            help = "display ranked entries according to the right formula")
    parser.add_argument("--version",
            action='store_true',
            required=False,
            help = "display version information")
    args = parser.parse_args().__dict__

    # check if incompatible arguments
    inc=0
    for i in args.keys() :
        #if str(i) != "None" or i != False:
        ii = str(args[i])
        if ii not in ["None","False"]:
            print(i)
            inc = inc+1
    if inc>1 :
        print("Are incompatible arguments! Exiting...")
        logging.info("Incompatible arguments! Exiting...")
        sys.exit()


    if args['import'] != None:
        path = args["import"]
        if len(path) >2: 
            print("ERROR : too many arguments!" + str(path[2:]))
            logging.info("ERROR : too many arguments!" + str(path[2:]))
            sys.exit()
        cat_choice = ""
        if len(path) == 1 :
            cat_list = get_category()
            cat_choice = input("Enter category for the new entries: (default is 'None')\nCategories already found in db : " + str(cat_list) + "\n=> ")
        else :
            cat_choice = path[1]
        if cat_choice == "" : # if user input is empty
            cat_choice == "None"
        filename=path[0]
        print("\n#Importing from " + filename + "...\n")
        logging.info("\n#Importing from " + filename + "...\n")
        fun_import_from_txt(filename, cat_choice)

    if args['rank'] != None:
       pass 

    if args['settings'] != None:
       pass









if __name__ == "__main__" :
    logging.basicConfig(level=logging.INFO, filename = 'debug.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    main()



