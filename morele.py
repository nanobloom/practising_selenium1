import os
import time
import sqlite3
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
#from selenium.common.exceptions import StaleElementReferenceException
#from selenium.common.exceptions import NoSuchElementException

class Morele(webdriver.Chrome):
    def __init__(self, time=10, path=r"/opt/chromedriver"):
        self.time = time
        self.path = path
        if self.path not in os.environ['PATH']:
            os.environ['PATH'] += os.pathsep + self.path    
        super().__init__()
        self.maximize_window()
        self.implicitly_wait(self.time)


    def login(self):
        self.get('https://www.morele.net/login')

        if self.find_element(By.LINK_TEXT, 'Nie pamiętam hasła'):
            username = os.environ['MORELE_USERNAME']
            username_field = self.find_element(By.ID, 'username')
            username_field.send_keys(username)

            password = os.environ['MORELE_PASSWORD']
            password_field = self.find_element(By.ID, 'password-log')
            password_field.send_keys(password)

            button = self.find_element(By.XPATH, '//*[@id="login_form"]/button')
            button.click()


    def filtering(self):
        self.get('https://www.morele.net/')

        try:
            WebDriverWait(self, 15).until(expected_conditions.element_to_be_clickable((
                By.CSS_SELECTOR, 'button[class="btn btn-secondary btn-secondary-outline btn-md close-cookie-box"]')))
            self.find_element(By.CSS_SELECTOR, 'button[class="btn btn-secondary btn-secondary-outline btn-md close-cookie-box"]').click()
        except:
            pass           

        hover_field = self.find_element(By.LINK_TEXT, 'Podzespoły komputerowe')
        action = ActionChains(self)
        action.move_to_element(hover_field).perform()


    def GPU(self, model):
        def getting_details():
            product_list_parent = self.find_element(By.CSS_SELECTOR, 'div[data-controller="product-list"]')
            product_list = product_list_parent.find_elements(By.CSS_SELECTOR, 'div[data-product-position]')
            cards = {}
            for item in product_list:
                name = item.get_attribute("data-product-name")
                name = name.lstrip("Karta graficzna ")
                name = name.split('(')[0]
                price = item.get_attribute("data-product-price")
                price = price.split('.')[0] + " zł"
                cards[name] = price
            return cards

        field = self.find_element(By.LINK_TEXT, 'Karty graficzne')
        field.click()

        time.sleep(3)
        down_arrow = self.find_element(By.CSS_SELECTOR, 'span[data-fcollection-toggle=".f-collection-item-8143-2835"]')
        down_arrow.click()

        try:        
            GPU_selection = self.find_element(By.CSS_SELECTOR, f'div[data-name="GeForce RTX {model}"')
        except Exception as e:
            if e.__class__.__name__ == 'NoSuchElementException':
                print(f'Cannot find GeForce RTX {model}')
                cards = {"none":"none"}
                return cards
            else:
                print(Exception)
                exit()
        GPU_selection.click()                        

        time.sleep(3)
        sorting_dropdown_menu = self.find_element(By.XPATH, "//button[contains(., 'Sortowanie')]")
        action = ActionChains(self)
        action.move_to_element(sorting_dropdown_menu).click().perform()

        ascending_price = self.find_element(By.CSS_SELECTOR, 'li[data-dropdown-value="price|asc"]')
        ascending_price.click()

        try:
            cards = getting_details()
        except:
            cards = getting_details()
        
        return cards


    def CPU(self):
        field = self.find_element(By.LINK_TEXT, 'Procesory')
        field.click()


    def SSD(self):
        field = self.find_element(By.LINK_TEXT, 'Dyski SSD')
        field.click()
      

    def choose_category(self, item, model):
        self.filtering()
        if item == 'GPU':
            return self.GPU(model)
        if item == 'CPU':
            self.CPU()
        if item == 'SSD':
            self.SSD()


    def injecting_into_database(driver, dictio, model):
        dt = datetime.now().strftime("%d %B %Y")
        table_name = f'{dt} - RTX {model}'

        con = sqlite3.connect('database.db')
        c = con.cursor()

        create_table_query = f'CREATE TABLE "{table_name}" (Graphics_Card, Price)'
        c.execute(create_table_query)

        inserting_query = f'INSERT INTO "{table_name}" VALUES (?,?)'
        
        for i in dictio:
            pair = (i, dictio[i])
            c.execute(inserting_query, pair)

        con.commit()
        con.close()


GPUs = ['3040', '3045', '3050', '3060', '3060 Ti', '3070', '3070 Ti', '3080', '3080 Ti', '3090', '3090 Ti']

if __name__=='__main__':
    with Morele() as bot:
        for GPU in GPUs:
            while True:
                try:
                    dictio = bot.choose_category(item='GPU', model=GPU)
                except Exception as e:
                    print(e)
                    continue
                bot.injecting_into_database(dictio, model=GPU)
                break
