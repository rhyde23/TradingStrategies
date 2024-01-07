#This script calculates the Relative Strength Index (RSI) based on a given stock ticker and time period in days
import getStockInfo
def calculate_rsi(ticker:str, period_in_days:int) :
    hist_data = getStockInfo.get_historical_data(ticker, str(period_in_days+1)+"D")
    print(hist_data["Close"])
    gain_sum, loss_sum = 0, 0
    for i in range(1, period_in_days+1) :
        difference = hist_data.iloc[i]["Close"]-hist_data.iloc[i-1]["Close"]
        if difference >= 0 :
            gain_sum += difference
        else :
            loss_sum += -difference
    avg_gain, avg_loss = gain_sum/period_in_days, loss_sum/period_in_days
    rs = avg_gain/avg_loss
    return 100-(100/(1+rs))

print(calculate_rsi("MSFT", 14))
