import requests, subprocess, sys, time
from datetime import datetime
from pytz import timezone
import yfinance as yf

#This function checks to see if yfinance is up-to-date
def check_up_to_date(name):
    latest_version = str(subprocess.run([sys.executable, '-m', 'pip', 'install', '{}==random'.format(name)], capture_output=True, text=True))
    latest_version = latest_version[latest_version.find('(from versions:')+15:]
    latest_version = latest_version[:latest_version.find(')')]
    latest_version = latest_version.replace(' ','').split(',')[-1]

    current_version = str(subprocess.run([sys.executable, '-m', 'pip', 'show', '{}'.format(name)], capture_output=True, text=True))
    current_version = current_version[current_version.find('Version:')+8:]
    current_version = current_version[:current_version.find('\\n')].replace(' ','') 

    return latest_version == current_version

#Quit program if yfinance is not up-to-date
if not check_up_to_date("yfinance") :
    print("yfinance is not up-to-date. Run \"pip install yfinance --upgrade\" to update yfinance.")
    quit()


#Selection Strategies

def selection1() :
    pass

#Entrance Strategies

def entrance1() :
    pass

#Exit Strategies

def exit1() :
    pass

#Globals

indicator_inputs_required = {
    "RSI":[5, 9, 14],
    "EMA":[10, 20, 50, 100, 200],
    "MACD":[(12, 26, 9), (5, 35, 5), (19, 39, 9)]
}

indicator_outputs = {indicator_name:{} for indicator_name in indicator_inputs_required}

indicator_historical = {}

indicator_data_points_needed = {
    "RSI":2,
    "EMA":1,
    "MACD":3,
}

ticker = ""
price = 0

historical_period_length = 5
hist_data = None
day_on = 0

#Indicator Functionality

def avg_change_formula(current_change, period_length, new_difference) :
    return ((current_change*(period_length-1))+new_difference)/period_length

def ema_formula(recent_value, period_length, current_ema) :
    

def calculate_historical_rsi_data() :
    global indicator_historical, loading_index
    difference = hist_data.iloc[day_on]["Close"]-hist_data.iloc[day_on-1]["Close"]
    
    for period in indicator_inputs_required["RSI"] :
        if day_on < period :
            if difference >= 0 :
                indicator_historical[ticker][loading_index] += difference

            else :
                indicator_historical[ticker][loading_index+1] += -difference

        else :

            if day_on == period :
                indicator_historical[ticker][loading_index] = indicator_historical[ticker][loading_index]/period
                indicator_historical[ticker][loading_index+1] = indicator_historical[ticker][loading_index+1]/period

            if difference >= 0 :
                indicator_historical[ticker][loading_index] = avg_change_formula(indicator_historical[ticker][loading_index], period, difference)
                indicator_historical[ticker][loading_index+1] = avg_change_formula(indicator_historical[ticker][loading_index+1], period, 0)

            else :
                indicator_historical[ticker][loading_index] = avg_change_formula(indicator_historical[ticker][loading_index], period, 0)
                indicator_historical[ticker][loading_index+1] = avg_change_formula(indicator_historical[ticker][loading_index+1], period, -difference)
                
        loading_index += indicator_data_points_needed["RSI"]

def calculate_historical_ema_data() :
    global indicator_historical, loading_index
    recent_close = hist_data.iloc[day_on]["Close"]
    for period in indicator_inputs_required["EMA"] :
        exp_percentage = 2/(period+1)
        indicator_historical[ticker][loading_index] = (recent_close*exp_percentage)+(indicator_historical[ticker][loading_index]*(1-exp_percentage))
        
        loading_index += indicator_data_points_needed["EMA"]

def calculate_historical_macd_data() :
    global indicator_historical, loading_index
    recent_close = hist_data.iloc[day_on]["Close"]
    for combination in indicator_inputs_required["MACD"] :
        exp_percentage = 2/(combination[0]+1)
        indicator_historical[ticker][loading_index] = (recent_close*exp_percentage)+(indicator_historical[ticker][loading_index]*(1-exp_percentage))

        exp_percentage = 2/(combination[1]+1)
        indicator_historical[ticker][loading_index+1] = (recent_close*exp_percentage)+(indicator_historical[ticker][loading_index+1]*(1-exp_percentage))

        exp_percentage = 2/(combination[2]+1)
        macd = indicator_historical[ticker][loading_index]-indicator_historical[ticker][loading_index+1]
        indicator_historical[ticker][loading_index+2] = (macd*exp_percentage)+(indicator_historical[ticker][loading_index+2]*(1-exp_percentage))

        loading_index += indicator_data_points_needed["MACD"]

        
def calculate_historical_indicators() :
    global indicator_historical, hist_data, day_on, loading_index
    while True :
        try :
            hist_data = yf.Ticker(ticker).history(period=str(historical_period_length)+"y")
            break
        except :
            pass
    loading_index = 1
    day_on = 0

    #list = [last_price, avg_gains, avg_losses, emas, fast_emas, slow_emas, macd_emas]
    data_points_needed = sum([indicator_data_points_needed[key]*len(indicator_inputs_required[key]) for key in indicator_data_points_needed])+1
    indicator_historical[ticker] = [0]*data_points_needed
    indicator_historical[ticker][0] = hist_data.iloc[-2]["Close"]
    
    while day_on < len(hist_data)-1 :
        loading_index = 1
        calculate_historical_rsi_data()
        calculate_historical_ema_data()
        calculate_historical_macd_data()
        day_on += 1

    indicator_historical[ticker] = tuple([round(value, 5) for value in indicator_historical[ticker]])
        

