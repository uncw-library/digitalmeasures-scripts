# scrape_directory.py

import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

APP_ROOT = os.path.split(os.path.realpath(__file__))[0]
LOG_FILE = os.path.join(APP_ROOT, "geckodriver.log")


class SeleniumDriver:
    def __init__(self):
        options = Options()
        options.add_argument("-headless")
        self.driver = webdriver.Firefox(
            executable_path="geckodriver", options=options, service_log_path=LOG_FILE
        )

    def lookup_directory(self, firstname="", lastname=""):
        self.driver.get("https://itsappserv01.uncw.edu/directory/")

        radio_elem = self.driver.find_element_by_id("rdoSearchTable_0")
        firstname_elem = self.driver.find_element_by_name("txtFirstName")
        lastname_elem = self.driver.find_element_by_name("txtLastName")
        submit_elem = self.driver.find_element_by_name("btnSearch")

        radio_elem.send_keys(Keys.ARROW_RIGHT)
        firstname_elem.clear()
        firstname_elem.send_keys(firstname)
        lastname_elem.clear()
        lastname_elem.send_keys(lastname)
        submit_elem.send_keys(Keys.RETURN)

        try:
            response_table = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.ID, "gvDirectory"))
            )
        except TimeoutException:
            return []
        response_rows = response_table.find_elements_by_xpath("tbody/tr")

        row_dicts = []
        for num, row in enumerate(response_rows):
            if num == 0:
                continue
            name, pos, dept, _, email, _ = [
                i.text for i in row.find_elements_by_xpath("td")
            ]
            row_dict = {
                "table_row": num,
                "name": name,
                "pos": pos,
                "dept": dept,
                "email": email,
            }
            row_dicts.append(row_dict)

        return row_dicts
