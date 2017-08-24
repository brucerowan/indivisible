from selenium import webdriver #tool for automating browswers
from bs4 import BeautifulSoup
import time
import pandas as pd
from os import walk
import numpy as np

browser = webdriver.PhantomJS()
browser.set_window_size(1120, 550)
browser.get('http://resistancenearme.org/') #opens the page

# Allow the page to load completely 
# before we start locating elements in the DOM.
from selenium.webdriver.support.ui import WebDriverWait
def custom_condition(driver):
    import time
    time.sleep(7)
    return True

WebDriverWait(browser, 10).until(custom_condition)

# The webpagelists events of types 'Resistance Event' or 'Town Hall'
# by default. Interesting events are of type Other.


# first need to click on dropdown-toggle to expand it 
dropdowns= browser.find_elements_by_class_name("dropdown-toggle")
event_dd= dropdowns[3]
event_dd.click()

# next click on every event category in dropdown 
el=browser.find_elements_by_xpath('//a[@data-filter="meetingType"]')

for element in el:
	time.sleep(3)
	element.click()
	time.sleep(3)
	event_dd.click()


#create html parser from this webpage now that events are listed 
s = BeautifulSoup(browser.page_source, 'html.parser')


#finds all events 
events= browser.find_elements_by_class_name('list-group-item')

#create lists to hold our event information
event=[]
category=[]
venues=[]
dates=[]

#for every event, append info to the proper list 
for i in range(1,len(events)):
	meta=events[i].find_elements_by_tag_name('ul')
	meta2= meta[0].find_elements_by_tag_name('li')

	date=meta[0].find_elements_by_class_name('event-date')
	venue=meta[0].find_elements_by_class_name('event-venue')
	if(len(date)<1):
		date='missing'
		dates.append(date)

	else:
		dates.append(date[0].text)
	
	if(len(venue)<1):
		venue='missing'
		venues.append(venue)
	else:
		venues.append(venue[0].text)
	lines= str(events[i].text).splitlines()
	
	
	event.append(lines[0])
	category.append(lines[3])

#create dataframe 
df= pd.DataFrame({'Events':event,
				  'Categories':category,
				  'Venues':venues,
				  'Dates':dates} )


#Creates a filename 
timestamp = time.strftime('%Y%m%d')
_filename = 'scraped_data/resist_near_me.csv_events_{}.csv'.format(timestamp)

#creates csv
df.to_csv(_filename,index=False)



####COMBINE CSVS (cant get to work)

#  find files
_CSVs = []
for dirpath, dirnames, fnames in walk('scraped_data'):
    _CSVs.extend([dirpath + '/' + f for f in fnames
                  if f.lower().endswith('.csv')])

    break
# read csv files 
df_list = []
for f in _CSVs:
    logging.debug('Reading CSV file {}'.format(f))
    df = pd.read_csv(f)
    logging.debug('Shape = {}'.format(df.shape))
    df_list.append(df)

logging.debug('Combining into single DataFrame...')
events_df = (df_list[0].append(df_list[1:],ignore_index=True).reset_index(drop=True))


# End session safely
browser.quit()