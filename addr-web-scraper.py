import requests
from lxml import html
import json
import re
import time

#base url to iterate
BASE_URL = 'http://www.addresses.com/page_number_X'

#XPATHs
#write XPath for the DOM object in the base url
addressXPath = '//p[@class="address"]/text()' 	#address
itemXPath = '//p[@class="items"]/text()'		#items (extra info related to address)

#clean addresses with extra information that can't be processed by Google's Geocoder
#these examples are based on sub-divisions of the Palermo Neighbourhood in Buenos Aires City
regex1 = "- Palermo .*?[Hollywood|Viejo|Soho|Chico] -"
regex2 = "- Barrio .*?Norte -"

#Google Geocoder
url_geocoder = "http://maps.googleapis.com/maps/api/geocode/json"

#number of pages to scrap
PAGES_TO_SCRAP = 30

#time between base url request
t_req = 10

#brake for t seconds every q queries to google
t = 10
q = 10

print('Addresses Web Scraper')
print('Base URL to Scrape: ' + BASE_URL)

print('setting up...')
url2 = BASE_URL
url3 = []
for i in  range(0,PAGES_TO_SCRAP):
	url3.append(re.sub('[X]',str(i),url2))

#start requests
print('requesting html pages...')
pages = []
trees = []
for url in url3:
	print(url)
	time.sleep(t_req)
	pages.append(requests.get(url))
for page in pages:
	trees.append(html.fromstring(page.text))

#parse HTML
print('parsing htmls...')
addresses = []
items = []
for tree in trees:
	addrs = tree.xpath(addressXPath)
	for d in addrs:
		print(d)
		d = re.sub(regex1,"",d)
		d = re.sub(regex2,"",d)
		addresses.append(d)
	items = items + tree.xpath(itemXPath)

#zip data records
zipped = zip(addresses,items)
zlist = list(zipped)

#create base file
print('creating address dump file...')
f = open('dump_base','w')
for z in zlist:
	z2 = re.sub('[()]','',str(z))
	#z3 = re.sub('[-]',',',z2)
	#z4 = re.sub("[']","",z3)
	z4 = re.sub("[']","",z2)
	f.write(z4 + '\n')
f.close()

#cross addresses dump with google's geocoder 
#TODO if closes conection go to zip
print('requesting geodecoded data...')
lats = []
lngs = []
addr_geoloc = []
i = 0
for addr in addresses:
	if i % q == 0:
		time.sleep(t)
	payload = {'address' : addr, 'components' : 'country:AR'}
	geoloc = requests.get(url_geocoder, params=payload)
	json_geoloc = json.loads(geoloc.text)
	print(json_geoloc['results'][0]['formatted_address'])
	addr_geoloc.append(json_geoloc['results'][0]['formatted_address'])
	lats.append(json_geoloc['results'][0]['geometry']['location']['lat'])
	lngs.append(json_geoloc['results'][0]['geometry']['location']['lng'])
	i = i + 1

#zip final data records
zipped = zip(addresses,addr_geoloc,lats,lngs,items)
zlist = list(zipped)

#create files
print('creating geocoder dump file...')
f = open('dump_geo','w')
for z in zlist:
	z2 = re.sub('[()]','',str(z))
	#z3 = re.sub('[-]',',',z2)
	#z4 = re.sub("[']","",z3)
	z4 = re.sub("[']","",z2)
	f.write(z4 + '\n')
f.close()
