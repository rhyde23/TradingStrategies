#Calculate Historical Data

#Imported Libraries

import yfinance as yf
import math 
#@ranaroussi's yfinance library - For accessing historical stock data like closing prices and stock statistics like Market Cap, Average Volume, etc.

#The "historical_list" list will store all of the numbers that I will need to calculate all of the required indicators after an updated live price of a stock is scraped. 
historical_list = []

#The "hist_data" variable will store the data from yfinance's .history() function, which accesses a stock's price history.
hist_data = None

#The "day_on" integer is the current index of interest within yfinance's historical closing price data for a stock. It will be set to 1 right now, which is the second oldest day.
day_on = 1

#"The loading_index" integer is the current index of the values I will populate within the "historical_list" list. It will start at 1 instead of 0 because the first value will be...
#reserved for yesterday's closing price, regardless of what technical indicator settings are required.
loading_index = 1

#The "avg_change_formula" function returns the "smoothed" update of an average change given the current average change, the period of length in days, and the new change.
def avg_change_formula(current_change, period_length, new_difference) :
    return ((current_change*(period_length-1))+new_difference)/period_length

#The "ema_formula" function returns the update of an EMA value given the current EMA, the period of length in days, and the most recent value to consider.
#This function works for Price EMAs as well as EMAs for anything, like a MACD EMA for MACD breakline calculation.
def ema_formula(recent_value, period_length, current_ema) :
    exp_percentage = 2/(period_length+1)
    return (recent_value*exp_percentage)+(current_ema*(1-exp_percentage))

#The "rsi_formula" function returns the final RSI value calculation given the average gain and average loss of closing prices from the same period.
def rsi_formula(average_gain, average_loss) :
    return 100-(100/(1+(average_gain/average_loss)))

#The "calculate_historical_rsi_data" function updates the "historical_list" list for each RSI period setting given the next closing price difference.
#Every time the integer index "day_on" increments by 1, this function will have to execute to update all of the values for RSI calculation within "historical_list"
def calculate_historical_rsi_data(inputs_required, data_points_needed) :

    #Declare that this function will be referencing/changing the global variables "historical_list" and "loading_index"
    global historical_list, loading_index

    #The "difference" float is the difference in closing price between the current day of interest within this stock's historical data and the previous day.
    difference = hist_data.iloc[day_on]["Close"]-hist_data.iloc[day_on-1]["Close"]
    if math.isnan(difference) :
        return None

    #This for loop iterates through every RSI input that is required to calculate.
    for period in inputs_required :

        #If there have not been enough days iterated through to calculate an initial average change, just keep adding to the gain and loss sums before "day_on" is equal to "period".
        if day_on < period :

            #If the change is positive...
            if difference >= 0 :

                #Add the change to the gain sum
                historical_list[loading_index] += difference
            
            #If the change is negative...
            else :

                #Add the change to the loss sum
                historical_list[loading_index+1] += -difference
        
        #If there have been enough days iterated through to calculate average change...
        else :

            #If the number of days iterated through thus far is exactly equal to the period length...
            if day_on == period :

                #Calculate the initial average gain by dividing the gain sum by the period length.
                historical_list[loading_index] = historical_list[loading_index]/period

                #Calculate the initial average loss by dividing the loss sum by the period length.
                historical_list[loading_index+1] = historical_list[loading_index+1]/period

            #If the change is positive...
            if difference >= 0 :

                #Use the "avg_change_formula" function to get the "smoothed" update of the average gain for this period given the new positive change in closing price.
                historical_list[loading_index] = avg_change_formula(historical_list[loading_index], period, difference)

                #Use the "avg_change_formula" function to get the "smoothed" update of the average loss for this period by inputting 0 as the new change in closing price since it is positive.
                historical_list[loading_index+1] = avg_change_formula(historical_list[loading_index+1], period, 0)

            #If the change is negative...
            else :

                #Use the "avg_change_formula" function to get the "smoothed" update of the average gain for this period by inputting 0 as the new change in closing price since it is negative.
                historical_list[loading_index] = avg_change_formula(historical_list[loading_index], period, 0)

                #Use the "avg_change_formula" function to get the "smoothed" update of the average loss for this period given the new negative change in closing price.
                historical_list[loading_index+1] = avg_change_formula(historical_list[loading_index+1], period, -difference)

        #Increase the "loading_index" integer by however many data points were updated by this function.
        loading_index += data_points_needed

#The "calculate_historical_ema_data" function updates the "historical_list" list for each EMA period setting given the next closing price.
#Every time the integer index "day_on" increments by 1, this function will have to execute to update all of the values for EMA calculation within "historical_list"
def calculate_historical_ema_data(inputs_required, data_points_needed) :

    #Declare that this function will be referencing/changing the global variables "historical_list" and "loading_index"
    global historical_list, loading_index

    #The "recent_close" float is the closing price of the current day of interest within this stock's historical data
    recent_close = hist_data.iloc[day_on]["Close"]

    #This loop iterates through each required EMA period length setting
    for period in inputs_required :

        #Use the "ema_formula" function to update the EMA value for this period given the recent closing price.
        historical_list[loading_index] = ema_formula(recent_close, period, historical_list[loading_index])

        #Increase the "loading_index" integer by however many data points were updated by this function.
        loading_index += data_points_needed

