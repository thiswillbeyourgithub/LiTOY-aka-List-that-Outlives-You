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
    logging.info("\n\n\n\n\n\n########################################\nSTARTING")
    if os.path.exists('database.db'):
        init_table()
    else:
        logging.info("db NOT found")
        print("NO DB FOUND (database.db), creating one...")
        init_table()







###################### main loop :



    ###################### script arguments :

    parser = argparse.ArgumentParser()
    parser.add_argument("--fight", "-f",
            nargs = "+",
            metavar = "mode",
            dest='fight',
            type = str,
            required=False,
            help = "pick entries at random and make them fight")
    parser.add_argument("--add", "-a",
            nargs = "*",
            type = str,
            metavar='formated_entry deck details',
            dest='addentry',
            required=False,
            help = "directly add an entry by putting it inside quotation mark like so : python3 ./__main__.py -a \"do this thing\" \"DIY\" \"I really need to do it that way\"")
    parser.add_argument("--import_from_txt", "-i",
            nargs = "*",
            type = str,
            metavar='database_path deck',
            dest='import',
            #default='new_entry.txt',
            required=False,
            help = "import from a textfile")
    parser.add_argument("--number", "-n",
            nargs = 1,
            type = int,
            metavar="limit",
            dest='nlimit',
            required=False,
            default=99999,
            help = "sets the limit of entries to process or display etc, default=999999")
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
    parser.add_argument("--deck", "-d",
            nargs = 1,
            type = str,
            metavar = "deck_name",
            dest="deck",
            required=False,
            help = "deck to display or fight")
    parser.add_argument("--tags", "-t",
            nargs = 1,
            type = str,
            metavar = "tags",
            dest="tags",
            required=False,
            help = "tags to display or fight")
    parser.add_argument("--external",
            action='store_true',
            required=False,
            dest="ext",
            help = "LINUX : open in sqlite browser")
    parser.add_argument("--verbose",
            action='store_true',
            required=False,
            help = "show debug to the console instead of just in the file")
    parser.add_argument("--check-consistency",
            action='store_true',
            required=False,
            dest="consistency",
            help = "Check the db for incoherent values (non exhaustive)")
    parser.add_argument("--version",
            action='store_true',
            required=False,
            help = "display version information")
    args = parser.parse_args().__dict__

    logging.info("LiTOY started with arguments : " + str(args))
    print(args)

    inc=0  # exits if incompatible arguments found
    for i in args.keys() :
        ii = str(args[i])
        inc_list=[]
        if ii not in ["None","False"] and i not in ["nlimit", "verbose", "decks", "tags"]:
            inc_list.append(i)
            inc = inc+1
    if inc>1 :
        print(inc_list)
        print("Are incompatible arguments! \n   Exiting...")
        logging.info("Incompatible arguments :" + str(inc_list) + "\n   Exiting...")
        sys.exit()

