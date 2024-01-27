from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Edge()

user_email = "reginaldjhyde@gmail.com"
user_password = "PythonIsAwesome!"

url = "https://finance.yahoo.com/portfolios/"
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
username.send_keys(user_email)

next_button = driver.find_element(By.NAME, "signin")
next_button.click()

time.sleep(3)
driver.fullscreen_window()

password = driver.find_element(By.ID, "login-passwd")
password.send_keys(user_password)

next_button2 = driver.find_element(By.NAME, "verifyPassword")
next_button2.click()

time.sleep(3)

driver.get("https://finance.yahoo.com/portfolio/p_0/view/v1")
driver.fullscreen_window()

def convert_volume_to_integer(volume_in_millions:str) :
    number_translations = {"K":1000, "M":1000000, "B":1000000000}
    return int(float(volume_in_millions[:-1])*number_translations[volume_in_millions[-1]])
    

print([element.text for element in driver.find_elements(By.XPATH, "//td/a[@data-test='quoteLink']")])
print([convert_volume_to_integer(element.text) for element in driver.find_elements(By.XPATH, "//td/fin-streamer[@data-field='regularMarketVolume']")])
