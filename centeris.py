from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from os import system, getenv, path, name
from dotenv import load_dotenv
import sys
from time import sleep
from rich import print
import json
import schedule

# load .env file
load_dotenv()


class CenterisScraping:
    def BrowserSetup(self):
        browser = webdriver.Chrome("Extension/chromedriver")
        browser.maximize_window()
        return browser

    def ConfigSearch(self):
        keyword_data = open("Config/config.json")
        data = json.load(keyword_data)
        keyword_list = []
        for i in range(len(data["querySearch"])):
            keyword_list.append(data["querySearch"][i])
        print(
            "Total Keyword [bold white]{}[/bold white]".format(
                len(keyword_list)
            )
        )
        return keyword_list

    def ConsultHandle(self, browser):
        keyword_list = self.ConfigSearch()

        # open https://www.centris.ca/en/consult-search?name=
        for i in range(len(keyword_list)):
            keyword_name = keyword_list[i]
            raw_data = []

            # Open Browser
            # browser = browserSetup()
            browser.implicitly_wait(5)
            sleep(2)
            browser.get(
                "https://www.centris.ca/en/consult-search?name={}".format(
                    keyword_name
                )
            )
            print(
                "Open Keyword : [bold white]{}[/bold white]".format(
                    keyword_name
                )
            )
            browser.implicitly_wait(3)
            sleep(2)
            total_page = str(
                browser.find_element_by_xpath(
                    "/html/body/main/div[7]/div/div/div[1]/div/div/ul/li[3]"
                ).text
            )[3:]
            for page in range(int(total_page)):
                sleep(2)
                web_page = BeautifulSoup(
                    browser.page_source, "html.parser"
                )
                href_tag = web_page.find_all(
                    "a", class_="a-more-detail"
                )
                for i in range(0, len(href_tag)):
                    raw_data.append(href_tag[i]["href"])
                browser.find_element_by_xpath(
                    "/html/body/main/div[7]/div/div/div[1]/div/div/ul/li[4]/a"
                ).click()
            clean_data = list(set(raw_data))
            print(clean_data)
            browser.implicitly_wait(5)
            sleep(3)
            browser.quit()

    def LoginHandle(self):
        browser = self.BrowserSetup()
        email_data = getenv("email")
        password_data = getenv("password")

        # Open Login Page
        browser.get("https://www.centris.ca/en/login?uc=2")
        browser.implicitly_wait(5)
        email_form = browser.find_element_by_id(
            "loginradius-login-emailid"
        )
        email_form.send_keys(email_data)

        password_form = browser.find_element_by_id(
            "loginradius-login-password"
        )
        password_form.send_keys(password_data)

        browser.find_element_by_id("loginradius-submit-login").click()
        browser.implicitly_wait(5)
        sleep(3)
        self.ConsultHandle(browser)
        # browser.quit()

    def main(self):
        schedule.every(1).minutes.do(self.LoginHandle)
        while True:
            try:
                schedule.run_pending()
                sleep(2)
            except KeyboardInterrupt:
                print("Program Stop")
                sys.exit()


if __name__ == "__main__":
    cs = CenterisScraping()
    cs.main()
