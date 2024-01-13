#This script calculates the variety of indicators used for entrance/exit strategies

import yfinance as yf


#This is the global variable that stores the historical data of a stock from yfinance
hist_data = None



def update_rsi(current_avg:float, period:int, difference:float) :
    return ((current_avg*(period-1))+difference)/period

#Function to calculate Relative Strength Index. Input = periods for RSI calculation in days 
def calculate_rsi(periods:list) :
    #This first loop calculates initial RSI value in the past before smoothing

    avg_gains, avg_losses = [0 for c in range(len(periods))], [0 for c in range(len(periods))]
    for i in range(1, len(hist_data)) :
        difference = hist_data.iloc[i]["Close"]-hist_data.iloc[i-1]["Close"]
        for x in range(len(periods)) :
            if i < periods[x] :
                if difference >= 0 :
                    avg_gains[x] += difference
                else :
                    avg_losses[x] += -difference
            else :
                if i == periods[x] :
                    avg_gains[x] = avg_gains[x]/periods[x]
                    avg_losses[x] = avg_losses[x]/periods[x]
                if difference >= 0 :
                    avg_gains[x] = update_rsi(avg_gains[x], periods[x], difference)
                    avg_losses[x] = update_rsi(avg_losses[x], periods[x], 0)
                else :
                    avg_gains[x] = update_rsi(avg_gains[x], periods[x], 0)
                    avg_losses[x] = update_rsi(avg_losses[x], periods[x], -difference)
    return [100-(100/(1+(avg_gains[ind]/avg_losses[ind]))) for ind in range(len(periods))]


    """
    for i in range(1, period+1) :
        difference = hist_data.iloc[i]["Close"]-hist_data.iloc[i-1]["Close"]
        if difference >= 0 :
            gain_sum += difference
        else :
            loss_sum += -difference

    avg_gains, avg_losses = [], []
    for period in periods : #Non-smoothed RSIs in the distant past
        avg_gains.append(gain_sum/period)
        avg_losses.append(loss_sum/period)

    #This loop smooths the RSIs until we reach the current date
    for x in range(period+1, len(hist_data)) :
        difference = hist_data.iloc[x]["Close"]-hist_data.iloc[x-1]["Close"]
        if difference >= 0 :
            for index in range(len(avg_gains)) :
                avg_gains[index] = ((avg_gains[index]*(period-1))+difference)/period
                avg_losses[index] = (avg_losses[index]*(period-1))/period
        else :
            avg_gain = (avg_gain*(period-1))/period
            avg_loss = ((avg_loss*(period-1))-difference)/period
    #Finally, we calculate the relative strength value and then return the RSI in terms of a value 0-100
    rs = (avg_gain/avg_loss)
    return 100-(100/(1+rs))
    """

#Function to update any EMA given a recent close value. Input = the current EMA, the given exponential percentage, and the recent close value
def update_ema(current_ema:float, exp_percentage:float, recent_close:float) :
    return (recent_close*exp_percentage)+(current_ema*(1-exp_percentage))


def calculate_ema(periods:list) :
    exponential_percentages = [2/(period+1) for period in periods]
    emas = [hist_data.iloc[0]["Close"] for i in range(len(periods))]
    for i in range(1, len(hist_data)) :
        recent_close = hist_data.iloc[i]["Close"]
        for x in range(len(periods)) :
            emas[x] = update_ema(emas[x], exponential_percentages[x], recent_close)
    return emas



#Function to calculate Exponential Moving Average, Moving Average Convergence/Divergence, and Moving Average Convergence/Divergence EMA.
#Input = period for fast EMA calculation in days, period for slow EMA calculation in days, and period for MACD EMA calculation in days
def calculate_macd(fast_periods:list, slow_periods:list, macd_periods:list) :
    #Calculate exponential percentages
    #for i in range
    #fast_exponential_percentages = [2/(fast_period+1) for fast_period in fast_periods]
    #slow_exponential_percentages = [2/(slow_period+1) for slow_period in slow_periods]
    #macd_exponential_percentages = [2/(macd_period+1) for macd_period in macd_periods]

    #Set all variables at default
    
    fast_ema = update_ema(0, 1, hist_data.iloc[0]["Close"])
    slow_ema = update_ema(0, 1, hist_data.iloc[0]["Close"])
    macd, macd_ema = None, None

    #Loop to update fast_ema, slow_ema, macd, and macd_ema
    for i in range(1, len(hist_data)) :
        fast_ema = update_ema(fast_ema, fast_exponential_percentage, hist_data.iloc[i]["Close"])
        slow_ema = update_ema(slow_ema, slow_exponential_percentage, hist_data.iloc[i]["Close"])
        if i == len(hist_data)-(macd_period+1) :
            macd = fast_ema-slow_ema
            macd_ema = update_ema(0, 1, macd)
        if i > len(hist_data)-(macd_period+1) :
            macd = fast_ema-slow_ema
            macd_ema = update_ema(macd_ema, macd_exponential_percentage, macd)
    #Return values
    return fast_ema, slow_ema, macd, macd_ema

#Main function that will return actual interpretations based on given technical indicators and parameters
def calculate_indicators(ticker:str) :
    #Access stock's historical data from yahoo finance
    global hist_data
    hist_data = yf.Ticker(ticker).history(period="1000D")

    #Test runs for right now
    print(calculate_rsi([5, 9, 14]))
    #print(calculate_ema_and_macd(12, 26, 9))
    #print(calculate_ema_and_macd(20, 50, 9))
    print(calculate_ema([10, 20, 50, 100, 200]))


calculate_indicators("MSFT")