def update_indicator_outputs() :
    difference = price-indicator_historical[ticker][0]
    loading_index = 1
    for period in indicator_inputs_required["RSI"] :
        if difference >= 0 :
            avg_gain = ((indicator_historical[ticker][loading_index]*(period-1))+difference)/period
            avg_loss = ((indicator_historical[ticker][loading_index+1]*(period-1)))/period 
            indicator_outputs["RSI"][period] = round(100-(100/(1+(avg_gain/avg_loss))), 4)
        else :
            avg_gain = ((indicator_historical[ticker][loading_index]*(period-1)))/period
            avg_loss = ((indicator_historical[ticker][loading_index+1]*(period-1))-difference)/period
            indicator_outputs["RSI"][period] = round(100-(100/(1+(avg_gain/avg_loss))), 4)

        loading_index += indicator_data_points_needed["RSI"]
            
    for period in indicator_inputs_required["EMA"] :
        exp_percentage = 2/(period+1)
        indicator_outputs["EMA"][period] = round((price*exp_percentage)+(indicator_historical[ticker][loading_index]*(1-exp_percentage)), 4)
        
        loading_index += indicator_data_points_needed["EMA"]

    for combination in indicator_inputs_required["MACD"] :
        exp_percentage = 2/(combination[0]+1)
        fast_ema = (price*exp_percentage)+(indicator_historical[ticker][loading_index]*(1-exp_percentage))

        exp_percentage = 2/(combination[1]+1)
        slow_ema = (price*exp_percentage)+(indicator_historical[ticker][loading_index+1]*(1-exp_percentage))

        exp_percentage = 2/(combination[2]+1)
        macd = fast_ema-slow_ema
        macd_ema = (macd*exp_percentage)+(indicator_historical[ticker][loading_index+2]*(1-exp_percentage))

        indicator_outputs["MACD"][combination] = (round(fast_ema-slow_ema, 4), round(macd_ema, 4))

        loading_index += indicator_data_points_needed["MACD"]

start = time.time()
test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'BRK', 'TSLA', 'LLY', 'AVGO', 'V', 'TSM', 'JPM', 'UNH', 'NVO', 'WMT', 'MA', 'XOM', 'JNJ', 'PG', 'HD', 'ORCL', 'ASML', 'COST', 'MRK', 'ABBV', 'TM', 'AMD', 'ADBE', 'CRM', 'CVX', 'BAC', 'KO', 'FMX', 'ACN', 'PEP', 'NVS', 'MCD', 'NFLX', 'TMO', 'CSCO', 'AZN', 'INTC', 'SHEL', 'ABT', 'LIN', 'SAP', 'TMUS', 'PDD', 'WFC', 'INTU', 'VZ', 'BABA', 'CMCSA', 'DIS', 'QCOM', 'DHR', 'AMGN', 'PFE', 'IBM', 'TXN', 'BHP', 'NOW', 'NKE', 'TTE', 'UNP', 'CAT', 'BX', 'HSBC', 'PM', 'MS', 'SPGI', 'GE', 'RY', 'AMAT', 'UPS', 'AXP', 'HON', 'UBER', 'ISRG', 'HDB', 'RTX', 'COP', 'BA', 'SNY', 'BUD', 'GS', 'LOW', 'T', 'BKNG', 'SONY', 'RIO', 'UL', 'SYK', 'PLD', 'BLK', 'NEE', 'MDT', 'VRTX', 'SCHW', 'ELV', 'LRCX', 'LMT', 'PANW', 'DE', 'TD', 'TJX', 'SHOP', 'MUFG', 'SBUX', 'PBR', 'REGN', 'C', 'BMY', 'MDLZ', 'PBR', 'ADI', 'PGR', 'GILD', 'ADP', 'MMC', 'CB', 'ETN', 'CVS', 'BP', 'MU', 'AMT', 'UBS', 'ABNB', 'CI', 'MELI', 'BSX', 'ZTS', 'FI', 'KLAC', 'SNPS', 'EQNR', 'IBN', 'INFY', 'ANET', 'CNI', 'CDNS', 'GSK', 'ITW', 'ARM', 'SHW', 'RELX', 'DEO', 'WDAY', 'HCA', 'ENB', 'SO', 'EQIX', 'WM', 'KKR', 'DUK', 'CME', 'CP', 'SLB', 'MO', 'CRWD', 'MCO', 'ICE', 'NOC', 'PYPL', 'MAR', 'BDX', 'CSX', 'BMO', 'TRI', 'GD', 'CNQ', 'SNOW', 'CL', 'STLA', 'SMFG', 'BTI', 'USB', 'TGT', 'MCK', 'TEAM', 'EOG', 'CMG', 'SCCO', 'SAN', 'FDX', 'LULU', 'BN', 'CTAS', 'MRVL', 'AON', 'ITUB', 'ORLY', 'VALE', 'PH', 'RACE', 'PNC', 'NTES', 'TDG', 'ROP']      
for ind, test_ticker in enumerate(test_tickers) :
    ticker = test_ticker
    calculate_historical_indicators()
    print(ind)

print(time.time()-start)

while True :
    start = time.time()
    for test_ticker in test_tickers :
        ticker = test_ticker
        price = 398.90
        update_indicator_outputs()
    #print(time.time()-start, "completed")
#print(indicator_historical[ticker])
#print()
#print(indicator_outputs)
#print(time.time()-start)
