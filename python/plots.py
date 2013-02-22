from mpl_toolkits.basemap import Basemap
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import fire

def plot_seattle(lons,lats,sizes=1,colors='r',marker='o',texts=None):
    """Given a list of longitudes and a list of latitudes, plot them on a map of Seattle using the specified sizes, colors, and markers."""
    m = Basemap(projection='merc',
                llcrnrlat=47.475,
                urcrnrlat=47.75,
                llcrnrlon=-122.4725,
                urcrnrlon=-122.225,
                resolution='h')
    m.drawcoastlines()

    x, y = m(lons,lats)
    m.scatter(x,y,s=sizes,color=colors,marker=marker,zorder=10)
    m.drawcoastlines()
    m.drawmapboundary(fill_color='#99ffff')
    m.fillcontinents(color='#ffff99',lake_color='#99ffff')
    plt.ion()
    plt.show()    
    
def plot_incidents(incidents,
                 locations,
                 type_re=None,
                 map_location_to_xy=(lambda x,y: (x,y)),
                 count_incident_as=(lambda i: len(i['units'])),
                 scale_size=False,
                 resize_by=(lambda x: 1),
                 marker='o'):
    """Given a list of incidents and a dictionary of locations (key = address, value = (lat,lng)), plot them on the map of Seattle.
        type_re is a regular expression to filter incident types (e.g. "Assault")
        map_location_to_xy can be modified to (e.g.) "snap to grid"
        count_incident_as allows us to count all checkins, only certain incidents, only once per incident, etc...
        if scale_size is true, size is rescaled to be between 0 (min) and 1 (max), before calling
        resize_by, which maps a raw count to a desired size"""
    rounds = defaultdict(int)
    for incident in incidents:
        loc = incident["location"]
        if loc in locations and locations[loc] and (type_re is None or re.search(type_re,incident['type'])):
            lat,lng = locations[loc]
            rlat,rlng = map_location_to_xy(lat,lng)
            c = count_incident_as(incident)
            if c > 0:
                rounds[(rlat,rlng)] += c
    
    rlats = [ll[0] for ll in rounds]
    rlons = [ll[1] for ll in rounds]
    max_incidents = max(rounds.values()) * 1.0
    if scale_size:
        sizes = [resize_by(i / max_incidents) for i in rounds.values()]
    else:
        sizes = [resize_by(i) for i in rounds.values()]
    colors = [(1.0,0.5 - 0.5 * i / max_incidents,0.5 - 0.5 * i / max_incidents,.75) for i in rounds.values()]
    plot_seattle(rlons,rlats,sizes,colors,marker)

def round_off(lat,lng,factor=200.0):
    """round a latitude and longitude to the nearest 1 / factor of a degree"""
    rlat = round(lat * factor) / factor
    rlon = round(lng * factor) / factor
    return (rlat,rlon)    

# based on # of checkins, snap to grid, radius ~ sqrt

incidents = fire.incidents
locations = fire.locations

plot_incidents(incidents,locations,
               map_location_to_xy=round_off,
               resize_by=(lambda x: x ** 0.5))

# just E31:

UNIT = 'E31'

plot_incidents(incidents,locations,
               map_location_to_xy=round_off,
               count_incident_as=(lambda i: 1 if UNIT in i['units'] else 0),
               resize_by=(lambda x: x ** 0.5))


# one point per incident
plot_incidents(incidents,locations)

# fires

plot_incidents(incidents,
               locations,
               type_re='(?i)(fire$|fire [^a])',
               resize_by=(lambda x: x))

# assaults           
               
plot_incidents(incidents,
               locations,
               type_re='(?i)(assault)',
               resize_by=(lambda x: x))


# average centroid of solo checkins for E trucks

CUTOFF = 100
counts_by_unit = fire.count_checkins_by(incidents)
good_units = set([u
                  for (u,c) in counts_by_unit.iteritems()
                  if c >= CUTOFF])

locs_by_unit = {u : [] for u in good_units}

for i in incidents:
    if len(i["units"]) <= 1:
        loc = i["location"]
        if loc in locations and locations[loc]:
            lat,lng = locations[loc]
            for u in i['units']:
                if u in good_units:
                    locs_by_unit[u].append((lat,lng))

def median(lst):
    n = len(lst)
    s = sorted(lst)
    if n == 0:
        return None
    elif n % 2 == 0:
        return 0.5 * s[n / 2 - 1]  + 0.5 * s[n / 2]
    else:
        return s[n / 2]
    

unit_centers = {}
for u,locs in locs_by_unit.iteritems():
    lat = median([ll[0] for ll in locs])
    lng = median([ll[1] for ll in locs])
    unit_centers[u] = (lat,lng)

max_incidents = max([len(locs) for locs in locs_by_unit.values()])
MIN_FONT_SIZE = 8
MAX_FONT_SIZE = 36

def font_size(num_incidents):
    return 1.0 * MIN_FONT_SIZE + (MAX_FONT_SIZE - MIN_FONT_SIZE) * num_incidents / max_incidents

m = Basemap(projection='merc',
            llcrnrlat=47.475,
            urcrnrlat=47.75,
            llcrnrlon=-122.4725,
            urcrnrlon=-122.225,
            resolution='h')
m.drawcoastlines()

for (u,(lat,lng)) in unit_centers.iteritems():
    if u[0] in ['E'] and lng and lat:
        color = 'k'
        x,y = m(lng,lat)
        plt.text(x,y,u,color=color,fontsize=font_size(len(locs_by_unit[u])),zorder=10)
m.drawcoastlines()
m.drawmapboundary(fill_color='#99ffff')
m.fillcontinents(color='#ffff99',lake_color='#99ffff')
plt.ion()
plt.show()

