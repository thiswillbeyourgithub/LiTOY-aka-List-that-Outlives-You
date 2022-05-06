#!/usr/bin/env python3.9
import time
import pandas as pd
import random
from pprint import pprint
import json
from prettytable import PrettyTable
from statistics import mean, stdev, median, StatisticsError
import prompt_toolkit
from pygments.lexers import JavascriptLexer
import webbrowser
import platform
import subprocess
import os
import pdb
from itertools import chain

from src.backend.backend import (get_meta_from_content,
                                 get_tags_from_content,
                                 move_flags_at_end,
                                 fetch_action,
                                 action_disable,
                                 action_star,
                                 process_review_answer,
                                 suggest_time_answer,
                                 pick_entries
                                 )
from src.backend.util import format_length, prompt_we, InvalidTimestamp
from src.backend.log import log_
from user_settings import (shortcuts, n_to_review, n_session, questions,
                           useless_last_years, useless_first_years,
                           user_life_expected, user_age, disable_lifebar,
                           col_red, col_gre, col_yel, col_rst, col_mgt_fg,
                           col_blink, col_bold, col_uline, spacer, col_blu)
from src.cli.get_terminal_size import get_terminal_size


def display_2_entries(id_left, id_right, mode, litoy, all_fields=False, cli=True):
    """
    Show the two entries to review side by side
    This function is actually part CLI but is highjacked by the GUI to
    easily extract all the information to show to the user in two columns
    """

    if cli:
        global sizex, sizey
        (sizex, sizey) = get_terminal_size()  # dynamic sizing
        side_by_side = print_side_by_side
        def cli_p(string):
            print(string)

    else:  # highjacking this function to get all the values to print
        sizex = sizey = 1
        def cli_p(string):
            pass

        pile = []
        def side_by_side(key, val1, val2):
            pile.append([key, [val1, val2]])
    cli_p("\n"*10)


    cli_p(col_blu + "#" * sizex + col_rst)
    if cli:
        print_memento_mori()
    cli_p(col_blu + "#" * sizex + col_rst)

    entry_left = litoy.df.loc[id_left, :].copy()
    entry_right = litoy.df.loc[id_right, :].copy()

    if all_fields != "all":
        side_by_side("ID", id_left, id_right)
        cli_p("." * sizex)

        if "".join(entry_left.tags + entry_right.tags) != "":
            tag_left = ', '.join(json.loads(entry_left.tags))
            tag_right = ', '.join(json.loads(entry_right.tags))
            side_by_side("Tags", tag_left, tag_right)
        if int(entry_left.starred) + int(entry_right.starred) != 0:
            side_by_side("Starred", entry_left.starred, entry_right.starred,
                         col=col_yel)

        side_by_side("iELO", entry_left.iELO, entry_right.iELO)
        side_by_side("tELO", entry_left.tELO, entry_right.tELO)
        side_by_side("K factor", entry_left.K, entry_right.K)
        cli_p("." * sizex)
        side_by_side("Entry", entry_left.content, entry_right.content)

    # print all fields, useful for debugging
    if all_fields == "all":
        for c in litoy.df.columns:
            side_by_side(str(c), str(entry_left[c]), str(entry_right[c]))

    # metadata :
    js = []
    js.append(json.loads(entry_left.metacontent))
    js.append(json.loads(entry_right.metacontent))
    for x in [0, 1]:
        for y in ["length", "title", "url", "type", "channel"]:
            if y not in js[x]:
                js[x][y] = "X"
            else:
                js[x][y] == str(js[x][y])
    cli_p("." * sizex)
    if (js[0]["title"] + js[1]["title"]) != "XX":
        side_by_side("Title", js[0]["title"], js[1]["title"])
    if (str(js[0]["length"]) + str(js[1]["length"])) != "XX":
        timestamps = []
        try:
            if js[0]["length"] == "X":
                timestamps.append("X")
            else:
                timestamps.append(format_length(js[0]["length"]))
        except InvalidTimestamp as e:
            timestamps.append("Error")
        try:
            if js[1]["length"] == "X":
                timestamps.append("X")
            else:
                timestamps.append(format_length(js[1]["length"]))
        except InvalidTimestamp as e:
            timestamps.append("Error")
        side_by_side("Length", timestamps[0], timestamps[1])
        cli_p("." * sizex)
    if (js[0]["url"] + js[1]["url"]) != "XX":
        side_by_side("Location", js[0]["url"], js[1]["url"])
    if (js[0]["channel"] + js[1]["channel"]) != "XX":
        side_by_side("Channel", js[0]["channel"], js[1]["channel"])
    if (js[0]["type"] + js[1]["type"]) != "XX":
        side_by_side("Media type", js[0]["type"], js[1]["type"])

    cli_p(col_blu + "#" * sizex + col_rst)

    if cli is False:
        return pile


