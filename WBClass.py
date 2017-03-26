from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as BS4
import time

USERNAME = ""
PASSWORD = ""

class Scrapper(object):
    def __init__(self):
        self.driver = webdriver.Chrome(executable_path="./chromedriver")
        self.wait = WebDriverWait(self.driver, 10)
        self.page_source = ''
        self.login()

    def login(self):
        try:
            self.driver.get("http://www.glassdoor.com/profile/login_input.htm")
            user_login = self.wait.until(EC.presence_of_element_located( (By.NAME, "username")))
            pw_login = self.driver.find_element_by_class_name("signin-password")
            login_button = self.driver.find_element_by_id("signInBtn")
            user_login.send_keys(USERNAME)
            user_login.send_keys(Keys.TAB)
            time.sleep(1)
            pw_login.send_keys(PASSWORD)
            time.sleep(1)
            login_button.click()

        except TimeoutException:
            print("TimeoutException! Username/password field or login button not found on glassdoor.com")
            exit()

    def fetch_page(self, url):
        try:
            time.sleep(2)
            self.driver.get(url)
            while not self.driver.find_elements_by_class_name('next'):
                print('waiting for page to load..')

            time.sleep(2)
            self.page_source = self.driver.page_source
            return self.driver.page_source
        except TimeoutException:
            print('An error occured, Please check if url is correct.')
            exit()

    def parse_data(self):
        data = []
        soup = BS4(self.page_source, "html.parser")
        elements_divs = soup.find_all('div', {'class': 'hreview'})

        for div in elements_divs:

            date = div.find('time', {'class': 'date subtle small'}).get('datetime').strip()
            title = div.find('span', {'class': 'summary'}).text.strip()
            rating = div.find('span', {'class': 'value-title'}).get('title').strip()

            valid = div.find('span', {'class': 'authorJobTitle'}).text.strip()
            if(valid):
                status=valid.split("-")[0]
                position =valid.split("-")[1]
            else:
                status=position=''

            element_body = div.find('div', {'class': 'cell reviewBodyCell'})

            valid = element_body.find('p', {'class': 'tightBot'})
            if valid and '(' in valid.text:
                duration = valid.text.split('(')[1]
            else:
                duration=''

            valid = element_body.find('p', {'class': 'pros noMargVert truncateThis wrapToggleStr'})
            pros = valid.text.strip() if valid else ''

            valid = element_body.find('p', {'class': 'cons noMargVert truncateThis wrapToggleStr'})
            cons = valid.text.strip() if valid else ''

            valid = element_body.find('p', {'class': 'adviceMgmt noMargVert truncateThis wrapToggleStr'})
            management_advice = valid.text.strip() if valid else ''

            outlook = {'recommends': None, 'approves': None, 'outlook': None}

            for item in element_body.find_all('div', {'class': 'middle'}):
                if 'Recommends' in item.text:
                    if 'green' in item.find('i').get('class'):
                        outlook['recommends'] = "1"
                    elif 'yellow' in item.find('i').get('class'):
                        outlook['recommends'] = "0"
                    elif 'red' in item.find('i').get('class'):
                        outlook['recommends'] = "-1"

                elif 'Outlook' in item.text:
                    if 'green' in item.find('i').get('class'):
                        outlook['outlook'] = "1"
                    elif 'yellow' in item.find('i').get('class'):
                        outlook['outlook'] = "0"
                    elif 'red' in item.find('i').get('class'):
                        outlook['outlook'] = "-1"
            review = {
                'headline': title,
                'rating': rating,
                'position': position,
                'status': status,
                'date': date,
                'duration': duration,
                'cons': cons,
                'pros': pros,
                'management_advice': management_advice,
                'recommends': outlook['recommends'],
                'outlook': outlook['outlook'],
            }

            data.append(review)

        return data

    def fetch_nextpage(self):
        time.sleep(4)
        soup = BS4(self.page_source, "html.parser")
        findpage = soup.find('li', {'class': 'next'})
        if findpage.find('a'):
            nextpage_url = 'http://glassdoor.com' + findpage.find('a').get('href')
            return nextpage_url
        else:
            return None
