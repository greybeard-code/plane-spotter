#####################################################
# Chainsaw's dump1090 Plane Spotter script
# plane_spotter_hourly.py
# version 1.0  June 2018
# based on Frank Reijn's airplane to Domoticz Pyhton script. V1.1
#
# Script will scan your dump1090 history and create a summary of close plane
# This script loads the history json files from /run/dump1090-mutability/
# Default only has the last hour, so need to run this hourly
#
# Additional libraries in python are required : json, yaml, math,time, glob
#  Please use google for HowTo.
# script should run as root or dump1090 user
#    so it has write access to the //run/dump1090-mutability/ directory


import json
import yaml
import math
import time
import glob

###############################################################
###  User Must Change These
## Furture - read from config.ini
#distance around your location in km
Dist2Plane=5
#your location - easy to find with google maps
### Must Be Changed #############
lonhome = -84.659194
lathome = 33.937000
# Place for html files
report_dir = "/var/www/html/"
# Where are the dump1090 histroy files?
hist_dir = "/run/dump1090-mutability/"

###############################################################

#Switch on debug statements
debug = 0
# data of all the planes from the files
planedata ={}
#Set report date
report_date= time.strftime("%Y%m%d")



# ADS-B Category Dictionary
cat_codes = {
	"A0" : "No ADS-B Emitter Category Information",
    "A1" : "Light (< 15 500 lbs.)",
    "A2" : "Small (15 500 to 75 000 lbs.)",
    "A3" : "Large (75 000 to 300 000 lbs.)",
    "A4" : "High Vortex Large(aircraft such as B-757)",
    "A5" : "Heavy (> 300 000 lbs.)",
    "A6" : "High Performance ( > 5 g acceleration and > 400kts)",
    "A7" : "Rotor-craft",
    "B0" : "No ADS-B Emitter Category Information",
    "B1" : "Glider/sailplane",
    "B2" : "Lighter-than-Air",
    "B3" : "Parachutist/Skydiver",
    "B4" : "Ultralight/hang-glider/paraglider",
    "B5" : "Reserved",
    "B6" : "Unmanned Aerial Vehicle",
    "B7" : "Space/Trans-atmospheric vehicle",
    "C0" : "No ADS-B Emitter Category Information",
    "C1" : "Surface Vehicle - Emergency Vehicle",
    "C2" : "Surface Vehicle - Service Vehicle",
    "C3" : "Fixed Ground or Tethered Obstruction",
    "C4" : "Reserved",
    "C5" : "Reserved",
    "C6" : "Reserved",
    "C7" : "Reserved",
	" " : "None"
}

#distance calculator
def distance(lat1, lng1, lat2, lng2):
	#return distance as meter if you want km distance, remove "* 1000"
	radius = 6371 * 1000

	dLat = (lat2-lat1) * math.pi / 180
	dLng = (lng2-lng1) * math.pi / 180

	lat1 = lat1 * math.pi / 180
	lat2 = lat2 * math.pi / 180

	val = math.sin(dLat/2) * math.sin(dLat/2) + math.sin(dLng/2) * math.sin(dLng/2) * math.cos(lat1) * math.cos(lat2)
	ang = 2 * math.atan2(math.sqrt(val), math.sqrt(1-val))
	return radius * ang

###########
#Start main routine
##########
# Load today's nearby datafiles
filename = hist_dir + '/nearby-' + report_date + '.json'
if debug:
	print "Reading " + filename

#Open the current json file
try:
	with open(filename) as f:
		json_data = f.read()
		f.close()
except IOError:
	planedata = {}
	if debug:
		print "File not found-" + filename + " continuing...."
else:
	#Loads the file using yaml, that clean up of unecode stuff
	planedata = yaml.safe_load(json_data)

# Read the history files
histfiles = glob.glob(hist_dir + '/history*.json')

