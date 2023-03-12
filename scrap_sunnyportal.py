import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from webdriver_manager.chrome import ChromeDriverManager
import traceback

import requests
import shutil
import os

RESULT_FOLDER = 'Scraped_Images/'
chromeoption = Options()
chromeoption.add_argument("--headless")
chromeoption.add_argument("--no-sandbox")
chromeoption.add_argument("--disable-dev-shm-usage")
chromeoption.add_argument("--enable-javascript")
chromeoption.add_argument("--nogpu")
chromeoption.add_argument("--disable-gpu")
chromeoption.add_argument("--window-size=1920,1080")
chromeoption.add_argument("--enable-javascript")
chromeoption.add_experimental_option("excludeSwitches", ["enable-automation"])
chromeoption.add_experimental_option('useAutomationExtension', False)
chromeoption.add_argument('--disable-blink-features=AutomationControlled')

#ua = UserAgent()
#userAgent = ua.random

driver = webdriver.Chrome(ChromeDriverManager().install(),options=chromeoption)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

driver.maximize_window()
try:
    print("Fetching web page")
    driver.get('https://www.sunnyportal.com/FixedPages/EnergyAndPower.aspx')

    print("Waiting for onetrust-accept-btn-handler")
    button_accept_cookie = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, "onetrust-accept-btn-handler")))
    button_accept_cookie.click()

    print("Reading the login credential")
    config_file = open('sunnyportal.ini', "r", encoding='utf-8')
    lines = config_file.readlines()
    str_email = lines[0]
    str_email = str_email.replace("\n", "")
    str_password = lines[1]
    str_password = str_password.replace("\n", "")
    print("Email Address:", str_email)
    print("Password:", str_password)

    print("Waiting for username field")
    text_email = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, "txtUserName")))
    text_email.send_keys(str_email)

    print("Waiting for password field")
    text_password = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, "txtPassword")))
    text_password.send_keys(str_password)

    print("Waiting for login button")
    button_login = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_Logincontrol1_LoginBtn")))
    button_login.click()

    """print("Waiting for shadow box close button")
    button_close = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.XPATH, "//img[contains(@class,'ShadowBoxCloseButton')]")))
    button_close.click()
    time.sleep(15)"""

    #print("waiting for terms of use...")
    #button_close = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "ctl00_ctl14_ConfirmTermsOfUse_GeneralMessageLinkButton")))
    #button_close.click()

    print("Waiting for Show Energy And Power Button")
    tab_day = driver.find_elements(By.ID, "ctl00_ContentPlaceHolder1_UserControlShowEnergyAndPower1_LinkButton_TabFront3")
    if tab_day:
        tab_day.click()
    tab_day = driver.find_elements(By.ID, "ctl00_ContentPlaceHolder1_UserControlShowDashboard1_UserControlShowEnergyAndPower1_LinkButton_TabFront3")
    if tab_day:
        tab_day.click()

    print("Waiting for prev button")
    with open("aa.txt", 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    button_previous_date = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_UserControlShowDashboard1_UserControlShowEnergyAndPower1_btn_prev")))
    button_previous_date.click()

    print("Waiting for image")
    img = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_UserControlShowDashboard1_UserControlShowEnergyAndPower1_MouseoverMiddleImg")))
    img.click()

    download_img = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "UserControlShowEnergyAndPower1$_diagram")))
    src = download_img.get_attribute('src')

    res = requests.get(src, stream=True)

    yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    RESULT_FOLDER = RESULT_FOLDER + str(yesterday) + "/sunnyportal"
    if not os.path.exists(RESULT_FOLDER):
        os.makedirs(RESULT_FOLDER)
    file_name = "sunnyportal_" + str(yesterday) + ".png"
    file_name = os.path.join(RESULT_FOLDER, file_name)

    if res.status_code == 200:
        with open(file_name, 'wb') as f:
            shutil.copyfileobj(res.raw, f)
        print('Image sucessfully downloaded: ', file_name)
    else:
        print('Image sucessfully downloaded By ID: ', file_name)
        with open(file_name, 'wb') as file:
            div_graph = WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
                (By.ID, "zoomDiagramCont")))
            file.write(div_graph.screenshot_as_png)
    time.sleep(5)

    print("Waiting for image close button")
    button_close_image = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//td[@id='zoomDiagramCancel']//img[@src='/Images/cancel.png']")))
    button_close_image.click()

    time.sleep(5)
except:
    ####### We can add the email sending code here #######
    print(traceback.format_exc())
    print("Scraping Failed!")
