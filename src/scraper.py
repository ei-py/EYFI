"""
This module is responsible for scraping web content.
"""
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from news.models import WebSource


def scrape_news(source: WebSource):
    """
    The main entry point for this module; it will orchestrate the entire
    scraping process for a given WebSource and return a list of dictionaries,
    each containing an article's title, source URL, and raw text content.
    """
    driver = _setup_driver()
    if not driver:
        return []

    scraped_data = []
    try:
        # Step 1: Get all the individual article links from the main list page
        article_links = _get_article_links(driver, source)

        # Step 2: Loop through each link and get the detailed content
        # For this proof-of-concept, let's only process the first 3 links
        # to keep the test runs fast. To process all, change article_links[:3] to article_links
        for link in article_links[:3]:
            details = _get_document_details(driver, link, source)
            if details:
                scraped_data.append(details)
            # Optional: Add a small delay here to be polite to the server
            # import time
            # time.sleep(1)

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
    finally:
        # Step 4: Clean up the driver
        _teardown_driver(driver)

    return scraped_data

def _setup_driver():
    """
    Initializes and returns a configured, headless Selenium Firefox driver.
    """
    print("Setting up headless Firefox driver...")
    options = Options()
    options.add_argument("--headless")
    options.set_preference('browser.download.folderList', 2)
    options.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/html')
    
    try:
        # Try common geckodriver locations
        geckodriver_paths = ['/snap/bin/geckodriver', '/usr/bin/geckodriver', '/usr/local/bin/geckodriver']
        service = None
        
        for path in geckodriver_paths:
            try:
                service = Service(path)
                break
            except:
                continue
        
        if service is None:
            # Fall back to Service() which searches PATH
            service = Service()
        
        driver = webdriver.Firefox(service=service, options=options)
        print("✅ Firefox driver initialized successfully.")
        return driver
    except Exception as e:
        print(f"❌ Error setting up Firefox driver: {e}")
        print("Make sure Firefox and geckodriver are installed:")
        print("  sudo snap install geckodriver")
        return None

def _get_article_links(driver, source: WebSource) -> list:
    """
    Navigates from the source's start page to the article list page
    and extracts the URLs for individual article pages.
    """
    try:
        start_url = source.base_url + source.paths["start"]
        print(f"Navigating to start page: {start_url}")
        driver.get(start_url)
        wait = WebDriverWait(driver, 10)

        # Step 1: Handle the cookie consent button.
        try:
            cookie_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, source.selectors["cookie_accept_button"])))
            print("Found cookie consent button, clicking...")
            cookie_button.click()
        except Exception:
            print(f"⚠️  Cookie consent button ('{source.selectors['cookie_accept_button']}') not found or not clickable, continuing...")
            pass

        # Step 2: Find and click the link to the proposals page.
        try:
            proposals_page_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, source.selectors["proposals_page_link"])))
            print("Found proposals page link, clicking...")
            proposals_page_link.click()
        except Exception as e:
            print(f"❌ Failed to find proposals page link with selector '{source.selectors['proposals_page_link']}': {e}")
            return []

        # Step 3: Now on the proposals list page, wait for the article links to be present.
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, source.selectors["article_link"])))
        except Exception as e:
            print(f"❌ Failed to find article links with selector '{source.selectors['article_link']}': {e}")
            return []
        
        # Step 4: Find all link elements.
        link_elements = driver.find_elements(By.CSS_SELECTOR, source.selectors["article_link"])
        
        # Step 5: Extract the href attribute from each element.
        urls = [element.get_attribute('href') for element in link_elements]
        print(f"✅ Found {len(urls)} article links.")
        return urls
        
    except Exception as e:
        print(f"❌ Error getting article links: {e}")
        return []

def _get_document_details(driver, article_url: str, source: WebSource) -> dict | None:
    """
    Takes a single proposal page URL, navigates to it, finds the link to
    the full document, and extracts both the document's text and its title.
    """
    try:
        print(f"Navigating to article details page: {article_url}")
        driver.get(article_url)
        wait = WebDriverWait(driver, 10)

        # Step 1: Extract progress bar, state, and stage data from the details page
        progress_stages = []
        current_stage = ""
        state = ""
        stage = ""
        try:
            progress_elements = driver.find_elements(By.CSS_SELECTOR, source.selectors["progress_bar"])
            if progress_elements:
                progress_stages = [el.text for el in progress_elements]
                for el in progress_elements:
                    if "latest-stage" in el.get_attribute("class"):
                        current_stage = el.text
                        break
        except Exception as e:
            print(f"⚠️  Could not find or parse progress bar for {article_url}: {e}")
            # If it fails, we just leave the lists empty, which is a safe default
            pass

        try:
            # Use By.XPATH for the state selector
            state_element = driver.find_element(By.XPATH, source.selectors["state"])
            state = state_element.text
        except Exception as e:
            print(f"⚠️  Could not find 'state' with selector '{source.selectors['state']}' for {article_url}: {e}")
        
        try:
            # The stage selector is still CSS_SELECTOR
            stage_element = driver.find_element(By.CSS_SELECTOR, source.selectors["stage"])
            stage = stage_element.text
        except Exception as e:
            print(f"⚠️  Could not find 'stage' with selector '{source.selectors['stage']}' for {article_url}: {e}")

        # Step 2: Find the link to the full document page.
        try:
            document_link_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, source.selectors["document_link"])))
            document_url = document_link_element.get_attribute('href')
        except Exception as e:
            print(f"❌ Failed to find document link with selector '{source.selectors['document_link']}': {e}")
            return None
        
        # Step 3: Navigate to the full document page.
        print(f"Navigating to full document page: {document_url}")
        driver.get(document_url)

        # Step 4: Extract the title and content.
        try:
            title_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, source.selectors["document_number_title"])))
            title = title_element.text.strip()
        except Exception as e:
            print(f"❌ Failed to find document number title with selector '{source.selectors['document_number_title']}': {e}")
            return None

        try:
            subject_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, source.selectors["document_subject_text"])))
            subject = subject_element.text.strip()
        except Exception as e:
            print(f"❌ Failed to find document subject text with selector '{source.selectors['document_subject_text']}': {e}")
            subject = '' # Set subject to empty if not found, summarizer will handle
            
        try:
            content_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, source.selectors["document_content"])))
            content = content_element.text
        except Exception as e:
            print(f"❌ Failed to find document content with selector '{source.selectors['document_content']}': {e}")
            return None
        
        print(f"Successfully extracted title: {title}, subject: {subject}...")
        return {
            "title": title, 
            "subject": subject, 
            "raw_content": content, 
            "source_url": document_url,
            "progress_stages": progress_stages,
            "current_stage": current_stage,
            "state": state,
            "stage": stage
        }

    except Exception as e:
        print(f"Error getting document details for {article_url}: {e}")
        return None

def _teardown_driver(driver):
    """
    Properly quits the Selenium driver and closes the browser to free up
    system resources.
    """
    if driver:
        print("Tearing down driver...")
        driver.quit()
        print("Driver closed.")
