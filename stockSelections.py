#This script is a temporary strategy of picking which stocks to apply automated technical analysis on
#Selects all the stocks from the top 100 most active stocks by volume and filters out stocks with low relative volume
#Scrapes information from tradingview.com

#Import Web Scraping libraries
import requests 
from bs4 import BeautifulSoup 

#Function to extract the list of 100 most traded stocks from tradingview.com and filters out stocks that don't meet minimum relative volume 
def selection1(minimum_relative_volume:int) :
    #Processes url request
    URL = "https://www.tradingview.com/markets/stocks-usa/market-movers-active/" 
    r = requests.get(URL)
    
    soup = BeautifulSoup(r.content, 'html.parser')
    accepted = []
    for stock in soup.find_all("tr", {"class":"row-RdUXZpkv listRow"}) :
        #Get stock ticker
        ticker = stock.attrs['data-rowkey'].split(":")[1]
        #Get its relative volume and accept stock if its relative volume is greater or equal to the minimum relative volume input
        try :
            relative_volume = float(stock.find_all("td", {"class":"cell-RLhfr_y4 right-RLhfr_y4"})[3].contents[0])
            if relative_volume >= minimum_relative_volume :
                accepted.append(ticker)
        except :
            pass
    #Return accepted list of stock tickers
    return accepted


#This script is just a potential strategy for locating which stocks to apply technical analysis, not the holy grail
print(selection1(2))