def print_memento_mori():
    """
    show a reminder that life is short and times is always passing by faster
    as time goes on.
    1 out of 100 times it will display additional warnings
    """
    if disable_lifebar is False:
        seg1 = useless_first_years
        seg2 = user_age - useless_first_years
        seg3 = user_life_expected - user_age - useless_last_years
        seg4 = useless_last_years
        resize = 1 / user_life_expected * (sizex - 17)
        if random.random() > 0.99:
            string = "REMEMBER THAT TIME IS RUNNING OUT"
            for i in range(5):
                color_set = [col_red, col_yel] * 3
                random.shuffle(color_set)
                col_rdm = (col for col in color_set)
                print(f"{col_mgt_fg}{col_blink}{col_bold}{col_uline}", end="")
                print(f"{next(col_rdm)}{string}", end=spacer * 2)
                print(f"{next(col_rdm)}{string}", end=spacer * 2)
                print(f"{next(col_rdm)}{string}", end="")
                print(col_rst, end="\n")
        print("Your life (" + col_red + str(int((seg2) / (seg2 + seg3) * 100)) +
              "%" + col_rst + ") : " + col_yel + "x" * int(seg1 * resize) +
              col_red + "X" * (int(seg2 * resize)) + col_gre +
              "-" * (int(seg3 * resize)) + col_yel + "x" * int(seg4 * resize) +
              col_rst)


def print_side_by_side(rowname, a, b, space=2, col=""):
    """
    from https://stackoverflow.com/questions/53401383/how-to-print-two-strings-large-text-side-by-side-in-python
    """
    rowname = rowname.ljust(15)
    a = str(a)
    b = str(b)
    col_width = int((int(sizex) - len(rowname)) / 2 - int(space) * 2)
    inc = 0
    while a or b:
        inc += 1
        if inc == 1:
            print(str(col) + str(rowname) + " " * space + "|" +
                  a[:col_width].ljust(col_width) + " " * space +
                  "|" + b[:col_width] + col_rst)
        else:
            print(str(col) + " " * (len(rowname) + space) + "|" +
                  a[:col_width].ljust(col_width) + " " * space +
                  "|" + b[:col_width] + col_rst)
        a = a[col_width:]
        b = b[col_width:]


def print_podium(df, sizex, args):
    "Show the highest ranked things to do in LiTOY "
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', sizex)
    pd.set_option('display.max_colwidth', int(sizex / 2.6))
    if args["verbose"] is True:  # print all fields
        pprint(df.sort_values(by="gELO", ascending=False)[0:10])
    else:
        dfp = df.loc[:, ["content", "gELO", "iELO", "tELO",
                         "tags", "disabled", "metacontent"]
                     ][df["disabled"] == 0]
        dfp["media_title"] = [(lambda x: json.loads(x)["title"]
                               if "title" in json.loads(x)
                               else "")(x)
                              for x in dfp.loc[:, "metacontent"]]
        pprint(dfp.loc[:,
                       ["media_title", "content",
                        "gELO", "iELO", "tELO", "tags"]
                       ].sort_values(by="gELO", ascending=False)[0:10])


