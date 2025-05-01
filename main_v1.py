#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import os
import requests
import time

#os.system('apt-get update && apt-get install -y libnss3 libgconf-2-4')

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By




# Function to read stock tickers from a file
def read_tickers_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]


# Read tickers from the file
ticker_file_path = "mytrade_tickers.txt"  # Update path if necessary
mytrade_tickers = read_tickers_from_file(ticker_file_path)

# Set up folder for saving images
output_folder = "mytrade_tickers"
os.makedirs(output_folder, exist_ok=True)

def setup():
    #print('--->Setup selenium start : ' + str(datetime.now()))
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--force-dark-mode')
    chrome_options.add_argument("--window-size=1280,720")

    driver = webdriver.Chrome(options=chrome_options)
    print('Setup selenium complete')
    return driver

# Function to capture screenshot of a TradingView chart
def capture_chart(ticker):
    try:
        # Load the TradingView chart URL for the stock
        url = f"https://www.tradingview.com/chart/?symbol=NSE:{ticker}&interval=5" 
        driver = setup()
        driver.get(url)
               
        # Wait for the chart to load
        WebDriverWait(driver, 7).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".chart-container")))

        # Optionally interact with elements (close pop-ups, etc.)
        try:
            close_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(),'×')]")))
            close_button.click()
        except Exception as e:
            print(f"No pop-up for {ticker}: {e}")

        # Wait for the full-screen button and click it
        try:
            full_screen_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@id='header-toolbar-fullscreen']")))
            full_screen_button.click()
            time.sleep(2)  # Wait for full screen transition
        except Exception as e:
            print(f"Full screen button not found for {ticker}: {e}")

        # Save screenshot of the chart
        screenshot_path = os.path.join(output_folder, f"{ticker}_chart.png")
        driver.save_screenshot(screenshot_path)
        print(f"Saved chart for {ticker} at {screenshot_path}")

    except Exception as e:
        print(f"Failed to capture chart for {ticker}: {e}")


# Iterate through the mytrading stocks and capture screenshots
for ticker in mytrade_tickers:
    capture_chart(ticker)

# Close the driver after the process is complete
#driver.quit()



# Telegram Configuration
#TELEGRAM_BOT_TOKEN = 'telegram_bot_token'  # Replace with your bot token
#TELEGRAM_CHAT_ID = 'telegram_chat_id'  # Replace with your chat ID (not phone number)

#print(os.path.exists('ABB_chart.png'))
def send_telegram_image(image_path):
    print(image_path)
    print(os.getenv("TELEGRAM_BOT_TOKEN"))
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    print(os.getenv("TELEGRAM_CHAT_ID"))
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendPhoto"
    try:
        with open(image_path, 'rb') as image_file:
            files = {'photo': image_file}
            data = {'chat_id': telegram_chat_id}
            response = requests.post(url, data=data, files=files)
            if response.status_code == 200:
                print(f"Sent {os.path.basename(image_path)} successfully")
            else:
                print(
                    f"Failed to send {os.path.basename(image_path)}. Error: {response.text}"
                )
    except Exception as e:
        print(f"Error sending {os.path.basename(image_path)}: {str(e)}")


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    try:
        response = requests.post(url,
                                 json={
                                     'chat_id': telegram_chat_id,
                                     'text': text
                                 })
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return False


# Send all captured charts
for ticker in mytrade_tickers:
    image_path = os.path.join(output_folder, f"{ticker}_chart.png")
    if os.path.exists(image_path):
        send_telegram_image(image_path)
        time.sleep(1)  # Prevent rate limiting
    else:
        print(f"Image not found for {ticker}")

# Get current time and send
current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
send_telegram_message(f"All charts sent at: {current_time}")

print("All images sent via Telegram!")

