#!/usr/bin/env python3

import time
import random
import sqlite3
import logging
import os
import sys
import argparse
import pprint

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
        create_table_in_db()
    else:
        logging.info("\n## db NOT found\n")
        print("NO DB FOUND (database.db), creating one...")
        create_table_in_db()


    # sets all deltas just in case
    logging.info("Updating all deltas")
    all_IDs = fetch_entry("ID >=0")
    for i in range(len(all_IDs)):
        #update_delta(str(all_IDs[i]["ID"]))
        pass
    logging.info("Done batch updating all deltas\n")
    logging.info("End of initialization\n\n")

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
            metavar='formated_entry category details',
            dest='addentry',
            required=False,
            help = "directly add an entry by putting it inside quotation mark like so : python3 ./__main__.py -a \"do this thing\" \"DIY\" \"I really need to do it that way\"")
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
    parser.add_argument("--edit", "-e",
            nargs = "*",
            type = str,
            metavar = "ID field newvalue",
            dest="editEntry",
            required=False,
            help = "edit specific field from an entry")
    parser.add_argument("--rank", "-r",
            nargs = "*",
            type = str,
            metavar = "SQL_condition",
            dest="rank",
            required=False,
            help = "display ranked entries according to the right formula")
    parser.add_argument("--external",
            action='store_true',
            required=False,
            dest="ext",
            help = "LINUX : open in sqlite browser")
    parser.add_argument("--verbose",
            action='store_true',
            required=False,
            help = "show debug to the console instead of just in the file")
    parser.add_argument("--version",
            action='store_true',
            required=False,
            help = "display version information")
    args = parser.parse_args().__dict__

    logging.info("LiTOY started with arguments : " + str(args))

    inc=0  # exits if incompatible arguments found
    for i in args.keys() :
        #if str(i) != "None" or i != False:
        ii = str(args[i])
        if ii not in ["None","False"]:
            inc = inc+1
    if inc>1 :
        print("Are incompatible arguments! Exiting...")
        logging.info("Incompatible arguments! Exiting...")
        sys.exit()
