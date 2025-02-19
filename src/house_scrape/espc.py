import os
from OSGridConverter import grid2latlong, latlong2grid
import re
from datetime import datetime
from house_scrape.utils import postcode_regex, write_errors, to_csv


def check_row(filename, row):
    if os.path.exists(filename):
        f = open(filename, "r").readlines()
        existing_data = [value.split(",")[1:-2] for value in f]
        if row in existing_data:
            return True
    return False


class ESPC:
    def __init__(self, area: str, proxy, filename="houses.csv"):
        self.proxy = proxy
        self.area = area
        self.link = "https://espc.com"
        self.filename = filename
        self.headers = [
            "ts",
            "agency",
            "house_type",
            "address",
            "postcode",
            "description",
            "price",
            "bathrooms",
            "living_rooms",
            "bedrooms",
            "area",
            "link",
        ]

    def parse_page(self, page=1):

        self.site = "https://espc.com/properties?ps=50&locations=%s" % self.area
        if page > 1:
            self.site += "&p=%s" % page

        status_code, self.data = self.proxy.get(self.site)
        no_response_text = "Sorry, we found no results which matched your selected criteria. Refine your search."
        if (
            self.data.title == "Server Error"
            or no_response_text in self.data.text
            or status_code != 200
        ):
            return None
        house_list = []
        houses = self.data.find_all("div", class_="propertyWrap")
        for house in houses:
            try:
                property_title = house.find("h3", class_="propertyTitle")
                address = property_title.find_all("span")

                house_type = address[0].text
                full_address = address[1].parent.text
                postcode_search = re.search(postcode_regex, full_address)
                start, stop = postcode_search.span()
                postcode = full_address[start:stop]
                full_address = (
                    full_address.replace(house_type, "").strip().replace(",", "")
                )

                description = house.find("div", class_="description").text.replace(
                    ",", ""
                )
                price = (
                    house.find("span", class_="price")
                    .text.replace("£", "")
                    .replace(",", "")
                )
                bathrooms = house.find("span", class_="icon bath").parent.text
                living_rooms = house.find("span", class_="icon couch").parent.text
                bedrooms = house.find("span", class_="icon bed").parent.text
                link = os.path.join(self.link, house.a.attrs["href"].strip("/"))

                ts = int(datetime.now().timestamp())
                agency = "ESPC"
                row = [
                    ts,
                    agency,
                    house_type,
                    full_address,
                    postcode,
                    description,
                    price,
                    bathrooms,
                    living_rooms,
                    bedrooms,
                    self.area,
                    link,
                ]

                for n, value in enumerate(row):
                    if isinstance(value, str):
                        for char in ["\n", ",", "'", '"']:
                            row[n] = row[n].replace(char, "")

                if check_row(self.filename, row[1:-2]):
                    print(
                        "Duplicate: row(%s) exists in file:%s" % (row[3], self.filename)
                    )
                else:
                    house_list.append(row)
                    print("Wrote: %s, %s to file" % (full_address, price))
            except AttributeError as e:
                print(e)
            except IndexError as e:
                print(e)
        return house_list

    def parse_site(self):
        page = 1
        while True:
            print("Parsing page %s" % page)
            data = self.parse_page(page)
            if data is None:
                return
            page += 1
            if data:
                to_csv(self.filename, data, self.headers)
        return True

    def get_areas(self):
        url = "https://espc.com/areas"
        status_code, data = self.proxy.get(url)
        areas = [
            link
            for link in data.find_all("a")
            if link.attrs.get("href", "").startswith("/areas/")
            and re.match("^\\w*", link.text).group()
        ]
        area_dict = dict()
        for area in areas:
            area_name = area.text
            area = area.attrs["href"].rsplit("/", 1)[-1]
            area_dict[area_name] = area
            area_url = os.path.join(url, area)
            status_code, data = self.proxy.get(area_url)
            if status_code == 200:
                new_areas = [
                    link
                    for link in data.find_all("a")
                    if link.attrs.get("href", "").startswith("/areas/")
                    and re.match("^\\w*", link.text).group()
                ]
                for new_area in new_areas:
                    new_area_name = new_area.text
                    new_area = new_area.attrs["href"].rsplit("/", 1)[-1]
                    area_dict[new_area_name] = new_area
        return area_dict

    def parse_areas(self):
        for area_name, area_link in self.get_areas().items():
            print(area_name)
            self.area = area_link
            self.parse_site()


def run_espc(proxy, place,file):
    espc = ESPC(place, proxy, file)
    espc.parse_areas()
    return True

def find_from_espc(proxy, place, file):
    espc = ESPC(place, proxy, file)
    espc.parse_site()
    return True
