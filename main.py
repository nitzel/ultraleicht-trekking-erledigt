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
class ThreadInfo():
    title: str
    url: str
    last_comment: str
    last_comment_by_author: bool
    """
    If true, the creator of the thread is the author of the last comment.
    However, this is `False` for the first comment of a thread!
    """

    timestamp: str
    """Timestamp of the last comment, isoformat"""


def handle_thread(thread: Tag) -> ThreadInfo:
    title = thread.text.strip()
    href = thread.attrs.get('href')
    href = urljoin(href, "?do=getLastComment")
    _, thread_soup = parse_url(href)

    last_comment = thread_soup.select_one(".cPost:last-of-type")

    has_author_badge = len(last_comment.select(".ipsComment_authorBadge")) > 0

    last_comment_text = last_comment.select_one(
        "[data-role='commentContent']").text.strip()

    timestamp_isoformat = last_comment.select_one(
        "time[datetime]").attrs.get("datetime")

    print("-", title)
    print("  -", href)
    print("  -", timestamp_isoformat)
    print("  -", "author_badge" if has_author_badge else "no author_badge")

    return ThreadInfo(
        title=title,
        url=href,
        last_comment=last_comment_text,
        timestamp=timestamp_isoformat,
        last_comment_by_author=has_author_badge,
    )


def handle_page(page_soup: BeautifulSoup) -> list[ThreadInfo]:
    selector = ".cTopicList .ipsDataItem_title .ipsContained a"
    threads = page_soup.select(selector)

    return [handle_thread(t) for t in threads]


def get_all_threads(max_page=100) -> list[ThreadInfo]:
    threads = []
    for page_id in range(1, max_page + 1):
        visited_url = f"https://www.ultraleicht-trekking.com/forum/forum/53-biete/page/{page_id}"
        print("Visiting", visited_url)
        actual_url, soup = parse_url(visited_url)
        if actual_url != visited_url:
            print("!! Aborting, last valid page id", page_id - 1)
            break
        threads += handle_page(soup)
    return threads


def reduce_whitespace(input_string):
    return re.sub(r'\s+', ' ', input_string).strip()


def export_csv(threads: list[ThreadInfo], filename: str):
    with open(filename, 'w', newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[
                "timestamp",
                "erledigt",
                "last_comment_by_author",
                "title",
                "url",
                "last_comment",
            ]
        )
        writer.writeheader()
        for thread in threads:
            thread.last_comment = reduce_whitespace(thread.last_comment)
            data = dataclasses.asdict(thread)
            last_comment = thread.last_comment.lower()
            keywords = ["erledigt", "verschoben"]
            data["erledigt"] = any(k for k in keywords if k in last_comment)
            writer.writerow(data)


def main():
    # Get last message from all threads
    threads = get_all_threads(max_page=50)

    # use cache to store them for development
    with open("threads.pkl", "wb") as f:
        pickle.dump(obj=threads, file=f)

    with open("threads.pkl", "rb") as f:
        threads = pickle.load(file=f)

    export_csv(threads=threads, filename="output.csv")


if __name__ == "__main__":
    print("Starting")
    main()
