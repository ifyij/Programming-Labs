# -*- coding: utf-8 -*-
"""
Created on Sun Feb 27 15:16:20 2022

@author: ifyij
"""

#!/usr/bin/env python3

import typing
from util import read_osm_data, great_circle_distance, to_local_kml_url

# NO ADDITIONAL IMPORTS!


ALLOWED_HIGHWAY_TYPES = {
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified',
    'residential', 'living_street', 'motorway_link', 'trunk_link',
    'primary_link', 'secondary_link', 'tertiary_link',
}


DEFAULT_SPEED_LIMIT_MPH = {
    'motorway': 60,
    'trunk': 45,
    'primary': 35,
    'secondary': 30,
    'residential': 25,
    'tertiary': 25,
    'unclassified': 25,
    'living_street': 10,
    'motorway_link': 30,
    'trunk_link': 30,
    'primary_link': 30,
    'secondary_link': 30,
    'tertiary_link': 25,
}

count = 0
idnum = 0
visited = set()
'''
for node in read_osm_data('resources/cambridge.ways'):
        if 'highway' in node['tags'].keys():
            if node['tags']['highway'] in ALLOWED_HIGHWAY_TYPES:
                for ele in node['nodes']:
                    if ele not in visited:
                        count+=1 
                        visited.add(ele)
                      
   
print(count)

#print(great_circle_distance((42.363745, -71.100999), (42.361283, -71.239677)))
t1 = None
t2 = None
prevt = None
currentt = None
dist = 0

for node in read_osm_data('resources/midwest.ways'):
    if node['id'] == 21705939:
        for nose in read_osm_data('resources/midwest.nodes'):
            if nose['id'] == node['nodes'][0]:
                prevt = (nose['lat'],nose['lon'])
        for i in range(1, len(node['nodes'])):
            for nose in read_osm_data('resources/midwest.nodes'):
                if nose['id'] == node['nodes'][i]:
                    currentt = (nose['lat'],nose['lon'])
                    dist += great_circle_distance(prevt,currentt)
                    prevt = currentt

data = read_osm_data('resources/cambridge.ways')
print(next(data))        
print('------------') 
print('------------')
data = read_osm_data('resources/cambridge.nodes')
print(next(data))   
'''
#speed idea: copy every id of a node into a set and do a visited, may not work, the issue is that 
#you have multiple dictionaries that are the same when the node is in a path multiple times

def build_internal_representation(nodes_filename, ways_filename):
    """
    Create any internal representation you you want for the specified map, by
    reading the data from the given filenames (using read_osm_data)
    
    Returns a dictionary of nodes, the keys are node ids
    the values are dictionarys with 'adjacent nodes' and 'coordinates' as keys
    'adjacent nodes' has a list of tuples (node id, speed limit for that way)
    'coordinate' is a tuple (lat,lon)
    """

    node_dict = {} #node dictionary that I return
    for ways in read_osm_data(ways_filename): #iterating through every way
        if 'highway' in ways['tags']: 
            if ways['tags']['highway'] in ALLOWED_HIGHWAY_TYPES:
                for ele in ways['nodes']: #iterating through every node in a way
                    adj_nodes = [] # adjacent node list initializationg
                    index = ways['nodes'].index(ele) #the index of the node in the list
                    
                    try:
                        maxspeed = ways['tags']['maxspeed_mph'] #making sure there is a maxspeed
                    except KeyError:
                        maxspeed = DEFAULT_SPEED_LIMIT_MPH[ways['tags']['highway']] #this is the maxspeed if there is none given
                   
                    #checking if the preceding or next node in the way can be added or not based off of index errors and oneways                    
                    if index > 0 and index < len(ways['nodes'])-1: 
                        adj_nodes.append((ways['nodes'][index+1],maxspeed)) # adding tuple of the form (node,speed)
                        if 'oneway' in ways['tags'].keys(): 
                            if 'yes' not in ways['tags']['oneway']: #checking one ways
                                adj_nodes.append((ways['nodes'][index-1],maxspeed))
                        else:
                            adj_nodes.append((ways['nodes'][index-1],maxspeed))
                    elif index == 0 and len(ways['nodes'])>1:
                        adj_nodes.append((ways['nodes'][index+1],maxspeed))
                    elif index == len(ways['nodes'])-1 and len(ways['nodes'])>1 :
                        if 'oneway' in ways['tags'].keys():
                            if 'yes' not in ways['tags']['oneway']: #checking one ways
                                adj_nodes.append((ways['nodes'][index-1],maxspeed))
                        else:
                            adj_nodes.append((ways['nodes'][index-1],maxspeed))
                               
                    if ele not in node_dict.keys():
                        node_dict[ele] = {'adjacent nodes': adj_nodes} #adding adjacent nodes to the dictionary answer
                    else:
                        node_dict[ele]['adjacent nodes'].extend(adj_nodes) #making sure I don't write over old nodes
                
    for node in read_osm_data(nodes_filename): #iterate through all the nodes to get the coordinates for each node in the dict
        if node['id'] in node_dict.keys():
            node_dict[node['id']]['coordinate'] = (node['lat'], node['lon']) #adding tuple (lat,lon) and creating a dict entry for it
    return node_dict #returning the represention
        


