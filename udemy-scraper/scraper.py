import json
import os

import extruct as extruct
import requests
from bs4 import BeautifulSoup

from libs.file.csv_tools import load_not_empty_lines
from libs.file.excel import print_2_excel_file


def get_request_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        # "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "x-api-key": "18f057d42feadf59b4943b7fb4c064fcd626778f",  # noqa
    }


class URLInfo:
    def __init__(self, url):
        self.url = url
        self.metadata = {}
        self.text = self.get_url_text()
        self.converted = self.convert(self.text, "https://www.udemy.com/")

    def get_url_text(self):
        # cookies = {"ud_cache_language": "ru", "ud_cache_brand": "UZru_RU", }
        # response = requests.get(self.url, headers=get_request_headers(), cookies=cookies, timeout=10)
        response = requests.get(self.url, headers=get_request_headers(), timeout=10)
        return response.text

    @classmethod
    def get_num_students(cls, text):
        bs = BeautifulSoup(text, "lxml")
        res: str = bs.select_one('div[data-purpose="enrollment"]').text
        res = res.replace("\xa0", "")
        res_int = 0
        try:
            res_int = int(res.split()[0])
        except ValueError:
            pass
        return res_int

    def convert(self, text, base_url):
        converted = extruct.extract(text, base_url=base_url)
        json_ld = converted["json-ld"][0]
        self.metadata["name"] = json_ld["name"]
        self.metadata["authors"] = ";".join([row["name"] for row in json_ld["creator"]])
        self.metadata["description"] = json_ld["description"]
        self.metadata["audienceType"] = "\n".join([at for at in json_ld["audience"]["audienceType"]])
        self.metadata["inLanguage"] = json_ld["inLanguage"]
        self.metadata["rating"] = json_ld["aggregateRating"]
        self.metadata["num_students"] = self.get_num_students(text)
        return converted

    @classmethod
    def get_fields(cls):
        return [
            "URL", "Title", "Authors", "Lang", "Number Students", "Rating Count", "Rating Value",
            "Audience Type", "Desc",
        ]

    def to_list(self):
        return [
            self.url, self.metadata["name"], self.metadata["authors"],
            self.metadata["inLanguage"], self.metadata["num_students"],
            self.metadata["rating"]["ratingCount"],
            float(self.metadata["rating"]["ratingValue"]),
            self.metadata["audienceType"],
            self.metadata["description"],
        ]


class Scraper:
    def __init__(self, urls):
        self.urls = urls
        self.data_src = []
        self.data = []
        self.process_urls()
        self.dump_info()

    def process_urls(self):
        for i, url in enumerate(self.urls):
            info = URLInfo(url)
            self.data_src.append(info)
            self.data.append([i + 1] + info.to_list())
        fields = URLInfo.get_fields()
        sort_fields_idx = [fields.index(field) + 1 for field in ["Number Students", "Rating Count", ]]
        self.data = sorted(self.data, key=lambda row: [-row[f] for f in sort_fields_idx])

    @classmethod
    def get_file_links(cls, filename):
        return load_not_empty_lines(os.path.join("in_files", filename))

    def dump_info(self):
        with open(os.path.join("out_files", "udemy_dump.json"), "w", encoding="utf-8") as f:
            f.write(json.dumps([row.converted for row in self.data_src], indent=8))


def main():
    links = Scraper.get_file_links("udemy_courses.txt")
    scraper = Scraper(links)

    print_2_excel_file(
        os.path.join("out_files", "udemy_courses.xlsx"), scraper.data, ["no"] + URLInfo.get_fields(),
        default_column=20
    )


if __name__ == "__main__":
    main()
