import os
import requests
import time
from zoneinfo import ZoneInfo
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Read tickers from file
def read_tickers_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

ticker_file_path = "mytrade_tickers.txt"
mytrade_tickers = read_tickers_from_file(ticker_file_path)

output_folder = "mytrade_tickers"
os.makedirs(output_folder, exist_ok=True)

# Setup Chrome driver once
def setup():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--force-dark-mode')
    chrome_options.add_argument("--window-size=1280,720")
    chrome_options.add_argument("--headless=new")  # Run in headless mode
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Capture chart using the same driver
def capture_chart(ticker, driver):
    try:
        url = f"https://www.tradingview.com/chart/?symbol=NSE:{ticker}&interval=5"
        driver.get(url)

        WebDriverWait(driver, 7).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".chart-container"))
        )

        try:
            close_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'×')]"))
            )
            close_button.click()
        except Exception:
            pass  # No pop-up or couldn't close

        try:
            full_screen_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@id='header-toolbar-fullscreen']"))
            )
            full_screen_button.click()
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".chart-container"))
            )
        except Exception:
            pass  # Fullscreen optional

        screenshot_path = os.path.join(output_folder, f"{ticker}_chart.png")
        driver.save_screenshot(screenshot_path)
        print(f"Saved chart for {ticker}")
    except Exception as e:
        print(f"Error with {ticker}: {str(e)}")

# Telegram setup once
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_image(image_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    try:
        with open(image_path, 'rb') as image_file:
            files = {'photo': image_file}
            data = {'chat_id': TELEGRAM_CHAT_ID}
            response = requests.post(url, data=data, files=files)
            if response.status_code == 200:
                print(f"Sent {os.path.basename(image_path)}")
            else:
                print(f"Failed to send {image_path}: {response.text}")
    except Exception as e:
        print(f"Error sending {image_path}: {str(e)}")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={'chat_id': TELEGRAM_CHAT_ID, 'text': text})
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return False

# Run driver once
driver = setup()

# Capture charts
for ticker in mytrade_tickers:
    capture_chart(ticker, driver)

driver.quit()

# Send images to Telegram
for ticker in mytrade_tickers:
    image_path = os.path.join(output_folder, f"{ticker}_chart.png")
    if os.path.exists(image_path):
        send_telegram_image(image_path)
        time.sleep(0.5)  # Optional: reduce if not rate-limited
    else:
        print(f"Missing image for {ticker}")

# Final status message
ist_now = datetime.now(ZoneInfo("Asia/Kolkata"))
current_time = ist_now.strftime("%Y-%m-%d %H:%M:%S")
send_telegram_message(f"All charts sent at (IST): {current_time}")

print("All done!")
