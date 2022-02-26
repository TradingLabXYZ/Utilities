import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(ChromeDriverManager().install())

driver.get("https://etherscan.io/tokentxns?a=0xd12d8b2f0480bf87d75a2559a397f486ed8eb026")
time.sleep(3)

links = driver.find_elements(By.TAG_NAME, "a")
for link in links:
    raw_link = str(link.get_attribute("href"))
    if "/tx/" in raw_link:
        print(raw_link)
        driver.execute_script('window.open("{}","_blank");'.format(raw_link))
        time.sleep(3)
        inner_html = driver.page_source
        print(inner_html[0:100])

driver.quit()
