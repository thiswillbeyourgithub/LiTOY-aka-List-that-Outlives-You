#!/usr/bin/env python3.9
import sys
sys.path.append("../../")
from user_settings import json_auto_save
from pathlib import Path
import time
import re
from pprint import pprint
import prompt_toolkit
import pdb
from .log import log_


def debug_signal_handler(signal, frame):
    """
    Make the whole script interruptible using ctrl+c,
    you can then resume using 'c'
    """
    pdb.set_trace()


def prompt_we(*args, **kargs):
    """
    wrapper for prompt_toolkit.prompt to catch Keyboard interruption cleanly
    """
    style = prompt_toolkit.styles.Style.from_dict({"": "ansibrightyellow"})
    try:
        return prompt_toolkit.prompt(*args, **kargs, style=style)
    except (KeyboardInterrupt, EOFError):
        log_("Exiting.", False)
        raise SystemExit()


def wrong_arguments_(args):
    "Print user arguments then exit"
    print("Exiting because called with wrong arguments \nYour arguments:")
    pprint(args)
    raise SystemExit()


def format_length(to_format, reverse=False):
    "displays 120 minutes as 2h0m etc"
    if reverse is False:
        minutes = to_format
        if minutes == "":
            return ""
        minutes = float(minutes)
        hours = minutes // 60
        days = hours // 24
        if days == 0:
            days = ""
        else:
            hours = hours-days*24
            days = str(int(days))+"d"
        if hours == 0 :
            hours = ""
        else:
            minutes = minutes-hours*60
            hours = str(int(hours))+"h"
        minutes = str(int(minutes))+"min"
        length = days+hours+minutes
        return length
    else:
        length = 0
        days = re.findall("\d+[jd]", to_format)
        hours = re.findall("\d+h", to_format)
        minutes = re.findall("\d+m", to_format)
        if days:
            length += 1440*int(days[0][:-1])
        if hours:
            length += 60*int(hours[0][:-1])
        if minutes:
            length += int(minutes[0][:-1])
        return str(length)


def json_periodic_save(litoy):
    """
    If json_auto_save is set to True, this function will save the whole litoy
    database in a new json file at startup. The idea is to avoid data loss
    by corrupting the xlsx file
    """
    if json_auto_save is True and len(litoy.df.index) > 5:
        json_dir = f'{str(Path(".").absolute())}/logs/json_backups/'
        json_name = "json_backup_" + str(int(time.time())) + ".json"
        Path(json_dir).mkdir(parents=True, exist_ok=True)
        jfile = Path(f"{json_dir}{json_name}")
        if jfile.exists():
            print("json file already exists!")
            raise SystemExit()
        jfile.touch()
        log_(f"automatically saving database as json file {json_name}")
        litoy.df.to_json(jfile, compression="bz2", index=True)
