#!/usr/bin/env python

import pycurl, StringIO, simplejson as json, urllib

# constants for Translink scraping

HTMLstopURL = 'http://nb.translink.ca/text/stop/{STOP}'
HTMLstopAndRouteURL = 'http://nb.translink.ca/text/stop/{STOP}/route/{ROUTE}'

JSONstopURL = 'http://nb.translink.ca/nextbus.ashx?cp=gsas%2F{CODE}=='
JSONstopAndRouteURL = 'http://nb.translink.ca/nextbus.ashx?cp=gssr%2F{CODE}==;{ROUTE}'


def makeCurlObject():
	c = pycurl.Curl()
	c.setopt(pycurl.COOKIEFILE, 'cookie.txt')
	c.setopt(pycurl.COOKIEJAR, 'cookie.txt')

	return c

def getURL(c, url, referer = False):
	c.setopt(pycurl.URL, url)

#	c.setopt(pycurl.HTTPHEADER, ['Accept: text/html, application/xml;q=0.9, application/xhtml+xml, image/png, image/webp, image/jpeg, image/gif, image/x-xbitmap, */*;q=0.1', 'Accept-Encoding: gzip, deflate', 'Cookie: nb.sgn='+getCookieCode(c) ])
#	c.setopt(pycurl.USERAGENT, 'Opera/9.80 (X11; Linux i686; U; en) Presto/2.10.229 Version/11.64')

#	if (referer != False):
#		c.setopt(pycurl.REFERER, referer)

	b = StringIO.StringIO()
	c.setopt(pycurl.WRITEFUNCTION, b.write)
	c.perform()

	html = b.getvalue()
	b.close()
	
	return html

def getStopCode(c, stopNumber):
	html = getURL(c, HTMLstopURL.replace('{STOP}', stopNumber))

	codeIndexStart = html.find('nbt.initSchedules(\'') + 19
	codeIndexEnd = codeIndexStart + 22
	code = html[codeIndexStart:codeIndexEnd]
	code = urllib.quote_plus(code)

	return code

def getStopAndRouteCode(c, stopNumber, route):
	html = getURL(c, HTMLstopAndRouteURL.replace('{STOP}', stopNumber).replace('{ROUTE}', route))

	codeIndexStart = html.find('nbt.initStopAndRoute(\'') + 22
	codeIndexEnd = codeIndexStart + 22
	code = html[codeIndexStart:codeIndexEnd]
	code = urllib.quote_plus(code)

	return code

def getCookieCode(c):
	""" code to get this nominally is:
	js = getURL(c, 'http://nb.translink.ca/Scripts/tl.nb.t.min.js')

	codeIndexStart = js.find('nb.sgn') + 9
	codeIndexEnd = codeIndexStart + 12
	code = js[codeIndexStart:codeIndexEnd]

	return code """

	# in practice the code doesn't change, so return the hardcoded value
	# (revert to that code if this situation changes)
	return 'SnVuVGFuZw0K'

def getStopJSON(stopNumber, route = False):
	c = makeCurlObject()

	# TODO: try to also set referer, and then other headers.

	if route == False:
		code = getStopCode(c, stopNumber)
		referer = 'http://nb.translink.ca/Text/Stop/' + stopNumber
		print code
		print JSONstopURL.replace('{CODE}', code)
		json = getURL(c, JSONstopURL.replace('{CODE}', code), referer)
		
	else:
		code = getStopAndRouteCode(c, stopNumber, route)
		print code
		print JSONstopAndRouteURL.replace('{CODE}', code).replace('{ROUTE}', route)
		json = getURL(c, JSONstopAndRouteURL.replace('{CODE}', code).replace('{ROUTE}', route))

	return json

#print getStopJSON('50233')
