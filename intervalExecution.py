#This script will run every interval

import calculateIndicators, itertools, requests
from bs4 import BeautifulSoup 

#SELECTION STRATEGIES
#Selection strategy that extracts the list of 100 most traded stocks from tradingview.com and filters out stocks that don't meet the minimum relative volume of 1.5
def selection1() :
    
    #Processes url request for tradingview.com of the most active stocks of the day
    r = requests.get("https://www.tradingview.com/markets/stocks-usa/market-movers-active/")

    #Apply BeautifulSoup() to the website request
    soup = BeautifulSoup(r.content, 'html.parser')

    #Empty list that will be populated with stock tickers that meet the relative volume criteria
    accepted = []

    #Loop that iterates through each stock in the top 100 most traded stocks of the day from tradingview.com
    for stock in soup.find_all("tr", {"class":"row-RdUXZpkv listRow"}) :
        
        #Get the ticker of the current stock
        ticker = stock.attrs['data-rowkey'].split(":")[1]
        
        #Get its relative volume and accept stock if its relative volume is greater or equal to the minimum relative volume input
        try :
            relative_volume = float(stock.find_all("td", {"class":"cell-RLhfr_y4 right-RLhfr_y4"})[3].contents[0])
            if relative_volume >= 1.5 :
                accepted.append(ticker)
        except :
            pass
        
    #Return accepted list of stock tickers
    return accepted

#Selection strategy that simply returns the "Big 7" tech stock of the modern era
def selection2() :
    return ["AAPL", "AMZN", "MSFT", "NVDA", "META", "TSLA", "GOOG"]

#ENTRANCE STRATEGIES

indicator_inputs_required = {
    "RSI":[],
    "EMA":[],
    "MACD":[],
}

def entrance1() :
    pass

def entrance2() :
    pass

def entrance3() :
    pass

#EXIT STRATEGIES

def exit1() :
    pass

def exit2() :
    pass


def execute_strategy(stock_selection, enter_strategy, exit_strategy) :
    for ticker in stock_selection :
        #Call calculateIndicators.calculate_indicators()

def main() :
    stockSelections = [stockSelection_function() in stockSelections_functions]
    for strategy in itertools.permutations(stockSelections, enterStrategies_functions, exitStrategies_functions) :
        #Call execute_strategy()
        pass



main()
