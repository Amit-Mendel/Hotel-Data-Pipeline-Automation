\# End-to-End Hotel Reservation Data Pipeline \& QA Automation


An enterprise-grade, End-to-End project integrating \*\*Data Engineering\*\*, \*\*QA Automation \& Web Scraping\*\*, and \*\*Business Intelligence (BI)\*\*.

\---


\##  Tech Stack \& Architecture



\- \*\*Language:\*\* Python 3.x

\- \*\*Data Engineering:\*\* Pandas, SQLAlchemy, PyODBC

\- \*\*Database:\*\* Microsoft SQL Server

\- \*\*QA Automation:\*\* Selenium WebDriver \& Web-Driver Manager

\- \*\*Business Intelligence:\*\* Tableau Desktop

\- \*\*Security:\*\* Python-Dotenv (Environment Variables)



\---



\##  Key Features



\### 1. Data Engineering \& SQL Pipeline

\- Modular database management system using Object-Oriented Programming (OOP).

\- Automated ingestion and processing of data directly into Microsoft SQL Server.



\### 2. QA Automation Bot

\- Selenium bot built with robust error handling and explicit waits (`WebDriverWait`).

\- Tracks validation milestones and uploads structured results into a dynamic audit table.



\### 3. Tableau Dashboard

\- Interactive executive metrics monitoring cancellation rates, room prices, and market trends.



\---



\##  Repository Structure



```text

├── data/                 # Raw data storage (HotelReservations\_cln.csv)

├── src/                  # Python source code

│   ├── database\_manager.py

│   ├── hotel\_automation.py

│   └── main.py

├── dashboards/           # Tableau packaged workbook (.twbx)

├── .gitignore            # Keeps environment credentials safe

├── requirements.txt      # Project dependencies

└── README.md             # Project documentation (This file)



Installation \& How to Run ##



Clone the repository to your local machine:

git clone https://github.com/Amit-Mendel/Hotel-Data-Pipeline-Automation



Install dependencies:

pip install -r requirements.txt



Configure your SQL Server name inside a local .env file:

DB\_SERVER=YOUR\_SERVER\_NAME

DB\_NAME=HotelReservations



Run the entire data pipeline:

python src/main.py



