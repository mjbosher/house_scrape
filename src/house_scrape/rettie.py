import os
from typing import Optional
from datetime import datetime
import re
from house_scrape.utils import postcode_regex, write_errors, to_csv, check_row

class Rettie:
    def __init__(self, area: str, proxy, filename="houses.csv"):
        self.proxy = proxy
        self.link = "https://www.rettie.co.uk"
        self.filename = filename        
        self.areas=self.get_areas()
	        	
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
        
    def get_areas(self) -> dict:
    	areas = dict()
    	url = os.path.join(self.link,"property-sale")
    	status_code, data = self.proxy.get(url)
    	area_boxes = data.find_all("div",class_="links links-box")
    	for area in area_boxes:
    	    for link in area.find_all("a"):
    	        area_name = link.text
    	        area_link = os.path.join(self.link.rstrip("/"), link.attrs["href"].strip("/"))
    	        areas[area_name] = area_link
    	return areas

    def get_page(self, url ,page=1):
        url = os.path.join(url,"show-32/page%s"%page)
        status_code, page =self.proxy.get(url)
        is_error=bool(page.find(text="We don't have any properties at the moment that match this search."))
        if status_code != 200 or is_error:
            return None
        return page
    def parse_page(self, area, page):
        data = []
        ts = int(datetime.now().timestamp())
        agency = "rettie"
        properties =  page.find_all("div",class_=["uk-card","card-property"])
        for item in properties:
            item_link =  item.find("a")
            text = item_link.attrs["aria-label"]
            address = text.replace("Click to find out more about ","").rsplit(",",1)[0]
            price_regex = re.compile(r"£(\d|,)*")
            try:
                price_start, price_end = re.search(price_regex, item.find("span").text).span()
                price = float(item.find("span").text.replace("£","")[price_start: price_end].replace(",",""))
            except:
                price = None
            try:
                postcode_start,postcode_end = re.search(postcode_regex,text).span()
                postcode = text[postcode_start, postcode_end]
            except:
                postcode = None
            link = os.path.join(self.link,item_link.attrs["href"].strip("/"))
            
            try:
                bedroom_p = item.find(class_="icon-bed").parent.p
                bedrooms=bedroom_p.text.split(" ",1)[0]
            except:
                bedrooms=0
                
            description=item.find("p",class_=None)
            
            try:
                _,end=re.search("Bedroom",bedroom_p.text).span()   
                house_type = bedroom_p[end:]
            except:
                house_type=None

            if price is not None:
                row=[ts, agency, house_type, address, postcode, description, price, 0, 0, bedrooms, area, link]
                if check_row(self.filename, row[1:-2]):
                    print(
                        "Duplicate: row(%s) exists in file:%s" % (row[3], self.filename)
                    )
                else:
                    data.append(row)
                    print("Wrote: %s  to file" %row)
        return data    
    
    def parse_area(self,area, link):
    	page = 0
    	while True:
    	    page+=1
    	    source_code=self.get_page(link, page)
    	    if not source_code:
    	        return True
    	    data = self.parse_page(area , source_code)
    	    if data:
    	        to_csv(self.filename, data, self.headers)
    	    print(area, page)
    	return True
    	
    def parse_site(self):
        areas = self.get_areas()
        for area_name, area_link in areas.items():
            self.parse_area(area_name,area_link)
        return True    
    	
def run_rettie(proxy, place, file):
    rettie = Rettie(place, proxy, file)
    rettie.parse_site()
    return True

def find_from_rettie(proxy, place, file):
    rettie = Rettie(place, proxy, file)
    link="https://www.rettie.co.uk/property-sale/%s"%place.replace(" ","-")
    rettie.parse_area(place, link)
    return True