def print_stats(df, printing=True):
    """
    shows statistics on the litoy database, but is also used to write at each
    launch the state of the database for later analysis
    """
    df = df.copy()
    df_nd = df[df['disabled'] == 0]
    df_virg = df[df['n_review'] == 0]
    df_nvirg = df[df['n_review'] != 0]
    try:
        all_delta_elos = list(df_nd.DiELO + df_nd.DtELO)
        completion_score = round(mean([
                                       mean(all_delta_elos),
                                       median(all_delta_elos)
                                     ]
                                      ) / len(df_nd.index), 3)
        durations = [float(json.loads(x)["length"]) for x in df["metacontent"] if "length" in json.loads(x)]
        table = PrettyTable()
        table.field_names = ["", "value"]
        table.align[""] = "l"
        table.align["value"] = "l"
        table.add_row(["Entries:", len(df)])
        table.add_row(["Nondisabled entries:", len(df_nd)])
        table.add_row(["Never reviewed entries:",
                       len(df_virg)])
        table.add_row(["Total reviews:",
                       round(df_nd.n_review.sum(), 1)])
        table.add_row(["Average number of review:",
                       round(df_nd['n_review'].mean(), 2)])
        table.add_row(["Total duration:", format_length(sum(durations))])
        table.add_row(["Progress score (lower is better):", completion_score])

        table2 = PrettyTable()
        table2.field_names = ["", "average", "sd", "median"]
        table2.align[""] = "l"
        table2.align["average"] = "l"
        table2.align["sd"] = "l"
        table2.align["median"] = "l"
        table2.add_row(["Importance score:",
                       int(df_nd.iELO.mean()),
                       int(df_nd.iELO.std()),
                       int(median(df_nd.iELO))])
        table2.add_row(["Time score:", int(df_nd.tELO.mean()),
                       int(df_nd.tELO.std()),
                       int(median(df_nd.tELO))])
        table2.add_row(["Global score:", int(df_nvirg.gELO.mean()),
                       int(df_nvirg.gELO.std()),
                       int(median(df_nvirg.gELO))])

        table2.add_row(["Delta scores:", int(mean(all_delta_elos)),
                       int(stdev(all_delta_elos)), int(median(all_delta_elos))])
        table2.add_row(["K value:", int(df_nd.K.mean()),
                       int(df_nd.K.std()), int(df_nd.K.median())])
        table2.add_row(["Time spent reviewing:",
                        int(df_nd.review_time.median()),
                        int(df_nd.review_time.std()),
                        int(median(df_nd.review_time))])
        table2.add_row(["Duration:",
                        format_length(mean(durations)),
                        format_length(stdev(durations)),
                        format_length(median(durations))])

        if printing is True:
            print(table)
            print("")
            print(table2)
        else:
            table.border = False
            table2.border = False
            log_(str(table))
            log_(str(table2))
    except StatisticsError as e:
        log_(f"Not enough data points to start reviewing: {e}", False)
        raise SystemExit()


