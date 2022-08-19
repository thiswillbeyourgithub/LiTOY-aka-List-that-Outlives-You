#!/usr/bin/env python3.9
import time
import youtube_dl
from youtube_dl.utils import DownloadError, ExtractorError
from pathlib import Path
import requests
import pdftotext
import get_wayback_machine
from bs4 import BeautifulSoup
from moviepy.editor import VideoFileClip
from newspaper import Article
from ebooklib import epub

from user_settings import average_word_length, headers, wpm
from src.backend.log import log_

def extract_epub(url):
    "extracts book duration and title from epub file"
    try:
        book = epub.read_epub(url)
        items = [x for x in book.get_items()]
        text_content = ""
        for item in items:
            if hasattr(item, "get_body_content"):
                 html = item.get_body_content()
                 soup = BeautifulSoup(html, "html.parser")
                 text_content += soup.text.replace("\n", " ")

        total_words = len(text_content) / average_word_length
        estimatedReadingTime = str(round(total_words / wpm, 1))

        res = {"type": "epub",
               "length": estimatedReadingTime,
               "title": book.title.replace("\n", ""),
               "url": url}
    except Exception as e:
        log_(f"Error: {e}", False)
        res = {"type": "epub (exception)",
               "url": url}
    return res



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

        if "duration" in video:
            length = str(round(video['duration'] / 60, 1))
            res.update({"length": length})
            res.update({"channel": video["uploader"]})
        else:
            log_("Youtube playlist detected.:", False)
            res["type"] = "video (youtube playlist)"
            if "playlist" not in res["title"].lower():
                res["title"] += " - Playlist"
            length = 0
            channels = []
            for ent in video["entries"]:
                length += ent["duration"]
                channels.append(ent["uploader"])
            res["length"] = str(round(length / 60, 1))
            if len(list(set(channels))) == 1:
                res["channel"] = channels[0]
            else:
                if "channel" in res:
                    del res["channel"]
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
    duration = round(clip.duration / 60, 1)
    title = clip.filename.strip()
    dic = {"type": "local video",
           "title": title.replace("\n", ""),
           "length": duration,
           "url": link}
    return dic


def extract_pdf_url(url):
    "extracts reading time from an online pdf"
    try:
        downloaded = requests.get(url, headers=headers, timeout=5)
    except requests.exceptions.ConnectTimeout as e:
        log_(f"Connection timed out, skipping url: {url}", False)
        temp_dic = {}
        temp_dic["type"] = "connection timed out"
        temp_dic["url"] = url
        return temp_dic
    open("./.temporary.pdf", "wb").write(downloaded.content)
    temp_dic = extract_pdf_local("./.temporary.pdf")
    temp_dic["type"] = "online pdf"
    temp_dic["url"] = url
    del temp_dic["title"]  # can't yet scrap pdf title reliably
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

    total_words = len(text_content) / average_word_length
    estimatedReadingTime = str(round(total_words / wpm, 1))

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

        total_words = len(text_content) / average_word_length
        estimatedReadingTime = str(round(total_words / wpm, 1))

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


def extract_webpage(url, simple_method=True):
    """
    extracts reading time from a webpage, output is a dictionnary containing
    estimation of the reading time ; title of the page ; if the wayback
    machine was used
    """
    wayback_used = 0
    if simple_method:
        article = Article(url)
        try:
            article.download()
            article.parse()
            title = article.title
            if title == "WWW Error Blocked Diagnostic":
                raise Exception("Exception, found title: 'WWW Error Blocked Diagnostic'")
            text_content = " ".join(article.text.replace("\n", " ").split())
        except Exception as e:
            log_(f"Error: {e}")
            simple_method = False
    if simple_method is False:
        log_("Using fallack extractor")
        try:
            req = requests.get(url, headers=headers, timeout=5)
        except requests.exceptions.ConnectTimeout as e:  # if timed out
            log_("Connection timed out, retrying once in 5 seconds...", False)
            time.sleep(5)
            try:
                req = requests.get(url, headers=headers, timeout=10)
            except requests.exceptions.ConnectTimeout as e:
                log_(f"Connection timed out again, skipping url: {url}", False)
                res = {"type": "connection timed out",
                       "url": url}
                return res
        except requests.exceptions.ConnectionError: # if url is dead use wayback machine
            log_(f"Using the wayback machine for {url}", False)
            wayback_used = 1
            wb = get_wayback_machine.get(url)
            try:
                url = wb.links['last memento']['url']
                req = requests.get(url, headers=headers, timeout=5)
            except (requests.exceptions.ConnectionError, AttributeError) as e:
                log_(f"ERROR: url could not be found even using wayback machine : \
{url} : {e}", False)
                res = {"type": "web page not found",
                       "url": url,
                       "used_wayback_machine": "wayback url not found"}
                return res
            except requests.exceptions.ConnectTimeout as e:
                log_(f"Connection timed out on wayback machine, skipping url: {url}", False)
                res = {"type": "connection timed out",
                       "url": url}
                return res

        # extracting divs and p elements and keeping the the smallest text
        html_page = req.content
        soup = BeautifulSoup(html_page, 'html.parser')
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

    total_words = len(text_content) / average_word_length
    estimatedReadingTime = str(round(total_words / wpm, 1))
    title = title.replace("\n", "").replace("\\n", "").strip()
    res = {"title": title,
           "type": "webpage",
           "length": estimatedReadingTime,
           "used_wayback_machine": wayback_used,
           "url": url}
    return res
