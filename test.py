#Example for using the Trading Strategies class
from TradingStrategies import TradingStrategies

#Selection strategy that filters out stocks with a market cap of less than 2 Billion and a price of less than $20 dollars per share.
def selection_one(stats) :
    return stats["MARKET_CAP"] > 2000000000 and stats["PRICE"] > 20

#Entrance Strategy geared towards standard settings for MACD, BBands, RSI, etc.
def midterm_entrance(inds) :

    #Get the live MACD setting of (12, 26, 9) <-- (fast EMA line, slow EMA line, MACD EMA)
    macd_tuple = inds["MACD"][(12, 26, 9)]

    #Get the live BBands setting of (20, 2)  <-- (SMA, standard deviations)
    bbands_tuple = inds["BBands"][(20, 2)]

    #If the following are true, buy the stock:
    #1. The price is below the lower Bollinger Band.
    #2. The Relative Strength Index (period=14) is less than or equal to 40.
    #3. The 20-day Exponential Moving Average is greater than the 50-day Exponential Moving Average.
    #4. The difference between the fast EMA and the slow EMA is greater than the MACD EMA
    #5. The 20-day Simple Moving Average is greater than the 50-day Simple Moving Average.
    if inds["PRICE"] <= bbands_tuple[0] and inds["RSI"][14] <= 40 and inds["EMA"][20] > inds["EMA"][50] and macd_tuple[0] > macd_tuple[1] and inds["SMA"][20] > inds["SMA"][50] :
        return True

    #If the following are true, short-sell the stock:
    #1. The price is above the upper Bollinger Band.
    #2. The Relative Strength Index (period=14) is greater than or equal to 60.
    #3. The 20-day Exponential Moving Average is less than the 50-day Exponential Moving Average.
    #4. The difference between the fast EMA and the slow EMA is less than the MACD EMA
    #5. The 20-day Simple Moving Average is less than the 50-day Simple Moving Average.
    if inds["PRICE"] >= bbands_tuple[2] and inds["RSI"][14] >= 60 and inds["EMA"][20] < inds["EMA"][50] and macd_tuple[1] > macd_tuple[0] and inds["SMA"][20] < inds["SMA"][50] :
        return False

#Entrance Strategy geared towards shorter-term settings for MACD, BBands, RSI, etc.
def shortterm_entrance(inds) :

    #Get the live MACD setting of (5, 35, 5) <-- (fast EMA line, slow EMA line, MACD EMA)
    macd_tuple = inds["MACD"][(5, 35, 5)]

    #Get the live BBands setting of (10, 2)  <-- (SMA, standard deviations)
    bbands_tuple = inds["BBands"][(10, 2)]

    #If the following are true, buy the stock:
    #1. The price is below the lower Bollinger Band.
    #2. The Relative Strength Index (period=9) is less than or equal to 40.
    #3. The 10-day Exponential Moving Average is greater than the 20-day Exponential Moving Average.
    #4. The difference between the fast EMA and the slow EMA is greater than the MACD EMA
    #5. The 10-day Simple Moving Average is greater than the 20-day Simple Moving Average.
    if inds["PRICE"] <= bbands_tuple[0] and inds["RSI"][9] <= 40 and inds["EMA"][10] > inds["EMA"][20] and macd_tuple[0] > macd_tuple[1] and inds["SMA"][10] > inds["SMA"][20] :
        return True

    #If the following are true, short-sell the stock:
    #1. The price is above the upper Bollinger Band.
    #2. The Relative Strength Index (period=9) is greater than or equal to 60.
    #3. The 10-day Exponential Moving Average is less than the 20-day Exponential Moving Average.
    #4. The difference between the fast EMA and the slow EMA is less than the MACD EMA
    #5. The 10-day Simple Moving Average is less than the 20-day Simple Moving Average.
    if inds["PRICE"] >= bbands_tuple[2] and inds["RSI"][9] >= 60 and inds["EMA"][10] < inds["EMA"][20] and macd_tuple[1] > macd_tuple[0] and inds["SMA"][10] < inds["SMA"][20] :
        return False

#Exit Strategy based on simple stoploss. 
def one_percent_stoploss(inds, price_entered_at, bought_or_shorted) :
    percent_change = (inds["PRICE"]-price_entered_at)/price_entered_at
    if abs(percent_change) > 0.01 :
        return True
    return False

#"strategies" list that contains all of the different strategies I want to try. TradingStrategies can handle many strategies, not just two.
strategies = [
    [selection_one, midterm_entrance, one_percent_stoploss, "MidtermStrat"],
    [selection_one, shortterm_entrance, one_percent_stoploss, "ShorttermStrat"]
]

obj = TradingStrategies(strategies)

#Run TradingStrategies.run_strategies(testing_mode, excel_path)
obj.run_strategies(True, "C:/Users/regin/OneDrive/Desktop/TestBook.xlsx")