def print_specific_entries(query, args, df):
    """
    shows the user the entries among the following choice:
    quickest, most important, disabled,  starred, disabled
    """
    if query in ["quick", "quick_tasks"]:
        log_("Showing quick entries", False)
        if args["verbose"] is True:  # print all fields
            pprint(df.sort_values(by="tELO", ascending=False)[0:10])
        else:
            df = df.loc[df["disabled"] == 0]
            pprint(df.loc[:,
                           ["media_title", "content",
                            "tELO", "tags"]
                           ].sort_values(by="tELO", ascending=False)[0:10])

    elif query in ["important", "important_tasks"]:
        log_("Showing important entries", False)
        if args["verbose"] is True:  # print all fields
            pprint(df.sort_values(by="iELO", ascending=False)[0:10])
        else:
            df = df.loc[df["disabled"] == 0]
            pprint(df.loc[:,
                           ["media_title", "content",
                            "iELO", "tags"]
                           ].sort_values(by="iELO", ascending=False)[0:10])

    elif query in ["starred", "starred_tasks"]:
        log_("Showing starred entries", False)
        df = df.loc[df.starred == 1].sort_values(by="gELO", ascending=False)[0:10]
        if len(df.index) == 0:
            log_("No starred entries.", False)
            raise SystemExit()

        if args["verbose"] is True:  # print all fields
            pprint(df)
        else:
            pprint(df.loc[:,
                           ["media_title", "content",
                            "gELO", "tags"]
                           ].sort_values(by="gELO", ascending=False)[0:10])

    elif query in ["disabled", "disabled_tasks"]:
        log_("Showing disabled entries", False)
        df = df.loc[df.disabled == 1].sort_values(by="gELO", ascending=False)[0:10]
        if len(df.index) == 0:
            log_("No disabled entries.", False)
            raise SystemExit()

        if args["verbose"] is True:  # print all fields
            pprint(df)
        else:
            pprint(df.loc[:,
                           ["media_title", "content",
                            "gELO", "tags"]
                           ].sort_values(by="gELO", ascending=False)[0:10])
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')
    pd.reset_option('display.width')
    pd.reset_option('display.max_colwidth')


def action_edit_entry(entry_id, litoy, field_list=None, field_auto_completer=None, auto_complete=None, shortcut_action_args=None):
    """
    edit entries via prompring user
    """
    df = litoy.df
    if auto_complete is None:
        cur_tags = litoy.get_tags(litoy.df)
        autocomplete_list = ["tags:"+tags for tags in cur_tags] + ["set_length:"]
        auto_complete = prompt_toolkit.completion.WordCompleter(autocomplete_list,
                              match_middle=True,
                              ignore_case=True,
                              sentence=False)
    if field_list is None:
        field_list = list(df.columns)
        field_auto_completer = prompt_toolkit.completion.WordCompleter(field_list, sentence=True)


    entry = df.loc[entry_id, :]
    log_(f"Entry to edit: {entry}", False)
    while True:
        print(f"Fields available for edition : {field_list}")
        chosenfield = prompt_we("What field do you want to edit? \
(q to exit)\n>", completer = field_auto_completer)
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

        try:
            old_value = str(entry[chosenfield])
        except KeyError as e:
            log_(f"ERROR: Shortcut : edit : wrong field name: {e}",
                 False)
            continue
        new_value = str(prompt_we("Enter the desired new value \
for field '" + chosenfield +"'\n>", default=old_value, **additional_args))

        if chosenfield == "content":
            new_value = move_flags_at_end(new_value)
            df.loc[entry_id, "metacontent"] = json.dumps(get_meta_from_content(new_value))
            df.loc[entry_id, "tags"] = json.dumps(sorted(get_tags_from_content(new_value)))
        df.loc[entry_id, chosenfield] = new_value
        litoy.save_to_file(df)
        log_(f'Edited entry with ID {entry_id}, field "{chosenfield}", {old_value} => {new_value}',
             False)
        break
    else:
        log_(f"Entry with ID {entry_id} was NOT edited.", False)
    if shortcut_action_args:
        display_2_entries(**shortcut_action_args, litoy=litoy)

def set_user_length_cli(entry_id, meta, litoy):
    """
    in cli, if no length is found in the metacontent: ask the user
    """
    log_(f"Asking user to complete length for ID {entry_id}")
    input_length = prompt_we(f"No length specified for entry #{entry_id}. \
How many minutes does it take? (q)\n>")
    if input_length not in ["q", "quit", "exit"]:
        if "set_length:" in litoy.df.loc[entry_id, "content"]:
            log_("WARNING: setting a length even though there is already one specified in `content`", False)
        formatted = format_length(input_length, to_machine_readable=True)
        meta["length"] = formatted
        litoy.df.loc[entry_id, "metacontent"] = json.dumps(meta)
        litoy.df.loc[entry_id, "content"] += f" set_length:{formatted}"
        litoy.save_to_file(litoy.df)


