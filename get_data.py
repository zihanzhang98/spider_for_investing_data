import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import os
import shutil
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys

ua = UserAgent()
headers = {'User-Agent': ua.chrome}


def request_page(url, headers):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
    except requests.RequestException:
        return None


country_set = {'日本', '韩国', '意大利', '新加坡', '泰国', '马来西亚', '越南', '德国', '澳大利亚', '美国', '阿联酋', '法国', '英国', '加拿大', '印度', '菲律宾',
               '俄罗斯', '西班牙', '斯里兰卡', '芬兰', '瑞典', '伊拉克', '比利时', '埃及', '以色列', '黎巴嫩'}

base_url = 'https://cn.investing.com/indices/world-indices'
base_url0 = 'https://cn.investing.com'
html = request_page(base_url, headers)
soup = BeautifulSoup(html, 'lxml')
tables = soup.find_all('table')
tbodies = []
for table in tables:
    tbody = table.find('tbody')
    tbodies.append(tbody)
country2tbody = {}
for tbody in tbodies:
    country = tbody.find('span').get('title')
    if country is not None and country in country_set:
        country2tbody[country] = tbody
country2urls = {}
sum_length = 0
for key in country2tbody.keys():
    urls = []
    tbody = country2tbody[key]
    tmp_as = tbody.find_all('a')
    for tmp in tmp_as:
        url = tmp.get('href')
        urls.append(base_url0 + url + '-historical-data')
    sum_length += len(urls)
    country2urls[key] = urls

current_time = time.strftime('%Y-%m-%d', time.localtime())
os.mkdir(current_time)
path = sys.argv[1]
for key in country2urls.keys():
    os.mkdir(path + '/' + current_time + '/' + key)
fileset = set()
country2names = {}
for key in country2urls.keys():
    urls = country2urls[key]
    names = []
    for url in urls:
        attempts = 0
        fail = True
        while attempts < 5 and fail:
            try:
                options = webdriver.ChromeOptions()
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')
                options.add_argument('--no-sandbox')
                desired_capabilities = DesiredCapabilities.CHROME
                desired_capabilities['pageLoadStrategy'] = 'none'
                driver = webdriver.Chrome(options=options)
                driver.get(url)
                name = (By.CSS_SELECTOR, '.float_lang_base_1.inlineblock')
                name = WebDriverWait(driver, 30, 0.5).until(EC.presence_of_element_located(name))
                namestr = name.text.replace(' ', '_').replace('/', '_')
                names.append(namestr)
                #names.append(driver.find_element_by_css_selector('.float_lang_base_1.inlineblock').text)
                print(names[-1])
                login = WebDriverWait(driver, 30, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, 'login')))
                login.click()
                email = driver.find_element_by_id('loginFormUser_email')
                email.click()
                email.send_keys('964108463@qq.com')
                password = driver.find_element_by_id('loginForm_password')
                password.click()
                password.send_keys('zhang19980531')
                password.send_keys(Keys.ENTER)
                sleep(15)
                WebDriverWait(driver, 60, 0.5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.newBtn.LightGray.downloadBlueIcon.js-download-data'))).click()
                sleep(10)
                filename = max([f for f in os.listdir(path)], key=os.path.getctime)
                if filename[-3:] == 'csv' and (filename not in fileset):
                    os.system('mv "%s/%s" %s/%s' % (path, filename, current_time, key))
                    fileset.add(filename)
                    attempts += 1
                    fail = False
                else:
                    print('Download failure: %s' % url)
                    attempts += 1
                driver.quit()
            except Exception as e:
                print('Download failure: %s' % url)
                attempts += 1
                driver.quit()
    country2names[key] = names

