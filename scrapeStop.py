#!/usr/bin/env python

import pycurl, StringIO, simplejson as json, urllib

# constants for Translink scraping

HTMLstopURL = 'http://nb.translink.ca/text/stop/{STOP}'
HTMLstopAndRouteURL = 'http://nb.translink.ca/text/stop/{STOP}/route/{ROUTE}'

JSONstopURL = 'http://nb.translink.ca/rideapi.ashx?cp=gsas%2F{CODE}=='
JSONstopAndRouteURL = 'http://nb.translink.ca/rideapi.ashx?cp=gssr%2F{CODE}==;{ROUTE}'


def makeCurlObject():
	c = pycurl.Curl()
	c.setopt(pycurl.COOKIEFILE, '')

	return c

def getURL(c, url):
	c.setopt(pycurl.URL, url)

	b = StringIO.StringIO()
	c.setopt(pycurl.WRITEFUNCTION, b.write)
	c.perform()

	html = b.getvalue()
	b.close()
	
	return html

def getStopCode(c, stopNumber):
	html = getURL(c, HTMLstopURL.replace('{STOP}', stopNumber))

	codeIndexStart = html.find('textSearchStop(\'') + 16
	codeIndexEnd = codeIndexStart + 22
	code = html[codeIndexStart:codeIndexEnd]
	code = urllib.quote_plus(code)

	return code

def getStopAndRouteCode(c, stopNumber, route):
	html = getURL(c, HTMLstopAndRouteURL.replace('{STOP}', stopNumber).replace('{ROUTE}', route))

	codeIndexStart = html.find('textSearchStopAndRoute(\'') + 24
	codeIndexEnd = codeIndexStart + 22
	code = html[codeIndexStart:codeIndexEnd]
	code = urllib.quote_plus(code)

	return code

def getStopJSON(stopNumber, route = False):
	c = makeCurlObject()

	if route == False:
		code = getStopCode(c, stopNumber)
		json = getURL(c, JSONstopURL.replace('{CODE}', code))
		
	else:
		code = getStopAndRouteCode(c, stopNumber, route)
		json = getURL(c, JSONstopAndRouteURL.replace('{CODE}', code).replace('{ROUTE}', route))

	return json

