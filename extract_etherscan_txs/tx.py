from bs4 import BeautifulSoup

def main():
    with open("tx.html") as fp:
        soup = BeautifulSoup(fp, "html.parser")
    timestamp = extract_timestamp(soup)
    extract_swap(soup)
    # print(timestamp)

def extract_timestamp(soup):
    div_timestamp = soup.find("div", {"id": "ContentPlaceHolder1_divTimeStamp"})
    raw_timestamp = div_timestamp.find("div", {"class": "col-md-9"}).text
    timestamp = raw_timestamp[raw_timestamp.find("(")+1:raw_timestamp.find(")")]
    timestamp = replace_month(timestamp)
    return timestamp

def extract_swap(soup):
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
    print(swaps_details)
    swaps = []
    i = 0
    while i < len(swaps_details) - 1:
        amount_now = swaps_details[i][-4]
        amount_next = swaps_details[i + 1][2]
        if amount_now == amount_next:
            new_swap = swaps_details[i] + swaps_details[i + 1]
            swaps_details.pop(i + 1)
            swaps_details[i] = new_swap
        i = i + 1    
    print(swaps_details)

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
    main()
