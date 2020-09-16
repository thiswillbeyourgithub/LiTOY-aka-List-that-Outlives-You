#!/usr/bin/env python3

# This file contains functions related to the SQL db :

import sqlite3
import logging


def import_from_txt(filename, category) :
        with open(filename) as f: # reads line by line
            content = f.readlines()
            content = [x.strip() for x in content] # removes \n character
            content = list(dict.fromkeys(content))

        # get a new and unused id for the new cards
        cursor.execute(''' SELECT max(ID) FROM LiTOY ''')
        newID = str(cursor.fetchone()[0])
        if newID == "None" :
            newID = "1"

        # importation
        for entry in content :
                entry = entry.replace("'","`") # otherwise it messes with the SQL

                unixtime = str(int(time.time())) # creation date of the entry

                query_exists = "SELECT ID FROM LiTOY WHERE entry = '"+entry + "'"
                cursor.execute(query_exists)
                existence = "False"
                try :
                    existence = str(cursor.fetchone()[0])
                except :
                    existence = "False"
                if existence == "False" :
                    query_create = "INSERT INTO LiTOY(ID, date_added, entry, time_spent_comparing, number_of_comparison, starred, category, disabled, done, K_value) VALUES (" + newID + ", " + unixtime + ", \'" + entry + "\', 0, 0, 0, '" + str(category) + "', 0, 0" + K_values[0] + ")"
                    cursor.execute(query_create)
                    print(" ## Entry imported : '" + entry + "'")
                    logging.info(" ## Entry imported : '" + entry + "'")
                else :
                    print(" ## Entry already exists in db : '" + entry + "'")
                    logging.info(" ## Entry already exists in db : '" + entry + "'")
                newID = str( int(newID)+1)
        db.commit()
        db.close()
        logging.info("Done importing\n")

def get_category() : # tested OK
    logging.info("Getting category list...")
    db = sqlite3.connect('LiTOY.db') ; cursor = db.cursor()
    query_get_cat = "SELECT category FROM LiTOY"
    cursor.execute(query_get_cat)
    categories = cursor.fetchall()
    categories = list(set(categories)) # remove duplicates
    new_list = categories
    for i,t in enumerate(categories) :
        new_list[i] = str(t).replace(",", "")
    db.commit()
    db.close()
    logging.info("Done getting category list\n")
    return ' '.join(new_list)

def get_sql_value(variable="*", condition="") : # tested OK
    db = sqlite3.connect('LiTOY.db') ; cursor = db.cursor()
    if condition == "" : query_ending = ""
    else : query_ending = " WHERE " + condition
    query_get = "SELECT " + variable + " FROM LiTOY" + query_ending
    #print(query_get)
    cursor.execute(query_get)
    logging.info(str("SQL GET REQUEST : " + query_get))
    result = cursor.fetchall()
    if len(result) == 1 :
        result = result[0]
    db.commit()
    db.close()
    return result

def put_sql_value(which, variable, new_value) : #tested OK
    db = sqlite3.connect('LiTOY.db') ; cursor = db.cursor()
    query_put = "UPDATE LiTOY SET "+ variable + " = '" + new_value + "' WHERE " + which
    cursor.execute(query_put)
    logging.info(str("SQL PUT REQUEST : " + query_put))
    db.commit()
    db.close()

def update_delta(entry_id) : # Tested OK
    logging.info("Updating delta for entry id "+entry_id)
#    db = sqlite3.connect('LiTOY.db') ; cursor = db.cursor()
#    cursor.execute("SELECT id, importance_elo, time_elo from LiTOY WHERE id =" + str(entry_id))
#    result = cursor.fetchall()[0]
    result = get_sql_value("id, importance_elo, time_elo","id = " + str(entry_id[0]))
#    db.commit()
#    db.close()
    importance_delta = str(int(result[1].split(sep='_')[-1]) - int(result[1].split(sep='_')[-2]))
    time_delta = str(int(result[2].split(sep='_')[-1]) - int(result[2].split(sep='_')[-2]))

    current_imp_delta = str(get_sql_value("delta_imp", "id = "+entry_id))
    if current_imp_delta != importance_delta :
        put_sql_value("id = " + entry_id, "delta_imp", importance_delta)
    else : logging.info("Importance delta already up to date for id " + entry_id)
    current_time_delta = str(get_sql_value("delta_time", "id = "+entry_id))
    if current_time_delta != time_delta :
        put_sql_value("id = " + entry_id, "delta_time", time_delta)
    else : logging.info("Time delta already up to date for id " + entry_id)
    logging.info("Done updating deltas\n")

def set_db_defaults_value(): # tested OK
    logging.info("Setting fields to their default value if needed :")
    var = get_sql_value("id, importance_elo, time_elo, done", "id >= 0")
#    for i,content in enumerate(var) :
#        entry_id = str(var[i][0])
#        importance_elo = str(var[i][1])
#        time_elo = str(var[i][2])
#        done_field = str(var[i][3])
#        if time_elo == "None" :
#            put_sql_value("id = " + entry_id, "time_elo", "0_"+default_score)
#        if importance_elo == "None" :
#            put_sql_value("id = " + entry_id, "importance_elo", "0_"+default_score)
#        if done_field == "1" :
#            put_sql_value("id = " + entry_id, "disabled", "1")
    entry_id = str(var[0])
    importance_elo = str(var[1])
    time_elo = str(var[2])
    done_field = str(var[3])
    if time_elo == "None" :
        put_sql_value("id = " + entry_id, "time_elo", "0_"+default_score)
    if importance_elo == "None" :
        put_sql_value("id = " + entry_id, "importance_elo", "0_"+default_score)
    if done_field == "1" :
        put_sql_value("id = " + entry_id, "disabled", "1")

    logging.info("Done setting fields to default value\n")


