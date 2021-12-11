#!/usr/bin/env python3.9
from pathlib import Path
import time
from pprint import pprint
import prompt_toolkit
import pdb
import re
from user_settings import json_auto_save
from src.backend.log import log_

class InvalidTimestamp(Exception):
    pass

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


def format_length(to_format, to_machine_readable=False):
    """
    displays 120 minutes as 2h0m, or the opposite
    to_machine_readable=False means 120 => 2h0m
    to_machine_readable=True means 2h0m => 120
    """
    if to_machine_readable is False:
        minutes = to_format
        if minutes == "X":
            return "X"
        minutes = int(float(minutes))
        days = int(minutes // 60 // 24)
        hours = int(minutes // 60 - days * 24)
        minutes = minutes % 60
        length = ""
        if days != 0:
            length += str(days) + "d"
        if hours != 0:
            length += str(hours) + "h"
        if minutes != 0:
            length += str(minutes) + "min"
        return length
    else:
        to_format = to_format.replace("min", "m").lower()
        if to_format in ["q", "quit", "exit", "skip"]:
            raise InvalidTimestamp("skip")

        match = re.match(r"(\d+[jd])?(\d+h)?(\d+m)?", to_format)
        if match.group() == "" or to_format == "":
            log_("Invalid timestamp format", False)
            raise InvalidTimestamp(to_format)
        length = 0
        days = re.findall(r"\d+[jd]", to_format)
        hours = re.findall(r"\d+h", to_format)
        minutes = re.findall(r"\d+m", to_format)
        if days:
            length += 1440 * int(days[0][:-1])
        if hours:
            length += 60 * int(hours[0][:-1])
        if minutes:
            length += int(minutes[0][:-1])
        if length == 0:
            print("Invalid time stamp!")
            breakpoint()
        return str(length)


