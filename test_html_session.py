from selenium import webdriver
from selenium.webdriver.common.by import By
import time


url = "https://finance.yahoo.com/portfolios/"

driver = webdriver.Edge()
driver.get(url)
driver.fullscreen_window()

try :
    sign_in = driver.find_element(By.XPATH, "//li[@id='header-profile-menu']/a[1]")
    sign_in.click()
except :
    sign_in = driver.find_element(By.XPATH, "//div[@id='login-container']/a[1]")
    sign_in.click()

time.sleep(3)
driver.fullscreen_window()

username = driver.find_element(By.ID, "login-username")
username.send_keys("reginaldjhyde@gmail.com")

next_button = driver.find_element(By.NAME, "signin")
next_button.click()

time.sleep(3)
driver.fullscreen_window()

password = driver.find_element(By.ID, "login-passwd")
password.send_keys("***REMOVED***")

next_button2 = driver.find_element(By.NAME, "verifyPassword")
next_button2.click()

time.sleep(3)

driver.get("https://finance.yahoo.com/portfolio/p_0/view/v1")
driver.fullscreen_window()


while True :
    tickers = [element.text for element in driver.find_elements(By.XPATH, "//td/a[@data-test='quoteLink']")]
    prices = [float(element.text) for element in driver.find_elements(By.XPATH, "//td/fin-streamer[@data-field='regularMarketPrice']")]

    for pair in list(zip(tickers, prices)) :
        print(pair)
    print()



