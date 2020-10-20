##!/usr/bin/env python3
#
###################################################################################
## Released under the GNU Lesser General Public License v2.
## Copyright (C) - 2020 - user "thiswillbeyourgithub" of the website "github".
## This file is part of LiTOY : a tool to help organiser various goals over time.
## Anki card template helping user to retain knowledge.
## 
## LiTOY is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## LiTOY is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with LiTOY.  If not, see <https://www.gnu.org/licenses/>.
## 
## for more information or to get the latest version go to :
## https://github.com/thiswillbeyourgithub/LiTOY
###################################################################################
#
#
#import logging
#import platform
#import subprocess
#import requests
#import re
#
#from .settings      import *
#from .functions     import *
#
#
## This file contains functions used to retrieve reading time from pdf or URL, 
#
#def process_all_metadata(entry):  # used to store information related links found etc in the entry
#    logging.info("Process all metadata : begin")
#    found = find_media(entry, "return")
#    if len(found)==0:
#        logging.info("Processing all metadata : none in entry with ID " + str(entry["ID"]))
#    else:
#        for item in found:
#            if default_path in item :
#                logging.info("Processing all metadata : identified as path")
#                pass
#            elif "http" in item :
#                if "pdf" in item : # if the webpage links to a pdf
#                    logging.info("Processing all metadata : identified as link to a pdf")
#                    pass
#                else :
#                    logging.info("Processing all metadata : identified as link to an article")
#                    # get url title
#                    title_re=re.compile(r'<title>(.*?)</title>', re.UNICODE )
#                    r = requests.get(item)
#                    if r.status_code == 200:
#                        match = title_re.search(r.text)
#                        if match:
#                            title = match.group(1)
#                            print(title)
#                            entry["metadata"] = entry["metadata"] + " urltabtitle='" + title + "'"
#                            push_dico(entry, "UPDATE")
#                        else : return Exception("No match for title in page")
#                    else : raise Exception(r.status_code)
#
#
#    
#    
#    logging.info("Process all metadata : done")
#
#
#
#def find_media(entry, action=""):
#    logging.info("Finding media : begin")
#    relevant_fields = ["entry","metadata"]
#    found=[]
#    for f in relevant_fields :
#        word = str(entry[f]).split(" ")
#        for ff in word:
#            if default_path in ff :
#                if action == "auto-open" :
#                    logging.info("Finding media : Openning folder : "+ff)
#                    if platform.system() == "Linux" :
#                        subprocess.Popen("nautilus", ff)
#                elif action == "return" :
#                    logging.info("Finding media : returning folder : "+ff)
#                    found.append(ff)
#
#            if "http://" in ff or "https://" in ff or "www" in ff:
#                if action == "auto-open" :
#                    logging.info("Finding media : Openning link : "+ff) 
#                    if platform.system() == "Linux" :
#                        subprocess.run([browser_path, ff])
#                    else :
#                        webbrowser.open_new_tab(ff)
#                elif action == "return" :
#                    logging.info("Finding media : returning link : "+ff)
#                    found.append(ff)
#    logging.info("Finding media : done")
#    return found
