#!/usr/bin/env python

import scrapeStop

HTML = False
# TODO: set this to true or false depending if we're supposed to print as HTML or unstyled

def print_timer_info(t):
        for timepoint in t:
                print '<!--%s: %f-->' % (timepoint[0], timepoint[1])

def print_route_info(nextbuses, route_number, destination, at_street):
	# TODO: find out what happens if routeNumber isn't in the collection, and handle that
	# TODO: handle json somehow now having a Stop or an AtStreet within that
	
	if len(nextbuses) == 0:
		print 'no information'
		return

	routeInfo = (route for route in nextbuses if route['RouteNo'] == route_number).next()

	print route_number.lstrip('0') + ' ' + destination.lower() + ' @ ' + at_street.title() + ':',

	departures = []
	for departure in routeInfo['Schedules']:
		if (departure['ExpectedCountdown'] < 90): # don't really care about buses that far out
			if (departure['ScheduleStatus'] == '*'):
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

def print_home_stops():
	stops = [	[50167,'003','downtown','28 Ave'], # 3 northbound
			[50247,'003','southbound','28 Ave'], # 3 southbound
			[51518,'025','eastbound','Main St'], #25 eastbound
			[51571,'025','westbound','Main St'], #25 westbound
			[61150,'033','eastbound','Main St'], #33 eastbound
			[61118,'033','westbound','Main St']  #33 westbound
		]

	if HTML:
		print 'Content-type: text/html\n'

	for stop in stops:
		stop_data = scrapeStop.get_stop_data(stop[0], stop[1])
		print_route_info(stop_data, stop[1], stop[2], stop[3])
		if HTML:
			print '<br/>'

	print_timer_info(scrapeStop.timer)


if __name__ == '__main__':
	print_home_stops()
