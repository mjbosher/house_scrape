import os

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
    	        area_link = os.path.join(self.link, link.attrs["href"])
    	        areas[area_name] = area_link
    	return areas
	
def run_rettie(proxy, place, file):
    rettie = Rettie(place, proxy, file)
    rettie.get_areas()
    #espc.parse_areas()
    # espc.parse_site()
    return True

def find_from_rettie(proxy, place, file):
    espc = Rettie(place, proxy, file)
    #espc.parse_site()
    #should parse areas
    return True
