#This script will run every interval

import calculateIndicators, requests
from bs4 import BeautifulSoup

from datetime import datetime
from pytz import timezone


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

indicator_outputs = {}

#Possible entrance strategy based on a mid-term analysis
def entrance1() :
    if indicator_outputs["RSI"][14] > 70 and indicator_outputs["EMA"][20] > indicator_outputs["EMA"][50] and indicator_outputs["MACD"][(12, 26, 9)][0] > indicator_outputs["MACD"][(12, 26, 9)][1] :
        return 1
    if indicator_outputs["RSI"][14] < 30 and indicator_outputs["EMA"][20] < indicator_outputs["EMA"][50] and indicator_outputs["MACD"][(12, 26, 9)][0] > indicator_outputs["MACD"][(12, 26, 9)][1] :
        return 2

#Possible entrance strategy based on a short-term analysis
def entrance2() :
    if indicator_outputs["RSI"][9] > 70 and indicator_outputs["EMA"][9] > indicator_outputs["EMA"][21] and indicator_outputs["MACD"][(5, 35, 5)][0] > indicator_outputs["MACD"][(5, 35, 5)][1] :
        return 1
    if indicator_outputs["RSI"][9] < 30 and indicator_outputs["EMA"][9] < indicator_outputs["EMA"][21] and indicator_outputs["MACD"][(5, 35, 5)][0] > indicator_outputs["MACD"][(5, 35, 5)][1] :
        return 2

#EXIT STRATEGIES

def exit1() :
    pass

def exit2() :
    pass

#######################################################################################################################################################################################

#Dictionary to pass to calculateIndicators.calculate_indicators that signals which values of which indicators to calculate
indicator_inputs_required = {
    "RSI":[9, 14],
    "EMA":[9, 20, 21, 50],
    "MACD":[(12, 26, 29),(5, 35, 5)]
}


#List of strategies to log performance data for

stock_selection_strategies = [selection1, selection2]

strategies = [
    (entrance1, exit1),
    (entrance2, exit2),
]

#######################################################################################################################################################################################

#List to track what stocks each strategy is currently holding
strategies_performance_tracking = [{"Holding":{}, "MaxHolding":0}]*(len(strategies)*len(stock_selection_strategies))

#List that will be populated by calling the stock selection strategy functions at the start of every iteration of the main loop.
#By calling the stock selection strategy functions at the start of every iteration and storing the selections, the main function saves the time from calling them for every single strategy permuation
stock_selections = [[]]*len(stock_selection_strategies)

#This function checks if the current Eastern Time is between the hours of 9:30 am and 4:00 pm, which is the trading day for the Nasdaq and NYSE 
def stock_exchanges_are_open() :
    #First, get the time in Eastern Time
    tz = timezone('EST')

    #Breaking the string version of this time data structure and extract the hours and minutes
    split_by_colon = str(datetime.now(tz)).split(" ")[1].split(":")
    hour, minutes = int(split_by_colon[0]), int(split_by_colon[1])

    #Calculate the total minutes elapsed
    minutes_elapsed = (hour*60)+minutes

    #Return if minutes are between 9:30 am and 4:00 pm
    return minutes_elapsed >= 570 and minutes_elapsed <= 960

#Main function that will run every strategy
def main() :

    #Indicate global status of indicator_outputs within this function. This variable is referenced within the Entrance and Exit Strategies.
    #It will be populated and updated with the proper values for each stock ticker in each strategy permutation
    global indicator_outputs

    #Main Loop of main function that will repeat during the whole trading day
    while True :

        #Testing line
        #calculateIndicators.calculate_indicators("MSFT", indicator_inputs_required, 1000)

        #Break the main loop if the stock exhchanges are not open
        if not stock_exchanges_are_open() :
            print("Stock exchanges are closed")
            break

        #Populate the stock_selections list by calling each stock selection strategy
        #By executing this before iterating through each permutation, this saves runtime and avoids unnecessary scraping from websites such as tradingview.com (First selection strategy)
        for stock_selection_strategy_index, stock_selection_strategy in enumerate(stock_selection_strategies) :
            stock_selections[stock_selection_strategy_index] = stock_selection_strategy()

        #This loop iterates through each stock selection 
        for stock_selections_index, stock_selections in enumerate(stock_selections) :

            #This loop iterates through each stock ticker for an individual stock selection
            for ticker in stock_selections :

                #indicator_outputs is updated for this new ticker with every indicator it will need for the Entrance and Exit Strategies' execution
                indicator_outputs = calculateIndicators.calculate_indicators(ticker, indicator_inputs_required, 1000)

                #This loop iterates through each permutation of entrance strategy and exit strategy.
                for strategy_index, strategy in enumerate(strategies) :

                    #Unpack the tuple 
                    enter_strategy, exit_strategy = strategy

                    #The "true_strategy_index" is the index within strategies_performance_tracking for the permutation of ALL 3 factors (selection, entrance, exit)
                    #Calculated by replicating what the index would be if each strategy tuple also included the stock selection
                    #The strategy tuples do not include stock selections for the purpose of saving runtime. This is why we populate the stock_selections list to only perform the functions once per main loop iteration
                    true_strategy_index = (stock_selections_index*len(stock_selection_strategies))+strategy_index

                    #If the ticker is currently held within this strategy permuation 
                    if ticker in strategies_performance_tracking[true_strategy_index]["Holding"] :  
                        exit_result = enter_strategy()

                    #If the ticker is not currently held within this strategy permuation 
                    else :
                        #
                        enter_result = enter_strategy()
                        if enter_result != None :
                            strategies_performance_tracking[true_strategy_index]["Holding"][ticker] = (indicator_outputs["CurrentPrice"], enter_result)
                            if len(strategies_performance_tracking[true_strategy_index]["Holding"]) > strategies_performance_tracking[true_strategy_index]["MaxHolding"] :
                                strategies_performance_tracking[true_strategy_index]["MaxHolding"] = len(strategies_performance_tracking[true_strategy_index]["Holding"])



main()
