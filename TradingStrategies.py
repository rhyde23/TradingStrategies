#NOTE: This project is heavily reliant on Yahoo Finance and @ranaroussi's yfinance package, which uses Yahoo Finance's API

#Imported Libraries/Scripts

#requests library - For processing url requests for live scraping data from Yahoo Finance watchlist
#time library - For use of the time.sleep() function to assure that web pages are fully loaded before being scraped
import requests, time

#datetime library - For accessing the current time and checking if the US Stock Markets are open
from datetime import datetime

#pytz library - For converting the current time in terms of Eastern Time
from pytz import timezone

#selenium library - For web scraping websites with dynamic content.
#Yahoo Finance's live stock watchlists are reliant on JavaScript, so a selenium webdriver is necessary to scrape them.
#A webdriver basically creates a copy of a web browser and automates/mimics user input and scrapes the website
#By contrast, Python's beautifulsoup4 can only load page sources (html).
from selenium import webdriver
from selenium.webdriver.common.by import By

#calculateHistoricalData script - Written by me for the purpose of calculating all the data needed for the quick update of technical indicators and stock statistics.
#By accessing historical data using the yfinance package, I can set up everything I need for technical indicator calculations so that the live price is the only missing piece.
#This script also collects data such as Market Cap, Average Volume, etc. (statistics that don't need to be scraped live)
#It is hugely important that this data collection happens separately from live scraping for effiency because this initial data collection ONLY NEEDS TO HAPPEN ONCE.
from calculateHistoricalData import calculate_historical_data, avg_change_formula, ema_formula, rsi_formula

#checkUpToDate script - contains the function "check_up_to_date" to check if a libaray is up-to-date
from checkUpToDate import check_up_to_date

#populateRequirements script - Written by me, contains functions to identify what indicators, indicator settings, and stock statistics are required to update live.
from populateRequirements import get_stock_statistic_requirements, get_indicator_requirements, translate_stat_names_to_yahoo

#recordExcelData script - Written by me, contains functions to record strategies performance metrics.
from recordExcelData import record_performance_data

#math library - For various mathematical functions, I need the "sqrt" or square root function for standard deviation calculations for Bollinger Bands calculations
from math import sqrt

#robin_stocks library - To authenticate Robinhood accounts and execute buy and sell stock orders.
import robin_stocks.robinhood as r

#pyotp - For 2-factor authentication for Robinhood signin.
import pyotp

#Quit program if @ranaroussi's yfinance package is not up-to-date
if not check_up_to_date("yfinance") :
    print("yfinance is not up-to-date. Run \"pip install yfinance --upgrade\" to update yfinance.")
    #quit()

