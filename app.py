from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import webdriver_manager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup

# system libraries
import os
import sys
import urllib

# recaptcha libraries
import pydub
import speech_recognition as sr

# selenium libraries
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# custom patch libraries
from patch import download_latest_chromedriver, webdriver_folder_name


import schedule
import threading

import time
from datetime import datetime, date, timedelta

from twocaptcha import TwoCaptcha

from multiprocessing import Process, Manager, Value


recaptcha_worker_list = []
recaptcha_token_list = []

is_test = True



def selectAvaliableTimeSlot(driver):
    # find available input
    input_list = driver.find_elements_by_name("step_2_CBP_ID")
    for index, input in enumerate(input_list):

        if is_test:
            removeElementAtribute(driver, input, "disabled")

        disabled = input.get_attribute("disabled")
        if disabled != 'true':
            tryClickElement(driver, input)



def recaptchaWorker(recaptcha_token_list):
    print("recaptchaWorker started")
    while True:
        print("recaptchaWorker working")

        start = datetime.now()


        url = "https://pbqc.quotabooking.gov.hk/booking/hk/index_tc.jsp"
        siteKey = "6Lcmk0kcAAAAAG-dUsJJUbEOf2Ph2ZdGLMCojehi"

        API_KEY = "be9f08edcbdaafe723d76dd8b17ad0df"
        config = {
                'server':           '2captcha.com', # can be also set to 'rucaptcha.com'
                'apiKey':           API_KEY,
                'defaultTimeout':    120,
                'recaptchaTimeout':  600,
                'pollingInterval':   5,
            }
        
        solver = TwoCaptcha(**config)

        try:
            result = solver.recaptcha(
                sitekey=siteKey,
                url=url,
                invisible=0,
                enterprise=1
            )

        except Exception as e:
            print(e)
            print("recaptchaWorker failed")

        else:

            end = datetime.now()
            print("recaptchaWorker success")
            result['startAt'] = start
            result['endAt'] = end
            result['timeSpent'] = end - start
            recaptcha_token_list.append(result)

        time.sleep(1)

def tryGetRecaptchaToken():

    while True:
        now = datetime.now()

        for index in range(len(recaptcha_token_list)):
            recaptcha_token = recaptcha_token_list.pop(0)
            endAt = recaptcha_token['endAt']
            # print("endAt : " + str(endAt))
            timeDelta = now - endAt

            # print("timeDelta : " + str(timeDelta))
            validTimeDelta = timedelta(seconds = 60)
            if timeDelta < validTimeDelta:
                return recaptcha_token['code']

        print("waiting for recaptcha token available")
        time.sleep(5)


def solveRecaptcha(driver, textAreaId):
    responseInput = driver.find_element_by_id(textAreaId)
    scrollToElement(driver, responseInput)

    token = tryGetRecaptchaToken()
    # show the input and enter the token
    setElementAttribute(driver, responseInput, "style", "")
    responseInput.send_keys(token)


def initDriver():
    while True:
        try:
            # create chrome driver
            chrome_path = os.path.normpath(
                os.path.join(os.getcwd(), webdriver_folder_name, "chromedriver.exe")
            )

            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--incognito")

            driver = webdriver.Chrome(chrome_path, chrome_options=chrome_options)
            return driver
        except Exception:
            # patch chromedriver if not available or outdated
            try:
                driver
            except NameError:
                is_patched = download_latest_chromedriver()
            else:
                is_patched = download_latest_chromedriver(
                    driver.capabilities["version"]
                )
            if not is_patched:
                sys.exit(
                    "[ERR] Please update the chromedriver.exe in the webdriver folder according to your chrome version:"
                    "https://chromedriver.chromium.org/downloads"
                )

def isElementVisible(element):
    location = element.location
    size = element.size
    w, h = size['width'], size['height']
    
    return h > 0

def ScheduleGoToPage(driver):
    while True:
        print("waiting to redirect")


def waitUntilLanding(driver):
  while True:

    try:
        targetElement = driver.find_element_by_id("step_1_other_documentId")
        if isElementVisible(targetElement):
            # print("landed")
            return
    except:
        print("cannot location element")
    # print("still loading")
    time.sleep(0.5)

def waitUntilPage2(driver):
  while True:
    targetElement = driver.find_element_by_id("pics_consent")

    if isElementVisible(targetElement):
        # print("now in page 2")
        return
    # print("still in  page 1")
    time.sleep(0.5)

def waitUntilPage4(driver):
    while True:
        targetElement = driver.find_element_by_id("user_note")

        if isElementVisible(targetElement):
            # print("now in final page")
            return
        # print("still in  page 3")
        time.sleep(0.5)


def scrollToElement(driver, element):
    driver.execute_script("arguments[0].scrollIntoView();", element)

def tryClickElement(driver, element):
    scrollToElement(driver, element)
    driver.execute_script("arguments[0].click();", element)

def setElementAttribute(driver, element, prop, value):
    driver.execute_script(f"arguments[0].setAttribute('{prop}','{value}')", element)

def removeElementAtribute(driver, element, prop):
    driver.execute_script(f"arguments[0].removeAttribute('{prop}')", element)


