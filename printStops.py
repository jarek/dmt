#!/usr/bin/env python

import sys
import scrapeStop

HTML = False
# TODO: set this to true or false depending if we're supposed to print as HTML or unstyled

STOP_SETS = {
	'home-downtown': {50167: ['50167', '003', 'downtown', '28th'],
			51571: ['51571', '025', 'UBC', 'Main'],
			61118: ['61118', '033', 'UBC', 'Main']},
	'downtown-home': {50035: ['50035', '003', 'Main', 'Seymour'],
			50233: ['50233', '003', 'Main', 'Terminal'],
			51513: ['51513', '025', 'Brentwood', 'Cambie']},
	'main-skytrain': {50233: ['50233', '003', 'Main', 'Terminal']}
	}

def format_timer_info(t):
	result = ''
        for timepoint in t:
                result = result + '<!--%s: %f-->' % (timepoint[0], timepoint[1]) + '\n'
	return result

def format_route_info(nextbuses, route_number, destination = '', at_street = ''):
	# TODO: find out what happens if routeNumber isn't in the collection, and handle that
	
	if len(nextbuses) == 0:
		return 'no information'

	if 'Code' in nextbuses and nextbuses['Code'] == '3005':
		if not route_number == '':
			return route_number.lstrip('0') + ': no estimates found'
		else:
			return 'no estimates found'

	if not route_number == '':
		routeInfo = (route for route in nextbuses if route['RouteNo'] == str(route_number)).next()
	else:
		routeInfo = nextbuses[0]
		route_number = routeInfo['RouteNo']

	result = route_number.lstrip('0') + ' ' + destination + ' @ ' + at_street + ': '

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

	if isinstance(stops_in_command, dict):
		return stops_in_command
	else:
		stops = {}
		for stop in stops_in_command:
			stop_data = stop.split(',')
			try:
				stops[int(stop_data[0])] = [str(stop_data[0]), '', '', '']
				if len(stop_data) > 1:
					stops[int(stop_data[0])][1] = str(stop_data[1]).rjust(3,'0')
			except:
				pass
				
		return stops

def format_default_stops():
	stops = {	50167: ['50167','003','downtown','28 Ave'], # 3 northbound
			50247: ['50247','003','southbound','28 Ave'], # 3 southbound
			51517: ['51518','025','eastbound','Main St'], #25 eastbound
			51517: ['51571','025','westbound','Main St'], #25 westbound
			61150: ['61150','033','eastbound','Main St'], #33 eastbound
			61118: ['61118','033','westbound','Main St']  #33 westbound
		}

	return format_stops(stops)

def format_stops(stops):
	result = ''
	if HTML:
		result = 'Content-type: text/html\n\n'

	for stop in stops:
		stop_info = stops[stop]
		stop_data = scrapeStop.get_stop_data(stop)
		result = result + format_route_info(stop_data, stop_info[1], stop_info[2], stop_info[3]) + '\n'
		if HTML:
			result = result + '<br/>\n'

	result = result + format_timer_info(scrapeStop.timer)

	return result

if __name__ == '__main__':
	if len(sys.argv) == 1:
		print format_default_stops()
	else:
		stops = get_stops_from_command(sys.argv[1:])
		print format_stops(stops)
