from selenium import webdriver
from selenium.webdriver.common.by import By
import time
url = "https://www.investing.com/portfolio/?portfolioID=YGAyYTVlYTVkMWFlM2YwOg%3D%3D"

driver = webdriver.Edge()
driver.get(url)


username = driver.find_element(By.ID, "loginFormUser_email")
username.send_keys("hyde9698@stthomas.edu")

username = driver.find_element(By.ID, "loginForm_password")
username.send_keys("***REMOVED***")

button = driver.find_elements(By.LINK_TEXT, "Sign In")[1]
button.click()

watchlist = driver.find_element(By.LINK_TEXT, "My Watchlist")
watchlist.click()

while True :
    #price = driver.find_element(By.ID, "50687600_last_6497").text
    re = driver.find_element(By.CLASS_NAME, "symbol plusIconTd left bold elp displayNone alert js-injected-user-alert-container")
    print(re)
    quit()

    #print(50687600_last_6497)

#time.sleep(5)

#username = driver.find_element(By.ID, "loginFormUser_email")
#username.send_keys("hyde9698@stthomas.edu")

#username = driver.find_element(By.ID, "loginForm_password")
#username.send_keys("***REMOVED***")

#button = driver.find_element(By.LINK_TEXT, "Sign In")
#button.click()
