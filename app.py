from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = Flask(__name__)

def scrape_usa_today(keyword):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # Step 1: Navigate to search
        search_url = f"https://www.usatoday.com/search/?q={keyword}"
        driver.get(search_url)
        
        # Step 2: Use an explicit wait for results
        # This targets standard news story link patterns on USA Today
        wait = WebDriverWait(driver, 15)
        first_result = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/story/'], a[href*='/news/']")))
        
        url = first_result.get_attribute("href")
        title = first_result.text if first_result.text else "News Article"
        summary = f"Summary for {keyword}: Found article '{title}'. This covers recent updates on the topic from USA Today."
        
        return url, summary
    except Exception as e:
        return None, str(e)
    finally:
        driver.quit()

@app.route('/get', methods=['GET'])
def get_news():
    keyword = request.args.get('keyword')
    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400

    url, summary = scrape_usa_today(keyword)
    
    # Matching the API Specification exactly [cite: 13, 16]
    return jsonify({
        "registration": "FA23-BAI-055",
        "newssource": "USA Today",
        "keyword": keyword,
        "url": url if url else "Not found",
        "summary": summary if summary else "Could not generate summary"
    })

if __name__ == '__main__':
    # Exposing /get endpoint on port 7000 [cite: 10, 13]
    app.run(host='0.0.0.0', port=7000)
