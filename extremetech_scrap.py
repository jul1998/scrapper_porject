import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
from selenium import webdriver
from selenium.webdriver.common.by import By

import time
import requests
from bs4 import BeautifulSoup

class ExtremeTechScrapper:
    def __init__(self, url):
        self.url = url

    def extract_detail_links(self):
        url = self.url
        response = requests.get(url)
        html_content = response.content


        soup = BeautifulSoup(html_content, "html.parser")
        link_elements = soup.select("a.product_img_link")
        page_links = [element["href"] for element in link_elements]
        return page_links

    def get_item_details(self, url):
        response = requests.get(url)
        html_content = response.content

        soup = BeautifulSoup(html_content, "html.parser")

        item_title = soup.select_one("h1[itemprop='name']")
        price_element = soup.select_one("span#our_price_display")

        strong_elements = soup.select("div#short_description_content strong")

        bullet_points = {}
        for index, strong in enumerate(strong_elements):
            bullet_points[strong.text] = strong.text

        if item_title:
            try:
                h1_text = item_title.text.strip()
                price = price_element.text.strip()
                print("Title:", h1_text)
                print("Price:", price)
                print("Link:", url)
                print("Screen:", bullet_points)
                print("\n")
                return [h1_text, price, url, bullet_points]
            except AttributeError:
                print("Title: NA")
                print("Price: NA")

                print("Link:", url)
                print("\n")
                return [None, None, url]
        else:
            print("H1 element not found")
            return None

    def scrape(self, filename="extremetech_data_scrape.csv"):
        all_links = self.extract_detail_links()
        all_items = []
        for link in all_links:
            item = self.get_item_details(link)
            all_items.append(item)

        df = pd.DataFrame(all_items, columns=["Title", "Price", "Link", "Bullet Points"])
        df.to_csv(f"{filename}.csv", index=False)


        print("Done")

        return df


# Example usage
scrapper = ExtremeTechScrapper("https://extremetechcr.com/tienda/27-monitores?id_category=27&n=10")
links = scrapper.extract_detail_links()
scrapper.scrape(filename="monitors_data")


