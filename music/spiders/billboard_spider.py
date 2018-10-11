import scrapy

import urllib

def split_artists(artists_string):
    artists = []
    for i in artists_string.split(", "):
        for i2 in i.split(" & "):
            artists.append(i2)
    return artists
        

def split_all_artists(all_artists):
    artists_split = all_artists.split(" Featuring ")
    
    featuring = []
    if len(artists_split) > 1:
        featuring = split_artists(artists_split[1])
            
    artists = split_artists(artists_split[0])
    
    return all_artists, artists, featuring


class Billboard200Crawler(scrapy.Spider):
    name = "billboard"
    start_urls = [
        "https://www.billboard.com/charts/billboard-200"
    ]
        
    def parse(self, response):
        raw_artists = response.css("div.chart-number-one__artist").extract_first()
        for data in raw_artists.split("\n"):
            if data[0] != "<":
                all_artists = data
                break
        all_artists, artists, featuring = split_all_artists(all_artists)
        title = urllib.parse.quote_plus(response.css("div.chart-number-one__title::text").extract_first())

        yield {
            "title" : title,
            "artist_string" : all_artists,
            "artists" : artists,
            "featuring": featuring,
            "position" : 1
        }

        metacritic_page = "https://www.metacritic.com/search/album/" + title + "/results"
        yield response.follow(metacritic_page, self.parse_metacritic)

        pitchfork_page = "https://pitchfork.com/search/?query=" + title
        yield response.follow(pitchfork_page, self.parse_pitchfork_search(title))

        for album in response.css("div.chart-list-item"):
            all_artists = album.css("::attr(data-artist)").extract_first()
            all_artists, artists, featuring = split_all_artists(all_artists)
            title = urllib.parse.quote_plus(album.css("::attr(data-title)").extract_first())
            yield {
                "title" : title,
                "artist_string" : all_artists,
                "artists" : artists,
                "featuring": featuring,
                "position" : int(album.css("::attr(data-rank)").extract_first())
            }

            metacritic_page = "https://www.metacritic.com/search/album/" + title + "/results"
            yield response.follow(metacritic_page, self.parse_metacritic)

            pitchfork_page = "https://pitchfork.com/search/?query=" + title
            yield response.follow(pitchfork_page, self.parse_pitchfork_search(title))

        next_page = response.css("li.dropdown__date-selector-option")[0].css("a::attr(href)").extract_first()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_metacritic(self, response):
        results = response.css("div.result_wrap")
        if len(results) != 0:
            yield {
                "title" : response.url[40:-8],
                "metacritic_score" : results[0].css("span.metascore_w::text").extract_first()
            }

    def parse_pitchfork_search(self, title):
        def parse(response):
            result = response.css("a.review__link::attr(href)").extract_first()
            if result is not None:
                yield response.follow(result, self.parse_pitchfork_review(title))
        return parse
    
    def parse_pitchfork_review(self, title):
        def parse(response):
            score = response.css("span.score::text").extract_first()
            yield {
                "title" : title,
                "pitchfork_score" : score
            }
        return parse
