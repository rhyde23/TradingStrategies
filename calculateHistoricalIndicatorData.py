#Calculate Initial Indicators

import yfinance as yf

historical_dictionary = []
hist_data = None
day_on = 0
loading_index = 1

def avg_change_formula(current_change, period_length, new_difference) :
    return ((current_change*(period_length-1))+new_difference)/period_length

def ema_formula(recent_value, period_length, current_ema) :
    exp_percentage = 2/(period_length+1)
    return (recent_value*exp_percentage)+(current_ema*(1-exp_percentage))

def rsi_formula(average_gain, average_loss) :
    return 100-(100/(1+(average_gain/average_loss)))

def calculate_historical_rsi_data(inputs_required, data_points_needed) :
    global historical_dictionary, loading_index
    difference = hist_data.iloc[day_on]["Close"]-hist_data.iloc[day_on-1]["Close"]
    
    for period in inputs_required :
        if day_on < period :
            if difference >= 0 :
                historical_dictionary[loading_index] += difference

            else :
                historical_dictionary[loading_index+1] += -difference

        else :

            if day_on == period :
                historical_dictionary[loading_index] = historical_dictionary[loading_index]/period
                historical_dictionary[loading_index+1] = historical_dictionary[loading_index+1]/period

            if difference >= 0 :
                historical_dictionary[loading_index] = avg_change_formula(historical_dictionary[loading_index], period, difference)
                historical_dictionary[loading_index+1] = avg_change_formula(historical_dictionary[loading_index+1], period, 0)

            else :
                historical_dictionary[loading_index] = avg_change_formula(historical_dictionary[loading_index], period, 0)
                historical_dictionary[loading_index+1] = avg_change_formula(historical_dictionary[loading_index+1], period, -difference)
                
        loading_index += data_points_needed

def calculate_historical_ema_data(inputs_required, data_points_needed) :
    global historical_dictionary, loading_index
    recent_close = hist_data.iloc[day_on]["Close"]
    for period in inputs_required :
    
        historical_dictionary[loading_index] = ema_formula(recent_close, period, historical_dictionary[loading_index])
        
        loading_index += data_points_needed

def calculate_historical_macd_data(inputs_required, data_points_needed) :
    global historical_dictionary, loading_index
    recent_close = hist_data.iloc[day_on]["Close"]
    for combination in inputs_required :
        historical_dictionary[loading_index] = ema_formula(recent_close, combination[0], historical_dictionary[loading_index])
        historical_dictionary[loading_index+1] = ema_formula(recent_close, combination[1], historical_dictionary[loading_index+1])
        macd = historical_dictionary[loading_index]-historical_dictionary[loading_index+1]
        historical_dictionary[loading_index+2] = ema_formula(macd, combination[2], historical_dictionary[loading_index+2])

        loading_index += data_points_needed

        
def calculate_historical_data(ticker, indicator_data_points_needed, indicator_inputs_required, stock_statistics_required) :
    global historical_dictionary, hist_data, day_on, loading_index
    historical_period_length = 5
    yfinance_ticker = yf.Ticker(ticker)
    while True :
        try :
            hist_data = yfinance_ticker.history(period=str(historical_period_length)+"y")
            break
        except :
            pass
        
    day_on = 0
    
    data_points_needed = sum([indicator_data_points_needed[key]*len(indicator_inputs_required[key]) for key in indicator_data_points_needed])+1
    historical_dictionary = [0]*data_points_needed
    historical_dictionary[0] = hist_data.iloc[-2]["Close"]
    
    while day_on < len(hist_data)-1 :
        loading_index = 1
        calculate_historical_rsi_data(indicator_inputs_required["RSI"], indicator_data_points_needed["RSI"])
        calculate_historical_ema_data(indicator_inputs_required["EMA"], indicator_data_points_needed["EMA"])
        calculate_historical_macd_data(indicator_inputs_required["MACD"], indicator_data_points_needed["MACD"])
        day_on += 1

    return tuple([round(value, 5) for value in historical_dictionary]), {statistic_required:yfinance_ticker.info[statistic_required] for statistic_required in stock_statistics_required}


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
