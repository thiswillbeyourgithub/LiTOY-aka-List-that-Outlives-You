#!/usr/bin/env python3.9

import sys
from pprint import pprint
from pathlib import Path
import time
from tqdm import tqdm
import pdb
from contextlib import suppress
import json
import webbrowser
import platform
import subprocess
import os
import re
import prompt_toolkit
from pygments.lexers import JavascriptLexer

from src.backend.util import prompt_we, format_length
from src.backend.media import (extract_youtube, extract_pdf_url,
                               extract_webpage, extract_local_video,
                               extract_pdf_local, extract_txt)
from user_settings import (shortcuts, n_to_review, default_score, K_values,
                           col_red, col_rst, n_session, questions)
from src.cli.cli import print_2_entries
from src.backend.scoring import (compute_global_score, expected_elo,
                                 update_elo, adjust_K)
from src.backend.log import log_


def DB_file_check(path):
    "Check if the file and database already exists, if not create the file"
    db_location = Path(path)
    if db_location.exists():
        log_(f"Database file found at {path}")
        try:
            return True
        except ValueError as e:
            log_(f"ERROR: Litoy database not found in file at {path} :\
{e}", False)
            return False
    else:
        answer = input(f"No database file found at {path}, do you want me to\
 create it?\ny/n?")
        if answer in ["y", "yes"]:
            db_location.touch()
            return False
        else:
            print("Exiting")
            raise SystemExit()


def importation(path, litoy):
    "Check if text file exists then import it into LiTOY"
    import_file = Path(path)
    if not import_file.exists():
        log_(f"ERROR: Import file not found at {path}, exiting", False)
        raise SystemExit()
    log_(f"Importing from file {path}", False)
    with import_file.open() as f:
        lines = f.readlines()
    lines = [li for li in lines if not str(li).startswith("#") and
             str(li) != "" and str(li) != "\n"]
    for line in tqdm(lines, desc="Processing line by line", unit="line",
                     ascii=False, dynamic_ncols=True, mininterval=0):
        line = line.strip()
        line = line.replace("\n", "")
        metacontent = get_meta_from_content(line)
        if not litoy.entry_duplicate_check(litoy.df, line, metacontent):
            line = move_flags_at_end(line)
            add_new_entry(litoy, line, metacontent)


def move_flags_at_end(string):
    """
    used to turn 'do something tags:reading it's important' to
    'do something it's important tags:reading
    """
    match = re.findall(r"tags:\w+", string)
    match.extend(re.findall("set_length:[0-9jhm]+", string))
    if "" in match:
        match.remove("")
    for m in match:
        string = string.replace(m, "")
    string += f" {' '.join(match)}"
    string = " ".join(string.split())
    return string.strip()


def add_new_entry(litoy, content, metacontent):
    "Add a new entry to the pandas dataframe"
    df = litoy.df
    tags = get_tags_from_content(content)

    # in case metacontent doesn't contain those keys, ignore exceptions:
    with suppress(KeyError, TypeError):
        # if url not working, reload it after 5 seconds :
        if "forbidden" in str(metacontent['title']).lower() or \
                "404" in str(metacontent['title']).lower() or\
                "403" in str(metacontent['title']).lower():
            log_(f"Waiting 5 seconds because apparent webpage loading limit \
 was reached while inspecting line : {content}", False)
            time.sleep(5)
            metacontent = get_meta_from_content(content)
        # if wayback machine was used : mention it in the tags
        if metacontent['wayback_used'] == "1":
            tags.append("wayback_machine")
        elif metacontent['wayback_machine'] == "wayback url not found":
            tags.append("url_not_found")
        metacontent.pop("wayback_used")

    try:
        newID = max(df.index) + 1
    except ValueError:  # first card
        newID = 1
    new_dic = {"date": str(int(time.time())),
               "content": content,
               "metacontent": json.dumps(metacontent),
               "tags": json.dumps(sorted(tags)),
               "iELO": default_score,
               "tELO": default_score,
               "DiELO": default_score,
               "DtELO": default_score,
               "gELO": compute_global_score(),
               "review_time": 0,
               "n_review": 0,
               "K": sorted(K_values)[-1],
               "starred": 0,
               "disabled": 0,
               }
    log_(f"Adding new entry # {newID} : {new_dic}")
    for k, v in new_dic.items():
        df.loc[newID, k] = v
    litoy.save_to_file(df)
    return newID


