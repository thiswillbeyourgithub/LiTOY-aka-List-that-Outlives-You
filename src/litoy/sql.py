#!/usr/bin/env python3

# This file contains functions related to the SQL db :

import sqlite3
import logging
import time


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
    cat_list = list(set(cat_list)).sort()
    db.commit() ;   db.close()
    return cat_list



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
            #put_sql_value("id = " + entry_id, "disabled", "1")
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










################################################################# CODE GRAVEYARD
'''
#def get_category() : # tested OK #before using dictionnary
#    logging.info("Getting category list...")
#    open_db()
#    query_get_cat = "SELECT category FROM LiTOY"
#    cursor.execute(query_get_cat)
#    categories = cursor.fetchall()
#    categories = list(set(categories)) # remove duplicates
#    new_list = categories
#    for i,t in enumerate(categories) :
#        new_list[i] = str(t).replace(",", "")
#    close_db()
#    logging.info("Done getting category list\n")
#    return ' '.join(new_list)

#def get_sql_value(variable="*", condition="") : # tested OK
#    db = sqlite3.connect('database.db') ; cursor = db.cursor()
#    if condition == "" : query_ending = ""
#    else : query_ending = " WHERE " + condition
#    query_get = "SELECT " + variable + " FROM LiTOY" + query_ending
#    #print(query_get)
#    cursor.execute(query_get)
#    logging.info(str("SQL GET REQUEST : " + query_get))
#    result = cursor.fetchall()
#    if len(result) == 1 :
#        result = result[0]
#    db.commit()
#    db.close()
#    return result

#def put_sql_value(which, variable, new_value) : #tested OK
#    db = sqlite3.connect('database.db') ; cursor = db.cursor()
#    query_put = "UPDATE LiTOY SET "+ variable + " = '" + new_value + "' WHERE " + which
#    cursor.execute(query_put)
#    logging.info(str("SQL PUT REQUEST : " + query_put))
#    db.commit()
#    db.close()

#def update_delta(entry_id) : # Tested OK
#    logging.info("Updating delta for entry id "+entry_id)
##    db = sqlite3.connect('database.db') ; cursor = db.cursor()
##    cursor.execute("SELECT id, importance_elo, time_elo from LiTOY WHERE id =" + str(entry_id))
##    result = cursor.fetchall()[0]
#    result = get_sql_value("id, importance_elo, time_elo","id = " + str(entry_id[0]))
##    db.commit()
##    db.close()
#    importance_delta = str(int(result[1].split(sep='_')[-1]) - int(result[1].split(sep='_')[-2]))
#    time_delta = str(int(result[2].split(sep='_')[-1]) - int(result[2].split(sep='_')[-2]))
#
#    current_imp_delta = str(get_sql_value("delta_imp", "id = "+entry_id))
#    if current_imp_delta != importance_delta :
#        put_sql_value("id = " + entry_id, "delta_imp", importance_delta)
#    else : logging.info("Importance delta already up to date for id " + entry_id)
#    current_time_delta = str(get_sql_value("delta_time", "id = "+entry_id))
#    if current_time_delta != time_delta :
#        put_sql_value("id = " + entry_id, "delta_time", time_delta)
#    else : logging.info("Time delta already up to date for id " + entry_id)
#    logging.info("Done updating deltas\n")

#def set_db_defaults_value(): # tested OK
#    logging.info("Setting fields to their default value if needed :")
#    var = get_sql_value("id, importance_elo, time_elo, done", "id >= 0")
##    for i,content in enumerate(var) :
##        entry_id = str(var[i][0])
##        importance_elo = str(var[i][1])
##        time_elo = str(var[i][2])
##        done_field = str(var[i][3])
##        if time_elo == "None" :
##            put_sql_value("id = " + entry_id, "time_elo", "0_"+default_score)
##        if importance_elo == "None" :
##            put_sql_value("id = " + entry_id, "importance_elo", "0_"+default_score)
##        if done_field == "1" :
##            put_sql_value("id = " + entry_id, "disabled", "1")
#    entry_id = str(var[0])
#    importance_elo = str(var[1])
#    time_elo = str(var[2])
#    done_field = str(var[3])
#    if time_elo == "None" :
#        put_sql_value("id = " + entry_id, "time_elo", "0_"+default_score)
#    if importance_elo == "None" :
#        put_sql_value("id = " + entry_id, "importance_elo", "0_"+default_score)
#    if done_field == "1" :
#        put_sql_value("id = " + entry_id, "disabled", "1")
#
#    logging.info("Done setting fields to default value\n")

'''
