import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
class IntelecScrapper:
    def __init__(self, url):
        self.driver = webdriver.Chrome()
        self.url = url

    def extract_item_links(self, limit_page_count):
        self.driver.get(self.url)
        all_links = []

        previous_items_count = 0
        current_items_count = 0
        page_count = 0

        while page_count < limit_page_count:
            time.sleep(2)

            # Scroll to the bottom of the page
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for new content to load
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "product-thumb"))
                )
            except:
                break

            # Count the number of items loaded on the page
            current_items_count = len(
                self.driver.find_elements(By.CSS_SELECTOR, "a.product-img")
            )

            # If the number of items has not changed, no more pages to load
            if current_items_count == previous_items_count:
                break

            previous_items_count = current_items_count
            page_count += 1

        # Find elements with the specified CSS selector
        elements = self.driver.find_elements(By.CSS_SELECTOR, "a.product-img")
        links = [element.get_attribute("href") for element in elements]

        # Print the links
        for link in links:
            all_links.append(link)

        print(all_links)

        return all_links

    def get_item_details(self, url):
        response = requests.get(url)
        html_content = response.content

        soup = BeautifulSoup(html_content, "html.parser")

        item_title = soup.select_one("h1.title.page-title span")
        item_price = soup.find(class_=["product-price", "placeholder-price-new"])

        if item_title:
            try:
                item_text = item_title.get_text(strip=True)
                item_price = item_price.get_text(strip=True)
                print("Element Text:", item_text)
                print("Element Price:", item_price)
                print("Element url:", url)
                return [item_text, item_price, url]
            except AttributeError:
                print("Title: ", item_title)
                print("Element Price:", item_price)
                print("Element url:", url)
                return [None, None, url]
        else:
            print("No data found")

    def scrape(self, filemame="data", limit_page_count=3):
        all_links = self.extract_item_links(limit_page_count=limit_page_count)
        data = []
        for link in all_links:
            data.append(self.get_item_details(link))

        df = pd.DataFrame(data, columns=["Title", "Price", "Link"])
        df.to_csv(f"{filemame}.csv", index=False)

        print("Done")
        return df




    def close_driver(self):
        self.driver.close()




scraper = IntelecScrapper("https://www.intelec.co.cr/MONITORES")
scraper.scrape(filemame="Monitors_intelec",limit_page_count=5)
scraper.close_driver()

