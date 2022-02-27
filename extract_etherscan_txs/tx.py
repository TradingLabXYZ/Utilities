import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def parse_txs(html):
    soup = BeautifulSoup(html, "html.parser")
    timestamp = extract_timestamp(soup)
    info = extract_tx_info(timestamp, soup)
    print(info)

def extract_timestamp(soup):
    div_timestamp = soup.find("div", {"id": "ContentPlaceHolder1_divTimeStamp"})
    raw_timestamp = div_timestamp.find("div", {"class": "col-md-9"}).text
    timestamp = raw_timestamp[raw_timestamp.find("(")+1:raw_timestamp.find(")")]
    timestamp = replace_month(timestamp)
    return timestamp.replace(" +UTC", "")

def extract_tx_info(timestamp, soup):
    info_details = get_info_from_soup(soup)
    if info_details[0][0] == "Swap":
        info_details = merge_swaps(info_details)
        info_details = clean_swaps(timestamp, info_details)
    if info_details[0][0] in ["Collect", "Remove", "Add"]:
        info_details = clean_liquidity(timestamp, info_details)
    if info_details[0][0] == "From":
        info_details = clean_transfer(timestamp, info_details)
    return info_details

def get_info_from_soup(soup):
    info_details = []
    div_sections = soup.find_all("div", {"class": "col-md-9"})
    for div_section in div_sections:
        div_infos = div_section.find_all("div", {"class": "media-body"})
        for div_info in div_infos:
            temp_info_details = []
            if div_info:
                spans_info = div_info.find_all(["span", "img", "a"])
                for span_info in spans_info:
                    if span_info.text:
                        temp_info_details.append(span_info.text.strip())
            if temp_info_details[0] in ["Swap", "Collect", "Remove", "Add", "From"]:
                info_details.append(temp_info_details)
    return info_details

def merge_swaps(info_details):
    i = 0
    while i < len(info_details) - 1:
        amount_now = info_details[i][-4]
        amount_next = info_details[i + 1][2]
        if amount_now == amount_next:
            new_swap = info_details[i] + info_details[i + 1]
            info_details.pop(i + 1)
            info_details[i] = new_swap
        i = i + 1    
    return info_details

def clean_swaps(timestamp, info_details):
    swaps_cleaned = []
    for swap in info_details:
        from_qty = swap[2]
        from_pair = swap[3]
        to_qty = swap[-4]
        to_pair = swap[-3]
        swaps_cleaned.append([
            timestamp, "Swap", from_qty, from_pair, to_qty, to_pair
        ])
    return swaps_cleaned

def clean_liquidity(timestamp, info_details):
    liquidity_cleaned = []
    for liquidity in info_details:
        tx_type = liquidity[0]
        qty1 = liquidity[1]
        pair1 = liquidity[2]
        qty2 = liquidity[4]
        pair2 = liquidity[5]
        liquidity_cleaned.append([
            timestamp, tx_type, qty1, pair1, qty2, pair2
        ])
    return liquidity_cleaned

def clean_transfer(timestamp, info_details):
    transfer_cleaned = []
    for transfer in info_details:
        tx_type = "Transfer"
        from_add = transfer[1]
        to_add = transfer[5]
        qty = transfer[9]
        pair = transfer[11]
        transfer_cleaned.append([
            timestamp, tx_type, from_add, to_add, qty, pair
        ])
    return transfer_cleaned

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
    with open("tx.html") as fp:
        parse_txs(fp)
