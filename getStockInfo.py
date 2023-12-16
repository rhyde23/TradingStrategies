#This script accesses data from Yahoo Finance

import yfinance as yf

msft = yf.Ticker("MSFT")

# get historical market data
hist = msft.history(period="1mo")
print(hist)
print(type(hist))
