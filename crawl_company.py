from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import jsonlines
import time
import json
from time import sleep

def main():
    start_urls = []
    '''with open('txtfile_category/company_url.txt', "r") as f:
        for line in f:
            if line != None:
                start_urls.append(line)'''
    with jsonlines.open('jsonfile_category/company_url.jsonl', "r") as f:
        for line in f:
            if line['company_url'] != "":
                start_urls.append(line['company_url'])
    print(len(start_urls))

    chrome_options = Options()
    #chrome_options.add_argument('--headless')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    browser = webdriver.Chrome(executable_path='chromedriver.exe', chrome_options=chrome_options)
    # login
    url1 = "https://www.linkedin.com/"
    browser.get(url1)
    browser.implicitly_wait(10)
    username = browser.find_element("xpath", '//*[@id="session_key"]')
    password = browser.find_element("xpath", '//*[@id="session_password"]')
    username.send_keys("18801342429@163.com")
    password.send_keys("KELLY990520@kelly")
    login_btn = browser.find_element("xpath", "//button[@class='sign-in-form__submit-button']")
    sleep(1)
    login_btn.click()

    f = open('jsonfile_category/companies1.jsonl', 'wb')
    i = 1
    for url in start_urls:
        url = url.split("?", 1)[0]+'/about'
        print(url)
        browser.get(url)
        browser.implicitly_wait(5)
        try:
            desc = browser.find_element('xpath', '//section[@class="artdeco-card p5 mb4"]/p').text
        except:
            desc = ""
        try:
            info = browser.find_element('xpath', '//section[@class="artdeco-card p5 mb4"]/dl').text
        except:
            info = ""
        try:
            element = browser.find_element('xpath', '//div[@class="org-top-card-primary-content__logo-container"]/img[@src]')
            img_url = element.get_attribute("src")
            print(img_url)
        except:
            img_url = ""
        c_dict = {'desc': desc, 'info': info, "url": url, 'img_url': img_url}
        line = json.dumps(c_dict, ensure_ascii=False) + "\n"
        f.write(line.encode("utf-8"))
        time.sleep(2)
        print(i)
        i+=1

if __name__ == "__main__":
    main()