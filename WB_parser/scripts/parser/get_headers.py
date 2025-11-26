from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from time import sleep
from fake_useragent import UserAgent

options = Options()
options.add_argument('--window-size=800,600')
options.add_argument('--disable-blink-features=AutomationControlled')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get('https://www.wildberries.ru')
while driver.get_cookies() == []:
    sleep(1)

cookies = driver.get_cookies()
driver.close()

cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
Cookie = f'_wbauid={cookies_dict.get('_wbauid')}; x_wbaas_token={cookies_dict.get('x_wbaas_token')}'

UserAgent = UserAgent()

headers = {
    'User-Agent': f'{UserAgent.chrome}',
    'Cookie' : f'{Cookie}',
}