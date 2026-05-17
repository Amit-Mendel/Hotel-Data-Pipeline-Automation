import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from ReservationToSQL import DataBaseManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class HotelAutomation:
    def __init__(self):
        self.driver = None
        logging.info('Initializing Hotel Automation Bot..')

    def start_browser(self):
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service)
            self.driver.maximize_window()
            logging.info("Browser started successfully.")
        except Exception as e:
            logging.error(f'Failed to open browser: {e}')
            raise

    def navigate_to_site(self,url):
        if self.driver:
            logging.info(f'Navigating to {url}')
            self.driver.get(url)
        else:
            logging.error('Driver is Not Initializing')

    def login(self, username, password):
        try:
            wait = WebDriverWait(self.driver, 10)
            user_field = self.driver.find_element(By.ID, "username")
            user_field.send_keys(username)
            logging.info("Username entered.")

            pass_field = self.driver.find_element(By.ID, "password")
            pass_field.send_keys(password)
            logging.info("Password entered.")

            login_button = self.driver.find_element(By.ID, "login")
            login_button.click()
            logging.info("Login button clicked.")
        except Exception as e:
            logging.error(f'Login failed')
            raise

    def get_available_locations(self):
        try:
            location_element = self.driver.find_element(By.ID, "location")
            select = Select(location_element)
            all_options = select.options
            locations = [opt.get_attribute("value") for opt in all_options if opt.get_attribute("value") != ""]
            logging.info(f"Dynamic discovery: Found {len(locations)} locations on site.")
            return locations
        except Exception as E:
            logging.error(f'Failed to discover locations')

    def search_hotels(self, location, room_type):
        try:
            room_map = {
                "Room_Type 1": "Standard",
                "Room_Type 2": "Double",
                "Room_Type 3": "Deluxe",
                "Room_Type 4": "Super Deluxe",
                "Room_Type 5": "Standard",
                "Room_Type 6": "Double",
                "Room_Type 7": "Deluxe"
            }
            site_room_text = room_map.get(room_type, "Standard")
            wait = WebDriverWait(self.driver, 5)


            location_element = wait.until(EC.presence_of_element_located((By.ID, "location")))
            Select(location_element).select_by_value(location)
            room_type_element = self.driver.find_element(By.ID, "room_type")
            Select(room_type_element).select_by_visible_text(site_room_text)

            checkin_date = (datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y")
            checkout_date = (datetime.now() + timedelta(days=3)).strftime("%d/%m/%Y")
            in_date_field = self.driver.find_element(By.ID, "datepick_in")
            in_date_field.clear()
            in_date_field.send_keys(checkin_date)

            out_date_field = self.driver.find_element(By.ID, "datepick_out")
            out_date_field.clear()
            out_date_field.send_keys(checkout_date)

            logging.info(f'Selected: {location} | {room_type} | Dates={checkin_date}-{checkout_date}')
            self.driver.find_element(By.ID, "Submit").click()
            logging.info("Search submitted")
        except Exception as e:
            logging.error(f'Error during hotel search: {e}')
            raise

    def get_hotel_price(self):
        try:
            wait = WebDriverWait(self.driver, 5)
            if "No Hotels" in self.driver.page_source or "SearchHotel.php" in self.driver.current_url:
                logging.warning("No hotels found for this search. Skipping...")
                return None

            price_element = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//input[contains(@id, 'price_night') or contains(@name, 'price_night')]")))
            if price_element:
                price_text = price_element[0].get_attribute("value")
                import  re
                numeric_price = re.sub(r'[^\d.]', '', price_text)
                if numeric_price:
                    price_cleaned = float(numeric_price)
                    logging.info(f"Successfully extracted price from site: {price_cleaned}")
                    return price_cleaned

        except Exception as e:
            logging.error(f"Failed to extract price")
            return None



    def close_browser(self):
        if self.driver:
            self.driver.quit()
            logging.info('Browser closed')

if __name__ == "__main__":
    Demo_URL = "https://adactinhotelapp.com/"
    load_dotenv()
    db_server = os.getenv("DB_SERVER")
    db_name = os.getenv("DB_NAME")
    db = DataBaseManager(db_server, db_name)
    db.connect()
    query = """
    SELECT room_type_reserved, MAX(avg_price_per_room) AS avg_price_per_room 
    FROM reservations 
    GROUP BY room_type_reserved
    """
    test_data = db.get_query(query)

    if test_data is not None and not test_data.empty:
        print('Data from SQL loaded')
        audit_result = []
        bot = HotelAutomation()
        bot.start_browser()
        bot.navigate_to_site(Demo_URL)
        site_user = os.getenv("SITE_USER")
        site_pass = os.getenv("SITE_PASS")
        bot.login(site_user, site_pass)
        available_cities = bot.get_available_locations()
        if available_cities:
            for index, row in test_data.iterrows():
                room_type = row['room_type_reserved']
                sql_price = row['avg_price_per_room']

                current_city = available_cities[index % len(available_cities)]
                logging.info(f'Checking: {current_city} | {room_type}')

                bot.search_hotels(current_city, room_type)
                site_price = bot.get_hotel_price()
                if site_price is not None:
                    current_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    audit_result.append({
                        "City": current_city,
                        "Room Type": room_type,
                        "SQL Price": sql_price,
                        "Site Price": site_price,
                        "Variance": round(site_price - sql_price, 2),
                        "Audit_Date": current_now
                    })
                    print(f"    [SUCCESS] Found site price: {site_price} | Variance: {round(site_price - sql_price, 2)}")
                else:
                    logging.warning(f"Skipping report for {current_city} - No price found on site.")

                bot.navigate_to_site('https://adactinhotelapp.com/SearchHotel.php')

                time.sleep(2)
        bot.close_browser()

        print("\n" + "=" * 50)
        print("         FINAL QA AUDIT REPORT")
        print("=" * 50)

        if audit_result:
            report_df = pd.DataFrame(audit_result)
            print(report_df.to_string(index=False))
            db.save_df_to_sql(report_df, "QA_Audit_Results")
        else:
            print("   The report is empty. All combinations yielded no results on site.")
            print("=" * 60)
        print("=" * 50)