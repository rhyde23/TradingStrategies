#This script calculates the variety of indicators used for entrance/exit strategies

#Import the Python package yfinance. yfinance is an open source project that scrapes stock quotes and other stock data from Yahoo Finance
import yfinance as yf

#This is the global variable that stores the historical data of a stock from yfinance
hist_data = None

#Function to create the RSI "smoothing effect" based on the next closing price difference
#Input = the current average gain/loss, the RSI period in days, and the next closing price difference between a day and its previous day
def update_rsi(current_avg:float, period:int, difference:float) :
    return ((current_avg*(period-1))+difference)/period

#Function to calculate Relative Strength Indexes (RSI's)
#Input = periods for RSI calculation in days 
def calculate_rsi(periods:list) :
    
    #Set the default average gain and average loss values for each period to 0
    avg_gains, avg_losses = [0]*len(periods), [0]*len(periods)

    #Main loop that iterates through every day's closing stock price going back in history, ideally starts 1000 days ago
    for i in range(1, len(hist_data)) :
        
        #Calculate difference between the current day's closing price and the previous day's closing price
        difference = hist_data.iloc[i]["Close"]-hist_data.iloc[i-1]["Close"]

        #Loop that iterates through every RSI period of the function's input
        for x in range(len(periods)) :

            #If the number of days iterated so far in the Main loop hasn't reached the RSI period, keep adding the closing price difference until initial smoothing.
            if i < periods[x] :

                #If the difference is a gain, add it to the average gain for this RSI period
                if difference >= 0 :
                    avg_gains[x] += difference

                #If the difference is a loss, add it to the average loss for this RSI period
                else :
                    avg_losses[x] += -difference

            #If the number of days iterated so far in the Main loop HAS reached the RSI period, begin smoothing effect
            else :

                #If the number of days iterated so far in the Main loop is exacly equal to the RSI period, calculate initial RSI value before smoothing by dividing the total sums so far by the RSI period in days
                if i == periods[x] :
                    avg_gains[x] = avg_gains[x]/periods[x]
                    avg_losses[x] = avg_losses[x]/periods[x]

                #If the difference is a gain, smooth average gain and average loss using the difference for the average gain and 0 for the average loss
                if difference >= 0 :
                    avg_gains[x] = update_rsi(avg_gains[x], periods[x], difference)
                    avg_losses[x] = update_rsi(avg_losses[x], periods[x], 0)

                #If the difference is a loss, smooth average gain and average loss using the difference for the average loss and 0 for the average gain
                else :
                    avg_gains[x] = update_rsi(avg_gains[x], periods[x], 0)
                    avg_losses[x] = update_rsi(avg_losses[x], periods[x], -difference)

    #Return the RSI value for each RSI period input using the RSI formula
    return [100-(100/(1+(avg_gains[ind]/avg_losses[ind]))) for ind in range(len(periods))]

#Function to update any Exponential Moving Average (EMA) given a recent close value using the EMA formula
#Input = the current EMA, the exponential percentage, and the recent close value
def update_ema(current_ema:float, exp_percentage:float, recent_close:float) :
    return (recent_close*exp_percentage)+(current_ema*(1-exp_percentage))

#Function to calculate Exponential Moving Averages (EMAS's)
#Input = periods for EMA calculation in days 
def calculate_ema(periods:list) :

    #Calculate the exponential percentages for each input period using the exponential percentage formula
    exponential_percentages = [2/(period+1) for period in periods]

    #Set all the EMA's for each input period to the first available closing price from the yahoo finance data
    emas = [hist_data.iloc[0]["Close"]]*len(periods)

    #Main loop that iterates through every day's closing stock price going back in history, ideally starts 1000 days ago
    for i in range(1, len(hist_data)) :

        #Define this day's closing price
        recent_close = hist_data.iloc[i]["Close"]

        #Loop that iterates through every EMA period of the function's input
        for x in range(len(periods)) :

            #Update EMA for this period using the "update_ema" function
            emas[x] = update_ema(emas[x], exponential_percentages[x], recent_close)

    #Return every EMA value for each period
    return emas


#Function to calculate Moving Average Convergence/Divergences (MACD's) and their EMA's. 
#Input = MACD combinations in the form of the tuple: (Fast EMA period in days, Slow EMA Period in days, MACD EMA Period in days)
def calculate_macd(combinations:list) :
    
    #Set all MACD factors for each combination to an empty list
    fast_exponential_percentages, slow_exponential_percentages, macd_exponential_percentages, fast_emas, slow_emas, macds, macd_emas = [], [], [], [], [], [], []

    #Loop that iterates through every MACD combination and populates each empty list
    for combination in combinations :

        #Calculate the exponential percentage for the fast EMA period using the exponential percentage formula 
        fast_exponential_percentages.append(2/(combination[0]+1))

        #Calculate the exponential percentage for the slow EMA period using the exponential percentage formula 
        slow_exponential_percentages.append(2/(combination[1]+1))

        #Calculate the exponential percentage for the MACD EMA period using the exponential percentage formula
        macd_exponential_percentages.append(2/(combination[2]+1))

        #Set fast period EMA's and slow period EMA's to the default value of the first closing price from the yfinance closing price data 
        fast_emas.append(hist_data.iloc[0]["Close"])
        slow_emas.append(hist_data.iloc[0]["Close"])

        #Set MACD's and MACD's EMA's to a null value 
        macds.append(None)
        macd_emas.append(None)

    #Main loop that iterates through every day's closing stock price going back in history, ideally starts 1000 days ago
    for i in range(1, len(hist_data)) :

        #Loop that iterates through every MACD combination input
        for x in range(len(combinations)) :

            #Update fast EMA and slow EMA for this MACD combination using the "update_ema" function
            fast_emas[x] = update_ema(fast_emas[x], fast_exponential_percentages[x], hist_data.iloc[i]["Close"])
            slow_emas[x] = update_ema(slow_emas[x], slow_exponential_percentages[x], hist_data.iloc[i]["Close"])
            
            #If the number of days iterated so far in the Main loop is equal to this combination's MACD period, set its initial MACD value and its inital MACD EMA.
            if i == len(hist_data)-(combinations[x][2]+1) :
                macds[x] = fast_emas[x]-slow_emas[x]
                macd_emas[x] = macds[x]

            #If the number of days iterated so far in the Main loop is greater than this combination's MACD period, update its MACD value and its MACD EMA using the "update_ema" function
            elif i > len(hist_data)-(combinations[x][2]+1) :
                macds[x] = fast_emas[x]-slow_emas[x]
                macd_emas[x] = update_ema(macd_emas[x], macd_exponential_percentages[x], macds[x])
                
    #Return each MACD and MACD EMA for each MACD setting combination
    return list(zip(macds, macd_emas))

#Main function to return a stock's technical indicator values
#Input = pending
def calculate_indicators(ticker:str) :
    
    #Access stock's historical data from yahoo finance
    global hist_data
    hist_data = yf.Ticker(ticker).history(period="1000D")

    #Test runs for right now
    print(calculate_rsi([5, 9, 14]))
    print(calculate_ema([10, 20, 50, 100, 200]))
    print(calculate_macd([(12, 26, 9), (5, 35, 5), (19, 39, 9)]))


calculate_indicators("AAPL")

