from webbot import Browser
from bs4 import BeautifulSoup as soup
import time
import datetime
from decimal import Decimal

web = Browser(showWindow=False) # Open browswer instance without showing GUI
# web.go_to('https://google.com')
# Bottom few lines are browser interaction, doing what one would do to get physically into the UPS Status webpages
web.go_to('http://192.168.185.10')

#web.click('Advanced', tag='button')
#web.click('Proceed to 192.168.185.10', classname='small-link')

web.type('apc')
web.type('icarus', into= 'Password')

web.click('Log On', tag='span')

web.click('Status')
web.click('UPS')

Alarm_counter = 0

# This loop refreshes the UPS status page, retreives the source, and records [Inputvoltage, units, Frequency of AC, units, charge of battery, %]
while True:

	page_source = web.get_page_source()

	page_soup = soup(page_source, "html.parser") # Use BeautifulSoup to read the html format
	data = page_soup.findAll("div", {"class":"dataField"}) # Search for fields in the html with data about the UPS and put it in a list
	date_time = page_soup.findAll("div", {"id":"sitemap"})

	source_inputvoltage = data[3].select_one("div[class=dataValue]").text # This element in the data list contains information about power going into UPS
	source_batterystate = data[10].select_one("div[class=dataValue]").text # This element in the data list contains the charge percentage of the UPS battery
	source_timestamp = date_time[0].select_one("span[class=divided]").text

	# Top source variables are in string format with weird indentations and return statements.
	# Make each "word" in the string into list elements for easier recording
	source_inputvoltage = source_inputvoltage.split()
	source_batterystate = source_batterystate.split()
	source_timestamp = source_timestamp.split()

	UPS_state = source_inputvoltage + source_batterystate + source_timestamp
	e = datetime.datetime.now()
	difference = datetime.date.today()

	UPSstatus_file = open("UPSstatus" + difference.strftime('%Y%m%d') +  ".txt", 'a')
	UPSstatus_file.write("%s %s %s %s %s\t%s %s\t %s/%s/%s\t %s:%s:%s \n" % (UPS_state[0], UPS_state[1], UPS_state[2], UPS_state[3], UPS_state[4], UPS_state[5], UPS_state[6], e.month, e.day, e.year, e.hour, e.minute, e.second))
	UPSstatus_file.close()
	
	voltage = Decimal(UPS_state[0])
	battery = Decimal(UPS_state[5])
	
	
	print("%d VAC  %d  %s/%s/%s %s:%s:%s" % (voltage, battery, e.month, e.day, e.year, e.hour, e.minute, e.second))
	
	# Boolean Logic for ramp down begins
	UPSstatus_boolean = open("UPSstatus_boolean.txt", "w")
	
	boolean_value = 0
	if voltage < 1 and Alarm_counter < 5:
		print("Alarm Boolean: True")
		Alarm_counter+=1
		print("Warning! Alarm Counter Value Is %i\n" % Alarm_counter)
		UPSstatus_boolean.write("0")
	elif Alarm_counter == 5:
		print("Sending Ramp Down Signal Now! (UPS Voltage could be back to normal, but alarm time was reach, hence ramp down will persist)")
		print("Alarm Counter Value Is %i\n" % Alarm_counter)
		UPSstatus_boolean.write("1")
	else:
		print("Alarm Boolean: False\n")
		UPSstatus_boolean.write("0")
		Alarm_counter = 0
	UPSstatus_boolean.close()
	time.sleep(5)
	web.refresh()