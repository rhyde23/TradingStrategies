#This script accesses data from Yahoo Finance

import yfinance as yf

def get_historical_data(ticker, p) :
    return yf.Ticker(ticker).history(period=p)
