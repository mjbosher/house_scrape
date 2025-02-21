from enum import Enum
import os
from house_scrape.utils import TimedRequests
from house_scrape.espc import run_espc, find_from_espc
from house_scrape.rettie import run_rettie, find_from_rettie

class Agencies(Enum):
    espc = False
    rettie=True


def main(proxy, place, file):
    for agency in Agencies:
        if agency.value == True:
            print("STARTING SCAPE for %s" % agency.name)
            func = eval(f"run_{agency.name}") if not place else eval(f"find_from_{agency.name}")
            func(proxy, place, file)


if __name__ == "__main__":
    proxy = TimedRequests(limit=100, time=5)
    place = None

    directory = "data"
    if place:
        file = f"{os.path.join(directory, place)}.csv"
    else:
        file = f"{os.path.join(directory, 'scotland')}.csv"

    main(proxy, place, file)
