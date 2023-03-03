'''
The intention is to extract course details from the collegedunia website and store it into a data frame in a clean format. Since the area of data analytics particularly interests me,
I have taken the url for a query returning data analytics courses across the world. I've used selenium and python for this.
'''

#Data extraction for College Dunia
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

#initialize driver
driver = webdriver.Chrome()

#setting up search url and query keywords
listings = pd.DataFrame(columns=['name','location','course_name','fees_yrly','duration','rankings'])
link = 'https://collegedunia.com/study-abroad/data-science-and-analytics/master-colleges' #driver.find_element(By.CLASS_NAME, "//*[@id="rso"]/div[1]/div/div/div[1]/div/div/div[1]/div/a")
driver.get(link)
driver.maximize_window()
next_page = '99'
n = 0
while n < int(next_page[-1]):
    driver.implicitly_wait(6)
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    next_pages = driver.find_elements(By.CLASS_NAME, "page-link")
    next_page = next_pages[-1].get_attribute('href')
    print(f'n: {n}')
    print(f'length of next_pages:{len(next_pages)}')
    print(next_page)
    details = driver.find_elements(By.XPATH,"""//*[@id="__next"]/div[2]/section/div/div[3]/div[2]/div[2]/div""")
    for entry in details:   
        try:
            name = entry.find_element(By.TAG_NAME,"h3").text
        except:
            name = None
        try:
            location = entry.find_element(By.CSS_SELECTOR,"div.jsx-2188674517.location").text
        except:
            location = None
        try:
            course_name = entry.find_element(By.CSS_SELECTOR,"span.jsx-2188674517.text-md.d-block.text-none ").get_attribute("title")
        except:
            course_name = None
        try:
            fees_yrly = entry.find_element(By.CSS_SELECTOR,"span.jsx-2188674517.lr-key.w-40.d-block.font-weight-semi.text-primary.course-fee.text-right.text-md").text
        except:
            fees_yrly = None
        try:
            duration = entry.find_element(By.CSS_SELECTOR,"span.jsx-2188674517.text-primary.dur-truncate.w-40.text-right").text
        except:
            duration = None
        try:
            rankings = [i.text for i in entry.find_elements(By.CSS_SELECTOR,"span.jsx-2188674517.rank-span")]
        except:
            rankings = None
        listings = listings.append({'name':name,'location':location,'course_name':course_name,'fees_yrly':fees_yrly,'duration':duration,'rankings':rankings},ignore_index=1)
    n+=1
    driver.get(next_page)

#creating a copy data frame to work with
listings_new = listings.copy()
listings_new[['city', 'country']] = listings_new['location'].str.split(", ",expand=True)

#extracting fee information from string object into 2 new columns, one to store numerical value and the other to store the string part
listings_new['fee'] = listings_new['fees_yrly'].str.extract("(\d+.\d)")
listings_new['value'] = listings_new['fees_yrly'].str[-4:]

#creating a mapping dictionary to map the numberical value of the equivalent string in the 'value' column
unique_values = listings_new['value'].unique()
uval = list(unique_values)
multiplyer = [100000, 0, 10000, 1]
fee_key = dict( zip(uval, multiplyer))
listings_new['value'] = listings_new['value'].map(fee_key)

#creating another mapping dictionary to map the approx. time in years of the course duration
duration_unique = list(listings_new['duration'].unique())
duration_map = [1,2,1,1,1.34,1,1.25,4,1.5,1,1,3,1,1.75,1.5,3,1,1.25]
duration_dict = dict(zip(duration_unique,duration_map))
listings_new['duration(yrs)'] = listings_new['duration'].map(duration_dict)

#performing some cleanup operations
listings_new['fees_per_year'] = listings_new['fee'].astype(float)*listings_new['duration(yrs)']*listings_new['value']
listings_new['total_fees'] = listings_new['fees_per_year']*listings_new['duration(yrs)']
listings_new.drop(columns=['fee','value','location','fees_yrly'],inplace=True)
listings_new[['fees_per_year', 'total_fees']] = listings_new[['fees_per_year', 'total_fees']].round(2)
listings_new['ranks'] = listings_new['rankings'].str.findall("\d+")
listings_new['rank_THE'] = listings_new['ranks'].str[0]
listings_new['rank_QS'] = listings_new['ranks'].str[1]
listings_new.drop(['rankings','ranks'], axis=1,inplace=True)
