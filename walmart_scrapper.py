import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WalmartScraper:
    def __init__(self):
        self.driver = webdriver.Chrome()

    def extract_item_links(self, url, limit_page_count=3):
        self.driver.get(url)
        all_links = []
        page_count = 0
        while page_count < limit_page_count:
            time.sleep(2)
            # Scroll to the bottom of the page
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for new content to load
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "vtex-product-summary-2-x-productBrand")))
            except:
                break

            page_count += 1

        # Find elements with the specified class name
        elements = self.driver.find_elements(By.CSS_SELECTOR, "section.vtex-product-summary-2-x-container a")
        links = [element.get_attribute("href") for element in elements]

        # Print the text content of each element
        for link in links:
            all_links.append(link)

        print(all_links)

        return all_links

    def get_item_details(self, url):
        response = requests.get(url)
        html_content = response.content

        soup = BeautifulSoup(html_content, "html.parser")

        item_title = soup.select_one(".vtex-store-components-3-x-productBrand.vtex-store-components-3-x-productBrand--quickview")
        price = soup.find(class_="vtex-store-components-3-x-currencyContainer vtex-store-components-3-x-currencyContainer--summary")
        item_sku = soup.find(class_="vtex-product-identifier-0-x-product-identifier__value")

        if item_title:
            try:
                item_text = item_title.get_text(strip=True)
                item_price = price.get_text(strip=True)
                item_sku_value = item_sku.get_text(strip=True)
                print("Element Text:", item_text)
                print("Element Price:", item_price)
                print("Element SKU:", item_sku_value)
                print("Element Link:", url)
                print("\n")
                return [item_text, item_price, item_sku_value, url]
            except AttributeError:
                print("Element Price: NA")
                item_sku_value = item_sku.get_text(strip=True)
                print("Element SKU:", item_sku_value)
                print("Element Link:", url)
                print("\n")
                return [item_text, "NA", item_sku_value, url]
        else:
            print("Element not found")

    def scrape(self, url, file_name="walmart_data_scrape", limit_page_count=3):
        cellphones_links = self.extract_item_links(url, limit_page_count=limit_page_count)
        data = []
        for cellphone_link in cellphones_links:
            item_data = self.get_item_details(cellphone_link)
            if item_data:
                data.append(item_data)

        columns = ["Element Text", "Element Price", "Element SKU", "Element Link"]
        df = pd.DataFrame(data, columns=columns)
        df.to_excel(f"{file_name}.xlsx", index=False)
        print("Data saved to 'scraped_data.xlsx'")

    def close(self):
        self.driver.quit()

scraper = WalmartScraper()
walmart_url = "https://www.walmart.co.cr/cervezas-vinos-y-licores/cervezas"
scraper.scrape(walmart_url, file_name="new_data_walmart", limit_page_count=6)
scraper.close()
