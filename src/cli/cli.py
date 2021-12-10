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

from src.backend.backend import (get_meta_from_content,
                                 get_tags_from_content,
                                 move_flags_at_end,
                                 fetch_action,
                                 action_disable,
                                 action_star,
                                 process_review_answer)
from src.backend.util import format_length, prompt_we
from src.backend.log import log_
from user_settings import (shortcuts, n_to_review, n_session, questions,
                           useless_last_years, useless_first_years,
                           user_life_expected, user_age, disable_lifebar,
                           col_red, col_gre, col_yel, col_rst, col_mgt_fg,
                           col_blink, col_bold, col_uline, spacer, col_blu)
from src.cli.get_terminal_size import get_terminal_size


def print_2_entries(id_left, id_right, mode, litoy, all_fields=False, cli=True):
    """
    Show the two entries to review side by side
    This function is actually part CLI but is highjacked by the GUI to
    easily extract all the information to show to the user
    """
    global sizex, sizey
    (sizex, sizey) = get_terminal_size()  # dynamic sizing

    if cli:
        global print, side_by_side
    else:  # highjacking this function to get all the values to print
        def print(string):
            pass
        storage = []
        def side_by_side(key, val1, val2):
            storage.append([key, [val1, val2]])


    print(col_blu + "#" * sizex + col_rst)
    print_memento_mori()
    print(col_blu + "#" * sizex + col_rst)

    entry_left = litoy.df.loc[id_left, :].copy()
    entry_right = litoy.df.loc[id_right, :].copy()

    if all_fields != "all":
        side_by_side("ID", id_left, id_right)
        print("." * sizex)

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
        print("." * sizex)
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
            if y not in js[x].keys():
                js[x][y] = "X"
            else:
                js[x][y] == str(js[x][y])
    print("." * sizex)
    if (js[0]["title"] + js[1]["title"]) != "XX":
        side_by_side("Title", js[0]["title"], js[1]["title"])
    if (str(js[0]["length"]) + str(js[1]["length"])) != "XX":
        side_by_side("Length",
                     format_length(js[0]["length"]),
                     format_length(js[1]["length"]))
        print("." * sizex)
    if (js[0]["url"] + js[1]["url"]) != "XX":
        side_by_side("Location", js[0]["url"], js[1]["url"])
    if (js[0]["channel"] + js[1]["channel"]) != "XX":
        side_by_side("Channel", js[0]["channel"], js[1]["channel"])
    if (js[0]["type"] + js[1]["type"]) != "XX":
        side_by_side("Media type", js[0]["type"], js[1]["type"])

    print(col_blu + "#" * sizex + col_rst)

    if cli is False:
        return storage


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


def side_by_side(rowname, a, b, space=2, col=""):
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
                               if "title" in json.loads(x).keys()
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
        table = PrettyTable()
        table.field_names = ["", "value"]
        table.align[""] = "l"
        table.align["value"] = "r"
        table.add_row(["Number of entries in LiTOY:", len(df)])
        table.add_row(["Number of non disabled entries in LiTOY:", len(df_nd)])
        table.add_row(["Number of entries that have never been reviewed:",
                       len(df_virg)])
        table.add_row(["Total number of review:",
                       round(df_nd.n_review.sum(), 1)])
        table.add_row(["Average number of review:",
                       round(df_nd['n_review'].mean(), 2)])

        table2 = PrettyTable()
        table2.field_names = ["", "average", "sd", "median"]
        table2.align[""] = "l"
        table2.align["average"] = "r"
        table2.align["sd"] = "r"
        table2.align["median"] = "r"
        table2.add_row(["Importance score:",
                       round(df_nd.iELO.mean(), 1),
                       round(df_nd.iELO.std(), 2),
                       round(median(df_nd.iELO), 2)])
        table2.add_row(["Time score:", round(df_nd.tELO.mean(), 1),
                       round(df_nd.tELO.std(), 2),
                       round(median(df_nd.tELO), 2)])
        table2.add_row(["Global score:", round(df_nvirg.gELO.mean(), 1),
                       round(df_nvirg.gELO.std(), 2),
                       round(median(df_nvirg.gELO), 2)])

        all_delta_elos = list(df_nd.DiELO + df_nd.DtELO)
        table2.add_row(["Delta scores:", round(mean(all_delta_elos), 1),
                       round(stdev(all_delta_elos), 2), round(median(all_delta_elos), 2)])
        table2.add_row(["K value:", round(df_nd.K.mean(), 1),
                       round(df_nd.K.std(), 2), round(df_nd.K.median())])
        table2.add_row(["Time spent reviewing:",
                        round(df_nd.review_time.median(), 1),
                        round(df_nd.review_time.std(), 2),
                        round(median(df_nd.review_time), 2)])

        completion_score = round(mean([
                                       mean(all_delta_elos),
                                       median(all_delta_elos)
                                     ]
                                      ) / len(df_nd.index), 3)
        if printing is True:
            print(table)
            print("")
            print(table2)
            print(f"Progress score: {completion_score:>20}")
            print("(lower is better)")
        else:
            table.border = False
            table2.border = False
            log_(str(table))
            log_(str(table2))
            log_(f"Progress score: {round(completion_score, 3):>20}")
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


