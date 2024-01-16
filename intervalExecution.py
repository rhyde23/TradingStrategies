#This script will run every interval

import calculateIndicators, requests
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

#Dictionary to pass to calculateIndicators.calculate_indicators that signals which values of which indicators to calculate
indicator_inputs_required = {
    "RSI":[9, 14],
    "EMA":[9, 20, 21, 50],
    "MACD":[(12, 26, 29),(5, 35, 5)]
}

#Indicator outputs dictionary that will be populated when calculateIndicators.calculate_indicators is executed
indicator_outputs = {}

#Possible entrance strategy based on a mid-term analysis
def entrance1() :
    if indicator_outputs["RSI"][14] > 70 and indicator_outputs["EMA"][20] > indicator_outputs["EMA"][50] and indicator_outputs["MACD"][(12, 26, 9)][0] > indicator_outputs["MACD"][(12, 26, 9)][1] :
        return 1
    if indicator_outputs["RSI"][14] < 30 and indicator_outputs["EMA"][20] < indicator_outputs["EMA"][50] and indicator_outputs["MACD"][(12, 26, 9)][0] > indicator_outputs["MACD"][(12, 26, 9)][1] :
        return 2
    return 0

#Possible entrance strategy based on a short-term analysis
def entrance2() :
    if indicator_outputs["RSI"][9] > 70 and indicator_outputs["EMA"][9] > indicator_outputs["EMA"][21] and indicator_outputs["MACD"][(5, 35, 5)][0] > indicator_outputs["MACD"][(5, 35, 5)][1] :
        return 1
    if indicator_outputs["RSI"][9] < 30 and indicator_outputs["EMA"][9] < indicator_outputs["EMA"][21] and indicator_outputs["MACD"][(5, 35, 5)][0] > indicator_outputs["MACD"][(5, 35, 5)][1] :
        return 2
    return 0


#EXIT STRATEGIES

def exit1() :
    pass

def exit2() :
    pass

#Function that will execute one strategy
def execute_strategy(stock_selection, enter_strategy, exit_strategy) :
    global indicator_outputs
    for ticker in stock_selection :
        indicator_outputs = calculateIndicators.calculate_indicators(ticker, indicator_inputs_required, 1000)
        enter_result = enter_strategy() 

#List of strategies to log performance data for 
strategies = [
    [],
    [],
    [],
]

#Main function that will run every strategy
def main() :
    for strategy in strategies :
        #Call execute_strategy()
        pass



main()
