import requests, subprocess, sys, time
from datetime import datetime
from pytz import timezone
import yfinance as yf
from selenium import webdriver
from selenium.webdriver.common.by import By
from calculateHistoricalIndicatorData import calculate_historical_indicators, avg_change_formula, ema_formula, rsi_formula

#This function checks to see if yfinance is up-to-date
def check_up_to_date(name):
    latest_version = str(subprocess.run([sys.executable, '-m', 'pip', 'install', '{}==random'.format(name)], capture_output=True, text=True))
    latest_version = latest_version[latest_version.find('(from versions:')+15:]
    latest_version = latest_version[:latest_version.find(')')]
    latest_version = latest_version.replace(' ','').split(',')[-1]

    current_version = str(subprocess.run([sys.executable, '-m', 'pip', 'show', '{}'.format(name)], capture_output=True, text=True))
    current_version = current_version[current_version.find('Version:')+8:]
    current_version = current_version[:current_version.find('\\n')].replace(' ','') 

    return latest_version == current_version

#Quit program if yfinance is not up-to-date
if not check_up_to_date("yfinance") :
    print("yfinance is not up-to-date. Run \"pip install yfinance --upgrade\" to update yfinance.")
    quit()


#Selection Strategies

def selection1() :
    pass

#Entrance Strategies

def entrance1() :
    pass

#Exit Strategies

def exit1() :
    pass

#Globals

indicator_inputs_required = {
    "RSI":[5, 9, 14],
    "EMA":[10, 20, 50, 100, 200],
    "MACD":[(12, 26, 9), (5, 35, 5), (19, 39, 9)]
}

indicator_data_points_needed = {
    "RSI":2,
    "EMA":1,
    "MACD":3,
}

indicator_outputs = {indicator_name:{} for indicator_name in indicator_inputs_required}

indicator_historical = {}

ticker = ""

price = 0

strategies = [
    (selection1, entrance1, exit1)
]

strategies_performance_tracking = [{"Holding":{}, "MaxHolding":0, "Exited":[]}]*len(strategies)

#Indicator Functionality


def update_indicator_outputs() :
    difference = price-indicator_historical[ticker][0]
    loading_index = 1
    for period in indicator_inputs_required["RSI"] :
        if difference >= 0 :
            avg_gain = avg_change_formula(indicator_historical[ticker][loading_index], period, difference)
            avg_loss = avg_change_formula(indicator_historical[ticker][loading_index+1], period, 0)
        else :
            avg_gain = avg_change_formula(indicator_historical[ticker][loading_index], period, 0)
            avg_loss = avg_change_formula(indicator_historical[ticker][loading_index+1], period, -difference)
            
        indicator_outputs["RSI"][period] = round(rsi_formula(avg_gain, avg_loss), 4)

        loading_index += indicator_data_points_needed["RSI"]
            
    for period in indicator_inputs_required["EMA"] :
        indicator_outputs["EMA"][period] = round(ema_formula(price, period, indicator_historical[ticker][loading_index]), 4)
        
        loading_index += indicator_data_points_needed["EMA"]

    for combination in indicator_inputs_required["MACD"] :
        fast_ema = ema_formula(price, combination[0], indicator_historical[ticker][loading_index])
        
        slow_ema = ema_formula(price, combination[1], indicator_historical[ticker][loading_index+1])

        macd_ema = ema_formula(fast_ema-slow_ema, combination[2], indicator_historical[ticker][loading_index+2])

        indicator_outputs["MACD"][combination] = (round(fast_ema-slow_ema, 4), round(macd_ema, 4))

        loading_index += indicator_data_points_needed["MACD"]
                                                                                 
#This function gets the current minutes elapsed in Eastern Time
def get_minutes_elapsed() :
    #First, get the time in Eastern Time
    tz = timezone('EST')

    #Breaking the string version of this time data structure and extract the hours and minutes
    split_by_colon = str(datetime.now(tz)).split(" ")[1].split(":")
    hour, minutes = int(split_by_colon[0]), int(split_by_colon[1])

    #Calculate the and return total minutes elapsed
    return (hour*60)+minutes

driver = webdriver.Edge()

def open_webbdriver(user_email, user_password) :
    url = "https://finance.yahoo.com/portfolios/"
    driver.get(url)
    driver.fullscreen_window()

    try :
        sign_in = driver.find_element(By.XPATH, "//li[@id='header-profile-menu']/a[1]")
        sign_in.click()
    except :
        sign_in = driver.find_element(By.XPATH, "//div[@id='login-container']/a[1]")
        sign_in.click()

    time.sleep(3)
    driver.fullscreen_window()

    username = driver.find_element(By.ID, "login-username")
    username.send_keys(user_email)

    next_button = driver.find_element(By.NAME, "signin")
    next_button.click()

    time.sleep(3)
    driver.fullscreen_window()

    password = driver.find_element(By.ID, "login-passwd")
    password.send_keys(user_password)

    next_button2 = driver.find_element(By.NAME, "verifyPassword")
    next_button2.click()

    time.sleep(3)

    driver.get("https://finance.yahoo.com/portfolio/p_0/view/v1")
    driver.fullscreen_window()

def scrape_live_data() :
    return list(zip([element.text for element in driver.find_elements(By.XPATH, "//td/a[@data-test='quoteLink']")], [float(element.text) for element in driver.find_elements(By.XPATH, "//td/fin-streamer[@data-field='regularMarketPrice']")]))

def main() :
    user_email = "reginaldjhyde@gmail.com"
    user_password = "PythonIsAwesome!"
    open_webbdriver(user_email, user_password)
    scraped_data = scrape_live_data()
    for scraped_stock in scraped_data :
        indicator_historical[scraped_stock[0]] = calculate_historical_indicators(scraped_stock[0], indicator_data_points_needed, indicator_inputs_required)

    while True :
        minutes_elapsed = get_minutes_elapsed()
        if not (minutes_elapsed >= 570 and minutes_elapsed <= 960) :
            print("Stock exchanges are closed")
            break

        scraped_data = scrape_live_data()
        for scraped_stock in scraped_data :
            ticker, price = scraped_stock
            update_indicator_outputs()
            
            for strategy in strategies :
                if 
main()