for filename in histfiles:
	if debug:
		print "Reading " + filename

	#Open the file
	with open(filename) as f:
		json_data = f.read()

	#Loads the file uisng yaml, that clean up of unecode stuff
	data = yaml.safe_load(json_data)
	# time stamp of file
	timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data["now"]))
	list=data["aircraft"]

	#search for the planes
	for item in list:
		# Plane Data Strings - Clear 'em out
		ICAOhex = " "
		flightname = " "
		squawk = " "
		altitude = " "
		category = " "
		dist = 9999
		count = 1
		lastseen = timestamp
		if 'hex' in item.keys():
			ICAOhex = item["hex"]
		if 'flight' in item.keys():
			flightname = item["flight"]
		if 'squawk' in item.keys():
			squawk = item["squawk"]
		if 'altitude' in item.keys():
			altitude = item["altitude"]
		if 'category' in item.keys():
			category = item["category"]
		if debug:
			print (planedata)
			print cat_codes[category]

		# if we have lat lon data, calculate the distance
		if 'lon' in item.keys():
			lon6=(item['lon'])
			lat6=(item['lat'])

			dist= int ( distance(lonhome,lathome,lon6,lat6)/1000)

			if debug:
				print str(dist)+ " Km"
			if dist < Dist2Plane:
				#print str(round(dist/1000))+ " Km"
				# if airplane is in my distance, I put it in the array
				# look to see if we already have the planes, then keep the better data
				if ICAOhex in planedata.keys():
					(oflightname, osquawk, oaltitude, odist, ocategory, ocount, olastseen ) = planedata[ICAOhex]
					if len(oflightname) > 2:
						 flightname = oflightname
					if len(osquawk) > 2:
						squawk = osquawk
					# higest altitude
					if 	oaltitude > altitude:
						altitude = oaltitude
					# lowest distance
					if dist < odist :
						dist = odist
					if len(category) > 1:
						category = ocategory
					count = ocount +1
					if olastseen > lastseen:
						lastseen = olastseen
				# create our plane data row, update the found plane array
				planedata[ICAOhex] = (flightname, squawk, altitude, dist, category, count, lastseen )
				if debug:
					print ( ICAOhex, " = " , planedata[ICAOhex])


	if debug:
		print "Done with file."

	f.close()

# done pulling files. Ready to output
#print "-"*50
if debug:
	print (planedata)
# save data to json file
filename = hist_dir + '/nearby-' + report_date + '.json'
if debug:
	print " Saving list to " + filename
json.dump(planedata, open(filename, 'wb'))

# Update 24 hour summary html
filename = report_dir + "psdaily-" + report_date + '.html'
cvs_shortname = "psdaily-" + report_date + '.cvs'
cvs_filename = report_dir + cvs_shortname
if debug:
	print " Saving report to " + filename
f = open(filename, 'w+')
cf = open(cvs_filename, 'w+')
# write file header
#need to add sortable table script and css
f.write("<html><head><title>Plane Spotter Daily</title></head><body>\n")
f.write("<h1>Plane Spotter Daily Report for " + report_date + "</h1>\n")
f.write("<p> This is a summary of the planes that have ADB-S installed and transmitting within " + str(Dist2Plane) + " Km of your location.\n ")
f.write("<p> The data is also avalible as a downloadable CVS sheet - " )
f.write(" <a href=\""+ cvs_shortname +"\"> "+ cvs_shortname + "</a> \n<p><hr> ")
#start table headers
f.write("<table>\n")
f.write("<thead><tr><th>ICAO</th><th>Flight </th><th>Squawk </th><th>Altd. </th><th>Dist. </th>")
f.write("<th> Category </th><th>Count </th><th>Last Seen</th></tr></thead>\n")
# write cvs headers
cf.write("ICAO,Flight,Squawk,Altd.,Dist.,Category,Count,Last Seen\n")
f.write("<tbody>\n")
for ICAOhex in sorted(planedata):
	(flightname, squawk, altitude, dist, category, count, lastseen ) = planedata[ICAOhex]
	### Need to add URLs to lookup data
	string = "<tr> <td> %s</td><td> %s</td><td> %s</td>\n" %  (ICAOhex ,flightname, squawk)
	f.write(string )
	string = "<td align=right> %s</td><td> %s km</td><td> %s</td>\n" % (altitude, dist, cat_codes[category])
	f.write(string )
	string = "<td> %s</td><td> %s</td></tr>\n" % (count, lastseen)
	f.write(string )
	# cvs data out
	string = "%s,%s,%s,%s,%s,%s,%s,%s\n" % (ICAOhex ,flightname, squawk, altitude, dist, cat_codes[category],count, lastseen )
	cf.write(string )
# write footer
f.write("</tbody> </table>")
f.write("</body> </html>")
f.close()
cf.close()

# Update 7 day report html
# On sundays, consolidate reports from 7 days ago to a weekly html & cvs


#Clean up old files
# create report index html
filename = report_dir + "plane-spotter.html"
if debug:
	print " Saving report to " + filename
f = open(filename, 'w+')
f.write("<html><head><title>Plane Spotter Reports</title></head><body>\n")
f.write("<h1>Plane Spotter Reports </h1>\n")
f.write("<p> Plane Spotter collects and summarizes data from dump1090 to track close-by aircraft. <br>")
f.write("By Chainsaw-ng. <p>")
f.write("<h1> Daily Reports </h1>\n")
dailyfiles = glob.glob(report_dir + "psdaily-*.html")
for filename in dailyfiles:
	filename = filename[ len(report_dir) : -5 ]
	f.write(" <a href =\""+ filename + ".html\"> " + filename +"</a> ")
f.write("<p> <h1> Weekly Reports </h1>\n")
weeklyfiles = glob.glob(report_dir + "psweekly-*.html")
for filename in weeklyfiles:
	filename = filename[ len(report_dir) : -5 ]
	f.write(" <a href =\""+ filename + ".html> " + filename +"</a> ")
f.write("</body> </html>")
f.close()
####  end   ####
