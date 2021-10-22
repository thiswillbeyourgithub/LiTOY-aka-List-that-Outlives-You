#!/usr/bin/env python3.9
import youtube_dl
from youtube_dl.utils import DownloadError, ExtractorError
from pathlib import Path
import requests
import pdftotext
import sys
sys.path.append("../..")
from user_settings import average_word_length, headers, wpm
import get_wayback_machine
from bs4 import BeautifulSoup
from moviepy.editor import VideoFileClip
from tqdm import tqdm
from .log import log_


def extract_youtube(url):
    "extracts video duration in minutes from youtube link, title etc"
    res = {}
    with youtube_dl.YoutubeDL({"quiet": True}) as ydl:
        try:
            video = ydl.extract_info(url, download=False)
        except (KeyError, DownloadError, ExtractorError) as e:
            log_(f"ERROR: Video link skipped because : error during information \
extraction from {url} : {e}", False)
            res.update({"type": "video not found", "url": url})
            return res

        title = video['title'].strip()
        res = {"type": "video",
               "title": title.replace("\n", ""),
               "url": url}
        if "uploader" in video.keys():
            res.update({"channel": video["uploader"]})
        try:
            length = str(round(video['duration']/60, 1))
            res.update({"length": length})
        except Exception as e:
            log_("Youtube link looks like it's a playlist, using fallbackmethod:", False)
            length = 0
            for ent in video["entries"]:
                length += ent["duration"]
            length = str(round(length/60, 1))
            res.update({"length": length})
    return res


def extract_local_video(link):
    """
    extracts video duration in minutes from local files
    https://stackoverflow.com/questions/3844430/how-to-get-the-duration-of-a-video-in-python
    """
    vid = Path(link)
    if not vid.exists():
        link = link.replace("\\", "")
        vid = Path(link)
    if not vid.exists():
        log_(f"ERROR : Thought this was a local video but file was not found! \
: {link}", False)
        return {"type": "local video not found",
                "url": link}
    clip = VideoFileClip(link)
    duration = round(clip.duration/60, 1)
    title = clip.filename.strip()
    dic = {"type": "local video",
           "title": title.replace("\n", ""),
           "length": duration,
           "url": link}
    return dic

def extract_pdf_url(url):
    "extracts reading time from an online pdf"
    downloaded = requests.get(url, headers=headers)
    open("./.temporary.pdf", "wb").write(downloaded.content)
    temp_dic = extract_pdf_local("./.temporary.pdf")
    temp_dic["type"] = "online pdf"
    temp_dic["url"] = url
    Path("./.temporary.pdf").unlink()
    return temp_dic


def extract_pdf_local(path):
    "extracts reading time from a local pdf file"
    if not Path(path).exists():
        path = path.replace(" ", "\\ ")
    try:
        with open(path, "rb") as f:
            text_content = pdftotext.PDF(f)
            text_content = " ".join(text_content).replace("\n", " ")
    except FileNotFoundError:
        log_(f"ERROR: Cannot find {path}, I thought it was a PDF", False)
        return {"type": "pdf not found",
                "url": path}

    total_words = len(text_content)/average_word_length
    estimatedReadingTime = str(round(total_words/wpm, 1))

    title = path.split(sep="/")[-1].strip()
    res = {"type": "local pdf",
           "length": estimatedReadingTime,
           "title": title.replace("\n", ""),
           "url": path}
    return res


def extract_txt(path):
    "extracts reading time from a text file"
    try:
        txt_file = Path(path)
        with txt_file.open() as f:
            lines = f.readlines()
        text_content = ' '.join(lines).replace("\n", " ")

        total_words = len(text_content)/average_word_length
        estimatedReadingTime = str(round(total_words/wpm, 1))

        title = path.split(sep="/")[-1].strip()
        res = {"type": "text",
               "length": estimatedReadingTime,
               "url": path,
               "title": title.replace("\n", "")}
        return res

    except ValueError as e:
        log_(f"ERROR: Cannot find {path} : {e}", False)
        res = {"type": "txt file not found",
               "url": path}
        return res


def extract_webpage(url, fallback_text_extractor=False):
    """
    extracts reading time from a webpage, output is a tupple containing
    estimation of the reading time ; title of the page ; if the wayback
    machine was used
    """
    try:
        wayback_used = 0
        res = requests.get(url, headers=headers)
    except requests.exceptions.ConnectionError:
        # if url is dead : use wayback machine
        tqdm.write(f"Using the wayback machine for {url}")
        wayback_used = 1
        wb = get_wayback_machine.get(url)
        try:  # if url was never saved
            url = wb.links['last memento']['url']
        except (requests.exceptions.ConnectionError, AttributeError) as e:
            log_(f"ERROR: url could not be found even using wayback machine : \
{url} : {e}", False)
            res = {"title": "web page not found",
                   "url": url,
                   "length": "-1",
                   "used_wayback_machine": "wayback url not found"}
            return res
        res = requests.get(url, headers=headers)
    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')

    # the smallest text find is usually the best
    if fallback_text_extractor is False:
        text_content = " ".join(
                        " ".join(
                            [x.text.replace("\n", " ")
                             for x in soup.find_all('p')]
                            ).split())
    else:
        log_("Using fallback text extractor")
        parsed_text_trial = []
        parsed_text_trial.append(' '.join([x.text.replace("\n", " ")
                                           for x in soup.find_all("div")]))
        parsed_text_trial.append(soup.get_text().replace("\n", " "))
        parsed_text_trial.append(" ".join([x.text.replace("\n", " ")
                                           for x in soup.find_all('p')]))
        parsed_text_trial = [" ".join(x.split()) for x in parsed_text_trial]
        parsed_text_trial.sort(key=lambda x: len(x))
        text_content = parsed_text_trial[0]

    titles = soup.find_all('title')
    if len(titles) != 0:
        title = soup.find_all('title')[0].get_text()
    else:
        title = "No title found"

    total_words = len(text_content)/average_word_length
    estimatedReadingTime = str(round(total_words/wpm, 1))
    title = title.replace("\n", "").replace("\\n", "").strip()
    res = {"title": title,
           "type": "webpage",
           "length": estimatedReadingTime,
           "used_wayback_machine": wayback_used,
           "url": url}
    if res['length'] == "-1":
        res.pop("length")
        res.pop("title")
        res["type"] = "webpage not found"
    return res
