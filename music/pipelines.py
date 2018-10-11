# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import hashlib
import json

class MusicPipeline(object):
    
    def __init__(self):
        self.albums = {}
        
    def process_item(self, item, spider):
        hash_string = item["title"]#hashlib.sha256(item["title"].encode() + item["artist_string"].encode()).hexdigest()
        if self.albums.get(hash_string) is not None:
            if item.get("position") is not None:
                if self.albums[hash_string]["position"] < item["position"]:
                    self.albums[hash_string]["position"] = item["position"]
                else:
                    for k in item:
                        self.albums[hash_string][k] = item[k]
            else:
                for k in item:
                    self.albums[hash_string][k] = item[k]
        else:
            self.albums[hash_string] = item
        return item

    def close_spider(self, spider):
        print(len(list(self.albums.values())))
        with open("billboard.json", "w") as f:
            f.write(json.dumps(list(self.albums.values())))
        pass
