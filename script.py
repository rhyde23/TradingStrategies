import requests, subprocess, sys
from bs4 import BeautifulSoup

from datetime import datetime
from pytz import timezone

from requests_html import HTMLSession
session = HTMLSession()

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
    
    #Processes url request for tradingview.com of the most active stocks of the day
    #r = requests.get("https://www.investing.com/portfolio/?portfolioID=YGAyYTVlYTVkMWFlM2YwOg%3D%3D")
    #r = requests.get("https://www.googletagservices.com/activeview/js/current/ufs_web_display.js?cache=r20110914")

    #Apply BeautifulSoup() to the website request
    #soup = BeautifulSoup(r.content, 'html.parser')
    #print(soup)
    #print("NVDA" in soup)
    
    r = session.get('https://www.googletagservices.com/activeview/js/current/ufs_web_display.js?cache=r20110914')

    r.html.render()
    #print(soup.find_all("td", {"data-column-name":"symbol"}))
    
    #for element in soup.find_all("tr") :#{"class":"datatable-v2_cell__IwP1U dynamic-table-v2_col-other__zNU4A text-right rtl:text-right"}) :
        #print(element)
        #print(finstreamer)
        #t, price = finstreamer = finstreamer.attrs['data-symbol'], float(finstreamer.attrs['value'])
        #print(t, price)
        #class="datatable-v2_cell__IwP1U dynamic-table-v2_col-other__zNU4A text-right rtl:text-right"
        #print(finstreamer.attrs["class"])]
        #print(finstreamer.find_all("div", {"class":"flex justify-end"})[0])
        #print(finstreamer)
        #prin
    #print(soup)

selection1()
