import requests
from bs4 import BeautifulSoup
import os
from time import sleep
import csv
import re

postcode_regex = re.compile(
    r"^([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([AZa-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9]?[A-Za-z])))) [0-9][A-Za-z]{2})$"
)


def write_errors(errors: list, filename: str):
    if os.path.exists(filename):
        file = open(filename, "a")
    else:
        file = open(filename, "w")

    for error in errors:
        file.write(error + "\n")
    file.close()


def to_csv(filename: str, data: list, headers: list):
    if os.path.exists(filename):
        f = open(filename, "a")
    else:
        f = open(filename, "w")
        data.insert(0, headers)

    writer = csv.writer(f)
    writer.writerows(data)

    f.close()
    return True

def check_row(filename, row):
    if os.path.exists(filename):
        f = open(filename, "r").readlines()
        existing_data = [value.split(",")[1:-2] for value in f]
        if row in existing_data:
            return True
    return False
    
class TimedRequests:
    def __init__(self, limit=15, time=10):
        self.time = time * 60
        self.limit = limit
        self.count = 0

    def get(self, site, soup=True):
        self.count += 1
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/29.0"
        }
        # scrape the website with the following header
        if self.count >= self.limit:
            self.count = 0
            sleep(self.time)
        if soup == False:
            return requests.get(site, headers=header)
        try:
            response = requests.get(site, headers=header)
            status_code = response.status_code
            site_data = response.text
        except:
            site_data = " "
        return status_code, BeautifulSoup(site_data, "html5lib")
