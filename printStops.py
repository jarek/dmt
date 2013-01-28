#!/usr/bin/env python

import sys
import scrapeStop

HTML = False
# TODO: set this to true or false depending if we're supposed to print as HTML or unstyled

STOP_SETS = {
	'home-downtown': [50167, 51571, 61118],
	'downtown-home': [50035, 50233, 51513],
	'main-skytrain': [50233]
	}

def format_timer_info(t):
	result = ''
        for timepoint in t:
                result = result + '<!--%s: %f-->' % (timepoint[0], timepoint[1]) + '\n'
	return result

def format_route_info(nextbuses, stop_info):
	# TODO: this function is a mess, needs to be cleaned up,
	# and the info-finding logic (handling error codes, finding
	# routeInfo, etc) possibly needs to be moved into data-layer
	# scrapeStop.py.

	route_number = ''
	destination = ''
	at_street = ''

	if 'route' in stop_info:
		route_number = stop_info['route']
	if 'direction' in stop_info:
		destination = stop_info['direction']
	if 'at_street' in stop_info:
		at_street = stop_info['at_street']
	
	if len(nextbuses) == 0:
		return 'no information'

	if 'Code' in nextbuses and nextbuses['Code'] == '3005':
		if not route_number == '':
			return str(route_number).lstrip('0') + ': no estimates found'
		else:
			return 'no estimates found'
	elif 'Code' in nextbuses and nextbuses['Code'] == '3002':
		return 'invalid stop number'

	if not route_number == '':
		routeInfo = (route for route in nextbuses if route['RouteNo'] == str(route_number).rjust(3, '0')).next()
	else:
		routeInfo = nextbuses[0]
		route_number = routeInfo['RouteNo'].lstrip('0')

	result = str(route_number) + ' ' + destination + ' @ ' + at_street + ': '

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
		result = result + ', '.join(departures[:3]) + ' minutes'
	else:
		result = result + 'none'

	return result

def get_stops_from_command(command):
	stops_in_command = []

	if isinstance(command, list) and len(command) > 1:
		stops_in_command = command
	else:
		command = command[0]

	if len(stops_in_command) == 0:
		if command in STOP_SETS:
			stops_in_command = STOP_SETS[command]
		else:
			stops_in_command = command.split(';')

	stops = []
	for stop in stops_in_command:
		stop_data = str(stop).split(',')
		if len(stop_data) > 1:
			# string passed in, need to process
			# format is stopnumber,routenumber
			try:
				stops.append([int(stop_data[0]), stop_data[1]])
			except:
				# invalid stop number format, etc - ignore
				pass
		else:
			try:
				stops.append(int(stop))
			except:
				pass

	return stops

def format_default_stops():
	stops = [
		50167, # 3 northbound
		50247, # 3 southbound
		51518, #25 eastbound
		51571, #25 westbound
		61150, #33 eastbound
		61118  #33 westbound
		]

	return format_stops(stops)

def format_stops(stops):
	result = ''
	if HTML:
		result = 'Content-type: text/html\n\n'

	for stop in stops:
		if isinstance(stop, list):
			stop_number = stop[0]
			if len(stop) > 1:
				route = stop[1]
		else:
			stop_number = stop
			route = False

		stop_info = scrapeStop.get_stop_info(stop_number, route)

		stop_nextbus = scrapeStop.get_stop_data(stop_number, route)

		result = result + format_route_info(stop_nextbus, stop_info) + '\n'
		if HTML:
			result = result + '<br/>\n'

	result = result + format_timer_info(scrapeStop.timer)

	return result

if __name__ == '__main__':
	if len(sys.argv) == 1:
		print format_default_stops()
	else:
		# command format is: "stop;stop;stop,route"
		# e.g. ./printStops.py "50167;51518,25"
		stops = get_stops_from_command(sys.argv[1:])
		print format_stops(stops)