#The TradingStrategies class
class TradingStrategies :

    #Initialize global variables for the class
    def __init__(self, strategies) :
       
        #The "strategies" list contains every permuation of selection strategy, entrance strategy, and exit strategy that will be tracked for this day's execution.
        self.strategies = strategies

        #The "indicator_data_points_needed" dictionary contains the number of data points needed for the live calculation of each technical indicator that will be stored in "indicator_historical"
        self.indicator_data_points_needed = {
            "RSI":2,
            "EMA":1,
            "MACD":3,
            "SMA":1,
            "BBands":2,
        }

        #The "indicators_available" dictionary contains all the indicators available and how many arguments are needed for setting specification
        self.indicators_available = {
            "RSI":1,
            "EMA":1,
            "MACD":3,
            "SMA":1,
            "BBands":2,
        }

        #The "stock_statistics_available" list contains all the names of stock statistics currently supported
        self.stock_statistics_available = ["MARKET_CAP", "VOLUME", "RELATIVE_VOLUME", "PRICE"]

        #The "indicator_inputs_required" dictionary contains all the specific settings for each indicator that will be used within the entrance/exit strategies
        self.indicator_inputs_required = {}

        #The "stock_statistics_required" list contains all of the stock statistics that will be used within the selection strategy
        self.stock_statistics_required = []

        #Iterate through each strategy and populate "indicator_inputs_required" and "stock_statistics_required"
        for strategy in strategies :

            #Call the "get_indicator_requirements" using the entrance and exit functions from this strategy and parse through all of their required indicator settings
            new_required_indicators = get_indicator_requirements(strategy[1], strategy[2], self.indicators_available)
            for new_required_key in new_required_indicators :

                #If the required indicator is not already within "indicator_inputs_required", add it
                if not new_required_key in self.indicator_inputs_required :
                    self.indicator_inputs_required[new_required_key] = new_required_indicators[new_required_key]

                #If the required indicator is already within "indicator_inputs_required", add the new settings that aren't already present
                else :
                    self.indicator_inputs_required[new_required_key] = list(set(self.indicator_inputs_required[new_required_key]+new_required_indicators[new_required_key]))

            #Update "stock_statistics_required" by adding the stock statistics from this strategy that aren't already present
            self.stock_statistics_required = list(set(self.stock_statistics_required+get_stock_statistic_requirements(strategy[0], self.stock_statistics_available)))
       
        #The "yahoo_statistics_required" dictionary contains all the statistics from yfinance needed for all the calculations within "stock_statistics_required"
        self.yahoo_statistics_required = translate_stat_names_to_yahoo(self.stock_statistics_required)

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
        self.strategies_performance_tracking = [[{}, [], 0, self.strategies[i][3]] for i in range(len(self.strategies))]

        #The "driver" variable will be the Microsoft Edge webdriver that I will automate to scrape live price and volume data from a Yahoo Finance stock watchlist
        self.driver = None

        #The "update_index" is the index of interest of the historical data for updating indicators
        #(the first value in the "historical_list" was set to yesterday's closing price and the second value will be the last recorded live price.)
        #First value is for RSI calculations, Second value is for BBands calculations
        self.update_index = 2

        #The "robinhood_login" variable is the response from python's robin_stocks that verifies account login.
        self.robinhood_login = None

        #The "deployed_strategy_name" is the name of the strategy that the user chooses to deploy with real trades.
        self.deployed_strategy_name = None

        #The "robinhood_investment_amount" float is the amount of money per trade the user wants to use for buy trades.
        self.robinhood_investment_amount = None

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

    #The "update_sma" function updates the SMA values for each required setting within the "indicators" dictionary.
    def update_sma(self) :
        #This for loop wil iterate through every required SMA period setting
        for period in self.indicator_inputs_required["SMA"] :

            #Calculate the live SMA value for this period by adding the current price and dividing the period length and store in the "indicators" dictionary
            self.indicators["SMA"][period] = round((self.indicator_historical[self.ticker][self.update_index]+self.price)/period, 4)

            #Increase the loading index by the number of data points that were used in this specific SMA period setting calculation
            self.update_index += self.indicator_data_points_needed["SMA"]

    #The "update_bbands" function updates the BBands values for each required combination within the "indicators" dictionary.
    def update_bbands(self) :
       
        #This for loop wil iterate through every required BBands period setting
        for combination in self.indicator_inputs_required["BBands"] :

            #The formula for a rolling standard deviation is as follows:
            #standard_deviation = sqrt(variance+((new - old) * (new - new_average + old - old_average) / period))

            #Unpack the old variance value from the last calculation from "self.indicator_historical"
            variance = self.indicator_historical[self.ticker][self.update_index+1]

            #Unpack the last recorded live price from the last variance calculation
            old = self.indicator_historical[self.ticker][1]

            #Calculate the new average by adding the sum of the previous period-1 days and the current live price and divide that by the period length
            new_average = (self.indicator_historical[self.ticker][self.update_index]+self.price)/combination[0]

            #Calculate the old average by adding the sum of the previous period-1 days and the last recorded live price and divide that by the period length
            old_average = (self.indicator_historical[self.ticker][self.update_index]+old)/combination[0]

            #Calculate the new variance using the rolling standard deviation from above
            new_variance = variance+((self.price - old) * (self.price - new_average + old - old_average) / combination[0])

            #Calculate the new standard deviation for this combination by taking the square root of the new variance
            new_standard_deviation = round(sqrt(new_variance), 4)
            
            #Calculate the lower and upper bands by subtracting and adding the standard deviation by this combination's stdev multiplier, respectively
            lower_band, middle_band, upper_band = new_average-(new_standard_deviation*combination[1]), new_average, new_average+(new_standard_deviation*combination[1])

            #Store the Lower Band, Middle Band, and Upper Band in "self.indicators" for this Bollinger Bands combination.
            self.indicators["BBands"][combination] = (lower_band, middle_band, upper_band)

            #Increase the loading index by the number of data points that were used in this specific BBands period setting calculation
            self.update_index += self.indicator_data_points_needed["BBands"]
           
    #The "update_indicators" function updates the "indicators" dictionary for every new scraped live stock price.
    def update_indicators(self) :

        #"The self.update_index" integer is the index of interest of this stock's historical data tuple from the "indicator_historical" dictionary
        #(the first value in the "historical_list" was set to yesterday's closing price and the second value will be the last recorded live price.)
        #First value is for RSI calculations, Second value is for BBands calculations
        self.update_index = 2

        #The "update_function_names" list preserves the indicator names in the correct order of how the historical calculation values were recorded in "self.indicator_historical".
        update_function_names = ["RSI", "EMA", "MACD", "SMA", "BBands"]

        #The "update_functions" list associates each indicator name as a string with the function that updates them in real time
        update_functions = [self.update_rsi, self.update_ema, self.update_macd, self.update_sma, self.update_bbands]

        #Call all of the update functions for each technical indicator.
        #Iterate through update function for each technical indicator.
        for ufn_ind, update_function_name in enumerate(update_function_names) :

            #If the indicator is required.
            if update_function_name in self.indicator_inputs_required :

                #Call its update function.
                update_functions[ufn_ind]()

        #Update the live stock price in "self.indicators"
        self.indicators["PRICE"] = self.price

    #The "update_stock_statistics" function updates the "stock_statistics" dictionary for every new scraped live stock price.
    def update_stock_statistics(self) :

        #If Market Cap is a required statistic, update
        if "MARKET_CAP" in self.stock_statistics_required :
            self.stock_statistics["MARKET_CAP"] = self.stock_statistics_historical[self.ticker]["marketCap"]

        #If Volume is a required statistic, update
        if "VOLUME" in self.stock_statistics_required :
            self.stock_statistics["VOLUME"] = self.volume

        #If Relative Volume is a required statistic, update
        if "RELATIVE_VOLUME" in self.stock_statistics_required :
            self.stock_statistics["RELATIVE_VOLUME"] = round(self.volume/self.stock_statistics_historical[self.ticker]["averageVolume"], 3)

        #If Price is a required statistic, update
        if "PRICE" in self.stock_statistics_required :
            self.stock_statistics["PRICE"] = self.price
                                                                                     
    #The "get_minutes_elapsed" function gets the current minutes elapsed in Eastern Time
    def get_minutes_elapsed(self) :
        #First, get the time in Eastern Time
        tz = timezone('US/Eastern')

        #Breaking the string version of this time data structure and extract the hours and minutes
        split_by_colon = str(datetime.now(tz)).split(" ")[1].split(":")
        hour, minutes = int(split_by_colon[0]), int(split_by_colon[1])

        #Calculate the and return total minutes elapsed
        return (hour*60)+minutes


    #The "open_webdriver" function opens the initial webdriver
    def open_webdriver(self, url) :

        #The "driver" is the Microsoft Edge webdriver that I will automate to scrape live price and volume data from a Yahoo Finance stock watchlist
       
        try :
            self.driver = webdriver.Edge()
        except :
            self.driver = webdriver.Chrome()
       
       
        #Load the this url and make the webdriver fullscreen
        self.driver.get(url)

    #The "automated_webdriver_signin" function automates the entire login process for the Yahoo Finance website to get to the stock watchlist site
    def automated_webdriver_signin(self, user_email, user_password, user_watchlist) :
       
        #Try automated sign-in
        try :

            #Make webdriver fullscreen
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

            #The string "user_watchlist_link" returns the string of the link associated with this watchlist name
            user_watchlist_link = [element.get_attribute("href") for element in self.driver.find_elements(By.TAG_NAME, "a") if "portfolio/p_" in element.get_attribute("href") and element.text == user_watchlist][0]

            #If the last two characters of the "user_watchlist_link" are "v2"
            if user_watchlist_link[-2:] == "v2" :

                #Correct the last two characters of "user_watchlist_link" to "v1" to make sure the webdriver will view the portfolio on the correct setting.
                user_watchlist_link[:-1]+"1"
           
            #Redirect the webdriver to the watchlist url and make it fullscreen
            self.driver.get(user_watchlist_link)
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
        scraped_prices = [float(element.text.replace(",", "")) for element in self.driver.find_elements(By.XPATH, "//td/fin-streamer[@data-field='regularMarketPrice']")]

        #The "scraped_prices" list is populated with all the live volumes present in the watchlist. The "convert_volume_to_integer" function is used to convert the raw texts from the website to integers.
        scraped_volumes = [self.convert_volume_to_integer(element.text) for element in self.driver.find_elements(By.XPATH, "//td/fin-streamer[@data-field='regularMarketVolume']")]

        #Return the zip of these three lists to create a list of tuples like ("MSFT", 400.02, 1720000)
        return list(zip(scraped_tickers, scraped_prices, scraped_volumes))

    #The "webdriver_prompt" function prompts the user on whether or not they want to attempt an automated sign-in to their Yahoo Finance account.
    def webdriver_prompt(self) :

        #This loop will continue until the user answers a valid "yes" or "no" answers
        while True :

            #These print statements prompt the user through the terminal or IDLE shell.
            print("Would you like to attempt an automated sign in or redirect the webdriver to your desired watchlist manually?")
            print("Enter \"yes\" for automated sign-in or \"no\" for manual sign-in: ")
            print()

            #User input for their choice
            choice = input(">> ")

            #If the choice is "yes", prompt the user for their Yahoo Finance account information and attempt automated sign-in.
            if choice in ["yes", "y", "YES", "Yes", "Y"] :
               
                print()
               
                #The "user_password" string will be entered in the password field for the Yahoo Finance sign-in page.
                user_email = input("Enter the email of your Yahoo Finance! account >> ")
               
                print()

                #The "user_password" string will be entered in the password field for the Yahoo Finance sign-in page.
                user_password = input("Enter the password of your Yahoo Finance! account >> ")
               
                print()
               
                #The "user_watchlist" string url will be redirected to once sign-in is successful.
                user_watchlist = input("Enter the name of your desired Yahoo Finance! watchlist >> ")
               
                print()

                #Direct the webdriver to Yahoo Finance.
                self.open_webdriver("https://finance.yahoo.com/portfolios/")

                #Execute the "automated_webdriver_signin" function using the user's Yahoo Finance account information.
                self.automated_webdriver_signin(user_email, user_password, user_watchlist)

                #Return True to signigy that the user attempted the automated sign-in.
                return True

            #If the choice is "no", redirect the webdriver to Yahoo Finance and.
            elif choice in ["no", "n", "NO", "No", "N"] :
                self.open_webdriver("https://finance.yahoo.com/portfolios/")

                #Return False to signigy that the user did not attempt the automated sign-in.
                return False

            #If the user input to the prompt was not a clear "yes" or "no" answer, continue prompting them.
            else :
                print("Please give a \"yes\" or \"no\" answer.")
                print()

    #The "webdriver_on_watchlist" function returns whether or not the webdriver is on a live watchlist
    def webdriver_on_watchlist(self) :

        #If the webdriver's current url is on a specific portfolio
        if self.driver.current_url[:36] == "https://finance.yahoo.com/portfolio/" :

            #If the last two characters of the webdriver's url is v2, correct it to v1 to make sure the webdriver is viewing the portfolio on the correct setting.
            if self.driver.current_url[-2:] == "v2" :

                #Redirect the webdriver to the v1 version of this portfolio.
                self.driver.get(self.driver.current_url[:-1]+"1")

            #Return True to signify that the webdriver is on a specific live portfolio watchlist.
            return True

        #Return False to signify that the webdriver is not on a specific live portfolio watchlist.
        return False

    #The "exit_trade" function exits the trade for a strategy based on the current status of self.ticker
    def exit_trade(self, strategy_index) :

        #Get the Price at Entry float and Bought or Shorted boolean from strategies performance tracking
        price_at_entry, bought_or_shorted = self.strategies_performance_tracking[strategy_index][0][self.ticker]

        #Add this trade to the finished trades list in the performance tracking.
        self.strategies_performance_tracking[strategy_index][1].append((self.ticker, price_at_entry, bought_or_shorted, self.price))

        #Delete this holding from "strategies_performance_tracking" list.
        del self.strategies_performance_tracking[strategy_index][0][self.ticker]

    #The "prompt_user_for_real_deployment" function asks the user if they want to deploy the strategy using Robinhood.
    def prompt_user_for_real_deployment(self)  :

        #Prompt the user about Robinhood strategy deployment
        print("Would you like to deploy once of your strategies? You will need to provide your username, password, and 2-factor authentication code if 2-factor authentication is set up for your account.")

        #Notify user about short-selling.
        print("Note: Robinhood currently does not support short-selling, so short sales from a deployed strategy will not be executed.")

        print("Enter \"yes\" or \"no\"")
        print()

        #Loop until user inputs a valid yes or no answer
        while True :

            #Prompt user for yes or no
            choice = input(">> ")

            #If the user picks yes 
            if choice in ["yes", "y", "YES", "Yes", "Y"] :

                #Get the list of the names of strategies inputting by the user.
                list_of_strategy_names = [s[-1] for s in self.strategies]

                #Loop until user inputs an existing strategy name
                while True :

                    print()

                    #Prompt the user for an existing strategy name
                    strategy_name = input("Enter the name of the strategy you want to deploy with real-life trades >> ")

                    #If the inputted name exists in the users' strategies
                    if strategy_name in list_of_strategy_names :

                        #Define/Update "self.deployed_strategy_name"
                        self.deployed_strategy_name = strategy_name

                        #Break the strategy name prompt loop
                        break

                    #If the inputting name doesn't exist in the users' strategies.
                    else :

                        #Notify the user to input a valid strategy name.
                        print()
                        print("Invalid strategy name. Please double check your list of strategy names.")
                        
                    print()

                #Loop until the user inputs a valid login to Robinhood    
                while True :
                    
                    print()

                    #Prompt the user for the username/email for their Robinhood account.
                    robinhood_username = input("Enter your username/email for your Robinhood acount >> ")

                    print()
                    
                    #Prompt the user for the password for their Robinhood account.
                    robinhood_password = input("Enter your password for your Robinhood acount >> ")
                    
                    print()

                    #Prompt the user for the 2-factor authentication code for their Robinhood account.
                    robinhood_2fa = input("Enter the 2-factor authentication code for your Robinhood acount, if it exists. If not, enter nothing. >> ")

                    print()

                    #If the user doesn't have 2fa
                    if robinhood_2fa == "" :

                        #Try to login
                        try :

                            #Define "robinhood_login"
                            self.robinhood_login = r.login(robinhood_email, robinhood_password)

                            #Break the Robinhood login prompt loop
                            break

                        #If login fails, print error message
                        except :
                            print("There was an error in your robhinhood sign-in. Please double check your credentials.")

                    #If the user has 2fa
                    else :

                        #Try to login
                        try :

                            #Use pyotp to get a temporary 2fa
                            totp = pyotp.TOTP(robinhood_2fa).now()

                            #Define "robinhood_login"
                            self.robinhood_login = r.login(robinhood_username, robinhood_password, mfa_code=totp)

                            #Break the Robinhood Login prompt loop
                            break

                        #If the login fails, print error message
                        except :
                            print("There was an error in your robhinhood sign-in. Please double check your credentials.")

                #Loop until the user enters a valid per investment amount
                while True :

                    #Try to convert input into a float
                    try :

                        #Define "robinhood_investment_amount" as the float version of the user input.
                        self.robinhood_investment_amount = float(input("How much from your account would you like to invest for buy trades? (In $) >> "))

                        print()

                        #Break the investment amount prompt loop.
                        break

                    #If the input is not a valid float, print error message.
                    except :
                        
                        print()
                        print("Please enter a valid dollar amount.")
                        print()

                #Break the yes/no prompt loop
                break

            #If the user picks no
            elif choice in ["no", "n", "NO", "No", "N"] :
                print()

                #Break the yes/no prompt loop
                break

            #If the user does not enter a valid yes/no answer
            else :

                #Print error message
                print()
                print("Please give a \"yes\" or \"no\" answer.")
                print()
                
            print()
    
    #The "run_strategies" function is the main function that executes this day's execution to track performance of trading strategy permutations
    def run_strategies(self, testing_mode, excel_sheet_path) :

        #Execute the "prompt_user_for_real_deployment" to prompt the user for Robinhood sign-in info if they wish to deploy a strategy for real trades.
        self.prompt_user_for_real_deployment()

        #Call the "webdriver_prompt" function to sign in to YFinance Live Watchlist.
        attempted_automated_signin = self.webdriver_prompt()

        #Call the "webdriver_on_watchlist" function to see if the sign-in fails
        if not self.webdriver_on_watchlist() :

            #If the attempted sign-in was automated, print this message
            if attempted_automated_signin :
                print("Automated sign-in failed. Please redirect webdriver to your desired stock watchlist.")
                print()

            #If the attempted sign-in was not automated, print this message
            else :
                print("Redirect webdriver to your desired stock watchlist.")
                print()

        #The "print_error_message_interval" integer is the amount of seconds that will pass between each error message
        print_error_message_interval = 60
       
        #The "print_error_message_again" float is the current time in seconds + the print error message interval
        print_error_message_again = time.time()+print_error_message_interval
       
        #Do not proceed with process until the webdriver is on a live watchlist
        while not self.webdriver_on_watchlist() :

            #Print error message every interval.
            if time.time() >= print_error_message_again :
                print("Redirect webdriver to your desired stock watchlist.")
                print()

                #Update "print_error_message_again"
                print_error_message_again = time.time()+60

        #Print success message for webdriver redirect to Yahoo Finance Live Watchlist
        print("Success! The webdriver has reached your desired watchlist to scrape live stock data.")
        print()

        #Print message that explains the next process of scraping Yahoo Finance data
        print("Now the Historical Data will be accessed from Yahoo Finance and indicator calculations will be made...")
        print()
       
        #Call the "scrape_live_data" function once before the interval execution loop to get the list of stock tickers in the watchlist
        scraped_data = self.scrape_live_data()

        #The "expected_time_in_minutes" float is the expected amount of time the scraping will take, it is derived by multiplying the amount of stocks in the watchlist by the average seconds per stock (5 seconds)
        expected_time_in_minutes = (len(scraped_data)*5)/60

        #Print the expected time in minutes for this process
        print("This process is expected to take "+str(int(expected_time_in_minutes))+"-"+str(int(expected_time_in_minutes+1))+" minutes.")

        #This for loop iterates through each of the stock tickers in the watchlist, calculates its historical indicator and statistical data, and stores it in "stock_statistics_historical"
        for scraped_stock in scraped_data :

            #Print message that this current stock is about to be scraped
            print(scraped_stock[0], " is being scraped...")

            #Record the time just before "calculate_historical_data" is called for this stock
            scrape_start = time.time()

            #Call "calculate_historical_data" and record into "self.indicator_historical" for this stock
            self.indicator_historical[scraped_stock[0]], self.stock_statistics_historical[scraped_stock[0]] = calculate_historical_data(scraped_stock[0], self.indicator_data_points_needed, self.indicator_inputs_required, self.yahoo_statistics_required)

            #Print the amount of time it took for "calculate_historical_data" to finish
            print("Completed in ", time.time()-scrape_start)
            print()

        #The "intervals_executed" integer will record the number of main loop iterations are completed.
        intervals_executed = 0
       
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

                #Call the "update_stock_statistics" function to update the "stock_statistics" dictionary for this stock
                self.update_stock_statistics()
               
                #This for loop iterates through each strategy permuation and tracks their performance
                for strategy_index, strategy in enumerate(self.strategies) :

                    #If this stock is currently held by this strategy permutation
                    if self.ticker in self.strategies_performance_tracking[strategy_index][0] :

                        #The "bought_or_sold_at_entrance" boolean indicates whether the user bought or sold the stock when they entered the trade
                        bought_or_sold_at_entrance = self.strategies_performance_tracking[strategy_index][0][self.ticker][1]

                        #If this strategy permutation decided to exit the trade                        
                        if strategy[2](self.indicators, self.strategies_performance_tracking[strategy_index][0][self.ticker][0], bought_or_sold_at_entrance) :

                            #Execute the "exit_trade" function to exit the trade for this stock.
                            self.exit_trade(strategy_index)
                           
                            #Print message for this entrance
                            print("Strategy \""+strategy[-1]+"\" has exited "+self.ticker)

                            #If the trade is a buy exit and this is the selected deployed strategy
                            if strategy[3] == self.deployed_strategy_name and bought_or_sold_at_entrance :

                                #Call the "order_buy_fractional_by_price" function to execute the trade on Robinhood
                                r.orders.order_sell_fractional_by_price(self.ticker, self.robinhood_investment_amount, timeInForce='gfd', extendedHours=False)

                    #If this stock is not currently held by this strategy permutation
                    else :

                        #If this stock has not already been bought or sold
                        if not any(self.ticker in completed_trade for completed_trade in self.strategies_performance_tracking[strategy_index][1]) :

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

                                    #Print message for this entrance
                                    print("Strategy \""+strategy[-1]+"\" has "+["Sold", "Bought"][entrance_result]+" "+self.ticker)

                                    #If the trade is a buy entrance and this is the selected deployed strategy
                                    if strategy[3] == self.deployed_strategy_name and entrance_result :

                                        #Call the "order_buy_fractional_by_price" function to execute the trade on Robinhood
                                        r.orders.order_buy_fractional_by_price(self.ticker, self.robinhood_investment_amount, timeInForce='gfd', extendedHours=False)

            #Record how long this iteration of the main scraping loop took
            print("Completed in ", time.time()-start, "["+str(intervals_executed)+"]")

            #Add one to the "intervals_executed" integer.
            intervals_executed += 1

        #Exit all trades
        scraped_data = self.scrape_live_data()

        #Iterate through each stock currently held
        for scraped_stock in scraped_data :

            #Unpack ticker, price, and volume
            self.ticker, self.price, self.volume = scraped_stock

            #Iterate through each strategy
            for strategy_index in range(len(self.strategies)) :

                #If the stock is in this strategy, call the "exit_trade" function to exit the trade for this stock for this strategy.
                if self.ticker in self.strategies_performance_tracking[strategy_index][0] :
                    self.exit_trade(strategy_index)

        #Record Excel Sheet Data
        record_performance_data(excel_sheet_path, self.strategies_performance_tracking)
