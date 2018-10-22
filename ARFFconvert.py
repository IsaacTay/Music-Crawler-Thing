import json

def main():
    with open("albums.arff", "w+") as out_file, open("billboard.json", "r") as in_file:
        out_file.write("@RELATION albums\n\n")
        arff_attr = [("name", "string"),
                     ("artist", "string"),
                     ("billboard", "numeric"),
                     ("metacritic", "numeric"),
                     ("pitchfork", "numeric"),
                     ("grammy", "numeric")
        ]
        for (attr_name, attr_type) in arff_attr:
            out_file.write("@ATTRIBUTE " + attr_name + " " + attr_type + "\n")
        out_file.write("\n@data\n")        
        for album in json.loads(in_file.read()):
            if album.get("position") is not None:
                artist = album.get("metacritic_artist")
                if artist is None:
                    artist = album["artists"][0]
                out_file.write(",".join([album["title"], artist, album["position"], album.get("metacritic_score", "?"), album.get("pitchfork_score", "?"), album.get("grammy", "0")]) + "\n")

if __name__ == "__main__":
    main()
