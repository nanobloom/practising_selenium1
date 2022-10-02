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

class Scraper(webdriver.Chrome):
    def __init__(self, time=10, path=r"/opt/chromedriver"):
        self.time = time
        self.path = path
        if self.path not in os.environ['PATH']:
            os.environ['PATH'] += os.pathsep + self.path    
        super().__init__()
        self.maximize_window()
        self.implicitly_wait(self.time)


    def login_Morele(self):
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


    def filtering_Morele(self):
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


    def GPU_Morele(self, model):
        def getting_details_Morele():
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

        if model.startswith('30'):
            down_arrow = self.find_element(By.CSS_SELECTOR, 'span[data-fcollection-toggle=".f-collection-item-8143-2835"]')
            prefix = 'GeForce RTX'
        else:
            down_arrow = self.find_element(By.CSS_SELECTOR, 'span[data-fcollection-toggle=".f-collection-item-8143-2837"]')
            prefix = 'Radeon RX'
        down_arrow.click()

        try:        
            GPU_selection = self.find_element(By.CSS_SELECTOR, f'div[data-name="{prefix} {model}"')
        except Exception as e:
            if e.__class__.__name__ == 'NoSuchElementException':
                print(f'Cannot find {prefix} {model}')
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
            cards = getting_details_Morele()
        except:
            cards = getting_details_Morele()
        
        return cards


    def CPU_Morele(self):
        field = self.find_element(By.LINK_TEXT, 'Procesory')
        field.click()


    def SSD_Morele(self):
        field = self.find_element(By.LINK_TEXT, 'Dyski SSD')
        field.click()
      

    def choose_category_Morele(self, item, model):
        self.filtering_Morele()
        if item == 'GPU':
            return self.GPU_Morele(model)
        if item == 'CPU':
            self.CPU_Morele()
        if item == 'SSD':
            self.SSD_Morele()


    def injecting_into_database_Morele(driver, dictio, model):
        dt = datetime.now().strftime("%d %B %Y")
        if model.startswith('30'):
            prefix = 'GeForce RTX'
        else:
            prefix = 'Radeon RX'
        table_name = f'{dt} - {prefix} {model}'

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


    def filtering_xkom(self):
        self.get('https://www.x-kom.pl/')

        def getting_details_xkom():
            product_list_parent = self.find_element(By.CSS_SELECTOR, 'div[id="listing-container"]')
            product_list = product_list_parent.find_elements(By.CSS_SELECTOR, 'div[class="sc-1s1zksu-0 dzLiED sc-162ysh3-1 irFnoT"]')
            cards = {}
            for item in product_list:
                name = item.find_element(By.CSS_SELECTOR, 'h3[class="sc-16zrtke-0 kGLNun sc-1yu46qn-9 feSnpB"]')
                name = name.get_attribute('title')
                name = name.lstrip('Karta graficzna ')
                price = item.find_element(By.CSS_SELECTOR, 'span[data-name="productPrice"]')
                price = price.get_attribute('innerHTML')
                price = price.split(',')[0].replace(" ", "") + price.split(',')[1].lstrip('00')
                cards[name] = price
            return cards

        try:
            WebDriverWait(self, 15).until(expected_conditions.element_to_be_clickable((
                By.CSS_SELECTOR, 'h3[class="sc-an0bcv-3 drEWFj"]')))
            self.find_element(By.CSS_SELECTOR, 'button[class="sc-15ih3hi-0 sc-1p1bjrl-8 iOlyHf"]').click()
            toggles = self.find_elements(By.CSS_SELECTOR, 'div[class="sc-1s6540e-2 PJFwA"]')
            for toggle in toggles:
                if toggle.get_attribute('style') == "transform: translateX(16px);":
                    toggle.click()
            save = self.find_element(By.CSS_SELECTOR, 'button[class="sc-15ih3hi-0 sc-1p1bjrl-8 iOlyHf"]')
            save.click()
        except:
            pass

        action = ActionChains(self)
        hover_fields = self.find_elements(By.CSS_SELECTOR, 'div[class="sc-13hctwf-5 bdvNWx"]')
        for hover_field in hover_fields:
            if hover_field.get_attribute('innerHTML') == 'Podzespoły komputerowe':
                action.move_to_element(hover_field).perform()

        item_list = self.find_elements(By.CSS_SELECTOR, 'p[class="sc-fzqPZZ ehVgFZ sc-a8nzxk-4 cYFNXB"]')
        for item in item_list:
            if item.get_attribute('innerHTML') == 'Karty graficzne':
                item.click()
        
        svg = self.find_element(By.XPATH, "//span[text()[contains(., 'NVIDIA GeForce')]]/../../button[@class='sc-15ih3hi-0 sc-cs8ibv-1 krqPaL']/span[@class='sc-1tblmgq-0 sc-1tblmgq-4 fmHGFd sc-cs8ibv-3 bHCpRh']/*[local-name() = 'svg']")
        svg.click()

        choose_model = self.find_element(By.XPATH, "//span[text()[contains(., 'GeForce RTX 3090 Ti')]]")
        choose_model.click()
        
        sorting_dropdown_menu = self.find_element(By.ID, "react-select-id2--value-item")
        self.execute_script("window.scrollTo(0,0);")
        sorting_dropdown_menu.click()

        ascending_price = self.find_element(By.CSS_SELECTOR, 'div[aria-label="Cena: od najtańszych"]')
        ascending_price.click()

        getting_details_xkom()




GPUs = ['3050', '3060', '3060 Ti', '3070', '3070 Ti', '3080', '3080 Ti', '3090', '3090 Ti', '6400', '6500 XT', '6600',
        '6600 XT', '6650 XT', '6700', '6700 XT', '6800', '6800 XT', '6900', '6900 XT', '6950 XT']

if __name__=='__main__':
    with Scraper() as bot:
        '''for GPU in GPUs:
            while True:
                try:
                    dictio = bot.choose_category_Morele(item='GPU', model=GPU)
                except Exception as e:
                    print(e)
                    continue
                bot.injecting_into_database_Morele(dictio, model=GPU)
                break'''
        bot.filtering_xkom()
        

