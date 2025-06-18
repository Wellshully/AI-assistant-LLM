from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)  # 讓 Chrome 開著不關

service = Service("C:/Users/welly/chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://www.youtube.com")
time.sleep(1)
search_box = driver.find_element(By.NAME, "search_query")
search_box.send_keys("zutomayo")
search_box.send_keys(Keys.ENTER)

# 程式結束，但 Chrome 保持開啟