def process_main():
    options = Options()
    options.add_argument("--disable-notifications")

    # skip queue url
    url = "https://pbqc.quotabooking.gov.hk/booking/hk/index.jsp"

    # hardcode info
    name = "Babon Myra cruzdo"
    passport_no = "P5155426B"
    passport_type = "Philippine Passport"
    email = " ja@ja-agency.com.hk"
    phone_no = "61258922"
    contact_name = "Camy Lor"

    food_type = "Western"

    can_english = True
    can_cantonese = False
    can_putonghua = False

    # init driver
    driver = initDriver()

    driver.implicitly_wait(5)
    driver.get(url)


    waitUntilLanding(driver)
    time.sleep(0.5)

    # page 1

    # select the passport type
    select = Select(driver.find_element_by_id('step_1_ATGC_NATCARDTYPE'))
    select.select_by_value(passport_type)

    # input passport_no
    passport_no_input = driver.find_element_by_id("step_1_other_documentId")
    passport_no_input.send_keys(passport_no)

    solveRecaptcha(driver, "g-recaptcha-response")

    # try submit the form
    passport_no_input.send_keys(Keys.RETURN)



    waitUntilPage2(driver)

    # page 2
    pics_consent_input = driver.find_element_by_id("pics_consent")
    tryClickElement(driver, pics_consent_input)

    nr_consent_input = driver.find_element_by_id("nr_consent")
    tryClickElement(driver, nr_consent_input)

    gr_consent_input = driver.find_element_by_id("gr_consent")
    tryClickElement(driver, gr_consent_input)

    # next_page
    next_button_2 = driver.find_element_by_id("note_2_confirm")
    tryClickElement(driver, next_button_2)

    time.sleep(0.5)

    # page 3

    # name
    step_2_fdh_name_input = driver.find_element_by_id("step_2_fdh_name")
    step_2_fdh_name_input.send_keys(name)


    # select food type
    select = Select(driver.find_element_by_id('step_2_fdh_meal_preference'))
    select.select_by_value(food_type)

    # language 
    
    # english
    can_english_element_id = "step_2_communicate_in_english_yes" if can_english  else "step_2_communicate_in_english_no"
    can_english_input = driver.find_element_by_id(can_english_element_id)
    tryClickElement(driver, can_english_input)

    # cantonese
    can_cantonese_element_id = "step_2_communicate_in_cantonese_yes " if can_cantonese  else "step_2_communicate_in_cantonese_no"
    can_cantonese_input = driver.find_element_by_id(can_cantonese_element_id)
    tryClickElement(driver, can_cantonese_input)

    # putonghua
    can_putonghua_element_id = "step_2_communicate_in_putonghua_yes " if can_putonghua  else "step_2_communicate_in_putonghua_no"
    can_putonghua_input = driver.find_element_by_id(can_putonghua_element_id)
    tryClickElement(driver, can_putonghua_input)

    # email 
    step_2_email_of_contact_person_input = driver.find_element_by_id("step_2_email_of_contact_person")
    step_2_email_of_contact_person_input.send_keys(email)

    # contact name
    step_2_name_of_contact_person_input = driver.find_element_by_id("step_2_name_of_contact_person")
    step_2_name_of_contact_person_input.send_keys(contact_name)


    # phone no
    step_2_tel_for_sms_notif_input = driver.find_element_by_id("step_2_tel_for_sms_notif")
    step_2_tel_for_sms_notif_input.send_keys(phone_no)

    step_2_tel_for_sms_notif_confirm = driver.find_element_by_id("step_2_tel_for_sms_notif_confirm")
    step_2_tel_for_sms_notif_confirm.send_keys(phone_no)

    # select the timeSlot
    selectAvaliableTimeSlot(driver)

    # next button
    step_2_form_control_confirm_button = driver.find_element_by_id("step_2_form_control_confirm")
    tryClickElement(driver, step_2_form_control_confirm_button)

    # page 4
    waitUntilPage4(driver)

    solveRecaptcha(driver, "g-recaptcha-response-1")

    # try to click the final button
    reference_element = driver.find_element_by_class_name('step_2_captchaCode_row')
    parent = reference_element.find_element_by_xpath('..')
    final_button = parent.find_element_by_tag_name("input")
    tryClickElement(driver, final_button)

    # suppose in arrive in here, will know the result
    time.sleep(99999)


def setSchedule():
    print("setting schedule")
    # schedule.every().monday.at("09:33").do(process_main)


def initRecaptcahWorker(worker_limit):
    for i in range(worker_limit):
        proc = Process(target=recaptchaWorker, args=(recaptcha_token_list, ))
        recaptcha_worker_list.append(proc)
        proc.start()


def checkTokenList():
    while True:
        print("current list : " + str(recaptcha_token_list))
        token = tryGetRecaptchaToken()
        print("can get token" + token)
        time.sleep(1)

def main():
    initRecaptcahWorker(1)
    # checkTokenList()
    process_main()

    # TODO: exact run
    # TODO: random select 

if __name__ == '__main__':   

    # global variables here
    manager = Manager()
    recaptcha_token_list = manager.list()
    main()
