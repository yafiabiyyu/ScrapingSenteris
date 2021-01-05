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
    def clear(self): 
        if name == 'nt': 
            _ = system('cls') 
        else: 
            _ = system('clear') 

    def BrowserSetup(self):
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        browser = webdriver.Chrome(
            "Extension/chromedriver", options=options
        )
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

    def SaveData(self, data, keyword_name):
        with open(
            "Storage/{}.json".format(keyword_name),
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(
            "New File Add : [bold green]{}.json[/bold green]".format(
                keyword_name
            )
        )

    def UpdateData(self, data, keyword):
        load_data = open("Storage/{}.json".format(keyword))
        old_data = json.load(load_data)
        tmp_new_data = []
        for i in range(len(data)):
            if data[i] in old_data:
                pass
            else:
                print(
                    "New Listing : [bold white]{}[/bold white]".format(
                        data[i]
                    )
                )
                tmp_new_data.append(data[i])
        latest_data = old_data + tmp_new_data
        with open(
            "Storage/{}.json".format(keyword), "w", encoding="utf-8"
        ) as f:
            json.dump(latest_data, f, ensure_ascii=False, indent=4)

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
            if path.isfile("Storage/{}.json".format(keyword_name)):
                print("[bold blue]Update File[/bold blue]")
                self.UpdateData(clean_data, keyword_name)
            else:
                print("[bold red]Add New File[/bold red]")
                self.SaveData(clean_data, keyword)
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
                self.clear()
                schedule.run_pending()
                sleep(2)
            except KeyboardInterrupt:
                print("Program Stop")
                sys.exit()


if __name__ == "__main__":
    cs = CenterisScraping()
    cs.main()