#The "calculate_historical_macd_data" function updates the "historical_list" list for each MACD combination setting given the next closing price.
#Every time the integer index "day_on" increments by 1, this function will have to execute to update all of the values for MACD calculation within "historical_list"
def calculate_historical_macd_data(inputs_required, data_points_needed) :

    #Declare that this function will be referencing/changing the global variables "historical_list" and "loading_index"
    global historical_list, loading_index

    #The "recent_close" float is the closing price of the current day of interest within this stock's historical data
    recent_close = hist_data.iloc[day_on]["Close"]

    #This loop iterates through each required MACD combination setting
    for combination in inputs_required :

        #Use the "ema_formula" function to update the Fast EMA value for this period given the recent closing price.
        historical_list[loading_index] = ema_formula(recent_close, combination[0], historical_list[loading_index])

        #Use the "ema_formula" function to update the Slow EMA value for this period given the recent closing price.
        historical_list[loading_index+1] = ema_formula(recent_close, combination[1], historical_list[loading_index+1])

        #Subtract the updated Slow EMA value from the updated Fast EMA value to get the updated MACD value for this period
        macd = historical_list[loading_index]-historical_list[loading_index+1]

        #Use the "ema_formula" function to update the MACD EMA value for this period given the recent MACD value update.
        historical_list[loading_index+2] = ema_formula(macd, combination[2], historical_list[loading_index+2])

        #Increase the "loading_index" integer by however many data points were updated by this function.
        loading_index += data_points_needed

#The "calculate_historical_data" function calculates all of the required historical data needed to efficiently update live indicator values and stock statistics.
def calculate_historical_data(ticker, indicator_data_points_needed, indicator_inputs_required, yahoo_statistics_required) :

    #Declare that this function will be referencing/changing the global variables "historical_list", "hist_data", "day_on", and "loading_index"
    global historical_list, hist_data, day_on, loading_index

    #The "historical_period_length" integer is the amount of years in the past that will be considered for historical data.
    historical_period_length = 5

    #The "yfinance_ticker" variable is the loaded object from yfinance for this stock
    yfinance_ticker = yf.Ticker(ticker)

    #This loop will load the historical data from yfinance for this stock
    while True :
        try :

            #The "hist_data" variable will be updated as a pandas dataframe containing all of the necessary closing prices for indicator calculations           
            hist_data = yfinance_ticker.history(period=str(historical_period_length)+"y")
            break
        
        except :
            print(ticker, "is not being loaded by yfinance") 

    #The "day_on" index is set to 1, or the second oldest day of the historical data because the change in price calculation for RSI calculations is defined as the current day close...
    #minus the previous day close
    day_on = 1

    #The "total_data_points_needed" integer is the sum of each indicator's required amount of data points that will be stored within the final product of historical data.
    total_data_points_needed = sum([indicator_data_points_needed[key]*len(indicator_inputs_required[key]) for key in indicator_data_points_needed if key in indicator_inputs_required])+1

    #The "historical_list" list will be the final product of historical data
    historical_list = [0]*total_data_points_needed

    #Set the first value of the "historical_list" to yesterday's closing price.
    #This will be necessary for RSI calculations as the live RSI update will be dependant on the live price - yesterday's closing price.
    historical_list[0] = hist_data.iloc[-2]["Close"]

    #This loop will iterate through every index of every day within the stock's historical data
    while day_on < len(hist_data)-1 :

        #Reset the "loading_index" index to 1. (the first value in the "historical_list" was set to yesterday's closing price)
        loading_index = 1

        #Execute the "calculate_historical_rsi_data" function to update the current calculation of each RSI value for each period setting.
        if "RSI" in indicator_inputs_required :
            calculate_historical_rsi_data(indicator_inputs_required["RSI"], indicator_data_points_needed["RSI"])

        #Execute the "calculate_historical_ema_data" function to update the current calculation of each EMA value for each period setting.
        if "EMA" in indicator_inputs_required :
            calculate_historical_ema_data(indicator_inputs_required["EMA"], indicator_data_points_needed["EMA"])

        #Execute the "calculate_historical_macd_data" function to update the current calculation of each MACD value for each combination setting.
        if "MACD" in indicator_inputs_required :
            calculate_historical_macd_data(indicator_inputs_required["MACD"], indicator_data_points_needed["MACD"])

        #Increment the "day_on" index by 1.
        day_on += 1

    #Round all the values in the "historical_list" to the 5th decimal place and return its tuple version and return every historical stock statistic required.
    return tuple([round(value, 5) for value in historical_list]), {statistic_required:yfinance_ticker.info[statistic_required] for statistic_required in yahoo_statistics_required}


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

#res = calculate_historical_data("GOOGL", indicator_data_points_needed, indicator_inputs_required, ["marketCap", "averageVolume"])[0]
