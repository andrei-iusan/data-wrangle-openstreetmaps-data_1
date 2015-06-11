#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymongo
from collections import Counter
import pprint

client = pymongo.MongoClient('mongodb://localhost:27017')

db = client.osm

def audit_amenities(db):
	''' Adds "amenity" tag to an element if the element contains
	a tag that is known to be an amenity type. '''
	MIN_APPEREANCE_OF_AMENITY = 3 
	amenities = db.bucharest.find({'amenity':{'$exists':1}})
	am_tags = [am['amenity'] for am in amenities]
	tags_count = Counter(am_tags)
	updated = {}
	for tag in tags_count:
		if tags_count[tag] >= MIN_APPEREANCE_OF_AMENITY:
			wr_res = db.bucharest.update({tag:{'$exists':1}},
								{'$set':{'amenity':tag}},
								upsert=False,
								multi=True)
			db.bucharest.update({tag:'yes'},
								{'$unset':{tag:''}},
								upsert=False,
								multi=True)

			updated[tag]=wr_res['n']
	return updated

def main():
	result = audit_amenities(db)
	pprint.pprint(result)

if __name__ == '__main__':
	main()