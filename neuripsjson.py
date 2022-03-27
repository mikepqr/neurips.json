import asyncio
import datetime as dt
import json
import sys

import bs4
import httpx
import tqdm
import tqdm.asyncio

urlroot = "https://papers.nips.cc"

limits = httpx.Limits(max_keepalive_connections=4, max_connections=8)


async def add_abstract_to_paper_with_client(paper, client):
    text = (await client.get(paper["url"])).text
    page = bs4.BeautifulSoup(text, "html.parser")
    try:
        ps = page.find("h4", text="Abstract").find_next_siblings("p")
        abstract = "\n".join(p.text for p in ps).strip()
    except AttributeError:
        abstract = ""
    return {**paper, **{"abstract": abstract}}


def get_paper_from_li(bullet):
    titlelink = bullet.find_next("a")
    url = urlroot + titlelink.attrs["href"]
    title = titlelink.text
    authors = [a.strip() for a in bullet.find_next("i").text.split(",")]
    return {"title": title, "authors": authors, "url": url}


def get_papers_from_url(url):
    r = httpx.get(url)
    r.raise_for_status()
    page = bs4.BeautifulSoup(r.text, "html.parser")
    papers = [
        get_paper_from_li(li)
        for li in page.find("div", "container-fluid").find_all("li")
    ]
    return papers


async def get_year(year):
    papers = get_papers_from_url(f"{urlroot}/paper/{str(year)}")
    for paper in papers:
        paper["year"] = year
    async with httpx.AsyncClient(timeout=None, limits=limits) as client:
        tasks = [add_abstract_to_paper_with_client(paper, client) for paper in papers]
        papers = await tqdm.asyncio.tqdm.gather(*tasks, desc=str(year))
    return papers


async def get_all_years(last_year=None):
    if last_year is None:
        last_year = dt.datetime.now().year - 1
    years = []
    for year in range(1987, last_year + 1):
        years.append(await get_year(year))
    return sum(years, [])


async def load_and_append_year(year):
    with open("neurips.json") as infile:
        old_papers = json.load(infile)
    print("Loaded {} papers from neurips.json".format(len(old_papers)))
    new_papers = await get_year(year)
    print("Added {} papers from {}".format(len(new_papers), year))
    return old_papers + new_papers


def print_usage_and_exit():
    usage = "command must be one of 'create' or 'add <year>'"
    print(usage)
    raise SystemExit(1)


if __name__ == "__main__":
    try:
        command = sys.argv[1]
    except IndexError:
        print_usage_and_exit()

    if command == "add":
        try:
            year = sys.argv[2]
        except (IndexError, ValueError):
            print_usage_and_exit()
        papers = asyncio.run(load_and_append_year(year))
    elif command == "create":
        papers = asyncio.run(get_all_years())
    else:
        print_usage_and_exit()

    with open("neurips.json", "w") as fp:
        json.dump(papers, fp, indent=2)
