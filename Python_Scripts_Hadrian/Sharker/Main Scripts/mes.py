from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def login():
    web2 = webdriver.Chrome()
    form_url2 = 'http://google.com'
    # form_url2 = 'http://c4ai.southeastasia.cloudapp.azure.com/toolroom/login.php'
    web2.get(form_url2)
    time.sleep(2)

    # adm = web2.find_element(By.XPATH, '//*[@id="username"]')
    # adm.send_keys('212782X')

    # pw = web2.find_element(By.XPATH, '/html/body/div[3]/div/div/form/div/div[3]/input')
    # pw.send_keys('212782X')

    # submit2 = web2.find_element(By.XPATH, '/html/body/div[3]/div/div/form/div/button')
    # submit2.click()
    time.sleep(3)
    web2.close()

