import scrapy

import urllib.parse

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
        nice_title = response.css("div.chart-number-one__title::text").extract_first()
        title = urllib.parse.quote(nice_title)
        main_artist = urllib.parse.quote(artists[0])

        yield {
            "title" : title,
            "main_artist": main_artist,
            "nice_title" : nice_title,
            "artist_string" : all_artists,
            "artists" : artists,
            "featuring": featuring,
            "position" : "1"
        }

        metacritic_page = "https://www.metacritic.com/search/album/" + title + "/results"
        yield response.follow(metacritic_page, self.parse_metacritic_score(title, main_artist))

        pitchfork_page = "https://pitchfork.com/search/?query=" + title
        yield response.follow(pitchfork_page, self.parse_pitchfork_search(title, main_artist))

        artist_search = urllib.parse.quote(artists[0])
        grammy_page = "https://www.grammy.com/search/" + artist_search
        yield response.follow(grammy_page, self.parse_grammy_search(main_artist))
        
        for album in response.css("div.chart-list-item"):
            all_artists = album.css("::attr(data-artist)").extract_first()
            all_artists, artists, featuring = split_all_artists(all_artists)
            nice_title = album.css("::attr(data-title)").extract_first()
            title = urllib.parse.quote(nice_title)
            main_artist = urllib.parse.quote(artists[0])
            yield {
                "title" : title,
                "main_artist" : main_artist,
                "nice_title" : nice_title,
                "artist_string" : all_artists,
                "artists" : artists,
                "featuring": featuring,
                "position" : album.css("::attr(data-rank)").extract_first()
            }

            metacritic_page = "https://www.metacritic.com/search/album/" + title + "/results"
            yield response.follow(metacritic_page, self.parse_metacritic_score(title, main_artist))

            pitchfork_page = "https://pitchfork.com/search/?query=" + title
            yield response.follow(pitchfork_page, self.parse_pitchfork_search(title, main_artist))

            artist_search = urllib.parse.quote(artists[0])
            grammy_page = "https://www.grammy.com/search/" + artist_search
            yield response.follow(grammy_page, self.parse_grammy_search(main_artist))

        next_page = response.css("li.dropdown__date-selector-option")[0].css("a::attr(href)").extract_first()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_metacritic_score(self, title, main_artist):
        def parse(response):
            results = response.css("div.result_wrap")
            if len(results) != 0:
                yield {
                    "title" : title,
                    "main_artist" : main_artist,
                    "metacritic_score" : results[0].css("span.metascore_w::text").extract_first()
                }
                next_page = results.css("a::attr(href)").extract_first()
                yield response.follow(next_page, self.parse_metacritic_artist(title, main_artist))
        return parse

    def parse_metacritic_artist(self, title, main_artist):
        def parse(response):
            yield {
                "title" : title,
                "main_artist" : main_artist,
                "metacritic_artist" : response.css("span.band_name::text").extract_first()
            }
        return parse

    def parse_pitchfork_search(self, title, main_artist):
        def parse(response):
            result = response.css("a.review__link::attr(href)").extract_first()
            if result is not None:
                yield response.follow(result, self.parse_pitchfork_review(title, main_artist))
        return parse
    
    def parse_pitchfork_review(self, title, main_artist):
        def parse(response):
            score = response.css("span.score::text").extract_first()
            yield {
                "title" : title,
                "main_artist" : main_artist,
                "pitchfork_score" : score
            }
        return parse

    def parse_grammy_search(self, main_artist):
        def parse(response):
            result = response.css("h2.person-group-full-name a::attr(href)").extract_first()
            if result is not None:
                yield response.follow(result, self.parse_grammy_nominations(main_artist))
        return parse
        
    def parse_grammy_nominations(self, main_artist):
        def parse(response):
            for title in response.css("span.field-content::text").extract():
                yield {
                    "title" : urllib.parse.quote(title),
                    "main_artist" : main_artist,
                    "grammy" : "1"
                }
        return parse
