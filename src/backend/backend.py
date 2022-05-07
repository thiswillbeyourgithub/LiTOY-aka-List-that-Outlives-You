#!/usr/bin/env python3.9

from pathlib import Path
import time
from tqdm import tqdm
import pdb
from contextlib import suppress
import json
import re

from src.backend.util import format_length, InvalidTimestamp
from src.backend.media import (extract_youtube, extract_pdf_url,
                               extract_webpage, extract_local_video,
                               extract_pdf_local, extract_txt,
                               extract_epub)
from user_settings import (shortcuts, n_to_review, default_score, K_values)
from src.backend.scoring import (compute_global_score, expected_elo,
                                 update_elo, adjust_K)
from src.backend.log import log_


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
    match.extend(re.findall("set_length:[0-9jdhm]+", string))
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


def fetch_action(user_input):
    "find action from user input"
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


def action_star(entry_id, litoy):
    "stars an entry_id during review"
    df = litoy.df.copy()
    if df.loc[entry_id, "starred"] == 0:
        df.loc[entry_id, "starred"] = 1
    else:
        df.loc[entry_id, "starred"] = 0
    litoy.save_to_file(df)
    log_(f"Starred entry_id {entry_id}", False)


def action_disable(entry_id, litoy):
    "disables an entry during review"
    df = litoy.df.copy()
    assert str(df.loc[entry_id, "disabled"]) == "0"
    df.loc[entry_id, "disabled"] = 1
    litoy.save_to_file(df)
    log_(f"Disabled entry {entry_id}", False)


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
        for word in splitted:
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

                elif "epub" in part:
                    log_(f"Extracting epub from {part}")
                    res = extract_epub(part)
                    break

                elif ".pdf" in part:
                    log_(f"Extracting pdf from {part}")
                    res = extract_pdf_local(part)
                    break

                elif ".md" in part or ".txt" in part:
                    log_(f"Extracting text data from {part}")
                    res = extract_txt(part)
                    break

    set_length = re.findall(r"set_length:((?:\d+[djhm])+)", string)
    if set_length:
        try:
            new_length = format_length(set_length[0], to_machine_readable=True)
        except InvalidTimestamp as e:
            if str(e) == "skip":
                log_("Skipping", False)
        else:
            log_(f"Setting length to {set_length[0]}", False)
            res.update({"length": new_length})
    else:
        if "length" in res:
            log_(f"Detected length: {format_length(res['length'])}", False)

    if res == {}:
        log_(f"No metadata were extracted for {string}")

    return res


def process_review_answer(keypress, entry_left, entry_right, mode,
                          start_time, litoy):
    """
    after a comparison has been made, compute new values and store them etc
    """
    id_left = entry_left.name
    id_right = entry_right.name
    mapping = {"a": 1, "z": 2, "e": 3, "r": 4, "t": 5, "q": 1, "w": 2}

    if keypress in mapping:
        keypress = mapping[keypress]
    keypress = round(int(keypress) / 6 * 5, 2)  # resize value from 1-5 to 0-5
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

    litoy.df.loc[id_left, :] = eL_new
    litoy.df.loc[id_right, :] = eR_new
    litoy.save_to_file(litoy.df)

    log_(f"Done reviewing {id_left} and {id_right}")


def suggest_time_answer(entry_left, entry_right):
    """
    suggest best answer to time questions, numbers are in minutes
    """
    left_length = float(json.loads(entry_left["metacontent"])["length"])
    right_length = float(json.loads(entry_right["metacontent"])["length"])
    diff = abs(left_length - right_length)
    ratio = left_length / right_length

    log_(f"Ratio: {ratio}", False)

    if diff < 5:  # if difference less than 5 minutes
        return "3"

    if ratio >= 1.5:  # 6/2 or more
        return "5"
    if ratio > 1.25:  # 5/4
        return "4"
    if ratio <= 1.25 and ratio >= 0.75:  # 3/4 to 5/4
        return "3"
    if ratio >= 0.66:  # 2/4
        return "2"
    else:  # 1/4 or less
        return "1"
