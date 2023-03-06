'''
The intention is to extract course details from the collegedunia website and store it into a data frame in a clean format. Since the area of data analytics particularly interests me,
I have taken the url for a query returning data analytics courses across the world. I've used selenium and python for this.
'''

#Data extraction for College Dunia
import pandas as pd
import numpy as np
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import matplotlib.pyplot as plt
import seaborn as sns
%matplotlib inline

#initialize driver
while True:
    course_domain = input("Enter Course Domain. Options:\neconomics\nfinance\npsychology\neducation\nlaw\narchitecture\nnursing\ndata-science-and-analytics\naccounting\nmedicine\nbusiness\nlanguage\nhistory\nengineering\nphysics\narts\nagriculture\ndesign\nenvironmental-studies\nhumanities\nmathematics\nbiology\nbiotechnology\nchemistry\ncommerce\nfashion-design\ngeography\ngraphic-design\ninformation-studies\npharmacy\ntourism-and-hospitality\nsciences\naviation\nsocial-studies\njournalism\nmanagement\nsocial-work")
    if course_domain not in "economics finance psychology education law architecture nursing data-science-and-analytics accounting medicine business language history engineering physics arts agriculture design environmental-studies humanities mathematics biology biotechnology chemistry commerce fashion-design geography graphic-design information-studies pharmacy tourism-and-hospitality sciences aviation social-studies journalism management social-work":
        print("Wrong domain input. Try again!")
        continue
    else:
        break

while True:    
    course_level = input("Enter level of course. Options:\nmaster\n bachelor")
    if course_level not in "master bachelor":
        print("Wrong level input. Try again!")
        continue
    else:
        break
        
st = time.time()
driver = webdriver.Chrome()

#setting up search url and query keywords
listings = pd.DataFrame(columns=['name','location','course_name','fees_yrly','duration','rankings'])
link = f'https://collegedunia.com/study-abroad/{course_domain}/{course_level}-colleges' #driver.find_element(By.CLASS_NAME, "//*[@id="rso"]/div[1]/div/div/div[1]/div/div/div[1]/div/a")
driver.get(link)
driver.maximize_window()
next_page = '99'
n = 0
while n < int(next_page[-1]):
    driver.implicitly_wait(6)
    #driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    try:
        next_pages = driver.find_elements(By.CLASS_NAME, "page-link")
        next_page = next_pages[-1].get_attribute('href')
    except:
        next_pages = ['0']
        next_page = next_pages
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
            fees_yrly = np.nan
        try:
            duration = entry.find_element(By.CSS_SELECTOR,"span.jsx-2188674517.text-primary.dur-truncate.w-40.text-right").text
        except:
            duration = None
        try:
            rankings = [i.text for i in entry.find_elements(By.CSS_SELECTOR,"span.jsx-2188674517.rank-span")]
        except:
            rankings = np.nan
        listings = listings.append({'name':name,'location':location,'course_name':course_name,'fees_yrly':fees_yrly,'duration':duration,'rankings':rankings},ignore_index=1)
    n+=1
    if next_page != next_pages:
        driver.get(next_page)

driver.quit()

#creating a copy data frame to work with
listings_new = listings.copy()
listings_new[['city', 'country']] = listings_new['location'].str.split(", ",expand=True)

#extracting fee information from string object into 2 new columns, one to store numerical value and the other to store the string part
listings_new['fee'] = listings_new['fees_yrly'].str.extract("(\d+.\d)")
listings_new['value'] = listings_new['fees_yrly'].str[-4:]
listings_new['duration(span)'] = listings_new['duration'].str.extract("([a-zA-Z]+)")
listings_new['duration(time)'] = listings_new['duration'].str.extract("(\d+)")

#creating a mapping dictionary to map the numberical value of the equivalent string in the 'value' column
fee_key = {'L/Yr':100000, np.nan: 0, 'K/Yr':10000, '--':1}
listings_new['value'] = listings_new['value'].map(fee_key)

#creating another mapping dictionary to map the approx. time in years of the course duration
duration_dict = {"Years":1,"Year":1,"Months":0.0834,"Weeks":0.01923}
listings_new['duration(span)'] = listings_new['duration(span)'].map(duration_dict)
listings_new['duration(yrs)'] = listings_new['duration(time)'].astype(float)*listings_new['duration(span)']

#performing some cleanup operations
listings_new = listings_new.dropna(subset=['name'])
listings_new['fees_per_year'] = listings_new['fee'].astype(float)*listings_new['value']
listings_new['total_fees'] = listings_new['fees_per_year']*listings_new['duration(yrs)']
listings_new.drop(columns=['fee','value','location','fees_yrly'],inplace=True)
listings_new[['fees_per_year', 'total_fees']] = listings_new[['fees_per_year', 'total_fees']].round(2)
listings_new['ranks'] = listings_new['rankings'].astype(str).str.findall("\d+")
listings_new['rank_THE'] = listings_new['ranks'].str[0].astype(np.float64)
listings_new['rank_QS'] = listings_new['ranks'].str[1].astype(np.float64)
listings_new.drop(['rankings','ranks','duration(time)','duration(span)'], axis=1,inplace=True)
listings_new = listings_new.drop_duplicates()
listings_new['rank_THE'] = listings_new['rank_THE'].fillna(0)
listings_new['rank_QS'] = listings_new['rank_QS'].fillna(0)

#summary visualization
plt.style.use('ggplot')
fig, ax = plt.subplots(1,1)
ax.set_xlim(0,20000000)
plt.xticks(rotation = 45)
ax.set_ylim(0,20000000)
sns.swarmplot(data= listings_new,x='country',y ='total_fees',hue='duration(yrs)')

#store data frame to csv
listings_new.to_csv(f"D:/{course_level} {course_domain}.csv",index=0)
et = time.time()
print(f'Elapsed time = {et - st}')


