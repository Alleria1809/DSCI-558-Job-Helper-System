from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import csv
import pandas as pd
import time
from time import sleep

def main():
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

    '''states = ['Texas', 'Florida', 'Georgia', 'Alaska', 'Hawaii', 'Massachusetts', 'Ohio', 'Washington', 'Arizona', 'Virginia',
              'Colorado', 'Illinois', 'New Jersey', 'North Carolina', 'Michigan', 'Oregon', 'New York', 'Indiana', 'Utah',
              'Montana', 'Maryland', 'Louisiana', 'Missouri', 'Minnesota', 'Kentucky', 'Wisconsin', 'Tennessee', 'Nevada',
              'Connecticut', 'Maine', 'South Carolina', 'Alabama', 'Iowa', 'Oklahoma', 'New Mexico', 'Mississippi', 'Wyoming',
              'Arkansas', 'Kansas', 'West Virginia', 'Rhode Island', 'Delaware', 'Nebraska', 'Vermont', 'Idaho', 'New Hampshire',
              'South Dakota', 'North Dakota']'''
    categories = ['Data Scientist', 'HR', 'Lawyer', 'Artist', 'Web Designer', 'Mechanical Engineer', 'Salesman', 'Civil Engineer',
                  'Software Developer', 'Business Analyst', 'Automation Tester', 'Electrical Engineer', 'Operations Manager',
                  'Network Security Engineer', 'Product Manager']
    #head = ['job_title', 'company_name', 'company_location', 'work_method', "work_type", "job_description"]
    for c in categories[:1]:
        category = c.lower().replace(" ", "%20")
        print(category)
        #f = open(f'job_positions_{state}.csv', 'a', newline='')
        #csvwriter = csv.writer(f)
        #csvwriter.writerow(head)
        url2 = f'https://www.linkedin.com/jobs/search/?keywords={category}&location=United%20States&refresh=true'
        #url2 = f'https://www.linkedin.com/jobs/search/?location={state}%2C%20United%20States&refresh=true'
        browser.get(url2)
        browser.implicitly_wait(10)

        # Get all links for these offers
        links = []
        # Navigate 13 pages
        print('Links are being collected now.')
        try:
            for page in range(2, 22):
                print("page: ", page)
                time.sleep(1)
                jobs_block = browser.find_element(By.CLASS_NAME, 'scaffold-layout__list-container')
                jobs_list = jobs_block.find_elements(By.CSS_SELECTOR, '.jobs-search-results__list-item')

                for job in jobs_list:
                    all_links = job.find_elements(By.TAG_NAME, 'a')
                    for a in all_links:
                        if str(a.get_attribute('href')).startswith("https://www.linkedin.com/jobs/view") and a.get_attribute('href') not in links:
                            links.append(a.get_attribute('href'))
                        else:
                            pass
                    # scroll down for each job element
                    browser.execute_script("arguments[0].scrollIntoView();", job)

                print(f'Collecting the links in the page: {page - 1}')
                # go to next page:
                browser.find_element("xpath", f"//button[@aria-label='Page {page}']").click()
                time.sleep(2)
        except:
            pass
        print('Found ' + str(len(links)) + ' links for job offers')
        with open(f"./txtfile_category/links_{category}.txt", "w") as ff:
            for link in links:
                ff.write(f"{link}\n")
        '''job_title = ""
        company_name = ""
        company_location = ""
        work_method = ""
        work_type = ""
    
        i = 0
        j = 1
        # Visit each link one by one to scrape the information
        print('Visiting the links and collecting information just started.')
        for i in range(len(links)):
            print(i)
            browser.get(links[i])
            i = i + 1
            time.sleep(2)
            # Click See more.
            try:
                browser.find_element(By.CLASS_NAME, "artdeco-card__actions").click()
                time.sleep(2)
            except:
                pass
    
            # Find the general information of the job offers
            contents = browser.find_elements(By.CLASS_NAME, 'p5')
            for content in contents:
                try:
                    job_title = content.find_element(By.TAG_NAME, "h1").text
                except:
                    pass
                try:
                    company_name = content.find_element(By.CLASS_NAME, "jobs-unified-top-card__company-name").text
                except:
                    pass
                try:
                    company_location = content.find_element(By.CLASS_NAME, "jobs-unified-top-card__bullet").text
                except:
                    pass
                try:
                    work_method = content.find_element(By.CLASS_NAME, "jobs-unified-top-card__workplace-type").text
                except:
                    pass
                time.sleep(1)
    
            try:
                work_type = browser.find_element("xpath", "//li[contains(@class, 'jobs-unified-top-card__job-insight')][1]/span").text
            except:
                pass
            # Scraping the job description
            job_description = browser.find_element(By.CLASS_NAME, "jobs-box__html-content").text
            #print(job_title, company_name, company_location, work_method, work_type, job_description)
            csvwriter.writerow([job_title, company_name, company_location, work_method, work_type, job_description])
            print(f'{job_title}Scraping the Job Offer {j} DONE.')
            j += 1
        print("time: ", time.time()-starttime)
        f.close()'''

if __name__ == "__main__":
    main()