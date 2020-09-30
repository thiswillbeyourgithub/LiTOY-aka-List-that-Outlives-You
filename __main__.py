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
    # links I used :
    # https://docs.python.org/3/howto/argparse.html
    # https://cmsdk.com/python/how-to-add-multiple-argument-options-in-python-using-argparse.html
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser()
    # mutually exclusive arguments :
    group_exclusive = parser.add_mutually_exclusive_group()
    group_exclusive.add_argument("-a",
            "--add",
            nargs = "1",
            type = str,
            metavar='formated_entry',
            dest='newentry',
            required=False,
            help = "directly add an entry by putting it inside quotation mark like so : python3 ./__main__.py add \"do x\"")
    group_exclusive.add_argument("-i",
            "--import_from_txt",
            nargs = "*",
            type = str,
            metavar='db_path category',
            dest='filepath',
            default='new_entry.txt',
            required=False,
            help = "import from a textfile")
    group_exclusive.add_argument("-s",
            "--settings",
            nargs = "3",
            type = str,
            metavar='var newvalue',
            dest='change_settings',
            required=False,
            help = "set user settings")
    group_exclusive.add_argument("-r",
            "--rank",
            nargs = "*",
            type = str,
            required=False,
            help = "display ranked entries according to the right formulae")

    # actually useful arguments :
    #parser.add_argument(dest="import_from_txt", help="import from txt file that has to be specified", type=str)

    # parse the arguments :
    args = parser.parse_args()
    #print(args)

    if args.filepath:
        #print(args.filepath)
        #while True :
           #import_bool =  input("\nDo you want to import new entries from a file? (y/n)\n=> ")
           #if import_bool == "y":
               if not args.filepath[1] :
                   cat_list = get_category()
                   cat_choice = input("Specify category for the new entries? (default is 'None')\nCategories already found in db : " + cat_list + "\n=> ")
               else :
                   cat_choice = args.filepath[1]
               if cat_choice == "" : # if empty user input
                   cat_choice == "None"
               #filename = input("\nWhat is the name of the file containing the new entries? Press Enter to use default file (new_entry.txt)\n(remember to put it in the same folder!)\n=> ")
               filename=args.filepath[0]
#               if filename == "" :
#                   filename = "new_entry.txt"
               print("\n ## Importing from " + filename + "...\n")
               logging.info("\n ## Importing from " + filename + "...\n")
               print(cat_choice)
               fun_import_from_txt(filename, cat_choice)
#           else :
#               print("\n ## No importation to do\n")
#               logging.info("\n ## No importation to do\n")
#               #break





if __name__ == "__main__" :
    logging.basicConfig(level=logging.INFO, filename = 'debug.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    main()



