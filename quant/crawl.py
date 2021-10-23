import pandas as pd
import numpy as np
import time
import pandas as pd
import numpy as np
import re as regex
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


user_name=  'dtdathsgs@gmail.com'
password = '*dksh123GAY'

PATH = '/home/dtd43/geckodriver'
def extract_price(string_price):
    return float(string_price.replace(',', ''))


def extract_cumulative_volume(string_volume):
    return float(string_volume.replace(',', ''))


def extract_trade_volume(string_volume):
    return float(string_volume.replace(',', ''))


def extract_time(string_time, currentDate):
    string_time = currentDate + " " + string_time
    datetime_object = datetime.strptime(string_time, "%Y-%m-%d %H:%M:%S")

    return datetime_object
def downloadWebData(stock_name, currentDate):
    try:
        #currentDate = datetime.now().strftime('%Y-%m-%d')
        options = Options()
        options.headless = True
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Firefox(options=options, executable_path='/home/dtd43/geckodriver')
        url = r"https://finance.vietstock.vn/" + \
            stock_name + r"/thong-ke-giao-dich.htm"
        driver.get(url)
        driver.maximize_window()  # we need to maximize the window for avoid the advertisement

        time.sleep(4)
        # we will not soup because the selenium will update the page reponsively but the soup could not
        timeData = []  # init the list for holding data

        priceData = []
        volumeData = []
        volume_per_trade = []
        maximum_page = int(driver.find_element_by_xpath(
            '//*[@id="deal-content"]/div/div/div[2]/div/div/div/span[1]/span[2]').text)

        first_time = 0
        for page in range(1, maximum_page + 1):
            # updat the table where we extract the data
            table_element = driver.find_element_by_xpath(
                '//*[@id="deal-content"]/div/div/div[2]/div/table/tbody')

            rows = table_element.find_elements(By.TAG_NAME, 'tr')

            for row in rows:
                td = row.find_elements(By.TAG_NAME, 'td')

                timeData.append(extract_time(td[0].text, currentDate))
                priceData.append(extract_price(td[1].find_element(By.CLASS_NAME, 'p-r-xs').text))
                volumeData.append(extract_cumulative_volume(td[3].text))
                volume_per_trade.append(extract_trade_volume(td[2].text))
            # we will create a button to put the next button
            if first_time == 0:
                driver.execute_script("window.scrollBy(0,250)")

            # we find the btn of the next page
            driver.find_element_by_xpath('//*[@id="btn-page-next"]').click()

            if first_time == 0:
                time.sleep(0.5)

                username = driver.find_element(
                    By.XPATH, '//*[@id="txtEmailLogin"]')
                password = driver.find_element(
                    By.XPATH, '//*[@id="txtPassword"]')
                username.send_keys('dtdathsgs@gmail.com')
                password.send_keys('*dksh123')
                driver.find_element(
                    By.XPATH, '//*[@id="btnLoginAccount"]').click()
                start_sleep_time = datetime.now()
                time.sleep(10)
                end_sleep_time = datetime.now()

                print(end_sleep_time - start_sleep_time)
                print('success login and collect stock data:{:}'.format(stock_name))
                driver.find_element_by_xpath(
                    '//*[@id="btn-page-next"]').click()
                first_time = 1
        df = pd.DataFrame(
            {'Time': timeData, 'Price': priceData, 'Volume_per_trade': volume_per_trade, 'Volume': volumeData})
        df.to_csv(stock_name + '-' + currentDate + '.csv')
        driver.close() # this code is aims to save the resources 
        return True
    except Exception as e:
        print(e)
        return False

class CollectMultiThreading():

    VN30_list = ['MBB', 'ACB', 'TCB', 'VJC', 'STB', 'VHM', 'SAB', 'HDB', 'BVH', 'CTG', 'BID', 'GAS', 
                'TPB', 'VPB', 'NVL', 'KDH', 'VCB', 'GVR', 'PLX', 'PNJ', 'SSI', 'PDR', 'POW', 'VNM', 
                'VIC', 'VRE', 'FPT', 'MWG', 'HPG', 'MSN']
    lack_list =  ['HPG','KDH','VPB']
    def __init__(self, stock_list = lack_list):
        self.stock_list = stock_list
        self.getStockList(usehose=False, usehnx=False)
    def getStockList(self, useVn30 = True, usehose = True, usehnx = True, useupcom = True):
        VN30_list = ['MBB', 'ACB', 'TCB', 'VJC', 'STB', 'VHM', 'SAB', 'HDB', 'BVH', 'CTG', 'BID', 'GAS', 
                'TPB', 'VPB', 'NVL', 'KDH', 'VCB', 'GVR', 'PLX', 'PNJ', 'SSI', 'PDR', 'POW', 'VNM', 
                'VIC', 'VRE', 'FPT', 'MWG', 'HPG', 'MSN']
        hose = pd.read_csv('hose.csv', index_col=0).Name.to_list()
        hnx = pd.read_csv('hnx.csv', index_col=0).Name.to_list()
        upcom = pd.read_csv('upcom.csv', index_col=0).Name.to_list()

        self.stock_list = []
        if not useVn30:
            for stock in VN30_list:
                if stock in hose:
                    hose.remove(stock)
        if usehose == True:
            for stock in hose:
                self.stock_list.append(stock)
        if usehnx == True:    
            for stock in hnx:
                self.stock_list.append(stock)
        if useupcom == True:    
            for stock in upcom:
                self.stock_list.append(stock)

    def downloadData(self):
        for i, item in enumerate(self.stock_list):
            start = datetime.now()
            #currentDate = datetime.now().strftime('%Y-%m-%d')
            currentDate = '2021-10-04'
            downloadWebData(item, currentDate=currentDate)
            end  = datetime.now()
            print('Time collecting the data:')
            print(end - start)
            print("finish crawl stock:{:}".format(item))

if __name__ == '__main__':
    downloader = CollectMultiThreading()
