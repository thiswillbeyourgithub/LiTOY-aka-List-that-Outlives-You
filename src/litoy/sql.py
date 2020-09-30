#!/usr/bin/env python3

# This file contains functions related to the SQL db :

import sqlite3
import logging
import time


def create_table_in_db():
    logging.info("\n ## Creating table if not found in db \n")
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
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute(query_create_table)
    db.commit(); db.close()








def import_from_txt(filename, category) :
        db = sqlite3.connect('database.db') ; cursor = db.cursor()

        with open(filename) as f: # reads line by line
            content = f.readlines()
            content = [x.strip() for x in content] # removes \n character
            content = list(dict.fromkeys(content))

        # get a new and unused id for the new cards
        cursor.execute('''SELECT max(ID) FROM LiTOY''')
        newID = str(cursor.fetchone()[0])
        if newID == "None" :
            newID = "1"

        # importation
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
                            number_of_comparison, \
                            starred, \
                            category, \
                            disabled, \
                            done, \
                            K_value\
                            ) \
                            VALUES (" + newID + ", " + unixtime + ", \'" + entry + "\', 0, 0, 0, '" + str(category) + "', 0, 0" + K_values[0] + ")"
                    cursor.execute(query_create)
                    print(" ## Entry imported : '" + entry + "'")
                    logging.info(" ## Entry imported : '" + entry + "'")
                else :
                    print(" ## Entry already exists in db : '" + entry + "'")
                    logging.info(" ## Entry already exists in db : '" + entry + "'")
                newID = str(int(newID)+1)
        db.commit() ;  db.close()
        logging.info("Done importing\n")


def get_category() :
    logging.info("Getting category list...")
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    all_entries = fetch_entry("ID >= 0")
    cat_list = []
    for i in range(len(all_entries)):
        cat_list.append(all_entries[i]['category'])
    cat_list = list(set(cat_list))
    cat_list.sort()
    db.commit() ;   db.close()
    return cat_list

def get_field_names():
    logging.info("Getting field names")
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    entry = fetch_entry("ID = 1")
    db.commit() ; db.close()
    return entry[0].keys()




def update_delta(entry_id) :
    logging.info("Updating delta for entry id "+entry_id)
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    entry = fetch_entry("ID = "+entry_id)[0]

    # extract from the format score_score_score etc that is stored in each relevant score field
    correct_importance_delta = str(int(entry['importance_elo'].split(sep='_')[-1]) - int(entry['importance_elo'].split(sep='_')[-2]))
    correct_time_delta = str(int(entry['time_elo'].split(sep='_')[-1]) - int(entry['time_elo'].split(sep='_')[-2]))

    logging.info("current delta_imp:" + str(entry['delta_imp']) + " ; current delta_time:" + str(entry['delta_time'])) 
    entry['delta_time'] = correct_time_delta
    entry['delta_imp'] = correct_importance_delta
    logging.info("new delta_imp:"+entry['delta_imp'] + " ; new delta_time:" + entry['delta_time'])
    db.commit() ;   db.close()

    push_dico(entry, "UPDATE")
    logging.info("Done updating deltas")


def set_db_defaults_value():
    logging.info("Setting fields to their default value if needed :")
    all_entries = fetch_entry("ID >=0")
    for i,content in enumerate(all_entries) :
        one_entry = all_entries[i]
        if one_entry['importance_elo'] == "None":
            one_entry['importance_elo'] = "0"+default_score
        if one_entry['time_elo'] == "None":
            one_entry['time_elo'] = "0"+default_score
        if one_entry["done"] == "1" :
            one_entry["disabled"] = 1
        push_dico(one_entry, "UPDATE")
    logging.info("Done setting fields to default value\n")



def fetch_entry(condition):
    db = sqlite3.connect('database.db') ; cursor = db.cursor()
    logging.info("Fetching whole entry on condition:"+condition)
    cursor.execute('''SELECT * FROM LiTOY WHERE '''+condition)
    fetched_raw = cursor.fetchall()
    columns = cursor.description
    db.commit() ;   db.close()
    dictio = turn_into_dict(fetched_raw, columns)
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



