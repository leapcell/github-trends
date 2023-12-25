import requests
from bs4 import BeautifulSoup
import os
from leapcell import Leapcell
import datetime

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}


leapclient = Leapcell(
    os.environ.get("LEAPCELL_API_KEY"),
)

table = leapclient.table("issac/github-trends", "tbl1739307213509033984")

def get_owner_pic(url):
    print(url)
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    img_element = soup.find("img", {"class": "avatar-user"})
    img =img_element["src"] if img_element else ""

    # delete all query string
    if "?" in img:
        img = img.split("?")[0]

    return img

def get_all_trending():
    url = "https://github.com/trending"
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")

    repos = soup.find_all("article", {"class": "Box-row"})

    today = datetime.datetime.now().strftime("%Y-%m-%d")

    data = []
    for repo in repos:
        title_element = repo.find("h2")
        title = title_element.text.strip() if title_element else ""
        title = title.replace("\n", "").replace(" ", "")
        desc_elem = repo.find("p")
        description = desc_elem.text.strip() if desc_elem else ""
        url = "https://github.com" + repo.find("a", {"class": "Link"})["href"]
        star_today = repo.find("span", {"class": "d-inline-block float-sm-right"}).text.strip()
        star_today = "".join([s for s in star_today.split() if s.isdigit()])
        stars = 0
        if star_today:
            stars = int(star_today)
        
        language = repo.find("span", {"itemprop": "programmingLanguage"}).text.strip() if repo.find("span", {"itemprop": "programmingLanguage"}) else ""

        avatar = get_owner_pic(url)

        item = {
            "name": title,
            "description": description,
            "url": url,
            "star_today": stars,
            "language": language,
            "avatar": avatar,
            "date": today,
        }
        print(item)

        data.append(item)

        table.upsert(item, on_conflict=["name", "date"])

    return data


if __name__ == "__main__":
    get_all_trending()