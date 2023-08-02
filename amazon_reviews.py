import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import logging


class AmazonReviews:
    def __init__(self, url):

        self.logger = logging.getLogger("AmazonReviews")
        self.logger.setLevel(logging.DEBUG)

        # Create a file handler to save the logs to a file
        file_handler = logging.FileHandler("scraping_log.txt")
        file_handler.setLevel(logging.DEBUG)

        # Create a formatter for the log messages
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        # Add the file handler to the logger
        self.logger.addHandler(file_handler)

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.url = url

    def get_reviews_from_page(self):
        try:
            self.driver.get(self.url)
            time.sleep(3)  # Add a delay to wait for the page to load

            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")

            reviews = []
            review_elements = soup.find_all("div", {"class": "a-section celwidget"})
            for review_element in review_elements:
                review_info = {}

                # Extract review title and rating
                title_element = review_element.find("a", {"data-hook": "review-title"})
                rating_element = review_element.find("i", {"data-hook": "review-star-rating"})
                if not title_element or not rating_element:
                    continue
                review_info["Title"] = title_element.text.strip()
                review_info["Rating"] = rating_element.find("span", {"class": "a-icon-alt"}).text.strip()

                # Extract review date
                date_element = review_element.find("span", {"data-hook": "review-date"})
                review_info["Date"] = date_element.text.strip()

                # Extract review body
                body_element = review_element.find("span", {"data-hook": "review-body"})
                review_info["Review"] = body_element.text.strip()

                reviews.append(review_info)

        except TimeoutException:
            self.logger.error("TimeoutException: The page took too long to load.")
            print("TimeoutException: The page took too long to load.")
            return []
        except StaleElementReferenceException:
            self.logger.error("StaleElementReferenceException: The page elements are not valid anymore.")
            print("StaleElementReferenceException: The page elements are not valid anymore.")
            return []
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            print(f"An unexpected error occurred: {e}")
            return []

        return reviews

    def go_to_next_page(self):
        """This function is to mainly check whether there is a next page or not
        This because Amazon leads to the login page if detects a bot, so the base_url is the one that
        modifies the page number and not the driver
        """
        try:
            next_page_link = self.driver.find_element(By.XPATH, "(//a[contains(text(),'Next page')])[1]")
            self.url = next_page_link.get_attribute("href")  # Update the URL for the next page
            next_page_link.click()
            time.sleep(1)  # Wait for the next page to load
            return True
        except Exception:
            self.logger.error("No more pages available")
            return False

    def convert_to_csv(self, reviews, filename="amazon_reviews"):
        # Create an empty DataFrame to hold the reviews
        df = pd.DataFrame(columns=["Title", "Rating", "Date", "Review", "neg", "neu", "pos", "compound"])

        # Analyze the sentiment for each review and add the scores to the DataFrame
        for review in reviews:
            sentiment_score = self.analyze_sentiment(review['Review'])
            review["neg"] = sentiment_score["neg"]
            review["neu"] = sentiment_score["neu"]
            review["pos"] = sentiment_score["pos"]
            review["compound"] = sentiment_score["compound"]

            # Append the review to the DataFrame
            df = pd.concat([df, pd.DataFrame([review])], ignore_index=True)

        # Save the DataFrame to a CSV file
        df.to_csv(f"{filename}.csv", index=False)
        return df


    def analyze_sentiment(self, text):
        sid = SentimentIntensityAnalyzer()
        sentiment_score = sid.polarity_scores(text)
        return sentiment_score

    def scrape_all_reviews(self, start_page, max_page):
        all_reviews = []
        while start_page <= 2:
            reviews = scrapper.get_reviews_from_page()
            all_reviews.extend(reviews)

            if not scrapper.go_to_next_page():
                break

            start_page += 1
            scrapper.url = base_url + str(start_page)
        return all_reviews

    def close_driver(self):
        self.driver.quit()


count = 0
if __name__ == "__main__":
    ASIN = 'B0B1VQ1ZQY'
    base_url = f"https://www.amazon.com/product-reviews/{ASIN}/ref=cm_cr_arp_d_paging_btm_next_1?pageNumber="
    page_number = 1
    scrapper = AmazonReviews(base_url + str(page_number))
    all_reviews = []

    while page_number <= 3:
        reviews = scrapper.get_reviews_from_page()
        all_reviews.extend(reviews)

        if not scrapper.go_to_next_page():
            break

        page_number += 1
        scrapper.url = base_url + str(page_number)

    scrapper.close_driver()
    scrapper.convert_to_csv(all_reviews, filename=f"amazon_reviews_{ASIN}")

    # Print the extracted reviews
    for i, review in enumerate(all_reviews, 1):
        print(f"Review {i}:")
        print(f"Title: {review['Title']}")
        print(f"Rating: {review['Rating']}")
        print(f"Date: {review['Date']}")
        print(f"Review: {review['Review']}")
        print("\n")
        # Analyze the sentiment of the review text
        sentiment_score = scrapper.analyze_sentiment(review['Review'])
        print("Sentiment Score:", sentiment_score)

        print("\n")

