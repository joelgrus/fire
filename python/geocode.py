import urllib2
import json
import datetime
import sys

from fire import *
from pymongo import ASCENDING, DESCENDING

GEOCODER_URL = 'http://localhost:8080/maps/api/geocode/json'

def good_loc(bad_loc):
    """poor-man's-URL-encode a scraped location, and add "Seattle, WA" onto the end"""
    return bad_loc.replace('  ',' ').replace(' ','+').replace('/','+at+') + ',+seattle,+wa'

def json_loc(bad_loc,geocoder_url):
    """turn a scraped location into a geocoder url to retrieve"""
    return geocoder_url + '?sensor=false&address=' + good_loc(bad_loc)

    locations = { i['location'] : None
              for i in incidents }

def geocode(location_list,geocoder_url=GEOCODER_URL):
    """take a list of locations and return a dictionary with the locations as the keys and the geocoding result as the value"""
    opener = urllib2.build_opener()

    loc_dict = {}

    count = 0
    for loc in remaining_locs:
        if count % 1000 == 0:
            print count,datetime.datetime.now(),loc
        count += 1
        try:
            jl = json_loc(loc,geocoder_url)
            req = urllib2.Request(jl)
            f = opener.open(req)
            loc_dict[loc] = json.load(f)
        except:
            print sys.exc_info()[0]
    return loc_dict

def persist_locations(location_dict,
                      connection_string=CONNECTION_STRING,
                      database_name=DATABASE_NAME,
                      location_collection_name=LOCATION_COLLECTION_NAME):
    "persist the locations to mongo"
    connection = Connection(connection_string)
    db = connection[collection_name]
    locs_coll = db[location_collection_name]
    locs_coll.create_index([("location",ASCENDING)])

    c = 1
    for (loc,geo) in locations.iteritems():
        if c % 1000 == 0:
            print c,loc
        locs_coll.insert(
            {"location" : loc,
              "geo" : geo})
        c += 1