#    if args['verbose'] != False:
#        #https://stackoverflow.com/questions/14058453/making-python-loggers-output-all-messages-to-stdout-in-addition-to-log-file
#            logging.basicConfig( level=logging.INFO,
#                    stream=sys.stdout,
#                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


    if args['fight'] != None:
        logging.info("Fight mode, argument : " + args['fight'])
        pass 

    if args['addentry'] != None:
        logging.info("adding entry : " + str(args['addentry']))
        fields = get_field_names()
        if fields == "None" :
            fields = ["ID", "date_added",
                    "entry", "details",
                    "category", "starred",
                    "progress", "importance_elo",
                    "date_importance_elo",
                    "time_elo", "date_time_elo",
                    "delta_imp", "delta_time",
                    "global_score", "time_spent_comparing",
                    "number_of_comparison", "disabled",
                    "done", "K_value"]
        newentry = {} 
        for i in fields :
            newentry[i]=""
        newentry['entry'] = args['addentry'][0]
        if len(args['addentry']) > 1:
            newentry['category'] = args["addentry"][1]
        if len(args['addentry']) >2 :
            newentry['details'] = args["addentry"][2]
        if len(args['addentry']) >3:
            print("Too many argument, follow this example : python3 __main__.py -a \"read this article\" \"reading_list\"")
            logging.info("Too many arguments : " + str(args['addentry']))
            sys.exit()

        if newentry['details'] == '' :
            print("No details added to entry")
        if newentry['category'] == '' :
            print("No category added to entry")

        cur_time = str(int(time.time()))
        newID = str(int(get_max_ID())+1)
        newentry['ID'] = newID
        newentry['date_added'] = cur_time
        newentry['starred'] = "0"
        newentry['progress'] = "None"
        newentry['importance_elo'] = "0_" + str(default_score)
        newentry['time_elo'] = "0_" + str(default_score)
        newentry['global_score'] = "None"
        newentry['date_importance_elo'] = cur_time
        newentry['date_time_elo'] = cur_time
        newentry['delta_imp'] = default_score
        newentry['delta_time'] = default_score
        newentry['time_spent_comparing'] = "0"
        newentry['number_of_comparison'] = "0"
        newentry['done'] = "0"
        newentry['disabled'] = 0
        logging.info("Pushing entry to db, ID = " + newID)
        print("Pushing entry to db, ID = " + newID)
        push_dico(newentry, "INSERT")
        



    if args['import'] != None:
        logging.info("Importing from file, arguments : " + str(args['import']))
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
        print("Importing from " + filename + "...\n")
        logging.info("Importing from " + filename + "...\n")
        fun_import_from_txt(filename, cat_choice)


    if args['rank'] != None:
        logging.info("Displaying ranks, arguments : " + str(args['rank']))
        condition=""
        limit = 0
        if len(args['rank']) not in [2, 3]:
            print("Invalid number of arguments : " + str(args['rank']))
            logging.info("Invalid number of arguments : " + str(args['rank']))
            print("correct syntax : --rank FIELD str(aight)/rev(erse)")
            sys.exit()

        if args['rank'][0] == "all":
            print("Printing all entries")
            logging.info("Printing all entries\n")
            condition = "ID >= 0 ORDER BY ID"
        try :
            limit = int(args['rank'][2])
            print("Displaying only n=" + limit)
            logging.info("Displaying only n=" + limit)
        except :
            logging.info("Will not limit display")

        if condition=="" : # order by field 
             condition = "ID >= 0 ORDER BY " + str(args['rank'][0])
             logging.info("Displaying by field " + str(args['rank'][0]))

        if args['rank'][1] in "reverse":
             condition = condition + " DESC"
        if args['rank'][1] in "straight":
             condition = condition + " ASC"
        if "DESC ASC" in condition :
            logging.info("wrong sorting order argument")
            print("wrong sorting order argument")
            sys.exit()
        all_cards = fetch_entry(condition)
        if limit != 0:
            all_cards = all_cards[:limit] 

        pprint.pprint(all_cards)
        logging.info("Done displaying ranks")

    if args['settings'] != None:
        logging.info('Change settings command, arguments : ' + str(args['settings']))
        # read line by line the settings file
#        file = open("src/litoy/settings.py", "r")
#        for line in file:
#            if settings[0] in line.split(sep=" "):
#                print(line)
#        file.close() 
        logging.info("Done changing settings")

    if args['version'] != False:
       print("Check out github at https://github.com/thiswillbeyourgithub/LiTOY/")
       logging.info("Display version")
       sys.exit()

#    if args['ext'] != False:
#        print("Openning in sqlite browser")
#        logging.info("Openning in sqlite browser\n")


    if args['editEntry'] != None:
        if len(args['editEntry']) != 3 :
                print("ERROR : needs 3 arguments, exiting")
                logging.info("Entry edit error : needs 3 arguments, provided : " + str(args['editEntry']))
                sys.exit()
        editID = str(args['editEntry'][0])
        logging.info("Editing entry, ID " + editID)
        editField = str(args['editEntry'][1])
        editValue = str(args['editEntry'][2])
        entry = fetch_entry("ID = " + editID)[0]
        entry[editField] = editValue
        if editField not in get_field_names():
            print("You're not supposed to create new fields like that!")
            logging.info("ERROR : trying to add a new field : " + editField)
            sys.exit()
        editPrevious = str(entry[editField])
        if editPrevious == editValue:
            print("Not edited : values are identical")
            logging.info("Not edited : values are identical")
            sys.exit()
        logging.info("Changed field " + editField + " from value " + editPrevious + " to value " + editValue)
        print("Changing field " + editField + " from value " + editPrevious + " to value " + editValue)
        push_dico(entry, "UPDATE")
        logging.info("Done editing field\n")
        print("Fresh entry :")
        print(entry)











if __name__ == "__main__" :
    logging.basicConfig(level=logging.INFO,
            filename = 'debug.log',
            filemode='a',
            #format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            format='%(asctime)s: %(message)s')
    main()



