#!/usr/bin/env python3
import re
from sys import argv
from urllib.error import URLError, HTTPError
from urllib.request import urlopen
from urllib.parse import quote, unquote
from queue import Queue
from bs4 import BeautifulSoup


def get_content(name):
    url = f"https://ru.wikipedia.org/wiki/{quote(name, safe='()_,-/')}"
    try:
        with urlopen(url) as page:
            return page.read().decode('utf-8', errors='ignore')
    except (URLError, HTTPError):
        return None


def extract_content(page):
    if page is None:
        return 0, 0
    start_tag = '<div id="mw-content-text"'
    end_tag = '<div class="printfooter"'
    start = page.find(start_tag)
    end = page.find(end_tag)
    if start != -1 and end != -1:
        return start, end
    return 0, 0


def extract_links(page, begin, end):
    content = page[begin:end]
    soup = BeautifulSoup(content, features="html.parser")
    links = set()
    for link in soup.find_all("a"):
        link_href = link.get('href')
        if link_href and is_wikipedia_article(link_href):
            page_name = extract_page_name(link_href)
            if page_name:
                links.add(page_name)
    return list(links)


def is_wikipedia_article(link):
    if ":" in link:
        return False
    wiki_link_pattern = re.compile(r'^/wiki/[^#]+$')
    return bool(wiki_link_pattern.match(link))


def extract_page_name(link):
    result = link.replace('/wiki/', '')
    anchor_index = link.find('#')
    if anchor_index != -1:
        result = result[:anchor_index]
    return unquote(result) if result else None


def find_chain(start, finish):
    if start.lower() == finish.lower():
        return [start]
    queue = Queue()
    queue.put(start)
    visited = {start: None}
    while not queue.empty():
        current = queue.get()
        content = get_content(current)
        if content is None:
            continue
        begin, end = extract_content(content)
        links = extract_links(content, begin, end)
        for link in links:
            if link.lower() == finish.lower():
                visited[link] = current
                return make_chain(link, visited)
            if link not in visited:
                visited[link] = current
                queue.put(link)
    return None


def make_chain(finish, visited):
    chain = []
    current = finish
    while current is not None:
        chain.append(current)
        current = visited[current]
    return chain[::-1]


def main():
    # if len(argv) < 2:
    #     print("Page name expected")
    #     return
    # chain = find_chain(argv[1], "Философия")
    chain = find_chain("Бумага", "Философия")
    if chain is not None:
        for link in chain:
            print(link)


if __name__ == '__main__':
    main()
