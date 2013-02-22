from collections import defaultdict, Counter
from pymongo import Connection

CONNECTION_STRING = 'localhost'
DATABASE_NAME = 'fire'
INCIDENT_COLLECTION_NAME = 'incidents'
LOCATION_COLLECTION_NAME = 'locations'
START_YEAR = 2004
END_YEAR = 2012

########
# 
# THIS IS HOW TO LOAD DATA
#
#######

def load_data(connection_string=CONNECTION_STRING,
              database_name=DATABASE_NAME,
              incident_collection_name=INCIDENT_COLLECTION_NAME,
              location_collection_name=LOCATION_COLLECTION_NAME,
              start_year=START_YEAR,
              end_year=END_YEAR):
    """load the incidents and location data from Mongo"""
    connection = Connection(connection_string)
    db = connection[database_name]

    locations = {}
    for loc in db[location_collection_name].find():
        key = loc["location"]
        value = None
        # I never cleaned up the geocoder output, so that the relevant values are at
        # loc["geo"]["results"][0]["geometry"]["location"]["lat"] and ...["lng"]
        if loc and "geo" in loc and loc["geo"] and "status" in loc["geo"] and loc["geo"]["status"] == "OK":
            xy = loc["geo"]["results"][0]["geometry"]["location"]
            value = (xy["lat"],xy["lng"])
            locations[key] = value

    incidents = [i for i in db[incident_collection_name].find()
                 if i['first_date'].year >= start_year
                 and i['first_date'].year <= end_year]

    return incidents,locations

incidents, locations = load_data()

def count_checkins_by(incidents,incident_unit_grouping=(lambda (i,u): u)):
    """count the number of checkins per incident_unit_grouping"""
    return Counter([incident_unit_grouping((i,u)) for i in incidents for u in i['units']])

checkins_by_user = count_checkins_by(incidents)
checkins_by_location = count_checkins_by(incidents,lambda (i,u): i['location'])
checkins_by_hour = count_checkins_by(incidents,lambda (i,u): i['first_date'].hour)
checkins_by_date = count_checkins_by(incidents,lambda (i,u): (i['first_date'].month,i['first_date'].day))

def truck_type(firetruck):
    """find the "type" of a truck by getting rid of its numbers (not perfect, but close enough"""
    return re.sub("[0-9]","",firetruck)


