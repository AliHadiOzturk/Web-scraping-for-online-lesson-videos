import json
import time
import urllib.request
from json.decoder import JSONDecoder
from json.encoder import JSONEncoder
from os import mkdir, path

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Course:
    def __init__(self, title, href):
        self.title = title
        self.href = href


class CourseEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class CourseRecord:
    def __init__(self, id, date, duration):
        self.date = date
        self.duration = duration
        self.id = id


def execute_js_click(driver, element):
    driver.execute_script("arguments[0].click();", element)


def wait(driver, element, by: By):
    return WebDriverWait(driver, 50).until(
        EC.presence_of_element_located((by, element)))


def download_video(url, path):
    print("Downloading video")
    urllib.request.urlretrieve(url, path)


def find_page_links(driver):
    try:
        return driver.find_elements_by_xpath(
            "//*[@id=\"main-content\"]/footer/ol/li")
    except Exception:
        pass


filesPath = "C:/Users/aliha/Desktop/Dersler/"

driver = webdriver.Chrome("chromedriver.exe")
driver.get("https://ekampus.ankara.edu.tr/login/index.php")

username = driver.find_element_by_id("username")
username.send_keys("")

pwd = driver.find_element_by_id("password")
pwd.send_keys("")
pwd.send_keys(Keys.ENTER)


elements = driver.find_elements_by_xpath(
    "/html/body/div[4]/div/div[1]/div[3]/div/div/div/div/ul/li[2]/ul/li")

courseList = []

for element in elements:
    a = element.find_element_by_tag_name("a")
    title = a.get_attribute("title")
    href = a.get_attribute("href")

    courseList.append(Course(title, href))

# for idx, data in enumerate(courseList):
#     print("Courses:")
#     print(str(idx) + " - "+data.title)

#print(json.dumps(courseList, indent=4, cls=CourseEncoder))

disabledCourses = input("Select to disable courses : ")

disabledCourses = disabledCourses.split(",")

for idx in disabledCourses:
    courseList.pop(int(idx))


# print("After deleted --------------")
# print(json.dumps(courseList, indent=4, cls=CourseEncoder))


for course in courseList:
    print("Checking for - >", course.title)
    pathToWrite = filesPath+course.title
    if not path.exists(pathToWrite):
        mkdir(pathToWrite)

    driver.get(course.href)
    virtualClassLink = driver.find_element_by_xpath(
        "/html/body/div[4]/div/div[2]/div[3]/div/div/section[1]/div/div/div/ul/li[1]/div[3]/ul/li[3]/div/div/div[2]/div/a").get_attribute("href")
    driver.get(virtualClassLink)

    iframe = driver.find_element_by_id("contentframe")

    driver.get(iframe.get_attribute("src"))

    driver.implicitly_wait(5)

    driver.find_element_by_id("side-menu-toggle").click()

    button = driver.find_element_by_xpath(
        "/html/body/div[1]/div/div[1]/aside/div/nav/ul/li[3]/a").click()
    # ActionChains(driver).move_to_element(button).click(button).perform()

    # WebDriverWait(driver, 10).until(EC.presence_of_element_located(
    #     (By.XPATH, "/html/body/div[1]/div/div[1]/aside/div/nav/ul/li[3]/a"))).click()

    driver.find_element_by_xpath(
        "/html/body/div[1]/div/div[1]/main/div[1]/div[1]/div/div[1]/div/button").click()

    driver.find_element_by_xpath(
        "/html/body/div[1]/div/div[1]/main/div[1]/div[1]/div/div[1]/div/ul/li[2]/button").click()
    datePicker = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.XPATH, "/html/body/div[1]/div/div[1]/main/div[1]/div[1]/div/div[1]/div/form/div[1]/input")))
    datePicker.clear()
    datePicker.send_keys("1.09.2020")

    input()

    time.sleep(5)

    pageLinks = []
    pageLinkCount = 0

    pageLinks = find_page_links(driver)

    morePages = False

    for pageLink in pageLinks:
        if "..." in pageLink.text:
            morePages = True

    count = 0
    if len(pageLinks) > 0:
        if morePages:
            pageLinkCount = len(pageLinks)-3
        else:
            pageLinkCount = len(pageLinks)-2

    while True:

        count += 1
        pageLinkCount -= 1

        trElements = driver.find_elements_by_xpath(
            "/html/body/div[1]/div/div[1]/main/div[1]/div[2]/table/tbody/tr")
        records = []

        trElements = driver.find_elements_by_xpath(
            "/html/body/div[1]/div/div[1]/main/div[1]/div[2]/table/tbody/tr")

        filePath = filesPath+"/"+course.title

        for tr in trElements:
            # tr.find_element_by_class_name("date")
            buttons = tr.find_elements_by_tag_name("button")
            # driver.find_element_by_tag_name
            try:
                btn = tr.find_element_by_tag_name("button")
                execute_js_click(driver, btn)
                # driver.execute_script("arguments[0].click();", btn)
            except NoSuchElementException:
                continue

            buttons = tr.find_elements_by_tag_name("button")

            buttonToClick = ''
            for button in buttons:
                if "izleyin" in button.text:
                    buttonToClick = button
                    execute_js_click(driver, buttonToClick)
                    # driver.execute_script(
                    #     "arguments[0].click();", buttonToClick)
                    break

            id = tr.find_element_by_xpath("td[1]/button/bdi[2]").text
            date = tr.find_element_by_xpath("td[2]/div/span[2]/span").text
            duration = tr.find_element_by_xpath("td[3]/span[2]").text
            records.append(CourseRecord(id, date, duration))

            driver.switch_to.window(driver.window_handles[-1])

            video_url = ''
            time.sleep(5)
            try:
                video_url = wait(
                    driver, "video", By.TAG_NAME).get_attribute("src")

                # = driver.find_element_by_tag_name(
                #   "video").get_attribute("src")
            except Exception:
                execute_js_click(driver, buttonToClick)
                driver.switch_to.window(driver.window_handles[-1])
                video_url = wait(
                    driver, "video", By.TAG_NAME).get_attribute("src")

            videoName = "{}-{}-{}-{}"
            videoName = videoName.format(course.title,
                                         id, date.replace(":", "").replace(".", ""), duration.replace(":", ""))

            filePath = pathToWrite+"/"+videoName+".mp4"
            for x in range(10):
                try:
                    download_video(video_url, filePath)
                    # urllib.request.urlretrieve(video_url, filePath)
                    break
                except Exception:
                    continue

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        if pageLinkCount <= 0 and morePages == False:
            break
        else:
            time.sleep(5)
            if morePages:
                pageLinks[-1].click()
                pageLinks = find_page_links(driver)
                pageLinkCount = len(pageLinks)-3
            else:
                pageLinks[-2].click()

        # print(records.__len__())


print("")
