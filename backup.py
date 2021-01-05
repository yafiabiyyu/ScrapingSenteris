from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from os import system, getenv, path, name
from dotenv import load_dotenv
from time import sleep
import json
import schedule
from rich import print

# load .env file
load_dotenv()


class CenterisScraping:
    def __init__(self):
        self.optionsBrowser = webdriver.ChromeOptions()
        self.optionsBrowser.add_argument("headless")
        self.browser = webdriver.Chrome("Extension/chromedriver",options=self.optionsBrowser)
        # self.browser = webdriver.Firefox(executable_path="Extension/geckodriver")
        self.browser.maximize_window()

    def clear(self): 
        if name == 'nt': 
            _ = system('cls') 
        else: 
            _ = system('clear') 

    def SaveData(self, data, keyword):
        with open(
            "Storage/{}.json".format(keyword), "w", encoding="utf-8"
        ) as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(
            "New File Add : [bold green]{}.json[/bold green]".format(
                keyword
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

    def ConfigSearch(self):
        keyword_data = open("Config/config.json")
        data = json.load(keyword_data)
        keyword_list = []

        for i in range(len(data["querySearch"])):
            keyword_list.append(data["querySearch"][i])
        print(
            "Total Keyword : [bold white]{}[/bold white]".format(
                len(keyword_list)
            )
        )
        return keyword_list

    def ConsultHandle(self):
        """
        This function for handle
        https://www.centris.ca/en/consult-search?name=
        """

        # Get keyword list from ConfigSearch()
        keyword_list = self.ConfigSearch()

        # open https://www.centris.ca/en/consult-search?name=
        for i in range(len(keyword_list)):
            keyword = keyword_list[i]
            # store raw data extract from web page
            raw_data = []

            self.browser.implicitly_wait(5)
            sleep(2)
            self.browser.get(
                "https://www.centris.ca/en/consult-search?name={}".format(
                    keyword
                )
            )
            print(
                "[bold green]Open Keyword : [/bold green] [bold white]{}[/bold white]".format(
                    keyword
                )
            )
            self.browser.implicitly_wait(3)
            sleep(2)
            total_page = str(
                self.browser.find_element_by_xpath(
                    "/html/body/main/div[7]/div/div/div[1]/div/div/ul/li[3]"
                ).text
            )[3:]
            print(
                "Total Page [bold white]{}[/bold white]".format(
                    total_page
                )
            )
            for page in range(int(total_page)):
                sleep(2)
                web_page = BeautifulSoup(
                    self.browser.page_source, "html.parser"
                )
                href_tag = web_page.find_all(
                    "a", class_="a-more-detail"
                )
                for i in range(0, len(href_tag)):
                    raw_data.append(href_tag[i]["href"])
                self.browser.find_element_by_xpath(
                    "/html/body/main/div[7]/div/div/div[1]/div/div/ul/li[4]/a"
                ).click()
            clean_data = list(set(raw_data))
            if path.isfile("Storage/{}.json".format(keyword)):
                print("[bold blue]Update File[/bold blue]")
                self.UpdateData(clean_data, keyword)
            else:
                print("[bold red]Add New File[/bold red]")
                self.SaveData(clean_data, keyword)
        self.browser.implicitly_wait(5)
        sleep(5)
        self.browser.close()

    def Start(self):
        email_data = getenv("email")
        password_data = getenv("password")

        # open browser for login
        self.browser.get("https://www.centris.ca/en/login?uc=2")
        self.browser.implicitly_wait(5)
        email_form = self.browser.find_element_by_id(
            "loginradius-login-emailid"
        )
        email_form.send_keys(email_data)

        password_form = self.browser.find_element_by_id(
            "loginradius-login-password"
        )
        password_form.send_keys(password_data)

        self.browser.find_element_by_id(
            "loginradius-submit-login"
        ).click()
        self.browser.implicitly_wait(5)
        sleep(2)
        self.ConsultHandle()
        # self.browser.close()

    def main(self):
        self.clear()
        self.Start()


if __name__ == "__main__":
    cs = CenterisScraping()
    # cs.main()
    schedule.every(1).minutes.do(cs.main)
    while True:
        schedule.run_pending()
        sleep(1)
