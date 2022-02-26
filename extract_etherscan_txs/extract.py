import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def parse_txs(html):
    soup = BeautifulSoup(html, "html.parser")
    timestamp = extract_timestamp(soup)
    swaps = extract_swap(timestamp, soup)
    print(swaps)

def extract_timestamp(soup):
    div_timestamp = soup.find("div", {"id": "ContentPlaceHolder1_divTimeStamp"})
    raw_timestamp = div_timestamp.find("div", {"class": "col-md-9"}).text
    timestamp = raw_timestamp[raw_timestamp.find("(")+1:raw_timestamp.find(")")]
    timestamp = replace_month(timestamp)
    return timestamp.replace(" +UTC", "")

def extract_swap(timestamp, soup):
    swaps_details = get_swaps_from_soup(soup)
    swaps_merged = merge_swaps(swaps_details)
    swaps_cleaned = clean_swaps(timestamp, swaps_merged)
    return swaps_cleaned

def get_swaps_from_soup(soup):
    swaps_details = []
    div_sections = soup.find_all("div", {"class": "col-md-9"})
    for div_section in div_sections:
        div_swaps = div_section.find_all("div", {"class": "media-body"})
        for div_swap in div_swaps:
            temp_swap_details = []
            if div_swap:
                spans_swap = div_swap.find_all(["span", "img", "a"])
                for span_swap in spans_swap:
                    if span_swap.text:
                        temp_swap_details.append(span_swap.text)
            if temp_swap_details[0] == "Swap":
                swaps_details.append(temp_swap_details)
    return swaps_details

def merge_swaps(swaps_details):
    i = 0
    while i < len(swaps_details) - 1:
        amount_now = swaps_details[i][-4]
        amount_next = swaps_details[i + 1][2]
        if amount_now == amount_next:
            new_swap = swaps_details[i] + swaps_details[i + 1]
            swaps_details.pop(i + 1)
            swaps_details[i] = new_swap
        i = i + 1    
    return swaps_details

def clean_swaps(timestamp, swaps_merged):
    swaps_cleaned = []
    for swap in swaps_merged:
        from_qty = swap[2]
        from_pair = swap[3]
        to_qty = swap[-4]
        to_pair = swap[-3]
        swaps_cleaned.append([
            timestamp, from_qty, from_pair, to_qty, to_pair
        ])
    return swaps_cleaned

def replace_month(timestamp):
    months = {
        "Jan": "01",
        "Feb": "02",
        "Mar": "03",
        "Apr": "04",
        "Mai": "05",
        "Jun": "06",
        "Jul": "07",
        "Aug": "08",
        "Sep": "09",
        "Oct": "10",
        "Nov": "11",
        "Dec": "12"
    }
    for month in months:
        timestamp = timestamp.replace(month, months[month])
    return timestamp


if __name__ == "__main__":
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://etherscan.io/tokentxns?a=0xd12d8b2f0480bf87d75a2559a397f486ed8eb026")
    time.sleep(3)
    temp_links = driver.find_elements(By.TAG_NAME, "a")
    links = []
    for link in temp_links:
        raw_link = str(link.get_attribute("href"))
        if "/tx/" in raw_link:
            links.append(raw_link)
    for link in links:
        print("\n", link)
        driver.get(link)
        time.sleep(3)
        parse_txs(driver.page_source)
    driver.quit()
