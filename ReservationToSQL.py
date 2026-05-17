import logging
from sqlalchemy import create_engine
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class DataBaseManager:
    def __init__(self,server,database):
        self.server = server
        self.database = database
        self.engine = None

        self.connection_url = f"mssql+pyodbc://@{self.server}/{self.database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"

    def connect(self):
        try:
            self.engine = create_engine(self.connection_url)
            with self.engine.connect() as conn:
                logging.info(f"Connected successfully to {self.database}")
        except Exception as e:
            logging.error(f"Could not connect to SQL server: {e}")

    def upload_csv_to_sql(self, csv_path, table_name):
        try:
            logging.info(f"Starting upload: Reading {csv_path}")
            df = pd.read_csv(csv_path)
            logging.info(f"Injecting {len(df)} rows into table {table_name}..")
            df.to_sql(table_name, con=self.engine, if_exists='replace', index = False)
            logging.info('Uploaded successfully')
        except FileNotFoundError:
            logging.error(f"The file {csv_path} was not found. check the file path.")
        except Exception as e:
            logging.error(f"Error was occurred during upload: {e}")

    def get_query(self, query):
        try:
            logging.info(f'Executing query: {query}')
            result_df = pd.read_sql(query, con=self.engine)
            return result_df
        except Exception as e:
            logging.error(f'Error was occurred during executing: {e}')
            return None

    def save_df_to_sql(self, df, table_name):
        try:
            df.to_sql(table_name, con=self.engine, if_exists='replace', index='false')
            print(f"\n[DB SUCCESS] Table '{table_name}' was successfully saved to SQL Server!")
        except Exception as e:
            print(f"\n[DB ERROR] Failed to save table to SQL: {e}")

if __name__ == "__main__":
    db = DataBaseManager(r"AMITLAPTOP\SQLEXPRESS", "Hotel Project")
    db.connect()
    db.upload_csv_to_sql('HotelReservations.csv', 'reservations')

    test_query = "SELECT avg(avg_price_per_room) AS average_price FROM reservations"
    data = db.get_query(test_query)
    if data is not None:
        avg_price = data.iloc[0]['average_price']
        print(f"\n--- SUCCESS ---")
        print(f"The average price is: {avg_price:.2f}")
