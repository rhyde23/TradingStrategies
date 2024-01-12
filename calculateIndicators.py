#This script calculates the variety of indicators used for entrance/exit strategies

import yfinance as yf


#This is the global variable that stores the historical data of a stock from yfinance
hist_data = None

#Function to calculate Relative Strength Index. Input = period for RSI calculation in days 
def calculate_rsi(period:int) :
    #This first loop calculates initial RSI value in the past before smoothing
    gain_sum, loss_sum = 0, 0
    for i in range(1, period+1) :
        difference = hist_data.iloc[i]["Close"]-hist_data.iloc[i-1]["Close"]
        if difference >= 0 :
            gain_sum += difference
        else :
            loss_sum += -difference
    avg_gain, avg_loss = gain_sum/period, loss_sum/period #Non-smoothed RSI in the distant past

    #This loop smooths the RSI until we reach the current date
    for x in range(period+1, len(hist_data)) :
        difference = hist_data.iloc[x]["Close"]-hist_data.iloc[x-1]["Close"]
        if difference >= 0 :
            avg_gain = ((avg_gain*(period-1))+difference)/period
            avg_loss = (avg_loss*(period-1))/period
        else :
            avg_gain = (avg_gain*(period-1))/period
            avg_loss = ((avg_loss*(period-1))-difference)/period
    #Finally, we calculate the relative strength value and then return the RSI in terms of a value 0-100
    rs = (avg_gain/avg_loss)
    return 100-(100/(1+rs))

#Function to calculate Exponential Moving Average. Input = period for EMA calculation in days
def calculate_ema(period:int) :
    #Calculate exponential percentage
    exponential_percentage = 2/(period+1)
    
    ema = hist_data.iloc[0]["Close"]
    for i in range(1, len(hist_data)) :
        ema = (hist_data.iloc[i]["Close"]*exponential_percentage)+(ema*(1-exponential_percentage))
    return ema

#Function to calculate Moving Average Convergence/Divergence. Input = fast EMA period in days, slow EMA period in days
def calculate_macd(fast_ema_period:int, slow_ema_period:int) :
    return calculate_ema(fast_ema_period)-calculate_ema(slow_ema_period)

#Main function that will return actual interpretations based on given technical indicators and parameters
def calculate_indicators(ticker) :
    #Access stock's historical data from yahoo finance
    global hist_data
    hist_data = yf.Ticker(ticker).history(period="1000D")

    #Test runs for right now
    print(calculate_rsi(14))
    print(calculate_ema(20))
    print(calculate_macd(12, 26))

calculate_indicators("MSFT")

