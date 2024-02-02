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

import traceback, re

#Quit program if @ranaroussi's yfinance package is not up-to-date
if not check_up_to_date("yfinance") :
    print("yfinance is not up-to-date. Run \"pip install yfinance --upgrade\" to update yfinance.")
    quit()

#The TradingStrategies class
class TradingStrategies :

    #Initialize global variables for the class
    def __init__(self, strategies) :
        
        #The "strategies" list contains every permuation of selection strategy, entrance strategy, and exit strategy that will be tracked for this day's execution. 
        self.strategies = strategies

        #The "indicators_available" list contains all the names of technical indicators currently supported
        self.indicators_available = ["RSI", "EMA", "MACD"]

        #The "indicator_data_points_needed" dictionary contains the number of data points needed for the live calculation of each technical indicator that will be stored in "indicator_historical"
        self.indicator_data_points_needed = {
            "RSI":2,
            "EMA":1,
            "MACD":3,
        }

        #The "stock_statistics_available" list contains all the names of stock statistics currently supported
        self.stock_statistics_available = ["MARKET_CAP", "VOLUME", "RELATIVE_VOLUME", "PRICE"]

        #The "indicator_inputs_required" dictionary contains all the specific settings for each indicator that will be used within the entrance/exit strategies
        self.indicator_inputs_required = {
            "RSI":[5, 9, 14],
            "EMA":[10, 20, 50, 100, 200],
            "MACD":[(12, 26, 9), (5, 35, 5), (19, 39, 9)]
        }

        self.indicator_price_required = True

        #The "yahoo_statistics_required" dictionary contains all the statistics from yfinance needed for all the calculations within "stock_statistics_required"
        self.yahoo_statistics_required = ["marketCap", "averageVolume"]

        #The "indicators" dictionary is updated for every scraped stock and contains the live calculations of every required setting of every required indicator for the current stock
        self.indicators = {indicator_name:{} for indicator_name in self.indicator_inputs_required}

        #The "stock_statistics" dictionary is updated for every scraped stock and contains the live stock statistics for the current stock
        self.stock_statistics = {}

        #The "indicator_historical" dictionary is populated only once using "calculate_historical_data" and contains all the data for every stock needed to make quick calculations for every...
        #...required setting of every required indicator.
        #This dictionary allows the "indicators" dictionary to be populated every iteration of a live stock price.
        #This dictionary saves runtime by ensuring every piece of necessary historical data is only scraped once.
        self.indicator_historical = {}

        #The "indicator_data_points_needed" dictionary is populated only once using "calculate_historical_data" and contains all the necessary historical stock statistical information used...
        #...in the selection strategies.
        self.stock_statistics_historical = {}

        #These three variables are updated with every live scraped stock and are used for calculating updated indicators and statistics for the iterating of each strategy

        #The "ticker" string represents the current stock ticker whose price and volume just got updated within the live scraping process.
        self.ticker = ""

        #The "price" float represents the current stock price that just got updated within the live scraping process.
        self.price = 0

        #The "volume" integer represents the current stock volume that just got updated within the live scraping process.
        self.volume = 0

        #Holding, Exited, MaxHolding
        #The "strategies_performance_tracking" list contains all of the data for each strategy permutation that will later be converted to proper performance metrics
        #For each performance tracking list for each strategy permutation, there is are currently three variables being tracked:
        #1. The "Holding" dictionary - {ticker:(price at time of entrance (float), True=Bought/False=shorted (boolean))}
        #2. The "Exited" list - [(ticker, price at time of entrance (float), True=Bought/False=shorted (boolean), price at time of exit (float))]
        #3. The "MaxHolding" integer - The maximum amount of stocks that were being held at one time during the trading day.
        self.strategies_performance_tracking = [[{}, [], 0]]*len(self.strategies)

        #The "driver" is the Microsoft Edge webdriver that I will automate to scrape live price and volume data from a Yahoo Finance stock watchlist
        self.driver = webdriver.Edge()

        #The "update_index" is the index of interest of the historical data for updating indicators
        self.update_index = 1

    def get_stock_statistic_requirements(self, selection_strategy) :
        requirements = {}
        while True :
            try :
                selection_strategy(requirements)
                break
            except KeyError as key_missing :
                stock_stat_name = str(key_missing).replace("'", "")
                if not stock_stat_name in self.stock_statistics_available :
                    exception_line = str(traceback.format_exc()).split("\n")[4]
                    print(exception_line, "  <---- "+stock_stat_name+" is an unsupported stock statistic at this time.")
                    quit()
                requirements[stock_stat_name] = 1
        return list(requirements.keys())
    
    def get_indicator_requirements(self, entrance_strategy, exit_strategy) :
        requirements = {"RSI":{}}
        while True :
            try :
                entrance_strategy(requirements)
                break
            except Exception :
                exception_line = str(traceback.format_exc()).split("\n")[4]
                required_keys = [required_key.replace("[", "").replace("]", "") for required_key in re.findall("\[{1}[^\[\]]+\]", exception_line)]
                if len(required_keys) != 2 :
                    print(exception_line, "  <---- This line should have exactly 2 inputs for an indicator value. Dictionary keys should be [\"(Indicator Name)\"][\"(Indicator Setting)\"]")
                    quit()
                if not required_keys[0] in self.indicators_available :
                    print(exception_line, "  <---- "+required_keys[0]+" is an unsupported indicator at this time.")
                    quit()

                try :
                    int(required_keys[1])
                except :
                    try :
                        tuple(required_keys[1])
                    except :
                        print("")
                    
                
                print(required_keys)
                quit()
    
    def populate_requirements(self) :
        for strategy in self.strategies :
            selection_strategy, entrance_strategy, exit_strategy = strategy
            print(self.get_stock_statistic_requirements(selection_strategy))
            print(self.get_indicator_requirements(entrance_strategy, exit_strategy))
            quit()
        

    #The "update_rsi" function updates the RSI values for each required setting within the "indicators" dictionary.
    def update_rsi(self) :

        #The "difference" float is the difference between the stock's current price and yesterday's closing price
        difference = self.price-self.indicator_historical[self.ticker][0]
        
        #This for loop wil iterate through every required RSI period setting 
        for period in self.indicator_inputs_required["RSI"] :

            #If the difference is positive (price has increased since yesterday's close), update the average gain and average loss accordingly using the "avg_change_formula" function
            if difference >= 0 :

                #The "avg_gain" float represents the average of all the positive daily changes in closing prices for this RSI period setting
                avg_gain = avg_change_formula(self.indicator_historical[self.ticker][self.update_index], period, difference)

                #The "avg_loss" float represents the average of all the negative daily changes in closing prices for this RSI period setting
                avg_loss = avg_change_formula(self.indicator_historical[self.ticker][self.update_index+1], period, 0)

            #If the difference is negative (price has decreased since yesterday's close), update the average gain and average loss accordingly using the "avg_change_formula" function
            else :
                #The "avg_gain" float represents the average of all the positive daily changes in closing prices for this RSI period setting
                avg_gain = avg_change_formula(self.indicator_historical[self.ticker][self.update_index], period, 0)

                #The "avg_loss" float represents the average of all the negative daily changes in closing prices for this RSI period setting
                avg_loss = avg_change_formula(self.indicator_historical[self.ticker][self.update_index+1], period, -difference)
     
            #Calculate the live RSI value for this period using the "rsi_formula" function and store in the "indicators" dictionary
            self.indicators["RSI"][period] = round(rsi_formula(avg_gain, avg_loss), 4)

            #Increase the loading index by the number of data points that were used in this specific RSI period setting calculation
            self.update_index += self.indicator_data_points_needed["RSI"]

    #The "update_ema" function updates the EMA values for each required setting within the "indicators" dictionary.
    def update_ema(self) :
        #This for loop wil iterate through every required EMA period setting 
        for period in self.indicator_inputs_required["EMA"] :

            #Calculate the live EMA value for this period using the "ema_formula" function and store in the "indicators" dictionary
            self.indicators["EMA"][period] = round(ema_formula(self.price, period, self.indicator_historical[self.ticker][self.update_index]), 4)

            #Increase the loading index by the number of data points that were used in this specific EMA period setting calculation
            self.update_index += self.indicator_data_points_needed["EMA"]

    #The "update_macd" function updates the MACD values for each required setting within the "indicators" dictionary.
    def update_macd(self) :
        #This for loop wil iterate through every required MACD period setting 
        for combination in self.indicator_inputs_required["MACD"] :

            #Calculate the live fast EMA value for this combination using the "ema_formula" function 
            fast_ema = ema_formula(self.price, combination[0], self.indicator_historical[self.ticker][self.update_index])

            #Calculate the live slow EMA value for this combination using the "ema_formula" function 
            slow_ema = ema_formula(self.price, combination[1], self.indicator_historical[self.ticker][self.update_index+1])

            #Calculate the live MACD EMA value for this combination using the "ema_formula" function 
            macd_ema = ema_formula(fast_ema-slow_ema, combination[2], self.indicator_historical[self.ticker][self.update_index+2])

            #Calculate and store the MACD value and the MACD EMA for this combination in the "indicators" dictionary
            self.indicators["MACD"][combination] = (round(fast_ema-slow_ema, 4), round(macd_ema, 4))

            #Increase the loading index by the number of data points that were used in this specific MACD combination setting calculation
            self.update_index += self.indicator_data_points_needed["MACD"]
            
    #The "update_indicators" function updates the "indicators" dictionary for every new scraped live stock price.
    def update_indicators(self) :

        #"The self.update_index" integer is the index of interest of this stock's historical data tuple from the "indicator_historical" dictionary
        self.update_index = 1

        #Call all of the update functions for each technical indicator.
        self.update_rsi()
        self.update_ema()
        self.update_macd()

        #Update the current price into the "indicators" dictionary if it is required
        if self.indicator_price_required :
            self.indicators["CurrentPrice"] = self.price

    #The "update_stock_statistics" function updates the "stock_statistics" dictionary for every new scraped live stock price.
    def update_stock_statistics(self) : 
        self.stock_statistics["MARKET_CAP"] = self.stock_statistics_historical[self.ticker]["marketCap"]
        self.stock_statistics["VOLUME"] = self.volume
        self.stock_statistics["RELATIVE_VOLUME"] = round(self.volume/self.stock_statistics_historical[self.ticker]["averageVolume"], 3)
        self.stock_statistics["PRICE"] = self.price
                                                                                     
    #The "get_minutes_elapsed" function gets the current minutes elapsed in Eastern Time
    def get_minutes_elapsed(self) :
        #First, get the time in Eastern Time
        tz = timezone('EST')

        #Breaking the string version of this time data structure and extract the hours and minutes
        split_by_colon = str(datetime.now(tz)).split(" ")[1].split(":")
        hour, minutes = int(split_by_colon[0]), int(split_by_colon[1])

        #Calculate the and return total minutes elapsed
        return (hour*60)+minutes


    #The "open_webdriver" function automates the entire login process for the Yahoo Finance website to get to the stock watchlist site
    def open_webdriver(self, user_email, user_password) :
        try : 
            #This is the initial url I will attempt to load, but it will take me to the general Yahoo Finance landing page
            url = "https://finance.yahoo.com/portfolios/"

            #Load the this url and make the webdriver fullscreen
            self.driver.get(url)
            self.driver.fullscreen_window()

            #This try-and-except code block accounts for a specific circumstance in which an ad generates above the sign-in button and changes how it is expressed in the website html.
            try :
                
                #Locate the signin button element and automate the webdriver to click it to redirect the webdriver to the sign-in url
                sign_in = self.driver.find_element(By.XPATH, "//li[@id='header-profile-menu']/a[1]")
                sign_in.click()

            #If the ad is generated above the sign-in button, locate it using this method instead    
            except :
                
                #Locate the signin button element and automate the webdriver to click it to redirect the webdriver to the sign-in url
                sign_in = self.driver.find_element(By.XPATH, "//div[@id='login-container']/a[1]")
                sign_in.click()

            #Wait for 3 seconds to let the page fully load (after webdriver redirects url) and make webdriver fullscreen
            time.sleep(3)
            self.driver.fullscreen_window()

            #Locate the username element and automate entering the "user_email" string into the username field.
            username = self.driver.find_element(By.ID, "login-username")
            username.send_keys(user_email)

            #Locate the next button and click to proceed with in the sign-in process
            next_button = self.driver.find_element(By.NAME, "signin")
            next_button.click()

            #Wait for 3 seconds to let the page fully load (after webdriver redirects url) and make webdriver fullscreen
            time.sleep(3)
            self.driver.fullscreen_window()

            #Locate the password element and automate entering the "user_password" string into the password field.
            password = self.driver.find_element(By.ID, "login-passwd")
            password.send_keys(user_password)

            #Locate the next button and click to proceed with in the sign-in process
            next_button2 = self.driver.find_element(By.NAME, "verifyPassword")
            next_button2.click()

            #Wait for 3 seconds to let the page fully load (after webdriver redirects url
            time.sleep(3)

            #Redirect the webdriver to the watchlist url and make it fullscreen
            self.driver.get("https://finance.yahoo.com/portfolio/p_0/view/v1")
            self.driver.fullscreen_window()
        except :
            #Error message
            print("There was an error with the WebDriver. If there is a captcha, complete it and run the script again. Otherwise, make sure to not interact with the WebDriver whatsoever while it is redirecting to your watchlist.") 

    #The "convert_volume_to_integer" converts a string like "2.74M" to the integer 2,740,000 
    def convert_volume_to_integer(self, volume_str:str) :

        #Remove the commas from the string
        volume_str = volume_str.replace(",","")

        #Try to return integer version of the string if it does not contain letters
        try :
            return int(volume_str)

        #Convert the letters to integers if the string contains letters
        except :

            #The "number_translations" dictionary converts K, M, and B to one thousand, one million, and one billion, respectively.
            number_translations = {"k":1000, "M":1000000, "B":1000000000}

            #Calculate actual integer using the "number_translations" 
            return int(float(volume_str[:-1])*number_translations[volume_str[-1]])

    #The "scrape_live_data" function is ran at every interval of this day's execution to scrape the live tickers, prices, and volumes of the stocks from the Yahoo Finance watchlist 
    def scrape_live_data(self) :

        #The "scraped_tickers" list is populated with all the tickers present in the watchlist
        scraped_tickers = [element.text for element in self.driver.find_elements(By.XPATH, "//td/a[@data-test='quoteLink']")]

        #The "scraped_prices" list is populated with all the live prices present in the watchlist    
        scraped_prices = [float(element.text) for element in self.driver.find_elements(By.XPATH, "//td/fin-streamer[@data-field='regularMarketPrice']")]

        #The "scraped_prices" list is populated with all the live volumes present in the watchlist. The "convert_volume_to_integer" function is used to convert the raw texts from the website to integers.
        scraped_volumes = [self.convert_volume_to_integer(element.text) for element in self.driver.find_elements(By.XPATH, "//td/fin-streamer[@data-field='regularMarketVolume']")]

        #Return the zip of these three lists to create a list of tuples like ("MSFT", 400.02, 1720000)
        return list(zip(scraped_tickers, scraped_prices, scraped_volumes))

    #The "deploy_strategies" function is the main function that executes this day's execution to track performance of trading strategy permutations
    def deploy_strategies(self, testing_mode) :

        self.populate_requirements()

        #The "user_email" string will be entered in the email field for the Yahoo Finance sign-in page
        user_email = "reginaldjhyde@gmail.com"

        #The "user_password" string will be entered in the password field for the Yahoo Finance sign-in page
        user_password = "PythonIsAwesome!"

        #Call the "open_webdriver" function to sign in and access the watchlist page with live stock prices and volumes
        self.open_webdriver(user_email, user_password)

        #Call the "scrape_live_data" function once before the interval execution loop to get the list of stock tickers in the watchlist
        scraped_data = self.scrape_live_data()

        #This for loop iterates through each of the stock tickers in the watchlist, calculates its historical indicator and statistical data, and stores it in "stock_statistics_historical"
        for scraped_stock in scraped_data :
            self.indicator_historical[scraped_stock[0]], self.stock_statistics_historical[scraped_stock[0]] = calculate_historical_data(scraped_stock[0], self.indicator_data_points_needed, self.indicator_inputs_required, self.yahoo_statistics_required)

        #This loop is the main interval execution loop. This loop will run during the whole trading day
        while True :

            #If this is not a test run to test code,
            if not testing_mode :

                #The "minutes_elapsed" integer is will be populated by the "get_minutes_elapsed" function.
                minutes_elapsed = self.get_minutes_elapsed()

                #If the total minutes elapsed in Eastern time is not between 9:30 AM and 4 PM, break the interval execution loop.
                if not (minutes_elapsed >= 570 and minutes_elapsed <= 960) :
                    print("Stock exchanges are closed")
                    break

            #Get the current time (in seconds) to track when the live data scraping for this interval started.
            start = time.time()

            #Call the "scrape_live_data" function to iterate through each live stock price and volume.
            scraped_data = self.scrape_live_data()

            #This loop iterates through each tuple of (ticker, live price, live volume) returned from the "scrape_live_data" function.
            for scraped_stock in scraped_data :

                #Unpack the tuple
                self.ticker, self.price, self.volume = scraped_stock

                #Call the "update_indicators" function to update the "indicators" dictionary for this stock
                self.update_indicators()

                print(self.ticker, self.price, self.indicators)

                #Call the "update_stock_statistics" function to update the "stock_statistics" dictionary for this stock
                self.update_stock_statistics()
                
                #This for loop iterates through each strategy permuation and tracks their performance
                for strategy_index, strategy in enumerate(self.strategies) :

                    #If this stock is currently held by this strategy permutation
                    if self.ticker in self.strategies_performance_tracking[strategy_index][0] :

                        #If this strategy permutation decided to exit the trade
                        if strategy[2](self.indicators, self.strategies_performance_tracking[strategy_index][0][self.ticker][1]) :

                            #Update "strategies_performance_tracking" list by logging the ticker, starting price, Buy/Short boolean, and current price
                            price_at_entry, bought_or_shorted = self.strategies_performance_tracking[strategy_index][0][self.ticker]
                            self.strategies_performance_tracking[strategy_index][1].append((self.ticker, price_at_entry, bought_or_shorted, self.price))

                            #Delete this holding from "strategies_performance_tracking" list
                            del self.strategies_performance_tracking[strategy_index][0][self.ticker]

                    #If this stock is not currently held by this strategy permutation
                    else :

                        #If this stock passes this strategy permutation's stock selection function
                        if strategy[0](self.stock_statistics) :

                            #Call this strategy permutation's entrance function 
                            entrance_result = strategy[1](self.indicators)

                            #If the result of this strategy permutation's entrance function is either True (Buy) or False (Short)
                            if entrance_result != None :

                                #Enter the trade by updating "strategies_performance_tracking" list with current price and True/False (Buy/Short) value
                                self.strategies_performance_tracking[strategy_index][0][self.ticker] = (self.price, entrance_result)

                                #Update the MaxHolding performance tracker by comparing the current number of trades held vs the current max number of trades held
                                current_holding = len(self.strategies_performance_tracking[strategy_index][0])
                                self.strategies_performance_tracking[strategy_index][2] = max(current_holding, self.strategies_performance_tracking[strategy_index][2])
            
            print("Completed in ", time.time()-start)
            quit()
            #print(self.strategies_performance_tracking)


def selection_test(stats) :
    return stats["MARKET_CAP"] > 1
        
def entrance_test(inds) :
    if inds["BBands"][14] <= 80 :
        return True
    if inds["RSI"][14] >= 80 :
        return False

def exit_test(inds, bought_or_shorted) :
    return True

strategies = [
    [selection_test, entrance_test, exit_test]
]

obj = TradingStrategies(strategies)

obj.deploy_strategies(False)
