#Calculate Historical Data

#Imported Libraries

import yfinance as yf
#@ranaroussi's yfinance library - For accessing historical stock data like closing prices and stock statistics like Market Cap, Average Volume, etc.

#The "historical_list" list will store all of the numbers that I will need to calculate all of the required indicators after an updated live price of a stock is scraped. 
historical_list = []

#The "hist_data" variable will store the data from yfinance's .history() function, which accesses a stock's price history.
hist_data = None

#The "day_on" integer is the current index of interest within yfinance's historical closing price data for a stock. It will be set to 1 right now, which is the second/second oldest day.
day_on = 1

#"The loading_index" integer is the current index of the values I will populate within the "historical_list" list. It will start at 1 instead of 0 because the first value will be...
#reserved for yesterday's closing price, regardless of what technical indicator settings are required.
loading_index = 1

#The "avg_change_formula" function returns the update of an average change given the current average change, the period of length in days, and the new change.
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

    #The "difference" float is the difference in closing price between the current day and the previous day.
    difference = hist_data.iloc[day_on]["Close"]-hist_data.iloc[day_on-1]["Close"]

    #This for loop iterates through every RSI input that is required to calculate.
    for period in inputs_required :

        #If there have not been enough 
        if day_on < period :
            if difference >= 0 :
                historical_list[loading_index] += difference

            else :
                historical_list[loading_index+1] += -difference

        else :

            if day_on == period :
                historical_list[loading_index] = historical_list[loading_index]/period
                historical_list[loading_index+1] = historical_list[loading_index+1]/period

            if difference >= 0 :
                historical_list[loading_index] = avg_change_formula(historical_list[loading_index], period, difference)
                historical_list[loading_index+1] = avg_change_formula(historical_list[loading_index+1], period, 0)

            else :
                historical_list[loading_index] = avg_change_formula(historical_list[loading_index], period, 0)
                historical_list[loading_index+1] = avg_change_formula(historical_list[loading_index+1], period, -difference)
                
        loading_index += data_points_needed

#The "calculate_historical_ema_data" function updates the "historical_list" list for each EMA period setting given the next closing price.
#Every time the integer index "day_on" increments by 1, this function will have to execute to update all of the values for EMA calculation within "historical_list"
def calculate_historical_ema_data(inputs_required, data_points_needed) :

    #Declare that this function will be referencing/changing the global variables "historical_list" and "loading_index"
    global historical_list, loading_index
    recent_close = hist_data.iloc[day_on]["Close"]
    for period in inputs_required :
    
        historical_list[loading_index] = ema_formula(recent_close, period, historical_list[loading_index])
        
        loading_index += data_points_needed

#The "calculate_historical_macd_data" function updates the "historical_list" list for each MACD combination setting given the next closing price.
#Every time the integer index "day_on" increments by 1, this function will have to execute to update all of the values for MACD calculation within "historical_list"
def calculate_historical_macd_data(inputs_required, data_points_needed) :

    #Declare that this function will be referencing/changing the global variables "historical_list" and "loading_index"
    global historical_list, loading_index
    recent_close = hist_data.iloc[day_on]["Close"]
    for combination in inputs_required :
        historical_list[loading_index] = ema_formula(recent_close, combination[0], historical_list[loading_index])
        historical_list[loading_index+1] = ema_formula(recent_close, combination[1], historical_list[loading_index+1])
        macd = historical_list[loading_index]-historical_list[loading_index+1]
        historical_list[loading_index+2] = ema_formula(macd, combination[2], historical_list[loading_index+2])

        loading_index += data_points_needed

        
def calculate_historical_data(ticker, indicator_data_points_needed, indicator_inputs_required, yahoo_statistics_required) :
    global historical_list, hist_data, day_on, loading_index
    historical_period_length = 5
    yfinance_ticker = yf.Ticker(ticker)
    while True :
        try :
            hist_data = yfinance_ticker.history(period=str(historical_period_length)+"y")
            break
        except :
            pass
        
    day_on = 1
    
    data_points_needed = sum([indicator_data_points_needed[key]*len(indicator_inputs_required[key]) for key in indicator_data_points_needed])+1
    historical_list = [0]*data_points_needed
    historical_list[0] = hist_data.iloc[-2]["Close"]
    
    while day_on < len(hist_data)-1 :
        loading_index = 1
        calculate_historical_rsi_data(indicator_inputs_required["RSI"], indicator_data_points_needed["RSI"])
        calculate_historical_ema_data(indicator_inputs_required["EMA"], indicator_data_points_needed["EMA"])
        calculate_historical_macd_data(indicator_inputs_required["MACD"], indicator_data_points_needed["MACD"])
        day_on += 1

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

#print(calculate_historical_data("MSFT", indicator_data_points_needed, indicator_inputs_required, ["marketCap", "averageVolume"]))
