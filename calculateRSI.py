#This script calculates the Relative Strength Index (RSI) based on a given stock ticker and time period in days

#Import script that accesses Python library yfinance
import getStockInfo

#Function to calculate RSI
#Arguments are: desired stock ticker, the RSI period, and the number of historical days to achieve "smoothing effect"
def calculate_rsi(ticker:str, period_in_days:int, historical_context:int) :
    #Access stock's historical data from yahoo finance
    hist_data = getStockInfo.get_historical_data(ticker, str(historical_context)+"D")

    #This first loop calculates initial RSI value in the past before smoothing
    gain_sum, loss_sum = 0, 0
    for i in range(1, period_in_days+1) :
        difference = hist_data.iloc[i]["Close"]-hist_data.iloc[i-1]["Close"]
        if difference >= 0 :
            gain_sum += difference
        else :
            loss_sum += -difference
    avg_gain, avg_loss = gain_sum/period_in_days, loss_sum/period_in_days #Non-smoothed RSI in the distant past

    #This loop smooths the RSI until we reach the current date
    for x in range(period_in_days+1, historical_context) :
        difference = hist_data.iloc[x]["Close"]-hist_data.iloc[x-1]["Close"]
        if difference >= 0 :
            avg_gain = ((avg_gain*(period_in_days-1))+difference)/period_in_days
            avg_loss = (avg_loss*(period_in_days-1))/period_in_days
        else :
            avg_gain = (avg_gain*(period_in_days-1))/period_in_days
            avg_loss = ((avg_loss*(period_in_days-1))-difference)/period_in_days
    #Finally, we calculate the relative strength value and then return the RSI in terms of a value 0-100
    rs = (avg_gain/avg_loss)
    return 100-(100/(1+rs))

print(calculate_rsi("CRM", 5, 1000))

