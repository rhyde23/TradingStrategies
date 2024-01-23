import requests, subprocess, sys, time
from datetime import datetime
from pytz import timezone
import yfinance as yf

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
    "RSI":[9, 14],
    "EMA":[9, 20, 21, 50],
    "MACD":[(12, 26, 29),(5, 35, 5)]
}

indicator_outputs = {indicator_name:{} for indicator_name in indicator_inputs_required}

indicator_historical = {}

ticker = ""
price = 0

historical_period_length = 1000
hist_data = None
day_on = 0

#Indicator Functionality

def calculate_historical_rsi_data() :
    
    difference = hist_data.iloc[day_on]["Close"]-hist_data.iloc[day_on-1]["Close"]
    
    for period_index, period in enumerate(indicator_inputs_required["RSI"]) :
        if day_on < period :

            #If the difference is a gain, add it to the average gain for this RSI period
            if difference >= 0 :
                indicator_historical[ticker][1] += difference

            #If the difference is a loss, add it to the average loss for this RSI period
            else :
                indicator_historical[ticker][2] += -difference

        #If the number of days iterated so far in the Main loop HAS reached the RSI period, begin smoothing effect
        else :

            #If the number of days iterated so far in the Main loop is exacly equal to the RSI period, calculate initial RSI value before smoothing by dividing the total sums so far by the RSI period in days
            if day_on == period :
                indicator_historical[ticker][1] = indicator_historical[ticker][1]/period
                indicator_historical[ticker][2] = indicator_historical[ticker][2]/period

            #If the difference is a gain, smooth average gain and average loss using the difference for the average gain and 0 for the average loss
            if difference >= 0 :
                indicator_historical[ticker][1] = ((indicator_historical[ticker][1]*(period-1))+difference)/period
                indicator_historical[ticker][2] = ((indicator_historical[ticker][2]*(period-1))+difference)/period 

            #If the difference is a loss, smooth average gain and average loss using the difference for the average loss and 0 for the average gain
            else :
                indicator_historical[ticker][1] = ((indicator_historical[ticker][1]*(period-1))+difference)/period
                indicator_historical[ticker][2] = ((indicator_historical[ticker][2]*(period-1))+difference)/period

def calculate_historical_indicators() :
    global indicator_historical, hist_data, day_on
    hist_data = yf.Ticker(ticker).history(period=str(historical_period_length)+"D")

    #list = [last_price, avg_gains, avg_losses]
    indicator_historical[ticker] = [0]*3
    indicator_historical[ticker][0] = hist_data[-2]
    
    while day_on < len(hist_data)-1 :
        calculate_historical_rsi_data()
        day_on += 1
        

def update_indicator_outputs() :
    
    difference = price-indicator_historical[ticker][0]
    
    for period_index, period in enumerate(indicator_inputs_required["RSI"]) :
        if difference >= 0 :
            indicator_outputs["RSI"][period] = ((indicator_historical[ticker][1]*(period-1))+difference)/period
            indicator_outputs["RSI"][2] = ((indicator_historical[ticker][1]*(period-1))+difference)/period 
        else :
            indicator_outputs["RSI"][1] = ((indicator_historical[ticker][0]*(period-1))+difference)/period
            indicator_outputs["RSI"][2] = ((indicator_historical[ticker][1]*(period-1))+difference)/period
                                          
#selection1()
