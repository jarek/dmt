#!/usr/bin/env python
# coding=utf-8

import cgi
import sys
import scrapeStop

HTML = True
# TODO: set this to true or false depending if we're supposed to print as HTML or unstyled

STOP_SETS = {
    'home-downtown': [50167, 51571, 61118],
    'downtown-home': [50035, 50233, 51513],
    'main-skytrain': [50233],
    'richmond-home': ['61337,3', 51513],
    'cambie-home': ['50415,15', '50415,33']
}

# TODO: have a setting to include an arbitrary offset in minutes to do the calculation for 
# N minutes from now automatically for me
# TODO: perhaps also have a setting to pull in the scheduled departures - could be 
# useful for loop departures like 61337,3 above

DEFAULT_STOPS = [
    50167, # 3 northbound
    50247, # 3 southbound
    51518, #25 eastbound
    51571, #25 westbound
    61150, #33 eastbound
    61118  #33 westbound
]

def format_timer_info(t):
    result = ''
    for timepoint in t:
        result = result + '<!--%s: %f-->' % (timepoint[0], timepoint[1]) + '\n'
    return result

def format_stop_route_info(data):
    result = ''

    if data['route_number']:
        result = scrapeStop.unpad_route_number(data['route_number'])

        if data['direction']:
            result = result + ' ' + data['direction']
        if data['at_street']:
            result = result + ' @ ' + data['at_street']

    if len(result) > 0:
        result = result + ': '

    return result

def format_route_info(nextbuses, route_number, stop_info):
    # extract sanely structured and named data out of the json provided
    data = scrapeStop.get_nextbus_info(nextbuses, route_number, stop_info)

    # get the formatted "route direction @ stop" string based on whatever
    # data is available
    data['formatted'] = format_stop_route_info(data)

    # return error messages early
    if data['error']:
        if data['error'] == 'invalid stop number':
            if 'stop_number' in stop_info:
                # special handling only here, otherwise 
                # fall through to general report below
                return str(stop_info['stop_number']) + ': ' \
                    + data['error']
        
        return data['formatted'] + data['error']

    departures = []
    for bus in data['buses']:
        if (bus['countdown'] < 90):
            # don't really care about buses more than 90 min away
            if bus['status'] == '*':
                # this is the only status message we care about
                departures.append(str(bus['countdown'])
                     + bus['status'])
            else:
                departures.append(str(bus['countdown']))

        # TODO: this ignores different destinations, which might be 
        # important to the user. come up with a way to show them nicely
        # (maybe "3a, 15b, 27a  - a: Main, b: Main-Marine Dr Stn" or 
        # something similar?)

    if len(departures) > 0:
        result = data['formatted'] + ', '.join(departures[:3]) + ' minutes'
    else:
        result = data['formatted'] + 'none'

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

def format_stops(stops):
    result = ''

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

        result = result + format_route_info(stop_nextbus, route, 
            stop_info) + '\n'
        if HTML:
            result = result + '<br/>\n'

    result = result + format_timer_info(scrapeStop.timer)

    return result

def get_command():
    command = '' # default

    # note: if invoking the script in a CGI context, something
    # (preferably "Content-type: text/html") MUST be printed 
    # before invoking cgi.FieldStorage(), and by extension this function.
    # not sure why, but so it is.
    cgi_arguments = cgi.FieldStorage()

    if 'command' in cgi_arguments:
        command = [ str(cgi_arguments['command'].value) ]
    elif len(sys.argv) > 1:
        command = sys.argv[1:]

    return command

if __name__ == '__main__':
    if HTML:
        print 'Content-type: text/html\n\n'

    command = get_command()

    if command == '':
        print '<ul>'
        for command in STOP_SETS:
            print '<li><a href="?command=%s">%s</a>' % (command, command)
        print '</ul>'

        #print format_stops(DEFAULT_STOPS)
    else:
        # command format is: "stop;stop;stop,route"
        # e.g. ./printStops.py "50167;51518,25"
        # test command: ./printStops.py "50167;50247;51518,3;11111"
        # web test: /dmt/printStops.py?command=50167%3B50247%3B51518,3%3B11111
        # (semicolon must be urlencoded to %3B)
        # includes a real stop with bad route (which we should try to
        # report correctly) and a fake stop number

        stops = get_stops_from_command(command)
        print format_stops(stops)