#    if args['verbose'] == True:
#        #https://stackoverflow.com/questions/14058453/making-python-loggers-output-all-messages-to-stdout-in-addition-to-log-file
#        file_handler = logging.FileHandler(filename='debug.log')
#        stdout_handler = logging.StreamHandler(sys.stdout)
#        handlers = [file_handler, stdout_handler]
#
#        logging.basicConfig(level=logging.INFO,
#                handlers=handlers,
#                format='%(asctime)s: %(message)s')
#        logger = logging.getLogger('LOGGER_NAME')
#    if args['verbose'] == False:
#        logging.basicConfig(level=logging.INFO,
#                filename = 'debug.log',
#                filemode='a',
#                format='%(asctime)s: %(message)s')
#        logger = logging.getLogger('LOGGER_NAME')


    if args['fight'] != None:
        logging.info("Fight : argument : " + str(args['fight']))
        if len(args['fight']) != 1:
            logging.info("Fight : wrong number of arguments : " + str(args['fight']))
            print("Fight : Wrong number of arguments")
            print('syntax : python3 __main__.py --fight MODE(i/t/random/other) -n NUMBER ')
            print("         python3 __main__.py --fight ti -n 25")
        
        try :
            limit = int(args['nlimit'][0])
        except TypeError:
            limit = int(args['nlimit'])
        if limit < 1:
            print('Fight : Invalid limit number')
            logging.info('Fight : Invalid limit number')
            sys.exit()
        else :
            logging.info("Fight " + str(limit) + " times")

        for n in range(limit):
            type_of_fight = args['fight'][0]
            mode=""
            if type_of_fight  in "time" :
                mode="time"
            if type_of_fight  in "importance" :
                mode="importance"
            if type_of_fight in "random" :
                mode=random.choice["time","importance"]

            if mode=="":
                print("Fight : invalid fight mode")
                logging.info("Fight : invalid fight mode")
                sys.exit()

            fighters = pick_2_entries(type_of_fight)
            print_2_entries(fighters, "all")
            print("\n")
            user_input = input(questions[mode] + "\n=>")
            waiting_shortcut(user_input, mode, fighters)



    if args['addentry'] != None:
        # python3 main --add todoX deck "tags tags" "details"
        if len(args['addentry']) not in [1,2,3,4] :
            logging.info("Addentry : wrong nomber of arguments : " + str(args['addentry']))
            print("Addentry : Wrong number of arguments")
            print('syntax : python3 __main__.py --add "change the tires" "thingsToDO" "garage diy for_madam" "I really need to do this using tool number 17"')
            print("         python3 __main__.py --add entry deck tags details")
            sys.exit()
        logging.info("Addentry : adding entry : " + str(args['addentry']))
        fields = get_field_names()
        if fields == "None" :
            fields = ["ID", "date_added", "entry", "details",
                    "tags", "deck", "starred", "progress", "importance_elo",
                    "date_importance_elo", "time_elo", "date_time_elo",
                    "delta_imp", "delta_time", "global_score", "time_spent_comparing",
                    "nb_of_fight", "disabled", "K_value"]
        newentry = {} 
        for i in fields :
            newentry[i]=""

        newentry['entry'] = args['addentry'][0]
        try : newentry['deck'] = args["addentry"][1] 
        except : newentry['deck'] = "None"
        try : newentry['tags'] = args["addentry"][2] 
        except : newentry['tags'] = ""
        try : newentry['details'] = args["addentry"][3]
        except : newentry['details'] = ""

#        if len(args['addentry']) > 1:
#            newentry['deck'] = args["addentry"][1]
#        if len(args['addentry']) >2 :
#            newentry['details'] = args["addentry"][2]
#        if len(args['addentry']) >3:
#            print("Addentry : Too many argument, follow this example : python3 __main__.py -a \"read this article\" \"reading_list\"")
#            logging.info("Addentry : Too many arguments : " + str(args['addentry']))
#            sys.exit()

