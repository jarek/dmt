#!/usr/bin/env python

import pycurl
import operator
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
    50167: {'route_number': 3, 'direction': 'north', 'at_street': '28th'},
    51571: {'route_number': 25, 'direction': 'west', 'at_street': 'Main'},
    61118: {'route_number': 33, 'direction': 'west', 'at_street': 'Main'},
    50035: {'route_number': 3, 'direction': 'south', 'at_street': 'Seymour'},
    50233: {'route_number': 3, 'direction': 'south', 'at_street': 'Terminal'},
    51513: {'route_number': 25, 'direction': 'east', 'at_street': 'Cambie'},
    50247: {'route_number': 3, 'direction': 'south', 'at_street': '28th'},
    51518: {'route_number': 25, 'direction': 'east', 'at_street': 'Main'},
    61150: {'route_number': 33, 'direction': 'east', 'at_street': 'Main'},
    50415: {'at_street': '16th'},
    61337: {'at_street': 'Marine Dr station'}
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

def unpad_route_number(route_number):
    return str(route_number).lstrip('0')

def pad_route_number(route_number):
    return str(route_number).rjust(3, '0')

def get_nextbus_info(nextbuses, route_number = '', stop_info = {}):
    # default result structure
    result = {'error': False, 'route_number': '', 'direction': '', 
        'at_street': '', 'buses': [], 'destinations': []}

    # rewrite provided data, if any, as default result
    if 'route_number' in stop_info:
        result['route_number'] = stop_info['route_number']
        if route_number:
            route_number = stop_info['route_number']
    if 'direction' in stop_info:
        result['direction'] = stop_info['direction']
    if 'at_street' in stop_info:
        result['at_street'] = stop_info['at_street']

    # actually parse response
    # first, look for known error conditions
    # and return early if they are indicated
    if 'Code' in nextbuses and nextbuses['Code'] == '3005':
        result['error'] = 'no estimates found'
        return result
    elif 'Code' in nextbuses and nextbuses['Code'] == '3002':
        result['error'] = 'invalid stop number'
        return result

    # find data in response, if any
    route_info = {}
    if route_number:
        routes = list(route for route in nextbuses if
            route['RouteNo'] == pad_route_number(route_number))
        if len(routes) > 0:
            route_info = routes[0]
        else:
            return 'invalid route number for given stop'
    elif len(nextbuses) > 0:
        # if route_number wasn't specified, just look at first route 
        # for the stop, if any
        route_info = nextbuses[0]
    else:
        result['error'] = 'no information found'

    if len(route_info) > 0:
        # information from service takes precedence over information
        # we had - write it into the result
        # this code assumes a standard API response with all the keys
        # ('RouteNo', 'Schedules', 'ExpectedCountdown', etc)  present.
        # a bit optimistic, but it works when API works normally...
        result['route_number'] = unpad_route_number(route_info['RouteNo'])
        result['direction'] = route_info['Direction'].lower()

        destinations = {}
        for run in route_info['Schedules']:
            bus_run = {}
            bus_run['destination'] = run['Destination'].title()
            destinations[bus_run['destination']] = True

            bus_run['countdown'] = run['ExpectedCountdown']
            # * indicates scheduled time. - indicates delay.
            # + indicates bus is running ahead of schedule
            # live update is indicated by ' ', trim it down to ''
            bus_run['status'] = run['ScheduleStatus'].strip()

            result['buses'].append(bus_run)

        # make a list of all the currently served destinations
        result['destinations'] = destinations.keys()

        # ensure list is sorted by next departure - sometimes
        # this might not be the case when destinations are interleaved
        result['buses'].sort(key=operator.itemgetter('countdown'))

    return result

def get_stop_data(stop_number, route = False):
    replace_and_json_parse_time_start = time.time()

    if route == False:
        url = API_STOP_URL \
            .replace('{STOP}', str(stop_number)) \
            .replace('{KEY}', API_KEY)
        json_text = get_URL(url)
        
    else:
        url = API_STOP_AND_ROUTE_URL \
            .replace('{STOP}', str(stop_number)) \
            .replace('{ROUTE}', pad_route_number(route)) \
            .replace('{KEY}', API_KEY)
        json_text = get_URL(url)

    result = json.loads(json_text)

    timer.append(['get stop #%d total, ms' % int(stop_number), \
        (time.time() - replace_and_json_parse_time_start)*1000.0])

    return result

def get_stop_info(stop_number, route = False):
    if stop_number in STOP_INFO:
        result = STOP_INFO[stop_number]
        result['stop_number'] = stop_number
        return result
    else:
        # TODO: query API for the information
        # and consider caching it in a file or database or something
        # so it can be looked up quicker in the future
        return {'stop_number': stop_number, 'route_number': '', 
            'direction': '', 'at_street': ''}

