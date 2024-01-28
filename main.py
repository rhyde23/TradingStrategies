#NOTE: This project is heavily reliant on Yahoo Finance and @ranaroussi's yfinance package, which uses Yahoo Finance's API

#Imported Libraries/Scripts 

import requests, time
#requests library - For processing url requests for live scraping data from Yahoo Finance watchlist
#time library - For use of the time.sleep() function to assure that web pages are fully loaded before being scraped

from datetime import datetime
#datetime library - For accessing the current time and checking if the US Stock Markets are open

from pytz import timezone
#pytz library - For converting the current time in terms of Eastern Time

from selenium import webdriver
from selenium.webdriver.common.by import By
#selenium library - For web scraping websites with dynamic content.
#Yahoo Finance's live stock watchlists are reliant on JavaScript, so a selenium webdriver is necessary to scrape them.
#A webdriver basically creates a copy of a web browser and automates/mimics user input and scrapes the website
#By contrast, Python's beautifulsoup4 can only load page sources (html).

from calculateHistoricalData import calculate_historical_data, avg_change_formula, ema_formula, rsi_formula
#calculateHistoricalData script - Written by me for the purpose of calculating all the data needed for the quick update of technical indicators and stock statistics.
#By accessing historical data using the yfinance package, I can set up everything I need for technical indicator calculations so that the live price is the only missing piece.
#This script also collects data such as Market Cap, Average Volume, etc. (statistics that don't need to be scraped live)
#It is hugely important that this data collection happens separately from live scraping for effiency because this initial data collection ONLY NEEDS TO HAPPEN ONCE.

from checkUpToDate import check_up_to_date
#checkUpToDate script - contains the function "check_up_to_date" to check if a libaray is up-to-date

#Quit program if @ranaroussi's yfinance package is not up-to-date
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

#Global Variables

#The "indicators_available" list contains all the names of technical indicators currently supported
indicators_available = ["RSI", "EMA", "MACD"]

#The "stock_statistics_available" list contains all the names of stock statistics currently supported
stock_statistics_available = ["MARKET_CAP", "VOLUME", "RELATIVE_VOLUME"]

#The "indicator_inputs_required" dictionary contains all the specific settings for each indicator that will be used within the entrance/exit strategies
indicator_inputs_required = {
    "RSI":[5, 9, 14],
    "EMA":[10, 20, 50, 100, 200],
    "MACD":[(12, 26, 9), (5, 35, 5), (19, 39, 9)]
}

#The "yahoo_statistics_required" dictionary contains all the statistics from yfinance needed for all the calculations within "stock_statistics_required"
yahoo_statistics_required = ["marketCap", "averageVolume"]

#The "indicators" dictionary is updated for every scraped stock and contains the live calculations of every required setting of every required indicator for the current stock
indicators = {indicator_name:{} for indicator_name in indicator_inputs_required}

#The "stock_statistics" dictionary is updated for every scraped stock and contains the live stock statistics for the current stock
stock_statistics = {}

#The "indicator_historical" dictionary is populated only once using "calculate_historical_data" and contains all the data for every stock needed to make quick calculations for every...
#...required setting of every required indicator.
#This dictionary allows the "indicators" dictionary to be populated every iteration of a live stock price.
#This dictionary saves runtime by ensuring every piece of necessary historical data is only scraped once.
indicator_historical = {}

#The "indicator_data_points_needed" dictionary contains the number of data points needed for the live calculation of each technical indicator that will be stored in "indicator_historical"
indicator_data_points_needed = {
    "RSI":2,
    "EMA":1,
    "MACD":3,
}

#The "indicator_data_points_needed" dictionary is populated only once using "calculate_historical_data" and contains all the necessary historical stock statistical information used...
#...in the selection strategies.
stock_statistics_historical = {}

#These three variables are updated with every live scraped stock and are used for calculating updated indicators and statistics for the iterating of each strategy

#The "ticker" string represents the current stock ticker whose price and volume just got updated within the live scraping process.
ticker = ""

#The "price" float represents the current stock price that just got updated within the live scraping process.
price = 0

#The "volume" integer represents the current stock volume that just got updated within the live scraping process.
volume = 0

#The "strategies" list contains every permuation of selection strategy, entrance strategy, and exit strategy that will be tracked for this day's execution. 
strategies = [
    (selection1, entrance1, exit1)
]

#Holding, Exited, MaxHolding
#The "strategies_performance_tracking" list contains all of the data for each strategy permutation that will later be converted to proper performance metrics
#For each performance tracking list for each strategy permutation, there is are currently three variables being tracked:
#1. The "Holding" dictionary - {ticker:(price at time of entrance (float), True=Bought/False=shorted (boolean))}
#2. The "Exited" list - [(ticker, price at time of entrance (float), True=Bought/False=shorted (boolean), price at time of exit (float))]
#3. The "MaxHolding" integer - The maximum amount of stocks that were being held at one time during the trading day.
strategies_performance_tracking = [[{}, [], 0]]*len(strategies)

#Indicator Functions