def action_edit_entry(entry_id, litoy, field_list=None, field_auto_completer=None, auto_complete=None):
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


def shortcut_and_action(id_left, id_right, mode, progress, litoy,
                        shortcut_auto_completer, available_shortcut):
    """
    makes the link between actions and their effect
    """
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
            input_length = prompt_we("No length specified for left entry. \
How many minutes does it take? (q)\n>")
            if input_length not in ["q", "quit", "exit"]:
                assert "set_length:" not in litoy.df.loc[id_left, "content"]
                formatted = format_length(input_length, to_machine_readable=True)
                meta_left["length"] = formatted
                litoy.df.loc[id_left, "metacontent"] = json.dumps(meta_left)
                litoy.df.loc[id_left, "content"] += f" set_length:{formatted}"
                litoy.save_to_file(litoy.df)
                entry_left = litoy.df.loc[id_left, :]
        meta_right = json.loads(entry_right["metacontent"])
        if "length" not in meta_right.keys():
            log_("Asking user to complete length.")
            input_length = prompt_we("No length specified for right entry. \
How many minutes does it take? (q)\n>")
            if input_length not in ["q", "quit", "exit"]:
                assert "set_length:" not in litoy.df.loc[id_right, "content"]
                formatted = format_length(input_length, to_machine_readable=True)
                meta_right["length"] = formatted
                litoy.df.loc[id_right, "metacontent"] = json.dumps(meta_right)
                litoy.df.loc[id_right, "content"] += f" set_length:{formatted}"
                litoy.save_to_file(litoy.df)
                entry_right = litoy.df.loc[id_right, :]

        def_time_ans = ""
        if mode == "time" and \
        "length" in json.loads(entry_left["metacontent"]) and \
        "length" in json.loads(entry_right["metacontent"]):
            # auto answers time questions
            left_length = float(json.loads(entry_left["metacontent"])["length"])
            right_length = float(json.loads(entry_right["metacontent"])["length"])
            ratio = left_length / right_length
            ratio2 = (left_length - right_length) / (left_length + right_length)
            if ratio >= 2:
                def_time_ans = "1"
            if ratio > 1.5:
                def_time_ans = "2"
            if ratio > 0.65:
                def_time_ans = "3"
            if ratio > 0.5:
                def_time_ans = "4"
            if ratio <= 0.5:
                def_time_ans = "5"

            if ratio2 > 0.4:
                def_time_ans = "5"
            if ratio2 < -0.4:
                def_time_ans = "1"

            if abs(ratio2) < 0.1:
                def_time_ans = "3"

        keypress = prompt_we(prompt_text,
                             completer=shortcut_auto_completer,
                             default=def_time_ans)

        if keypress not in available_shortcut:
            log_(f"ERROR: keypress not found : {keypress}")
            action = "show_help"
        else:
            action = str(fetch_action(keypress))
            log_(f"Shortcut found : Action={action}")

        if action == "answer_level":
            process_review_answer(keypress, entry_left, entry_right, mode,
                                  start_time, litoy)
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
                additional_args.update({"simple_method": False})
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
            action_edit_entry(id_left, litoy)
            print_2_entries(id_left, id_right, mode=mode, litoy=litoy)
            continue
        if action == "edit_right":
            action_edit_entry(id_right, litoy)
            print_2_entries(id_left, id_right, mode=mode, litoy=litoy)
            continue
        if action == "star_left":
            action_star(id_left, litoy)
            continue
        if action == "star_right":
            action_star(id_right, litoy)
            continue
        if action == "disable_left":
            action_disable(id_left, litoy)
            return action
        if action == "disable_both":
            action_disable(id_right, litoy)
            action_disable(id_left, litoy)
            return action
        if action == "disable_right":
            action_disable(id_right, litoy)
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
