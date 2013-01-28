#!/usr/bin/env python

import pycurl
import StringIO
import simplejson as json
import time
import translink_api_key # contains only the API_KEY constant

# constants for Translink scraping

API_KEY = translink_api_key.API_KEY

API_STOP_URL = 'http://api.translink.ca/rttiapi/v1/stops/{STOP}/estimates?apikey={KEY}'
API_STOP_AND_ROUTE_URL = 'http://api.translink.ca/rttiapi/v1/stops/{STOP}/estimates?apikey={KEY}&routeNo={ROUTE}'

API_HEADERS = ['Accept: application/json']

STOP_INFO = {
	50167: {'route': 3, 'direction': 'downtown', 'at_street': '28th'},
	51571: {'route': 25, 'direction': 'UBC', 'at_street': 'Main'},
	61118: {'route': 33, 'direction': 'UBC', 'at_street': 'Main'},
	50035: {'route': 3, 'direction': 'Main', 'at_street': 'Seymour'},
	50233: {'route': 3, 'direction': 'Main', 'at_street': 'Terminal'},
	51513: {'route': 25, 'direction': 'Brentwood', 'at_street': 'Cambie'},
	50247: {'route': 3, 'direction': 'Main', 'at_street': '28th'},
	51518: {'route': 25, 'direction': 'Brentwood', 'at_street': 'Main'},
	61150: {'route': 33, 'direction': '29th Avenue', 'at_street': 'Main'},
	}

timer = []

def get_URL(url):
	http_get_time_start = time.time()

	c = pycurl.Curl()

	c.setopt(pycurl.HTTPHEADER, API_HEADERS)
	
	c.setopt(pycurl.URL, url)

	b = StringIO.StringIO()
	c.setopt(pycurl.WRITEFUNCTION, b.write)
	c.perform()

	#timer.append(['http get, ms', (time.time() - http_get_time_start)*1000.0])

	html = b.getvalue()
	b.close()
	
	return html

def get_stop_data(stop_number, route = False):
	replace_and_json_parse_time_start = time.time()

	if route == False:
		url = API_STOP_URL.replace('{STOP}', str(stop_number))\
			.replace('{KEY}', API_KEY)
		json_text = get_URL(url)
		
	else:
		url = API_STOP_AND_ROUTE_URL.replace('{STOP}', str(stop_number))\
			.replace('{ROUTE}', route).replace('{KEY}', API_KEY)
		json_text = get_URL(url)

	result = json.loads(json_text)

	timer.append(['get stop #%d total, ms' % int(stop_number), \
		(time.time() - replace_and_json_parse_time_start)*1000.0])

	return result

def get_stop_info(stop_number, route = False):
	if stop_number in STOP_INFO:
		return STOP_INFO[stop_number]
	else:
		# TODO: query API for the information
		# and consider caching it in a file or database or something
		# so it can be looked up quicker in the future
		return {'route': '', 'direction': '', 'at_street': ''}

