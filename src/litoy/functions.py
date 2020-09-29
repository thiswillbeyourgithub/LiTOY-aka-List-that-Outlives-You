#!/usr/bin/env python3

import logging

# This file contains general functions used in the main loop :

def print_entry(entry_id):
    #entry_fields = get_sql_value("*","id = " + str(entry_id))
    entry_fields = fetch_entry("ID = " + entry_id)
    print ("Category : " + str(entry_fields['category']))
    print ("Entry : " + str(entry_fields['entry']))
    if entry_fields['details'] != "None" : print ("Details : " + str(entry_fields['details']))
    if entry_fields['progress'] != "None" :     print ("Progress : " + str(entry_fields['progress']))
    #print ("Importance Elo : " + str(entry_fields['importance_elo']))
    #print ("Time Elo : " + str(entry_fields['time_elo']))

def print_entry_all_fields(entry_id):
    #entry_fields = get_sql_value("*","id = " + str(entry_id))
    entry_fields = fetch_entry("ID = " + entry_id)
    print(entry_fields)
#    for i,f in enumerate(entry_fields):
#        print(str(i) + " ___ " + str(f))


def choose_fighting_entries(mode, condition=""): # tested seems OK
    condition = "disabled IS 0 AND " + condition
    all_ids_deltas_dates = get_sql_value("id, delta_imp, delta_time, date_importance_elo, date_time_elo, disabled",condition)
    if mode == "i" : mode = 1
    if mode == "t" : mode = 2
    all_ids_deltas_dates = list(all_ids_deltas_dates)
    #print(all_ids_deltas_dates)
    all_ids_deltas_dates.sort(reverse=True, key=lambda x : x[mode])
    highest_5_deltas = all_ids_deltas_dates[0:5]
    choice1 = random.choice(highest_5_deltas)
    randomness = random.random()
    if randomness > choice_threshold :
        while 1==1 :
            choice2 = random.choice(all_ids_deltas_dates)
            if choice2[0] == choice1[0]:
                print("Re choosing : selected the same entry")
                continue
            break
    else :
        print("Choosing the oldest seen entry")
        logging.info("Choosing the oldest seen entry")
        while 1==1 :
            all_ids_deltas_dates.sort(reverse=False, key=lambda x : str(x[mode+2]).split(sep="_")[-1])
            choice2 = all_ids_deltas_dates[0]
            while choice2[0] == choice1[0]:
                print("Re choosing : selected the same entry")
                choice1 = random.choice(highest_5_deltas)
            break
    return [choice1[0], choice2[0]]

def shortcut_reaction(key, mode, fighters):
    def get_key(val): 
        for key, value in my_dict.items(): 
             if val == value: 
                 return key 

    while 1==1 :
        logging.info("User types =>" + key)
        pass
        if key not in shortcut.values() :
            print("Error : key not found : " + key)
            logging.info("Error : key not found : " + key)
            continue
        action = get_key(key)
        if action == "answer_level" :
            cur_elo1 = get_sql_value("importance_elo, date_importance_elo, time_elo, date_time_elo", "id = "+fighters[0])
            cur_elo2 = get_sql_value("importance_elo, date_importance_elo, time_elo, date_time_elo", "id = "+fighters[1])
            cur_K_1 = get_sql_value("K", "id = "+fighters[0])
            cur_K_2 = get_sql_value("K", "id = "+fighters[1])


            new_elo1 = update_elo(cur_elo1, expected(cur_elo1, cur_elo2), int(key), cur_K_1)
            new_elo2 = update_elo(cur_elo2, expected(cur_elo2, cur_elo1), int(key), cur_K_2)
        break