#The "update_indicators" function updates the "indicators" dictionary for every new scraped live stock price.
def update_indicators() :

    #The "difference" float is the difference between the stock's current price and yesterday's closing price
    difference = price-indicator_historical[ticker][0]

    #"The loading_index" integer is the index of interest of this stock's historical data tuple from the "indicator_historical" dictionary
    loading_index = 1

    #This for loop wil iterate through every required RSI period setting 
    for period in indicator_inputs_required["RSI"] :

        #If the difference is positive (price has increased since yesterday's close), update the average gain and average loss accordingly using the "avg_change_formula" function
        if difference >= 0 :

            #The "avg_gain" float represents the average of all the positive daily changes in closing prices for this RSI period setting
            avg_gain = avg_change_formula(indicator_historical[ticker][loading_index], period, difference)

            #The "avg_loss" float represents the average of all the negative daily changes in closing prices for this RSI period setting
            avg_loss = avg_change_formula(indicator_historical[ticker][loading_index+1], period, 0)

        #If the difference is negative (price has decreased since yesterday's close), update the average gain and average loss accordingly using the "avg_change_formula" function
        else :
            #The "avg_gain" float represents the average of all the positive daily changes in closing prices for this RSI period setting
            avg_gain = avg_change_formula(indicator_historical[ticker][loading_index], period, 0)

            #The "avg_loss" float represents the average of all the negative daily changes in closing prices for this RSI period setting
            avg_loss = avg_change_formula(indicator_historical[ticker][loading_index+1], period, -difference)
 
        #Calculate the live RSI value for this period using the "rsi_formula" function and store in the "indicators" dictionary
        indicators["RSI"][period] = round(rsi_formula(avg_gain, avg_loss), 4)

        #Increase the loading index by the number of data points that were used in this specific RSI period setting calculation
        loading_index += indicator_data_points_needed["RSI"]

    #This for loop wil iterate through every required EMA period setting 
    for period in indicator_inputs_required["EMA"] :

        #Calculate the live EMA value for this period using the "ema_formula" function and store in the "indicators" dictionary
        indicators["EMA"][period] = round(ema_formula(price, period, indicator_historical[ticker][loading_index]), 4)

        #Increase the loading index by the number of data points that were used in this specific EMA period setting calculation
        loading_index += indicator_data_points_needed["EMA"]
    
    #This for loop wil iterate through every required MACD period setting 
    for combination in indicator_inputs_required["MACD"] :

        #Calculate the live fast EMA value for this combination using the "ema_formula" function 
        fast_ema = ema_formula(price, combination[0], indicator_historical[ticker][loading_index])

        #Calculate the live slow EMA value for this combination using the "ema_formula" function 
        slow_ema = ema_formula(price, combination[1], indicator_historical[ticker][loading_index+1])

        #Calculate the live MACD EMA value for this combination using the "ema_formula" function 
        macd_ema = ema_formula(fast_ema-slow_ema, combination[2], indicator_historical[ticker][loading_index+2])

        #Calculate and store the MACD value and the MACD EMA for this combination in the "indicators" dictionary
        indicators["MACD"][combination] = (round(fast_ema-slow_ema, 4), round(macd_ema, 4))

        #Increase the loading index by the number of data points that were used in this specific MACD combination setting calculation
        loading_index += indicator_data_points_needed["MACD"]

def update_stock_statistics() :
    #if "MARKET_CAP" in 
    stock_statistics["MARKET_CAP"] = stock_statistics_historical[ticker]["marketCap"]
    stock_statistics["VOLUME"] = volume
    stock_statistics["RELATIVE_VOLUME"] = round(volume/stock_statistics_historical[ticker]["averageVolume"], 3)
                                                                                 
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

def convert_volume_to_integer(volume_in_millions:str) :
    number_translations = {"K":1000, "M":1000000, "B":1000000000}
    return int(float(volume_in_millions[:-1])*number_translations[volume_in_millions[-1]])

def scrape_live_data() :
    scraped_tickers = [element.text for element in driver.find_elements(By.XPATH, "//td/a[@data-test='quoteLink']")]
    scraped_prices = [float(element.text) for element in driver.find_elements(By.XPATH, "//td/fin-streamer[@data-field='regularMarketPrice']")]
    scraped_volumes = [convert_volume_to_integer(element.text) for element in driver.find_elements(By.XPATH, "//td/fin-streamer[@data-field='regularMarketVolume']")]
    return list(zip(scraped_tickers, scraped_prices, scraped_volumes))

def main(testing_mode) :
    global ticker, price, volume
    user_email = "reginaldjhyde@gmail.com"
    user_password = "PythonIsAwesome!"
    open_webbdriver(user_email, user_password)
    scraped_data = scrape_live_data()
    for scraped_stock in scraped_data :
        indicator_historical[scraped_stock[0]], stock_statistics_historical[scraped_stock[0]] = calculate_historical_data(scraped_stock[0], indicator_data_points_needed, indicator_inputs_required, yahoo_statistics_required)

    while True :
        if not testing_mode :
            minutes_elapsed = get_minutes_elapsed()
            if not (minutes_elapsed >= 570 and minutes_elapsed <= 960) :
                print("Stock exchanges are closed")
                break

        start = time.time()
        
        scraped_data = scrape_live_data()
        for scraped_stock in scraped_data :
            ticker, price, volume = scraped_stock
            update_indicators()
            update_stock_statistics()
            print(ticker, price)
            print(indicators)
            print(stock_statistics)
            print()
            for strategy_index, strategy in enumerate(strategies) :
                if ticker in strategies_performance_tracking[strategy_index][0] :
                    if strategy[2]() :
                        strategies_performance_tracking[strategy_index][1].append((ticker)+strategies_performance_tracking[strategy_index][0]+(price))
                        del strategies_performance_tracking[strategy_index][0][ticker]
                else :
                    if strategy[0]() :
                        entrance_result = strategy[1]()
                        if entrance_result != None :
                            strategies_performance_tracking[strategy_index][0][ticker] = (price, entrance_result)
                            current_holding = len(strategies_performance_tracking[strategy_index][0][ticker])
                            strategies_performance_tracking[strategy_index][2][ticker] = max(current_holding, strategies_performance_tracking[strategy_index][2][ticker])
            
        print("Completed in ", time.time()-start)
        quit()

main(True)