def pick_entries(df):
    """
    Pick entries for the reviews : the left one is chosen randomly
    among the 5 with the highest pick_factor, then n_to_review other entries
    are selected at random among the half with the highest pick factor.
    Note: the pick_score goes down fast.
    """
    df = df.loc[df.disabled == 0].copy()
    df["pick_score"] = df.loc[:, "DiELO"].values + df.loc[:, "DtELO"]
    df.sort_values(by="pick_score", axis=0, ascending=False, inplace=True)

    left_choice_id = df.iloc[0:10].sample(1).index[0]

    df_h = df.iloc[0: int(len(df.index) / 2), :]
    right_choice_id = df_h.sample(min(n_to_review, len(df_h.index))).index

    picked_ids = [int(left_choice_id)]
    picked_ids.extend(right_choice_id)

    cnt = 0
    while picked_ids[0] in picked_ids[1:]:
        cnt += 1
        if cnt > 50:
            log_("Seem to be stuck in an endless loop. Openning debugger",
                 False)
            pdb.set_trace()
        log_("Picking entries one more time to avoid reviewing to itself",
             False)
        picked_ids = pick_entries(df)
    return picked_ids


def shortcut_and_action(id_left, id_right, mode, progress, litoy,
                        shortcut_auto_completer, available_shortcut,
                        cli=True):
    """
    makes the link between keypresses and actions
    shortcuts are stored at the top of the file
    """
    if cli:
        pass
    else:
        pass

    def fetch_action(user_input):
        "deduce action from user keypress"
        found = ""
        for action, keypress in shortcuts.items():
            if str(user_input) in keypress:
                if found != "":
                    log_("ERROR: Several corresponding shortcuts found! \
Quitting.", False)
                    raise SystemExit()
                found = action
        if action == "":
            log_(f"ERROR: No {str(user_input)} shortcut found", False)
            action = "show_help"
        return found

    def star(entry_id):
        "stars an entry_id during review"
        df = litoy.df.copy()
        df.loc[entry_id, "starred"] = 1
        litoy.save_to_file(df)
        log_(f"Starred entry_id {entry_id}", False)

    def disable(entry_id):
        "disables an entry during review"
        df = litoy.df.copy()
        assert str(df.loc[entry_id, "disabled"]) == "0"
        df.loc[entry_id, "disabled"] = 1
        litoy.save_to_file(df)
        log_(f"Disabled entry {entry_id}", False)

    def edit(entry_id):
        "edit an entry during review"
        log_(f"Editing entry {entry_id}")
        df = litoy.df

        # tags completion
        cur_tags = litoy.get_tags(litoy.df)
        autocomplete_list = ["tags:"+tags for tags in cur_tags] + ["set_length:"]
        auto_complete = prompt_toolkit.completion.WordCompleter(autocomplete_list,
                              match_middle=True,
                              ignore_case=True,
                              sentence=False)


        field_list = list(df.columns)
        field_auto_completer = prompt_toolkit.completion.WordCompleter(field_list, sentence=True)
        while True:
            entry = df.loc[entry_id, :]
            print(f"Fields available for edition : {field_list}")
            chosenfield = prompt_we("What field do you want to edit? \
(q to exit)\n>", completer=field_auto_completer)
            if chosenfield == "q" or chosenfield == "quit":
                break
            elif chosenfield == "metacontent":
                additional_args = {"lexer": prompt_toolkit.lexers.PygmentsLexer(JavascriptLexer)}
            elif chosenfield == "content":
                additional_args = {"completer": auto_complete}
            elif chosenfield == "tags":
                print(col_red + "You can't edit tags this way, you \
have to enter them in the 'content' field." + col_rst)
                time.sleep(1)
                continue
            else:
                additional_args = {}

            if str(chosenfield) not in entry.keys():
                log_("ERROR: Shortcut : edit : wrong field name", False)
                continue

            old_value = str(entry[chosenfield])

            new_value = str(prompt_we("Enter the desired new value \
for  field '" + chosenfield + "'\n>",
                            default=old_value,
                            **additional_args))
            if chosenfield == "content":
                new_value = move_flags_at_end(new_value)
                df.loc[entry_id, "metacontent"] = json.dumps(get_meta_from_content(new_value))
                df.loc[entry_id, "tags"] = json.dumps(sorted(get_tags_from_content(new_value)))
            df.loc[entry_id, chosenfield] = new_value
            litoy.save_to_file(df)
            log_(f'Edited field "{chosenfield}":\n* {old_value}\nbecame:\n* \
{new_value}', False)
            break

    action = ""
    while True:

        entry_left = litoy.df.loc[id_left, :]
        entry_right = litoy.df.loc[id_right, :]
        log_(f"Waiting for shortcut for {id_left} vs {id_right} for {mode}")

        start_time = time.time()
        action = ""
        log_(f"Asking question, mode : {mode}")
        prompt_text = f"{progress}/{n_to_review*n_session} {questions[mode]} \
(h or ? for help)\n>"

        meta_left = json.loads(entry_left["metacontent"])
        if "length" not in meta_left.keys():
            log_("Asking user to complete length.")
            input_length = prompt_we("No length specified for left entry.\n\
Enter the amount of time you expect it will take: (q)\n>")
            if input_length != "q":
                formatted = format_length(input_length, to_machine_readable=True)

            meta_left["length"] = formatted
            litoy.df.loc[id_left, "metacontent"] = json.dumps(meta_left)
            litoy.save_to_file(litoy.df)
            entry_left = litoy.df.loc[id_left, :]
        meta_right = json.loads(entry_right["metacontent"])
        if "length" not in meta_right.keys():
            log_("Asking user to complete length.")
            input_length = prompt_we("No length specified for right entry.\n\
Enter the amount of time you expect it will take: (q)\n>")
            if input_length != "q":
                formatted = format_length(input_length, to_machine_readable=True)

            meta_right["length"] = formatted
            litoy.df.loc[id_right, "metacontent"] = json.dumps(meta_right)
            litoy.save_to_file(litoy.df)
            entry_right = litoy.df.loc[id_right, :]

        def_time_ans = ""
        if mode == "time":
            # auto answers time questions
            left_length = float(json.loads(entry_left["metacontent"])["length"])
            right_length = float(json.loads(entry_right["metacontent"])["length"])
            ratio = left_length / right_length
            if ratio > 2:
                def_time_ans = "1"
            elif ratio > 1.5:
                def_time_ans = "2"
            elif ratio > 0.65:
                def_time_ans = "3"
            elif ratio > 0.5:
                def_time_ans = "4"
            else:
                def_time_ans = "5"

        keypress = prompt_we(prompt_text,
                             completer=shortcut_auto_completer,
                             default=def_time_ans)

        if keypress not in available_shortcut:
            log_(f"ERROR: keypress not found : {keypress}")
            action = "show_help"
        else:
            action = str(fetch_action(keypress))
            log_(f"Shortcut found : Action={action}")

        if action == "answer_level":  # where the actual review takes place
            if keypress == "a":
                keypress = 1
            if keypress == "z":
                keypress = 2
            if keypress == "e":
                keypress = 3
            if keypress == "r":
                keypress = 4
            if keypress == "t":
                keypress = 5
            keypress = round(int(keypress) / 6 * 5, 2)
            # resize value from 1-5 to 0-5
            date = time.time()
            assert entry_left["disabled"] == 0 and entry_right["disabled"] == 0

            eL_old = entry_left
            eR_old = entry_right
            eL_new = eL_old.copy()
            eR_new = eR_old.copy()

            if mode == "importance":
                elo_fld = "iELO"
                Delo_fld = "DiELO"
            else:
                elo_fld = "tELO"
                Delo_fld = "DtELO"
            eloL = int(eL_old[elo_fld])
            eloR = int(eR_old[elo_fld])

            eL_new[elo_fld] = update_elo(eloL, expected_elo(eloL, eloR),
                                         round(5 - keypress, 2), eL_old.K)
            eR_new[elo_fld] = update_elo(eloR, expected_elo(eloL, eloR),
                                         keypress, eR_old.K)
            log_(f"Elo: L: {eloL}=>{eL_new[elo_fld]} R: \
{eloR}=>{eR_new[elo_fld]}")

            eL_new["K"] = adjust_K(eL_old.K)
            eR_new["K"] = adjust_K(eR_old.K)
            eL_new[Delo_fld] = abs(eL_new[elo_fld] - eL_old[elo_fld])
            eR_new[Delo_fld] = abs(eR_new[elo_fld] - eR_old[elo_fld])
            eL_new["gELO"] = compute_global_score(eL_new.iELO, eL_new.tELO, 1)
            eR_new["gELO"] = compute_global_score(eR_new.iELO, eR_new.tELO, 1)
            eL_new["review_time"] = round(eL_new["review_time"] + min(date
                                          - start_time, 30), 3)
            eR_new["review_time"] = round(eR_new["review_time"] + min(date
                                          - start_time, 30), 3)
            eL_new["n_review"] += 1
            eR_new["n_review"] += 1

            df = litoy.df.copy()
            df.loc[id_left, :] = eL_new
            df.loc[id_right, :] = eR_new
            litoy.save_to_file(df)
            log_(f"Done reviewing {id_left} and {id_right}")
            break

        if action == "skip_review":
            log_("Skipped review", False)
            break

        if action == "show_all_fields":
            log_("Displaying the entries in full")
            print("\n" * 10)
            print_2_entries(int(id_left), int(id_right), mode, litoy, "all")
            continue

        if action == "show_few_fields":
            log_("Displaying only most important fields of entries")
            print("\n" * 10)
            print_2_entries(int(id_left), int(id_right), mode, litoy)
            continue

        if action == "open_media":
            log_("Openning media")
            for ent_id in [id_left, id_right]:
                ent = litoy.df.loc[ent_id, :]
                try:
                    path = str(json.loads(ent.metacontent)["url"])
                    if "http" in path:
                        webbrowser.open(path)
                    else:
                        if platform.system() == "Linux":
                            subprocess.Popen(["xdg-open", path],
                                             stdout=open(os.devnull, 'wb'))
                        elif platform.system() == "Windows":
                            os.startfile(path)
                        elif platform.system() == "Darwin":
                            subprocess.Popen(["open", path])
                        else:
                            log_("Platform system not found.", False)
                except (KeyError, AttributeError) as e:
                    log_(f"url not found in entry {ent_id} : {e}")
            time.sleep(1.5)  # better display
            print("\n" * 10)
            print_2_entries(int(id_left),
                            int(id_right),
                            mode=mode,
                            litoy=litoy)
            continue

        if action == "reload_media" or action == "reload_media_fallback_method":
            log_("Reloading media")
            additional_args = {}
            if action == "reload_media_fallback_method":
                additional_args.update({"fallback_method": True})
            for ent_id in [id_left, id_right]:
                df = litoy.df.copy()
                df.loc[ent_id, "content"] = move_flags_at_end(df.loc[ent_id,
                                                                     "content"])
                new_meta = get_meta_from_content(df.loc[ent_id, :]["content"],
                                                 additional_args)
                df.loc[ent_id, "metacontent"] = json.dumps(new_meta)
                litoy.save_to_file(df)
                entry_left = df.loc[id_left, :]
                entry_right = df.loc[id_right, :]
                log_(f"New metacontent value for {ent_id} : {new_meta}")
            print("\n" * 10)
            print_2_entries(int(id_left),
                            int(id_right),
                            mode=mode,
                            litoy=litoy)
            continue

        if action == "open debugger":
            log_("Openning debugger", False)
            print("To open a python console within the debugger, type in \
'interact'. You can load the database as a pandas DataFrame using df=litoy.df")
            pdb.set_trace()
            continue

        if action == "edit_left":
            edit(id_left)
            print_2_entries(id_left, id_right, mode=mode, litoy=litoy)
            continue
        if action == "edit_right":
            edit(id_right)
            print_2_entries(id_left, id_right, mode=mode, litoy=litoy)
            continue
        if action == "star_left":
            star(id_left)
            continue
        if action == "star_right":
            star(id_right)
            continue
        if action == "disable_left":
            disable(id_left)
            return action
        if action == "disable_both":
            disable(id_right)
            disable(id_left)
            return action
        if action == "disable_right":
            disable(id_right)
            return action

        if action == "undo":
            print("Undo function is not yet implemented, \
  manually correct the database using libreoffice calc after looking at \
  the logs. Or take a look at the saved json files")
            input("(press enter to resume reviewing session)")
            continue

        if action == "show_help":
            log_("Printing help :", False)
            pprint(shortcuts)
            continue

        if action == "repick":
            log_("Repicking entries", False)
            return "repick"

        if action == "quit":
            log_("Shortcut : quitting")
            print("Quitting.")
            raise SystemExit()


