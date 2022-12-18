from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from datetime import date
import pymongo
import time

# create database
myclient = pymongo.MongoClient("mongodb://localhost:27017")
mydb = myclient["dininghallscraper"]
mycol = mydb["dailymenu"]


# create DB model
menu = {
    "date": str(date.today()),
    "meals": [],
    "categories_by_meal": [],
    "items_by_category": []
}


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://wlu.campusdish.com/LocationsAndMenus/FreshFoodCompany")


# functions
def click_see_more_tabs():
    see_more_buttons = driver.find_elements('xpath',
                                            '//button[@class="sc-bczRLJ sc-dkzDqf dxzycQ cCjZjN sc-jtcaXd kbmsoJ '
                                            'CollapseDeemphasizedButton"]')
    for b in range(len(see_more_buttons)):
        actions = ActionChains(driver)
        actions.move_to_element(see_more_buttons[b]).click(see_more_buttons[b]).perform()


def open_meal_click_meal_dropdown():
    # open meal selector
    driver.find_element('xpath', '//button[@class="sc-eGAhfa grdPAz DateMealFilterButton"]').click()
    time.sleep(0.6)

    # click meal time dropdown
    driver.find_element('xpath', '//div[@class=" css-19xsdnl-indicatorContainer"]').click()
    time.sleep(0.6)


meal_times_list = []
categories_list = []
item_by_category_by_meal_list = []

# items for DB
meals_dict_list = []

# MAYBE DO THIS WITH CLASSES????

open_meal_click_meal_dropdown()

# meals
meal_string = ""
meals = driver.find_element('xpath', '//div[@class=" css-wuv0vk"]')
meal = meals.find_elements('xpath', './/*')

for m in range(len(meal)):
    item_by_category_by_meal_list.append([])
    meals = driver.find_element('xpath', '//div[@class=" css-wuv0vk"]')
    meal = meals.find_elements('xpath', './/*')

    meal_times_list.append(meal[m].text)
    menu.update({"meals": meal_times_list})
    print(meal[m].text)

    actions = ActionChains(driver)
    actions.move_to_element(meal[m]).click(meal[m]).perform()
    time.sleep(0.6)

    # close menu
    driver.find_element('xpath', '//button[@class="sc-bczRLJ sc-gsnTZi gObyWR SlTeX Done"]').click()
    time.sleep(0.6)

    # open all 'see more' tabs
    click_see_more_tabs()

    # read categories for meal
    categories = driver.find_elements('xpath', '//div[@class="sc-cLFqLo dlJlMt MenuStation_no-categories"]')
    temp_category_list = []
    for c in range(len(categories)):
        category_titles = categories[c].find_elements('xpath', '//h1[@class="sc-cwpsFg fMYhBw StationHeaderTitle"]')
        title = category_titles[c]
        temp_category_list.append(title.text)
        print(f" - {title.text}")
        items = categories[c].find_elements('xpath', './/span[@class="sc-hZFzCs dgVUGD HeaderItemNameLink"]')
        item_by_category_by_meal_list[m].append([])
        # add items from each category
        for i in range(len(items)):
            item = items[i]
            item_by_category_by_meal_list[m][c].append(item.text)
            menu.update({"items_by_category": item_by_category_by_meal_list})
            print(f"    - {item.text}")

    categories_list.append(temp_category_list)
    menu.update({"categories_by_meal": categories_list})

    # close all 'see less' tabs
    click_see_more_tabs()

    open_meal_click_meal_dropdown()

driver.close()

print(meal_times_list)
print(categories_list)
print(item_by_category_by_meal_list)

mycol.delete_many({})

mycol.insert_one(menu)
print(menu)
