#!/usr/bin/env python

import scrapeStop, json

def printRouteInfo(json, routeNumber):
	# TODO: find out what happens if routeNumber isn't in the collection, and handle that
	# TODO: handle json somehow now having a Stop or an AtStreet within that
	routeInfo = (route for route in json['NextBuses'] if route['RouteNo'] == routeNumber).next()

	print routeInfo['RouteNo'] + ' ' + routeInfo['Direction'] + ' @ ' + json['Stop']['AtStreet'] + ':',

	departures = []
	for departure in routeInfo['Schedules']:
		if (departure['ExpectedCountdown'] < 90): # don't really care about buses that far out
			if (departure['Source'] != 'et'):
				departures.append(str(departure['ExpectedCountdown']) + '*')
			else:
				departures.append(str(departure['ExpectedCountdown']))

	# TODO: for routes with more than one terminus, Schedules aren't interleaved, 
	# so second terminus could be being lost at the end. sort by ExpectedCountdown
	# before converting and trimming

	if (len(departures) > 0):
		print ', '.join(departures[:3]) + ' minutes'
	else:
		print 'none'

	return


stops = [	['50167','003'], # 3 northbound
		['50247','003'], # 3 southbound
		['51518','025'], #25 eastbound
		['51571','025'], #25 westbound
		['61150','033'], #33 eastbound
		['61118','033']  #33 westbound
	]

for stop in stops:
	stopData = json.loads(scrapeStop.getStopJSON(stop[0], stop[1]))
	printRouteInfo(stopData, stop[1])

