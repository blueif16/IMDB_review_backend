import time
import json
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import html
from bs4 import BeautifulSoup
import requests

def get_movie_id(tmdb_id):
    """
    Get the IMDb ID for a given TMDb ID.
    """
    api_key = "527f624a0e254fc9a30719aab2aaa08d"
    return requests.get(f"https://api.themoviedb.org/3/movie/{tmdb_id}/external_ids?api_key={api_key}").json()["imdb_id"]


def preprocess_page_source(page_source):
    """
    Preprocess the page source to decode unicode escapes, unescape HTML entities, and convert \u0026 to ASCII (&).
    Args:
        page_source (str): Raw page source.
    Returns:
        BeautifulSoup object: Parsed HTML content after preprocessing.
    """
    # Step 1: Clean invalid unicode escape sequences like \N before decoding
    # Replace \N with an empty string (or some placeholder text)
    page_source = re.sub(r'\\[uU][0-9A-Fa-f]{4}', '', page_source)  # Remove invalid unicode escapes

    # Step 2: Decode unicode escape sequences (e.g., \u0026 becomes &)
    page_source = bytes(page_source, "utf-8").decode("unicode_escape", errors="ignore")

    # Step 3: Replace specific Unicode escape sequences (e.g., \u0026 becomes &)
    page_source = page_source.replace('\u0026', '&')  # Convert \u0026 (ampersand) to ASCII '&'

    # Step 4: Unescape HTML entities (e.g., &#39; becomes ')
    page_source = html.unescape(page_source)

    # Step 5: Create BeautifulSoup object to parse the HTML content
    soup = BeautifulSoup(page_source, 'html.parser')

    return soup

def get_movie_reviews(movie_identifier, target_reviews = 200, show_browser = False):
    """
    Get the HTML content of IMDb reviews page for a given movie until the target number of reviews is fetched.
    """
    PATH = r"/home/ran/chromedriver"
    failed_path = "data/failed_reviews.txt"
    
    try:
        IMDB_ID = get_movie_id(movie_identifier)
    except Exception as e:
        print(f"Failed to get IMDB ID for {movie_identifier}: {str(e)}")
        return False
        
    review_url = f"https://www.imdb.com/title/{IMDB_ID}/reviews"

    # Initialize webdriver
    try:
        service = Service(PATH)
        options = webdriver.ChromeOptions()

        # Set the browser to headless (invisible) if show_browser is False
        if not show_browser:
            # options.add_argument('--headless')  # Runs the browser in headless mode
            options.add_argument('--disable-gpu')  # Optional: disable GPU hardware acceleration
            # options.add_argument('--no-sandbox')  # Avoids issues with sandboxing in headless mode

        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"Failed to initialize webdriver: {str(e)}")
        return False
    
    try:
        print(f"Getting page content from: {review_url}")
        driver.get(review_url)
        driver.implicitly_wait(2)

        see_more_buttons = driver.find_elements(By.CLASS_NAME, 'ipc-see-more__text')
        
        if len(see_more_buttons) > 1:
            see_more_button = see_more_buttons[1]
            actions = ActionChains(driver)
            actions.move_to_element(see_more_button).click().perform()
        else:
            print("Second 'See More' button not found, skipping to next movie.")
            driver.quit()
            return False

        total_time = 40
        all_reviews = set()
        start_time = time.time()

        while (time.time() - start_time) < total_time:
            pass

        page_content = driver.page_source
        soup = preprocess_page_source(page_content)
        print("Fetching final HTML after 30 seconds...")
        
        pattern = r'\"plaidHtml\":\"(.*?)\",\"__typename\":\"Markdown\"'
        all_reviews = set(re.findall(pattern, page_content))

        content_divs = soup.find_all('div', class_='ipc-html-content-inner-div')
        extracted_texts = [div.get_text() for div in content_divs]
        all_reviews.update(extracted_texts)

        fetched_count = len(all_reviews)

        if fetched_count < target_reviews:
            print("Fetched Failed" , "Total Fetched:", fetched_count)
            with open(failed_path, 'a', encoding='utf-8') as f:
                f.write(f"{[fetched_count, movie_identifier, IMDB_ID]}\n")
        else:
            print("Fetched successfully", "Total Fetched:", fetched_count)

        os.makedirs('data/reviews', exist_ok=True)
        reviews_file = f'data/reviews/{movie_identifier}_reviews.txt'

        reviews_data = list(all_reviews)

        with open(reviews_file, 'w', encoding='utf-8') as f:
            for review in reviews_data:
                f.write(review + '\n\n')

        print(f"Reviews for {movie_identifier} saved to: {reviews_file}")
        return True

    except Exception as e:
        print(f"Error processing movie {movie_identifier}: {str(e)}")
        return False

    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == '__main__':
    # movie_id = "tt0111161"  # Example movie ID for Shawshank Redemption
    movie_id = get_movie_id("238")
    # print(movie_id)
    get_movie_reviews(movie_id)