def review_mode_cli(litoy):
    available_shortcut = list(chain.from_iterable(shortcuts.values()))
    shortcut_auto_completer = prompt_toolkit.completion.WordCompleter(available_shortcut,
                                            sentence=False,
                                            match_middle=True,
                                            ignore_case=True)
    progress = 1
    picked_ids = pick_entries(litoy.df)
    entries = [litoy.df.loc[picked_ids[0], :],
               litoy.df.loc[picked_ids[1], :]]
    log_(f"Picked the following entries : {picked_ids}")
    mode = "importance"
    action = ""

    def check_if_finished(progress):
        if progress <= n_to_review*n_session:
            return False
        return True

    while True:
        disp_flds = "no"
        if progress % 2 == 0:
            mode = "time"
        else:
            mode = "importance"


        if action not in ["show_few_fields", "show_all_fields", "show_help"]:
            display_2_entries(entries[0].name,
                              entries[1].name,
                              litoy=litoy,
                              mode=mode,
                              all_fields=disp_flds)

        # if no length specified, ask the user:
        metas = []
        if mode == "importance":  # ask only once
            for i in range(len(entries)):
                metas.append(json.loads(entries[i]["metacontent"]))
                if "length" not in metas[i]:
                    try:
                        set_user_length_cli(entries[i].name, metas[i], litoy)
                    except InvalidTimestamp as e:
                        if str(e) == "skip":
                            log_("Skipping.", False)
                        continue
                    else:
                        entries[i] = litoy.df.loc[entries[i].name, :]

        # if both length specified, auto suggest time answer:
        def_time_ans = ""
        if mode == "time" and \
        "length" in json.loads(entries[0]["metacontent"]) and \
        "length" in json.loads(entries[1]["metacontent"]):
            def_time_ans = suggest_time_answer(entries[0], entries[1])

        # ask comparison question:
        start_time = time.time()
        prompt_text = f"{progress}/{n_to_review*n_session} {questions[mode]} (h or ? for help)\n>"
        log_(f"Waiting for shortcut for {entries[0].name} vs {entries[1].name} for {mode}")
        keypress = prompt_we(prompt_text,
                             completer=shortcut_auto_completer,
                             default=def_time_ans)

        if keypress not in available_shortcut:
            log_(f"ERROR: keypress not found : {keypress}", False)
            action = "show_help"
        else:
            action = str(fetch_action(keypress))
            log_(f"Shortcut found : {action}")

        if action == "answer_level":
            process_review_answer(keypress, entries[0], entries[1], mode,
                                  start_time, litoy)
            progress += 1

            if check_if_finished(progress):
                break

            if mode == "time":
                if entries[1].name == picked_ids[1]:
                    entries[1] = litoy.df.loc[picked_ids[2], :]
                else:
                    picked_ids = pick_entries(litoy.df)
                    entries = [litoy.df.loc[picked_ids[0], :],
                               litoy.df.loc[picked_ids[1], :]]
                    log_(f"Picked the following entries : {picked_ids}")
            continue

        elif action == "skip_review":
            log_("Skipped review.", False)

            if check_if_finished(progress):
                break

            progress += 1
            if mode == "time":
                if entries[1].name == picked_ids[1]:
                    entries[1] = litoy.df.loc[picked_ids[2], :]
                else:
                    picked_ids = pick_entries(litoy.df)
                    entries = [litoy.df.loc[picked_ids[0], :],
                               litoy.df.loc[picked_ids[1], :]]
                    log_(f"Picked the following entries : {picked_ids}")
            continue

        elif action == "show_all_fields":
            log_("Displaying the entries in full")
            display_2_entries(entries[0].name,
                              entries[1].name,
                              mode,
                              litoy,
                              "all")
            continue

        elif action == "show_few_fields":
            log_("Displaying only most important fields of entries")
            display_2_entries(entries[0].name,
                              entries[1].name,
                              mode,
                              litoy)
            continue

        elif action == "open_media":
            log_("Openning media")
            for ent_id in [entries[0].name, entries[1].name]:
                ent = litoy.df.loc[ent_id, :]
                try:
                    path = str(json.loads(ent.metacontent)["url"])
                    if "http" in path:
                        webbrowser.open(path, new=2)
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
            time.sleep(1)  # better display
            continue

        elif "reload_media" in action:
            log_("Reloading media")
            additional_args = {}
            if action == "reload_media_fallback_method":
                additional_args.update({"simple_method": False})
            for ent_id in [entries[0].name, entries[1].name]:
                df = litoy.df.copy()
                df.loc[ent_id, "content"] = move_flags_at_end(df.loc[ent_id,
                                                                     "content"])
                new_meta = get_meta_from_content(df.loc[ent_id, :]["content"],
                                                 additional_args)
                df.loc[ent_id, "metacontent"] = json.dumps(new_meta)
                litoy.save_to_file(df)
                entries[0] = df.loc[entries[0].name, :]
                entries[1] = df.loc[entries[1].name, :]
                log_(f"New metacontent value for {ent_id} : {new_meta}")
            continue

        elif action == "open debugger":
            log_("Openning debugger", False)
            print("To open a python console within the debugger, type in \
'interact'. You can load the database as a pandas DataFrame using df=litoy.df")
            pdb.set_trace()
            continue

        elif action.startswith("edit_"):
            if action.endswith("_left"):
                action_edit_entry(entries[0].name,
                                  litoy=litoy,
                                  shortcut_action_args={
                                      "id_left": entries[0].name,
                                      "id_right": entries[1].name,
                                      "mode": mode})
            elif action.endswith("_right"):
                action_edit_entry(entries[1].name,
                                  litoy=litoy,
                                  shortcut_action_args={
                                      "id_left": entries[0].name,
                                      "id_right": entries[1].name,
                                      "mode": mode})
            # reload entries
            entries = [litoy.df.loc[picked_ids[0], :],
                       litoy.df.loc[picked_ids[1], :]]

            continue

        elif action.startswith("star_"):
            if action.endswith("_left"):
                action_star(entries[0].name, litoy)
            elif action.endswith("_right"):
                action_star(entries[1].name, litoy)
            continue

        elif action.startswith("disable_"):
            picked_ids = pick_entries(litoy.df)
            log_(f"Picked the following entries : {picked_ids}")
            if action.endswith("_left"):
                action_disable(entries[0].name, litoy)
                entries[0] = litoy.df.loc[picked_ids[0], :]
            elif action.endswith("_right"):
                action_disable(entries[1].name, litoy)
                entries[1] = litoy.df.loc[picked_ids[1], :]
            elif action.endswith("_both"):
                action_disable(entries[0].name, litoy)
                action_disable(entries[1].name, litoy)
                entries = [litoy.df.loc[picked_ids[0], :],
                           litoy.df.loc[picked_ids[1], :]]
            if mode == "importance":
                progress += 2
            else:
                progress += 1
            continue

        elif action == "undo":
            print("Undo function is not yet implemented, \
  manually correct the database using libreoffice calc after looking at \
  the logs. Or take a look at the saved json files")
            input("(press enter to resume reviewing session)")

        elif action == "show_help":
            log_("Printing help :", False)
            pprint(shortcuts)
            input("Press enter to continue.")

        elif action == "repick":
            picked_ids = pick_entries(litoy.df)
            entries[1] = litoy.df.loc[picked_ids[1], :]
            log_(f"Picked the following entries : {picked_ids}")
            continue

        elif action == "quit":
            log_("Shortcut : quitting")
            print("Quitting.")
            raise SystemExit()
    log_("Finished reviewing sessions. Quitting.", False)
    raise SystemExit()
