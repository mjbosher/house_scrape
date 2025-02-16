from enum import Enum
from house_scrape.utils import TimedRequests
from house_scrape.espc import run_espc
import os


class Agencies(Enum):
    espc = True


def main(proxy, place, file):
    for agency in Agencies:
        if agency.value == True:
            print("STARTING SCAPE for %s" % agency.name)
            func = eval(f"run_{agency.name}")
            func(proxy, place, file)


if __name__ == "__main__":
    proxy = TimedRequests(limit=100, time=5)
    place = "scotland"

    directory = "data"
    file = f"{os.path.join(directory, place)}.csv"

    main(proxy, place, file)
