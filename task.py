import time
import timeit
import logging as log
import re
from pathlib import Path
from datetime import datetime

import selenium
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


SEARCH_PHRASE = "COVID"
CATEGORY = "NEWS"

def main():
    log.basicConfig(filename="task.log", level=log.INFO,
                    format="%(asctime)s %(levelname)-8s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
    log.info("Started")
    start = timeit.default_timer()

    browser = webdriver.Chrome()
    webdriver.Chrome()
    wait = WebDriverWait(browser, 15)
    log.info("Opening Website")
    browser.get("https://gothamist.com/")
    log.info("Searching search-button")
    search = browser.find_element(By.CLASS_NAME, "search-button")
    search.click()
    log.info("Waiting input to write search")
    search_input = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "search-page-input")))
    log.info("Writing input")
    search_input.send_keys(SEARCH_PHRASE)
    search_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "search-page-button")))
    search_button.click()
    log.info("Doing the search")
    log.info("Waiting the search")
    all_news = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "tag-small")))
    log.info("Catching the information")
    data = []
    for news in all_news:
        result = dict()

        title_el = news.find_element(By.CLASS_NAME, "h2")
        result["title"] = title_el.text
        category = news.find_element(By.CLASS_NAME, "p-button-label")
        result["category"] = category.text
        description = news.find_element(By.CLASS_NAME, "desc")
        result["description"] = description.text

        photo = news.find_element(By.CLASS_NAME, "prime-img-class")
        photo_src = photo.get_attribute("src")
        result["url_photo"] = photo_src

        photo_split = photo_src.split("/")
        photo_name = photo_split[4]

        photo_file = Path(photo_name + ".png")
        if photo_file.is_file() == False:
            photo_browser = webdriver.Chrome()
            photo_browser.get(photo_src)
            photo_browser.get_screenshot_as_file(photo_name + ".png")
            log.info("Saving Image:"+ photo_name )
            photo_browser.close()


        result["photo_name"] = photo_name

        count_search_phrases_title = title_el.text
        count_search_phrases_description = description.text
        result["count_search"] = count_search_phrases_title.count(SEARCH_PHRASE) + count_search_phrases_description.count(SEARCH_PHRASE)

        result["money"] = bool(re.search(r"^\$(0|[1-9][0-9]{0,2})(,\d{3})*(\.\d{1,2})?$", title_el.text ))

        search_date = datetime.now()
        result["search date"] = search_date

        result["search key"] = SEARCH_PHRASE

        data.append(result)

    df_data =pd.DataFrame(data)
    log.info("importing information" )
    
    path_news = Path("news.csv")
    if path_news.is_file() == False:
        df_data.to_csv("news.csv",mode="a")
    else:
        df_data.to_csv("news.csv",mode="a",header=False)

    #if CATEGORY is null:
    #df_data.to_csv("news.csv",mode="a")
    #else
    #df_filter = df_data.loc[df_data["category"].isin([CATEGORY])]
    #df_filter.to_csv("filter.csv",mode="a")

    browser.quit()
    end = timeit.default_timer()
    log.info("Duration: %f" %(end - start))
    log.info("Finished")







if __name__ == "__main__":
    main()