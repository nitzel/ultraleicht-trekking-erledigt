import csv
from dataclasses import dataclass
import dataclasses
from urllib.parse import urljoin
import pickle
import re

import requests
from bs4 import BeautifulSoup, Tag


def parse_url(url: str) -> tuple[str, BeautifulSoup]:
    """returning the url allows verifying the right page was loaded"""
    r = requests.get(url, timeout=10)
    return r.url, BeautifulSoup(r.content, 'html.parser')


@dataclass
class ThreadFinale():
    title: str
    url: str
    last_comment: str


def handle_thread(thread: Tag) -> ThreadFinale:
    title = thread.text.strip()
    href = thread.attrs.get('href')
    href = urljoin(href, "?do=getLastComment")
    _, thread_soup = parse_url(href)
    last_comment = thread_soup.select_one(
        ".cPost:last-of-type [data-role='commentContent']")
    last_comment = last_comment.text.strip()
    print("-", title)
    print("  -", href)
    # print("  -", last_comment)
    return ThreadFinale(
        title=title,
        url=href,
        last_comment=last_comment
    )


def handle_page(page_soup: BeautifulSoup) -> list[ThreadFinale]:
    selector = ".cTopicList .ipsDataItem_title .ipsContained a"
    threads = page_soup.select(selector)

    return [handle_thread(t) for t in threads]


def get_all_threads(max_page=100):
    threads = []
    for page_id in range(1, max_page):
        # visited_url = f"https://www.ultraleicht-trekking.com/forum/forum/58-philosophie/page/{page_id}"
        visited_url = f"https://www.ultraleicht-trekking.com/forum/forum/53-biete/page/{page_id}"
        actual_url, soup = parse_url(visited_url)
        if actual_url != visited_url:
            print("!! Aborting, last valid page id", page_id - 1)
            break
        threads += handle_page(soup)

    return threads

def reduce_whitespace(input_string):
    return re.sub(r'\s+', ' ', input_string).strip()


def export_csv(threads: list[ThreadFinale]):
    with open("output.csv", 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[
                                "erledigt", "title", "url", "last_comment", ])
        writer.writeheader()
        for thread in threads:
            thread.last_comment = reduce_whitespace(thread.last_comment)
            data = dataclasses.asdict(thread)
            last_comment = thread.last_comment.lower()
            keywords = ["erledigt", "verschoben"]
            data["erledigt"] = any(k for k in keywords if k in last_comment)
            writer.writerow(data)


def main():
    threads = get_all_threads(max_page=100)
    with open("threads.pkl", "wb") as f:
        pickle.dump(obj=threads, file=f)

    with open("threads.pkl", "rb") as f:
        threads = pickle.load(file=f)
    export_csv(threads=threads)

main()
