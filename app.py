from flask import Flask, request, Response
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
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
        wait = WebDriverWait(driver, 15)
        
        # Step 2: Get first result URL
        first_result = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/story/'], a[href*='/news/']")))
        url = first_result.get_attribute("href")
        
        # Step 3: Navigate to article to get actual text for the summary
        driver.get(url)
        time.sleep(3)
        
        # Pull text from the first few paragraphs for a "real" summary look
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        raw_text = " ".join([p.text for p in paragraphs[:2] if len(p.text) > 20])
        
        # Formatting to match the desired raw style
        formatted_summary = f"(PHOTO: USA TODAY) {raw_text[:300]}..."
        
        return url, formatted_summary
    except Exception as e:
        return None, f"Scraping failed: {str(e)}"
    finally:
        driver.quit()

@app.route('/get', methods=['GET'])
def get_news():
    keyword = request.args.get('keyword')
    if not keyword:
        return Response("keyword parameter missing", status=400)

    url, summary = scrape_usa_today(keyword)
    
    # Exact JSON keys as per Spec 
    response_dict = {
        "registration": "FA23-BAI-055",
        "newssource": "USA Today",
        "keyword": keyword,
        "url": url if url else "Not found",
        "summary": summary if summary else "Could not generate summary"
    }
    
    # Return pretty-printed JSON (multi-line) as seen in Spec [cite: 13]
    return Response(json.dumps(response_dict, indent=4), mimetype='application/json')

if __name__ == '__main__':
    # Exposing /get endpoint on port 7000 [cite: 10, 13]
    app.run(host='0.0.0.0', port=7000)
EOF
