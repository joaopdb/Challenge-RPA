
import timeit
import logging as log
import re
from pathlib import Path
from datetime import datetime

from robocorp import workitems
from robocorp.tasks import task
from RPA.Excel.Files import Files as Excel
from RPA.Browser.Selenium import Selenium

@task
def main():

    item = workitems.inputs.current
    SEARCH = item.payload
    SEARCH_PHRASE = SEARCH['SEARCH_PHRASE']

  
    log.basicConfig(filename="task.log", level=log.INFO,
                    format="%(asctime)s %(levelname)-8s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")
    log.info("Started")
    start = timeit.default_timer()
    browser_lib = Selenium()
    browser_lib.set_action_chain_delay(8)
    log.info("Opening Website")
    browser_lib.open_headless_chrome_browser("https://gothamist.com/")
    log.info("Resize Window")
    browser_lib.set_window_size(1080 ,3300)
    log.info("Removing overlay")
    #browser_lib.execute_javascript("document.getElementsByClassName('fc-dialog-overlay')[0].remove()")
    #browser_lib.execute_javascript("document.getElementsByClassName('fc-consent-root')[0].remove()")
    browser_lib.wait_and_click_button("xpath://*[@id=\"om-gk66zqvxcdypoosfxlyu-yesno\"]/div/button")
    log.info("Searching search-button")
    browser_lib.click_element_when_visible("class:search-button")
    log.info("Waiting input to write search")
    browser_lib.input_text_when_element_is_visible("class:search-page-input",SEARCH_PHRASE)
    log.info("Doing the search")
    browser_lib.click_element_when_visible("class:search-page-button")
    log.info("Waiting the search")
    browser_lib.wait_until_element_is_visible("class:tag-small",30)
    log.info("Catching the information")
    all_news = browser_lib.find_elements("class:tag-small")


   
    data = []
    for news in all_news:
        
        result = dict()

        log.info("Finding title of the news")
        title_el = browser_lib.find_element("class:h2",news)
        log.info("Catching title of the news")
        result["title"] = title_el.text

        log.info("Finding category")
        category = browser_lib.find_element("class:p-button-label",news)
        log.info("Catching category")
        result["category"] = category.text

        log.info("Finding description")
        description = browser_lib.find_element("class:desc",news)
        log.info("Catching description")
        result["description"] = description.text

        log.info("Finding URL Photo")
        photo_src = browser_lib.find_element("class:prime-img-class",news).get_attribute("src")
        log.info("Catching URL Photo")
        result["url_photo"] = photo_src
        
        log.info("Catching photo name")
        photo_split = photo_src.split("/")
        photo_name = photo_split[4]
        result["photo_name"] = photo_name
        photo_file = Path(f"output/{photo_name}.png")
        
        if photo_file.is_file() == False:
            log.info(f"Catching IMG Photo {photo_name}.png")
            photo_lib = Selenium()
            photo_lib.set_action_chain_delay(3)
            photo_lib.open_headless_chrome_browser(photo_src)
            photo_lib.set_window_size(318 ,212)
            photo_lib.screenshot(filename=f"output/{photo_name}.png")
            photo_lib.close_browser()
        

        count_search_phrases_title = title_el.text.count(SEARCH_PHRASE)
        count_search_phrases_description = description.text.count(SEARCH_PHRASE)
        result["count_search"] = count_search_phrases_title + count_search_phrases_description

        result["money"] = bool(re.search(r"^\$(0|[1-9][0-9]{0,2})(,\d{3})*(\.\d{1,2})?$", title_el.text ))
        log.info(f"Catching IMG Photo {photo_name}.png")
        search_date = datetime.now()
        result["search date"] = search_date

        log.info(f" {SEARCH_PHRASE}.")
        result["search key"] = SEARCH_PHRASE

        data.append(result)
    log.info("Closing All browser" )
    browser_lib.close_browser()
    browser_lib.close_all_browsers()

    excel = Excel()
    log.info("Create a workbook" )
    excel.create_workbook()
    log.info("importing information" )
    excel.append_rows_to_worksheet(content=data)
    log.info("Saving information" )
    excel.save_workbook(f"output/{SEARCH_PHRASE}.xlsx")
    log.info("Close Workbookn" )
    excel.close_workbook()

