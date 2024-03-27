#Testing the Trading Strategies class
from TradingStrategies import TradingStrategies


def selection_one(stats) :
    return stats["MARKET_CAP"] > 2000000000 and stats["PRICE"] > 20
        
def midterm_entrance(inds) :
    macd_tuple = inds["MACD"][(12, 26, 9)]
    if inds["RSI"][14] <= 30 and inds["EMA"][20] > inds["EMA"][50] and macd_tuple[0] > macd_tuple[1] and inds["SMA"][20] > inds["SMA"][50] :
        return True
    if inds["RSI"][14] >= 70 and inds["EMA"][20] < inds["EMA"][50] and macd_tuple[1] > macd_tuple[0] and inds["SMA"][20] < inds["SMA"][50] :
        return False

def shortterm_entrance(inds) :
    macd_tuple = inds["MACD"][(5, 35, 5)]
    if inds["RSI"][9] <= 30 and inds["EMA"][10] > inds["EMA"][20] and macd_tuple[0] > macd_tuple[1] and inds["SMA"][10] > inds["SMA"][20]:
        return True
    if inds["RSI"][9] >= 70 and inds["EMA"][10] < inds["EMA"][20] and macd_tuple[1] > macd_tuple[0] and inds["SMA"][10] < inds["SMA"][20] :
        return False

def one_percent_stoploss(inds, price_entered_at, bought_or_shorted) :
    percent_change = (inds["PRICE"]-price_entered_at)/price_entered_at
    if abs(percent_change) > 0.01 :
        return True
    return False

strategies = [
    [selection_one, midterm_entrance, one_percent_stoploss, "MidtermStrat"],
    [selection_one, shortterm_entrance, one_percent_stoploss, "ShorttermStrat"]
]

obj = TradingStrategies(strategies)

obj.deploy_strategies(False, "C:/Users/regin/OneDrive/Desktop/TestBook.xlsx")