#        if newentry['details'] == '' :
#            print("Addentry : No details added to entry")
#        if newentry['deck'] == '' :
#            print("Addentry : No deck added to entry")

        cur_time = str(int(time.time()))
        newID = str(int(get_max_ID())+1)
        newentry['ID'] = newID
        newentry['date_added'] = cur_time
        newentry['starred'] = "0"
        newentry['progress'] = ""
        newentry['importance_elo'] = "0_" + str(default_score)
        newentry['time_elo'] = "0_" + str(default_score)
        newentry['global_score'] = ""
        newentry['date_importance_elo'] = cur_time
        newentry['date_time_elo'] = cur_time
        newentry['delta_imp'] = default_score
        newentry['delta_time'] = default_score
        newentry['time_spent_comparing'] = "0"
        newentry['nb_of_fight'] = "0"
        newentry['disabled'] = 0
        newentry['K_value'] = K_values[0]
        logging.info("Addentry : Pushing entry to db, ID = " + newID)
        print("Addentry : Pushing entry to db, ID = " + newID)
        push_dico(newentry, "INSERT")
        



    if args['import'] != None:
        # python3 main --import filename deck
        logging.info("Import : Importing from file, arguments : " + str(args['import']))
        path=args["import"]
        filename=path[0]
        print("Import : from " + filename)
        if len(path) >3: 
            print("ERROR : too many arguments!" + str(path[2:]))
            logging.info("Import : ERROR too many arguments!" + str(path[2:]))
            sys.exit()
        cat_choice = ""
        if len(path) == 1 :
            cat_list = get_deck()
            cat_choice = input("Choose deck for the new entries: (default is 'None')\nDeck already found in db : " + str(cat_list) + "\n=> ")
        if len(path) == 2:
            cat_choice = path[1]
        if cat_choice == "" : # if user input is empty
            cat_choice == "None"
        fun_import_from_txt(filename, cat_choice)


    if args['rank'] != None:
        # python3 litoy main -r all rev -n 5
        logging.info("Ranks : Displaying ranks, arguments : " + str(args['rank']))
        condition=""
        if len(args['rank']) not in [0, 1, 2]:
            print("Invalid number of arguments : " + str(args['rank']))
            logging.info("Ranks : Invalid number of arguments : " + str(args['rank']))
            print("correct syntax : --rank FIELD r(everse)")
            sys.exit()

        if args['rank']==[] : proceed=True
        else : proceed=False

        if proceed==True or args['rank'][0] == "all" :
            logging.info("Ranks : Printing all entries\n")
            condition = "ID >= 0 ORDER BY ID"
        if condition=="" : # order by field 
             condition = "ID >= 0 ORDER BY " + str(args['rank'][0])
             logging.info("Ranks : Displaying by field " + str(args['rank'][0]))
        try :
            if str(args['rank'][1]) in "reverse":
                condition = condition + " DESC"
        except :
            condition = condition + " ASC"

        try :
            all_cards = fetch_entry(condition)
        except sqlite3.OperationalError :
            if " DESC" in condition :
                condition = "ID >=0 ORDER BY ID DESC"
            if " ASC" in condition :
                condition = "ID >=0 ORDER BY ID ASC"
            logging.info("Ranks : Field not found, using ID")
            print("Ranks : Field not found, using ID")
            all_cards = fetch_entry(condition)
        if len(all_cards)==0 :
            print("Ranks : No cards to display!\nEmpty db?")
            logging.info("Ranks : No cards to display!")
            sys.exit()

        try :
            limit = int(args['nlimit'][0])
        except TypeError:
            limit = int(args['nlimit'])
        if limit < 1:
            print('Ranks : Invalid limit number')
            logging.info('Ranks : Invalid limit number')
            sys.exit()
        else :
            logging.info("Ranks : Displaying only n=" + str(limit))
        all_cards = all_cards[:limit]
        logging.info("Ranks : No limit display")

        pprint.pprint(all_cards, compact=True)
        logging.info("Ranks : Done")

    if args['settings'] != None:
        logging.info('Settings : Change settings, arguments : ' + str(args['settings']))
        # read line by line the settings file
#        file = open("src/litoy/settings.py", "r")
#        for line in file:
#            if settings[0] in line.split(sep=" "):
#                print(line)
#        file.close() 
        logging.info("Settings : Done")

    if args['version'] != False:
        print("Version : Check out github at https://github.com/thiswillbeyourgithub/LiTOY/")
        logging.info("Version : Display version")
        sys.exit()

#    if args['ext'] != False:
#        print("External : Openning in sqlite browser")
#        logging.info("External : Openning in sqlite browser\n")


    if args['editEntry'] != None:
        if len(args['editEntry']) != 4 :
                print("Editentry : ERROR : needs 4 arguments\r    exiting")
                logging.info("Editentry : Entry edit error : needs 3 arguments, provided : " + str(args['editEntry']))
                sys.exit()
        editID = str(args['editEntry'][0])
        logging.info("Editentry : Editing entry, ID " + editID)
        editField = str(args['editEntry'][1])
        editValue = str(args['editEntry'][2])
        entry = fetch_entry("ID = " + editID)[0]
        entry[editField] = editValue
        if editField not in get_field_names():
            print("Editentry : You're not supposed to create new fields like that!")
            logging.info("Editentry : ERROR : trying to add a new field : " + editField)
            sys.exit()
        editPrevious = str(entry[editField])
        if editPrevious == editValue:
            print("Editentry : Not edited : values are identical")
            logging.info("Editentry : Not edited : values are identical")
            sys.exit()
        logging.info("Editentry : Changed field " + editField + " from value " + editPrevious + " to value " + editValue)
        print("Editentry : Changing field " + editField + " from value " + editPrevious + " to value " + editValue)
        push_dico(entry, "UPDATE")
        logging.info("Editentry : Done editing field\n")
        print("Editentry : Fresh entry :")
        print(entry)


    if args['consistency'] != False:
        check_db_consistency()









if __name__ == "__main__" :
    logging.basicConfig(level=logging.INFO,
            filename = 'debug.log',
            filemode='a',
            format='%(asctime)s: %(message)s')
    main()



