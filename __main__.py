#!/usr/bin/env python3

import time
import random
import pyfiglet
import sqlite3
import logging
import os

import src.litoy.sql
import src.litoy.elo
import src.litoy.functions
import settings



##################################### Main :
###################### initialization :

def main() :
    if os.path.exists('database.db'):
        logging.info("\n## db found\n")
        db = sqlite3.connect('database.db')
    else:
        logging.info("\n## db NOT found\n")
        sys.exit()
    cursor = db.cursor()

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


    while True :
        import_bool =  input("\nDo you want to import new entries from a file? (y/n)\n=> ")
        if import_bool == "y":
            category_list = get_category()
            cat_choice = input("Specify category for the new entries? (default is 'None')\nCategories already found in db : " + category_list + "\n=> ")
            if cat_choice == "" :
                cat_choice = "None"
            filename = input("\nWhat is the name of the file containing the new entries? Press Enter to use default file (new_entry.txt)\n(remember to put it in the same folder!)\n=> ")
            if filename == "" :
                filename = "new_entry.txt"
            print("\n ## Importing from " + filename + "...\n")
            logging.info("\n ## Importing from " + filename + "...\n")
            import_from_txt(filename, cat_choice)
        else :
            print("\n ## No importation to do\n")
            logging.info("\n ## No importation to do\n")
            break

    set_db_defaults_value()

    # sets all deltas just in case
    all_ids = get_sql_value("id")
    logging.info("Batch updating all deltas")
    for i in all_ids:
        i = list(i)[0]
        update_delta(str(i))
    logging.info("Done batch updating all deltas\n")


    print(" ## End of initialization\n\n")
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    print("#######################################################")
    print("#######################################################")
    print("                                                       ")
    #print(pyfiglet.figlet_format("LiTOY",font = "slant"))
    #print("~List That Outlives You.~                ")
    print(pyfiglet.figlet_format("List That Outlives You.",font = "slant"))
    print("                                                       ")
    print("#######################################################")
    print("#######################################################")
    print("\n\n\n\n\n\n\n\n\n\n\n")



    ###################### main loop :

    while 1==1:
        type_of_fight = input("Select mode:\nt = Compare time\ni = Compare importance\n\n\nYour choice => ")
        if type_of_fight !="i" and type_of_fight != "t" :
            print("Incorrect choice\n\n")
            continue
        fighters = choose_fighting_entries(type_of_fight)
        print("\n")
        print("#######################")
        print_entry(fighters[0])
        print("#######################")
        print_entry(fighters[1])
        print("\n\n")
        if type_of_fight == "t":
            user_input = input(question_time + "\n=>")
        if type_of_fight == "i":
            user_input = input(question_importance + "\n=>")
        shortcut_reaction(user_input,type_of_fight, fighters)
        break


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
