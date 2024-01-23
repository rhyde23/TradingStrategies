from selenium import webdriver
from selenium.webdriver.common.by import By
import time


url = "https://finance.yahoo.com/portfolios/"

driver = webdriver.Edge()
driver.fullscreen_window()
driver.get(url)

quit()

time.sleep(5) 

while True :
    try :
        sign_in = driver.find_element(By.LINK_TEXT, "Sign In")
        sign_in.click()
        break
    except :
        driver.quit()
        driver = webdriver.Edge()
        driver.get(url)
        time.sleep(5) 
        

time.sleep(5)

username = driver.find_element(By.ID, "login-username")
username.send_keys("reginaldjhyde@gmail.com")


next_button = driver.find_element(By.NAME, "signin")
next_button.click()

time.sleep(5) 

password = driver.find_element(By.ID, "login-passwd")
password.send_keys("***REMOVED***")


next_button2 = driver.find_element(By.NAME, "verifyPassword")
next_button2.click()

time.sleep(5) 

sidebar = driver.find_element(By.Id, "_yb_sidenav-btn")
sidebar.click()


#sign_in = driver.find_element(By.XPATH, "//div[@class='menu-section']/ul[1]/li[1]/a[1]")
#sign_in.click()

#with_email = driver.find_element(By.XPATH, "//form[1]/button[3]")
#with_email.click()

#username = driver.find_element(By.XPATH, "//input[@name='email']")
#username.send_keys("hyde9698@stthomas.edu")

#password = driver.find_element(By.XPATH, "//input[@name='password']")
#password.send_keys("***REMOVED***")

#submit = driver.find_element(By.XPATH, "//button[@type='submit']")
#while True :
    #submit.submit()


"""
driver.implicitly_wait(5)

clickButton("Sign in with Email")

driver.implicitly_wait(5)

fillField("email", "hyde9698@stthomas.edu")

fillField("password", "***REMOVED***")

driver.implicitly_wait(5)

clickButton("Sign In")
"""

#username = driver.find_element(By.CLASS_NAME, "input_input__WivCD")
#username.send_keys("hyde9698@stthomas.edu")

#print(username.get_attribute('innerHTML'))

#password = driver.find_element(By.CLASS_NAME, "input_input__WivCD input_password__2qtWo")
#password.send_keys("***REMOVED***")

#clickButton("Sign In")

#username = driver.find_element(By.ID, "loginFormUser_email")
#username.send_keys("hyde9698@stthomas.edu")

#username = driver.find_element(By.ID, "loginForm_password")
#username.send_keys("***REMOVED***")

#button = driver.find_elements(By.LINK_TEXT, "Sign In")[1]
#button.click()

#watchlist = driver.find_element(By.LINK_TEXT, "My Watchlist")
#watchlist.click()

#while True :
    #price = driver.find_element(By.ID, "50687600_last_6497").text
    #re = driver.find_element(By.CLASS_NAME, "symbol plusIconTd left bold elp displayNone alert js-injected-user-alert-container")
    #print(re)
    #quit()

    #print(50687600_last_6497)

#time.sleep(5)

#username = driver.find_element(By.ID, "loginFormUser_email")
#username.send_keys("hyde9698@stthomas.edu")

#username = driver.find_element(By.ID, "loginForm_password")
#username.send_keys("***REMOVED***")

#button = driver.find_element(By.LINK_TEXT, "Sign In")
#button.click()
