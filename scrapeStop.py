#!/usr/bin/env python

import pycurl, StringIO, json, urllib


# URLs
htmlURL = 'http://nb.translink.ca/text/stop/{STOP}/route/{ROUTE}'
jsonURL = 'http://nb.translink.ca/rideapi.ashx?cp=gssr%2F{CODE}==;{ROUTE}'


c = pycurl.Curl()
c.setopt(pycurl.COOKIEFILE, 'cookie.txt')
c.setopt(pycurl.URL, htmlURL.replace('{STOP}', '50166').replace('{ROUTE}', '003'))
b = StringIO.StringIO()
c.setopt(pycurl.WRITEFUNCTION, b.write)
c.perform()

html = b.getvalue()
b.close()
b = StringIO.StringIO() # clear
c.setopt(pycurl.WRITEFUNCTION, b.write)

codeIndexStart = html.find('textSearchStopAndRoute(\'') + 24
codeIndexEnd = codeIndexStart + 22
code = html[codeIndexStart:codeIndexEnd]
code = urllib.quote_plus(code)

c.setopt(pycurl.URL, jsonURL.replace('{CODE}', code).replace('{ROUTE}', '003'))
c.perform()

jsonString = b.getvalue()

data = json.loads(jsonString)
departures = data['NextBuses'][0]['Schedules']

for departure in departures:
	print departure['ExpectedCountdown'],
	if (departure['Source'] != 'et'):
		print '*',
	print

