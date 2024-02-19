#Testing the Trading Strategies class
from TradingStrategies import TradingStrategies


def selection_test(stats) :
    return stats["MARKET_CAP"] > 1
        
def entrance_test(inds) :
    if inds["RSI"][14] <= 80 :
        return True
    if inds["RSI"][14] >= 80 :
        return False

def exit_test(inds, bought_or_shorted) :
    return True

strategies = [
    [selection_test, entrance_test, exit_test, "TestStrategy"]
]

obj = TradingStrategies(strategies)

obj.deploy_strategies(True)
