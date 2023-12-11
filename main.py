from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

rootUrl = "https://taskmaster.info/show.php?id=1"

headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
}
req = Request(rootUrl, headers=headers)
html_page = urlopen(req).read()

soup = BeautifulSoup(html_page, "html.parser")

print(soup.prettify())
