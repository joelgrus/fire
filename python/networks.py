from collections import Counter, defaultdict
import networkx as nx
import re
import math
import fire

MIN_CHECKINS = 100
MIN_CONNECTIONS = 100

def compute_connections(incidents,
                incident_filter=(lambda i: True),
                min_checkins = MIN_CHECKINS):

    counts_by_unit = fire.count_checkins_by(incidents)
    good_units = set([u
                      for (u,c) in counts_by_unit.iteritems()
                      if c >= min_checkins])

    # compute connections

    connections = { u: defaultdict(int)
                    for u in good_units }

    for i in incidents:
        if incident_filter(i):
            gus = [u for u in i['units'] if u in good_units]
            for u1 in gus:
                for u2 in gus:
                    if u1 != u2:
                        connections[u1][u2] += 1
                        
    return connections, counts_by_unit

def make_networkx_graph(incidents,
                        incident_filter=(lambda i: True),
                        min_checkins=MIN_CHECKINS,
                        min_connections=MIN_CONNECTIONS):
    
    G = nx.Graph()

    connections, counts_by_unit = compute_connections(incidents,incident_filter,min_checkins)
    
    for unit in connections:
        G.add_node(unit)
    
    for u1 in connections:
        for u2 in connections[u1]:
            if connections[u1][u2] >= min_connections and u1 < u2:
                G.add_edge(u1,u2)

    return G
    
def centrality_and_avg_checkin_size(incidents,G):
    
                
def gexf(incidents,
         output_file,
         incident_filter=(lambda i: True),
         min_checkins = MIN_CHECKINS,
         min_connections = MIN_CONNECTIONS,
         weighted_edges = False):
    """create gexf file suitable for gephi-ing."""

    connections, counts_by_unit = compute_connections(incidents,incident_filter,min_checkins)

    try:
        f = open(OUTFILE,"w")

        f.write("""<?xml version="1.0" encoding="UTF-8"?>
        <gexf xmlns="http://www.gexf.net/1.2draft" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.gexf.net/1.2draft http://www.gexf.net/1.2draft/gexf.xsd" version="1.2">
            <meta lastmodifieddate="2009-03-20">
                <creator>Joel</creator>
                <description>Fire Trucks</description>
            </meta>
            <graph defaultedgetype="undirected">
                <attributes class="node">
                    <attribute id="0" title="name" type="string"/>
                    <attribute id="1" title="type" type="string"/>
                    <attribute id="2" title="incidents" type="integer"/>
                </attributes>
                <nodes>""")

        node_id = 0
        truck_to_id = {}
        for firetruck in connections:
            truck_to_id[firetruck] = node_id
            f.write('<node id="' + str(node_id) + '" label="' + firetruck + '">')
            f.write('<attvalues>')
            f.write('<attvalue for="0" value="' + firetruck + '"/>')
            f.write('<attvalue for="1" value="' + fire.truck_type(firetruck) + '"/>')
            f.write('<attvalue for="2" value="' + str(counts_by_unit[firetruck]) + '"/>')
            f.write('</attvalues></node>')
            node_id += 1

        f.write("</nodes><edges>")
        edge_id = 0

        for ft1,ft2s in connections.iteritems():
            for ft2 in ft2s:
                num_connections = connections[ft1][ft2]
                if ft1 < ft2 and num_connections >= min_connections:
                    node1 = str(truck_to_id[ft1])
                    node2 = str(truck_to_id[ft2])
                    weight = num_connections if weighted_edges else 1
                    f.write('<edge id="' + str(edge_id) + '" source="' + node1 + '" target="' + node2 + '" weight="' + weight + '"/>')
                    edge_id += 1
                    
        f.write("</edges></graph></gexf>")
    finally:
        f.close()