def find_short_path_heuristic(map_rep, node1, node2, fast = False):
    """
    Return the shortest path between the two nodes

    Parameters:
        map_rep: the result of calling build_internal_representation
        node1: node representing the start location
        node2: node representing the end location

    Returns:
        a list of node IDs representing the shortest path (in terms of
        distance) from node1 to node2
    This is with the heuristic version for comparison for a checkoff question, a 
    """
    id1 = node1
    id2 = node2
    
    #fast has no heuristic implementation 
    if fast:
        agenda = [(0,(id1,))] #initialize agenda (cost,(tuple of ids as node))
    else:
        #agenda is different for heuristic (estimated heuristic distance, current path distance, tuple of ids current path)
        agenda = [(great_circle_distance(map_rep[id1]['coordinate'],map_rep[id2]['coordinate']),0,(id1,))] 
   
    expanded = set() #initializing set
    
    while agenda:
        agenda.sort() #sorts by first index, either heuristic or normal cost
        if fast: #again its dif for the heuristic 
            current_path_tuple = agenda.pop(0) #takes the lowest cost path off the agenda 
            current_cost = current_path_tuple[0] #takes the first index of the node tuple, current cost
            current_path = current_path_tuple[1] #the tuple of id names
            terminal_vertex = current_path[-1] #takes the last id of the path
        else:
            current_path_tuple = agenda.pop(0)
            current_cost = current_path_tuple[1] #takes the current cost
            current_path = current_path_tuple[2] #tupe of id names, path
            terminal_vertex = current_path[-1] #takes the id off the path
        
        if terminal_vertex not in expanded: #making sure it is not expanded 
            expanded.add(terminal_vertex) #add it to expanded
            if terminal_vertex == id2: #checking if it reach the condition
            
                return list(current_path) #returns the tuple path
            else:
                for child,speed in map_rep[terminal_vertex]['adjacent nodes']: #expands the vertex to the different paths
                    if child not in expanded:
                        new_path = current_path + (child,) #adds the child to the path
                        if fast:
                            agenda.append((current_cost+ great_circle_distance(map_rep[terminal_vertex]['coordinate'],
                                                                             map_rep[child]['coordinate'])/speed,new_path)) #the cost is divided my speed to get speed
                        else:
                            length_of_new_path = current_cost+ great_circle_distance(map_rep[terminal_vertex]['coordinate'],
                                                                                     map_rep[child]['coordinate'])
                            agenda.append((length_of_new_path + great_circle_distance(map_rep[child]['coordinate'],map_rep[id2]['coordinate']),
                                           length_of_new_path,new_path)) #heuristic calculation
                       
    return None


def no_heuristic(map_rep, node1, node2, fast =False):
    """
    Return the shortest path between the two nodes

    Parameters:
        map_rep: the result of calling build_internal_representation
        node1: node representing the start location
        node2: node representing the end location

    Returns:
        a list of node IDs representing the shortest path (in terms of
        distance) from node1 to node2
    Not a heuristic version, see above comments
    """
    
    
    id1 = node1
    id2 = node2
            
    
    agenda = [(0,(id1,))] #distances: path, list implementation
    expanded = set()
    count = 0
    while agenda:
        agenda.sort()
        current_path_tuple = agenda.pop(0)
        current_cost = current_path_tuple[0]
        current_path = current_path_tuple[1]
        terminal_vertex = current_path[-1]
        count+=1
        
        
        if terminal_vertex not in expanded:
            expanded.add(terminal_vertex)
            if terminal_vertex == id2:
                print(count)
                return list(current_path)
            else:
                for child,speed in map_rep[terminal_vertex]['adjacent nodes']:
                    if child not in expanded:
                        new_path = current_path + (child,)
                        if fast == False:
                            agenda.append((current_cost+ great_circle_distance(map_rep[terminal_vertex]['coordinate'],
                                                                               map_rep[child]['coordinate']),new_path))
                        else:
                            agenda.append((current_cost+ great_circle_distance(map_rep[terminal_vertex]['coordinate'],
                                                                               map_rep[child]['coordinate'])/speed,new_path))
    return None
    
    

