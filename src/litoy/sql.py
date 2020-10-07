#!/usr/bin/env python3

# This file contains functions related to the SQL db :

import sqlite3
import logging
import time
import sys
from   .settings   import *


def init_table():
    logging.info("Init table")
    query_create_table = '\
            CREATE TABLE IF NOT EXISTS LiTOY(\
            ID INTEGER,\
            date_added INTEGER,\
            entry TEXT,\
            deck TEXT,\
            tags TEXT,\
            details TEXT,\
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
            nb_of_fight INTEGER,\
            K_value INTEGER,\
            disabled INTEGER\
            )'
    #logging.info("SQL CREATE REQUEST : " + query_create_table)
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute(query_create_table)
    db.commit(); db.close()
    logging.info("Done init table")



def fun_import_from_txt(filename, deck) :
    logging.info("Importing from file")
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    with open(filename) as f: # reads line by line
        content = f.readlines()
        content = [x.strip() for x in content] # removes \n character
        content = list(dict.fromkeys(content))

    # importation
    newID = str(int(get_max_ID())+1)
    for entry in content :
            entry = entry.replace("'","`") # otherwise it messes with the SQL

            unixtime = str(int(time.time())) # creation date of the entry

            query_exists = "SELECT ID FROM LiTOY WHERE entry = '"+entry + "'"
            cursor.execute(query_exists)
            #existence = "False"
            try :
                existence = str(cursor.fetchone()[0])
            except :
                existence = "False"

            if existence == "False" :
                query_create = "INSERT INTO LiTOY(\
ID, \
date_added, \
entry, \
time_spent_comparing, \
nb_of_fight, \
starred, \
deck, \
disabled, \
K_value,\
progress,\
importance_elo,\
time_elo,\
global_score,\
date_importance_elo,\
date_time_elo,\
delta_imp,\
delta_time\
) \
VALUES (" + str(newID) + ", " + unixtime + ", \'" + entry + "\', 0, 0, 0, '" + str(deck) + "', 0, " + str(K_values[0]) + " , '', " + str(default_score) + ", " + str(default_score) + ", '', " + unixtime + ", " + unixtime + ", " +str(default_score) + ", " + str(default_score) + ")"
                logging.info("SQL REQUEST : " + query_create)
                cursor.execute(query_create)
                print("Entry imported : '" + entry + "'")
                logging.info("Entry imported : '" + entry + "'")
            else :
                print("Entry already exists in db : '" + entry + "'")
                logging.info("Entry already exists in db : '" + entry + "'")
            newID = str(int(newID)+1)
    db.commit() ;  db.close()
    logging.info("Done importing from file")


def get_deck() :
    logging.info("Getting deck list...")
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    all_entries = fetch_entry("ID >= 0")
    cat_list = []
    for i in range(len(all_entries)):
        cat_list.append(all_entries[i]['deck'])
    cat_list = list(set(cat_list))
    cat_list.sort()
    db.commit() ;   db.close()
    return cat_list

def get_field_names():
    logging.info("Getting field names...")
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    entry = fetch_entry("ID = 1")
    db.commit() ; db.close()
    try :
        result = list(entry[0].keys())
    except :
        logging.info("No deck found")
        result = "None"
    return result

def get_max_ID():
    logging.info("Getting max ID...")
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    cursor.execute('''SELECT MAX(ID) FROM LiTOY''')
    maxID = cursor.fetchone()[0]
    db.commit() ; db.close()
    try : # if None
        maxID = int(maxID)
    except : # then 0
        maxID = 0 
    logging.info("MaxID = " + str(maxID))
    return maxID


def check_db_consistency():
    logging.info("Checking database consistency")
    def print_check(id, fieldname, value, error) :
        msg = "CONSISTENCY ERROR : ID="+str(id) + ", "+str(fieldname) + "='"+str(value)+"' <= " + error
        print(msg)
        logging.info(msg)
    all_entries = fetch_entry("ID >=0")
    for i,content in enumerate(all_entries) :
        one_entry = all_entries[i]
        try : int(one_entry['importance_elo'])
        except : print_check(i, "importance_elo", one_entry['importance_elo'], "Not an int")
        try : int(one_entry['time_elo'])
        except : print_check(i, "time_elo", one_entry['time_elo'], "Not an int")
        try : int(one_entry['date_importance_elo'])
        except : print_check(i, "date_importance_elo", one_entry['date_importance_elo'], "Not an int")
        try : int(one_entry['date_time_elo'])
        except : print_check(i, "date_time_elo", one_entry['date_time_elo'], "Not an int")

        if one_entry['entry'] == "" :
            print_check(i, "entry", one_entry['entry'], "Empty entry")

        try : int(one_entry['date_time_elo'])
        except : print_check(i, "date_time_elo", one_entry['date_time_elo'], "Not an int")



        # check if doublon id ou doublon entry
        # check delta imp et time
        # check if starred pas 0 ou 1
        # check if date added int
        # check if number of dates correspond to fighting number
        # check if empty deck
        # check if global score not int
        # check time comparing
        # check nb of fight is int
        # check K value part of the setting
    logging.info("Done checking consistency")



def fetch_entry(condition):
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    logging.info("Fetching whole entry on condition : "+condition)
    queryFetch = 'SELECT * FROM LiTOY WHERE ' + str(condition)
    logging.info("SQL REQUEST : " + queryFetch)
    cursor.execute(queryFetch)
    fetched_raw = cursor.fetchall()
    columns = cursor.description
    db.commit() ;   db.close()
    dictio = turn_into_dict(fetched_raw, columns)
    logging.info("Done fetching Dictionnary")
    return dictio

def turn_into_dict(fetched_raw, columns=""):
    # https://stackoverflow.com/questions/28755505/how-to-convert-sql-query-results-into-a-python-dictionary
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    col_name = [col[0] for col in columns]
    fetch_clean = [dict(zip(col_name, row)) for row in fetched_raw]
    db.commit() ;   db.close()
    logging.info("Turned sql result into dictionnary")
    return fetch_clean

def push_dico(dico, mode):
    # https://blog.softhints.com/python-3-convert-dictionary-to-sql-insert/
    logging.info('Pushing dictionnary : ' + str(dico) + " ; mode = " + str(mode))
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    if mode == "INSERT" :
        columns = ', '.join("`" + str(x).replace('/', '_') + "`" for x in dico.keys())
        values = ', '.join("'" + str(x).replace('/', '_') + "'" for x in dico.values())
        query = "INSERT INTO LiTOY ( %s ) VALUES ( %s );" % (columns, values)
    if mode == "UPDATE" :
        query = "UPDATE LiTOY SET "
        entry_id = dico.pop('ID')
        for a,b in dico.items():
            query = query + str(a) + " = \'" + str(b) + "\', "
        query = query[0:len(query)-2] + " WHERE ID = " + str(entry_id) + " ;"
    logging.info("SQL push_dico:" + query)
    cursor.execute(query)
    db.commit() ;   db.close()
    logging.info('Done pushing dictionnary')



