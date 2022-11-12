import time
from collections import deque
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from openpyxl import Workbook


class Job:
    def __init__(self, title, company, location, description, link):
        self.title = title
        self.company = company
        self.location = location
        self.description = description
        self.link = link

    def __str__(self):
        return f"{self.title} - {self.company} - {self.location} - {self.link}"

    def checkHasVisaString(self):
        return "visa" in self.description.lower()


class GoogleCareer:

    def __init__(self, url):
        self.linkList = deque([])
        self.jobs = deque([])
        self.url = url
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                                       options=webdriver.ChromeOptions())
        self.driver.get(self.url)

    def findJobPostings(self):
        driver = self.driver
        driver.implicitly_wait(10)
        self.clickFirstJobPost()
        self.saveLinkResults()

        for link in self.linkList:
            driver.get(link)
            driver.implicitly_wait(10)
            self.jobs.append(
                Job(self.getJobTitle(), self.getCompanyName(), self.getJobLocation(), self.getJobDescription(), link))

        self.saveXlsxFile()

        self.driver.close()

    def clickFirstJobPost(self):
        driver = self.driver
        driver.implicitly_wait(10)

        searchResults = driver.find_element(By.ID, "search-results")
        searchResultsList = searchResults.find_elements(By.TAG_NAME, "li")
        searchResultsList[0].click()

    def saveLinkResults(self):
        driver = self.driver

        searchResults = driver.find_element(By.ID, "search-results-sidebar")
        searchResultsList = searchResults.find_elements(By.XPATH, "li")

        for idx in range(1, len(searchResultsList)):
            self.linkList.append(searchResultsList[idx].find_element(By.TAG_NAME, "a").get_attribute("href"))

    def getJobTitle(self):
        driver = self.driver
        jobTitle = driver.find_element(By.XPATH,
                                       '//*[@id="jump-content"]/div[1]/div/div[2]/main/div/div/div[1]/div[1]/h1')
        return jobTitle.text

    def getJobDescription(self):
        driver = self.driver
        jobContent = driver.find_element(By.XPATH,
                                         '//*[@id="jump-content"]/div[1]/div/div[2]/main/div/div/div[1]/div[2]')
        return jobContent.text

    def getCompanyName(self):
        driver = self.driver
        companyName = driver.find_element(By.XPATH,
                                          '//*[@id="jump-content"]/div[1]/div/div[2]/main/div/div/div[1]/div[1]/ul[2]/li[1]/span')
        return companyName.text

    def getJobLocation(self):
        driver = self.driver
        jobLocation = driver.find_element(By.XPATH,
                                          '//*[@id="jump-content"]/div[1]/div/div[2]/main/div/div/div[1]/div[1]/ul[2]/li[2]')
        return jobLocation.text

    def saveXlsxFile(self):
        write_wb = Workbook()
        write_ws = write_wb.active

        write_ws.append(["Title", "Company", "Location", "Description", "Link", "visa"])

        for job in self.jobs:
            write_ws.append([job.title, job.company, job.location, job.description, job.link, job.checkHasVisaString()])

        write_wb.save("jobs.xlsx")
        pass


if __name__ == '__main__':
    start = time.time()
    GoogleCareer('https://careers.google.com/jobs/results/').findJobPostings()
    print(time.time() - start, "초 소요됨")
