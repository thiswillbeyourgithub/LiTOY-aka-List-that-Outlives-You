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
            metadata TEXT,\
            starred INTEGER,\
            progress TEXT,\
            importance_elo TEXT,\
            date_importance_elo TEXT,\
            time_elo TEXT,\
            date_time_elo TEXT,\
            delta_importance INTEGER,\
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
    #db.commit(); db.close()

    # persistent settings and data :
    query_create_pers_sett_table = '\
            CREATE TABLE IF NOT EXISTS PERS_SETT(\
            date TEXT,\
            deck TEXT,\
            mode TEXT,\
            seq_delta TEXT,\
            who_fought_who TEXT\
            )'
    #logging.info("SQL CREATE REQUEST : " + query_create_pers_sett_table)
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute(query_create_pers_sett_table)
    db.commit(); db.close()
    logging.info("Done init table")



def fun_import_from_txt(filename, deck, tags) :
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
tags,\
disabled, \
K_value,\
progress,\
importance_elo,\
time_elo,\
global_score,\
date_importance_elo,\
date_time_elo,\
delta_importance,\
delta_time\
) \
VALUES (" + str(newID) + ", " + unixtime + ", \'" + entry + "\', 0, 0, 0, '" + str(deck) +"', '" + str(tags) + "', 0, " + str(K_values[0]) + " , '', " + str(default_score) + ", " + str(default_score) + ", '', " + unixtime + ", " + unixtime + ", " +str(default_score) + ", " + str(default_score) + ")"
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


def get_decks() :
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

def get_tags() :
    logging.info("Getting tag list : begin")
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    all_entries = fetch_entry("ID >= 0")
    tag_list = []
    for i in range(len(all_entries)):
        tag_list.append(all_entries[i]['tags'])
        if tag_list[-1] == None:
            tag_list[-1] = ""
    tag_list = list(set(tag_list))
    tag_list.sort()
    try :
        tag_list.remove("")
    except ValueError:
        pass
    db.commit() ;   db.close()
    logging.info("Getting tag list : done")
    return tag_list

def get_deck_delta(deck, mode):
    logging.info("Getting delta : begin")
    all_cards = fetch_entry("ID >=0 AND disabled = 0 AND deck is '" + str(deck) + "'")
    wholedelta = 0
    for i in all_cards:
        wholedelta += int(i["delta_"+str(mode)])
    return wholedelta
    logging.info("Getting delta : done")

def get_field_names():
    logging.info("Getting field names : begin")
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    entry = fetch_entry("ID = 1")
    db.commit() ; db.close()
    try :
        result = list(entry[0].keys())
    except :
        logging.info("No deck found")
        result = "None"
    logging.info("Getting field names : done")
    return result

def get_max_ID():
    logging.info("Getting maxID : begin")
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    cursor.execute('''SELECT MAX(ID) FROM LiTOY''')
    maxID = cursor.fetchone()[0]
    db.commit() ; db.close()
    try : # if None
        maxID = int(maxID)
    except : # then 0
        maxID = 0 
    logging.info("MaxID = " + str(maxID))
    logging.info("Getting maxIS : done")
    return maxID

def get_sequential_deltas(deck, mode):
    logging.info("Getting sequential deltas : begin")
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    cursor.execute('SELECT date, seq_delta FROM PERS_SETT WHERE mode IS "'+ mode +'"')
    delta_x_dates_raw = cursor.fetchall()
    columns = cursor.description
    db.commit() ; db.close()
    delta_x_dates = turn_into_dict(delta_x_dates_raw, columns)

    logging.info("Getting sequential deltas : delta")
    return delta_x_dates

def check_db_consistency():
    logging.info("Checking database consistency")
    compute_Global_score()
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
    logging.info("Fetching  : whole entry on condition : "+condition)
    queryFetch = 'SELECT * FROM LiTOY WHERE ' + str(condition)
    logging.info("Fetching : SQL : " + queryFetch)
    cursor.execute(queryFetch)
    fetched_raw = cursor.fetchall()
    columns = cursor.description
    db.commit() ;   db.close()
    dictio = turn_into_dict(fetched_raw, columns)
    logging.info("Fetching : Done")
    return dictio

def turn_into_dict(fetched_raw, columns=""):
    # https://stackoverflow.com/questions/28755505/how-to-convert-sql-query-results-into-a-python-dictionary
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    col_name = [col[0] for col in columns]
    fetch_clean = [dict(zip(col_name, row)) for row in fetched_raw]
    db.commit() ;   db.close()
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
        entry_id = dico['ID']
        for a,b in dico.items():
            query = query + str(a) + " = \'" + str(b) + "\', "
        query = query[0:len(query)-2] + " WHERE ID = " + str(entry_id) + " ;"
    logging.info("SQL push_dico:" + query)
    cursor.execute(query)
    db.commit() ;   db.close()
    logging.info('Pushing dictionnary : Done')

def push_persist_data(deck, mode, time, id1, id2, score):
    logging.info("Pushing persistent data  : begin")
    db = sqlite3.connect('database.db') ; cursor = db.cursor()

    delta_to_add = str(get_deck_delta(deck, mode))
    query_delta = "INSERT INTO PERS_SETT ( date, mode, deck, seq_delta, who_fought_who ) VALUES ( " + str(time) + ", '" + mode + "', '" + deck + "', " + delta_to_add + ", '" + id1+"_"+id2+":"+score + "')"
    #logging.info("SQL PUSH PERSI DATA : " + query_delta)
    cursor.execute(query_delta)
    db.commit() ; db.close()
    logging.info("Pushing persistent data : latest delta = " + delta_to_add)
    logging.info("Pushing persistent data : done")

