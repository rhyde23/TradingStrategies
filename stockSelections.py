#This script contains all of the possible stock selection strategies

#Import Web Scraping libraries
import requests 
from bs4 import BeautifulSoup 

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


print(selection2())