def find_short_path_nodes(map_rep, node1, node2, fast =False):
    """
    Return the shortest path between the two nodes

    Parameters:
        map_rep: the result of calling build_internal_representation
        node1: node representing the start location
        node2: node representing the end location

    Returns:
        a list of node IDs representing the shortest path (in terms of
        distance) from node1 to node2
    """
    
    
    return find_short_path_heuristic(map_rep, node1, node2,fast) #i used this to test the heuristic vs no heuristic version

        
    
   
        
        
        
        

def find_short_path(map_rep, loc1, loc2, fast = False):
    """
    Return the shortest path between the two locations

    Parameters:
        map_rep: the result of calling build_internal_representation
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of distance) from loc1 to loc2.
    """
    n1 = 0 #node1 id
    n2 = 0 #node2 id
    ans = [] #answer initialized
    
    pos_nodes = list(map_rep.items()) # list of possible nodes with coordinates and ids
    closestloc1 = (pos_nodes[0][0], pos_nodes[0][1]['coordinate']) #closest set to the first in the list
    closestloc2 = (pos_nodes[0][0], pos_nodes[0][1]['coordinate']) #closest set to the first in the list
    
    for i in range(1,len(pos_nodes)): #goes through the rest of the list to see whats the closest
        current_loc = (pos_nodes[i][0],pos_nodes[i][1]['coordinate'])
        clos_dist1 = great_circle_distance(closestloc1[1], loc1) #closest distance between the first coordinate
        clos_dist2 = great_circle_distance(closestloc2[1], loc2) #closest distance between the second coordinate
        curr_dist1 = great_circle_distance(current_loc[1], loc1) #current distance between the first coordinate
        curr_dist2 = great_circle_distance(current_loc[1], loc2) #current distance betwen the second coordinate
        if curr_dist1 <= clos_dist1: #checking if the current node is closer to the first coordinate
            closestloc1 = current_loc
        if curr_dist2 <= clos_dist2: #same thing with the second
            closestloc2 = current_loc

    n1 = closestloc1[0] #get the node id of the first and second
    n2 = closestloc2[0]
                   
    
    short_ids = find_short_path_nodes(map_rep, n1, n2, fast) #list of nodes of shortest path
    if short_ids == None:
        return None
    for ele in short_ids:
        ans.append(map_rep[ele]['coordinate']) #gets the coordinate
    return ans
        
    


def find_fast_path(map_rep, loc1, loc2):
    """
    Return the shortest path between the two locations, in terms of expected
    time (taking into account speed limits).

    Parameters:
        map_rep: the result of calling build_internal_representation
        loc1: tuple of 2 floats: (latitude, longitude), representing the start
              location
        loc2: tuple of 2 floats: (latitude, longitude), representing the end
              location

    Returns:
        a list of (latitude, longitude) tuples representing the shortest path
        (in terms of time) from loc1 to loc2.
    """
    return find_short_path(map_rep, loc1, loc2, True) #fast version


if __name__ == '__main__':
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    scoop = build_internal_representation('resources/cambridge.nodes', 'resources/cambridge.ways')
    #print(scoop[5458770478])
    '''
    pos_nodes = list(scoop.items())
    closestloc1 = (pos_nodes[0][0], pos_nodes[0][1]['coordinate'])
    closestloc2 = (pos_nodes[0][0], pos_nodes[0][1]['coordinate'])
    
    for i in range(1,len(pos_nodes)):
        current_loc = (pos_nodes[i][0],pos_nodes[i][1]['coordinate'])
        clos_dist1 = great_circle_distance(closestloc1[1], (41.4452463, -89.3161394))
        curr_dist1 = great_circle_distance(current_loc[1], (41.4452463, -89.3161394))
        if curr_dist1 <= clos_dist1:
            closestloc1 = current_loc
       
    print(closestloc1[0])
    '''
    loc1 = (42.3858, -71.0783)
    loc2 = (42.5465, -71.1787)
    find_short_path(scoop, loc1, loc2)

    
    
    
    