def get_tags_from_content(string):
    "extracts tags from a line in the import file"
    splitted = string.split(" ")
    result = []
    for word in splitted:
        if word.startswith("tags:"):
            temp = str(word[5:])
            # removes non letter from tags, usually ,
            while not temp.replace("_", "").replace("-", "").isalnum():
                temp = temp[:-1]
            result.append(temp)
    return list(set(result))


def get_meta_from_content(string, additional_args=None):
    """
    extracts all metadata from a line in the import file
    this does not include tags, which are indicated using tags:sometag in the
    line. Instead it's for example the length of a youtube video which link
    appears in the content.
    If several links are supplied, only the first one will be used
    """
    if additional_args is None:
        additional_args = {}
    with suppress(UnboundLocalError, NameError):
        global last
        since = time.time() - last
        last = time.time()
        if since < 2:
            log_(f"Sleeping for {2-since} seconds", False)
            time.sleep(2 - since)

    splitted = string.split(" ")
    res = {}
    if "type:video" in string:  # this forces to analyse as a video
        for w in splitted:
            if word.startswith("http") or word.startswith("www."):
                log_(f"Extracting info from video {word}")
                res = extract_youtube(word)
                

    elif "type:local_video" in string:  # fetch local video files
        for part in string.split("\""):
            if "/" in part:
                log_(f"Extracting info from local video {part}")
                res = extract_local_video(part)

    else:
        for word in splitted:
            if word.startswith("http") or word.startswith("www."):
                if "ytb" in word or "youtube" in word:
                    log_(f"Extracting info from video {word}")
                    res = extract_youtube(word)
                    break

                elif word.endswith(".pdf"):
                    log_(f"Extracting pdf from {word}")
                    res = extract_pdf_url(word)
                    break

                else:
                    log_(f"Extracting text from webpage {word}")
                    res = extract_webpage(word, **additional_args)
                    break

    if res == {}:
        if "/" in string:  # might be a link to a file
            for part in string.split("\""):
                if ".mp4" in part or\
                        ".mov" in part or\
                        ".avi" in part or\
                        ".webm" in part:
                    if "/" in part:
                        log_(f"Extracting info from local video {part}")
                        res = extract_local_video(part)
                        break

                elif ".pdf" in part:
                    log_(f"Extracting pdf from {part}")
                    res = extract_pdf_local(part)
                    break

                elif ".md" in part or ".txt" in part:
                    log_(f"Extracting text data from {part}")
                    res = extract_txt(part)
                    break

    set_length = re.findall(r"set_length:((?:\d+[jhm])+)", string)
    if set_length:
        new_length = format_length(set_length[0], to_machine_readable=True)
        log_(f"Setting length to {set_length[0]}", False)
        res.update({"length": new_length})

    if res == {}:
        log_(f"No metadata were extracted for {string}")

    return res
