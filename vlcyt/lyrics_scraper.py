import requests
from bs4 import BeautifulSoup


def get_lyrics(song_title):
    """
    Returns lyrics for a passed in song title.
    """
    with requests.session() as c:
        url = r"https://search.azlyrics.com/search.php?"

        query = {"q": song_title}
        r = requests.get(url, params=query)

        soup = BeautifulSoup(r.content, "html.parser")
        lyrics_url = soup.td.a["href"]
        if "http" not in lyrics_url:
            lyrics_url = url + lyrics_url[1:]
            lyrics_url = lyrics_url[0 : lyrics_url.find("&")]

        r2 = requests.get(lyrics_url)
        soup2 = BeautifulSoup(r2.content, "html.parser")
        lyrics = soup2.select("div.col-xs-12:nth-child(2) > div:nth-child(8)")
        return lyrics[0].get_text()

def main():
    pass

if __name__ == "__main__":
    main()
