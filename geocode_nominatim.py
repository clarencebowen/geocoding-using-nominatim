#!/usr/bin/env python
import requests
from psycopg2 import connect
from psycopg2.extras import DictCursor

with open('../credentials.txt') as f:
	credentials = [x.strip().split(':') for x in f.readlines()]

for dbname,user,host,password,port in credentials:
	connection = "dbname='" + dbname + "' user='"  + user + "' host='" + host + "' password='" + password + "' port=" + port + ""

try:
    conn = connect(connection)
except:
    print "Unable to connect to database"
	
cur = conn.cursor(cursor_factory=DictCursor)

def addr_web_lookup(usr_addr_input, usr_limit = 10):
	query_args = {
		'q':usr_addr_input, 
		'format': 'json', 
		'countrycodes': 'US', 
		'addressdetails': 1,
		'limit':usr_limit,
		'bounded':1,
		'polygon_geojson': 1
	}

	resp = requests.post('http://nominatim.openstreetmap.org/search?', params=query_args)
	
	data = resp.json()
	
	if data: # data is a list of address geocoded dictionaries
		for d in data:
			display_name = d["display_name"]
			lat = d["lat"]
			lon = d["lon"]
			classLoc = d["class"]		
			typeLoc = d["type"]				
			importance = d["importance"]
			place_id = d["place_id"]
			(bbox_lat_bottom,bbox_lat_top,bbox_lon_left,bbox_lon_right) = (d["boundingbox"][0],d["boundingbox"][1],d["boundingbox"][2],d["boundingbox"][3])

			#print "display_name:",display_name," (lat,lon): (", lat, lon, ")" #display_name, bbox_lat_bottom, bbox_lat_top,bbox_lon_left,bbox_lon_right, lat, lon
			
			"""
			# execute the below CREATE in case geocoded_locations does not exist
			# create table geocoded_locations (location_name text, lat double precision, lon double precision, importance double precision);
			"""
			cur.execute("""
			INSERT INTO geocoded_locations(
			location_name,
			lat,
			lon,
			importance
			) 
			SELECT ''%s'',%s,%s,%s""", 
			(
			display_name.encode('ascii','ignore'),
			lat,
			lon,
			importance,
			) ); 

		conn.commit()

addr_web_lookup(usr_addr_input='5 Times Square')
