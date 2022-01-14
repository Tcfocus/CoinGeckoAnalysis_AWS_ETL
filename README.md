# CoinGeckoAnalysis_AWS_ETL

## ETL Pipeline - API data to AWS Redshift Data Warehouse

### Overview:

The purpose of this project is to create an ETL pipeline for visualizing and analyzing large sets of data. The data of interest is cryptocurrency data, which is retrieved from the CoinGecko API in JSON format. The data is then transformed and loaded into S3, and finally loaded into a Redshift Data Warehouse to allow for different queries and analyses to be performed.

## Initial Visualization
Tableau was used as the tool for visualizing the data and performing further exploration upon completition of the scripts.

![image](https://user-images.githubusercontent.com/46071768/149466021-4822f22d-7a92-43bf-912f-474e3dc663a5.png)
![image](https://user-images.githubusercontent.com/46071768/149466031-b1ff63a3-7f4e-4511-8499-949311d44d0e.png)

### Source Data:
Coingecko is a cryptocurrency tracking website that provides an API for independently sourced crypto data, including information on live prices, exchange columes, historical data, and more. This project focuses on lower market-cap coins, and two main API calls are used:
	1. /coins/markets = list of coins with current price, market cap, etc.
	2. /coins/{id}/market_chart = historical price and volume data for specified coins

### ETL Pipeline:
Python is the primary language utilized to create this pipeline, and SQL is used to perform DDL commands to define the database tables. Python interacts with AWS S3 via the boto3 Python package, and with Redshift via psycopg2.

The AWS (S3 and Redshift) cloud-based architecture was utilized due to its ability to scale if larger amounts of data are handled, as well as for it's simple integration with the pipeline and other tools.

The primary steps of the ETL pipeline are:  
	1. JSON data is retrived via API calls -- Coingecko API is called to access unique data about multiple tokens, as well as historical price and volume data. The two calls create two unique tables of data: CoinList (single record per coin with various fields), and CoinPrice (numerous rows of historical price/volume data for each coin)  
	2. The JSON data is cleaned up and converted into a CSV -- JSON-formatted information is provided by the API calls, which are then converted into dataframes to be cleaned and transformed.  
	3. The CSV's is uploaded to S3 for storage -- Two sets of CSV data are loaded in AWS S3 buckets.  
	4. Redshift tables are deleted and new ones are created to fit the data schema --The existing tables are dropped, and new tables are created on each run of the script.  
	5. The S3 data is loaded into Redshift -- The CSV's residing in S3 are loaded into their respective Redshift tables.  
	6. Create visuals and perform analysis via Tableau -- Analyze the top-performing assets, identify and trends, and continue to explore the data.  

Files and Running the scripts:
  * Prep: Update all relevant information in the aws.cfg file, including aws account information and table names.
  * The order in which to run the scripts is to first execute GetCoinDataToS3.py, followed by etl_S3toRedshift.py.

### Data schemas:
The finalized data schema is as follows, and the common field of 'id' is used as the primary key for both tables, as well as the foreign key for CoinPrice to relate to CoinList:

CoinList:
  * id VARCHAR PRIMARY KEY  
  * symbol VARCHAR  
  * name VARCHAR  
  * image VARCHAR  
  * current_price FLOAT  
  * market_cap BIGINT  
  * market_cap_rank INT  
  * fully_diluted_valuation FLOAT
  * total_volume DECIMAL
  * high_24h FLOAT
  * low_24h FLOAT
  * price_change_24h FLOAT
  * price_change_percentage_24h DECIMAL
  * market_cap_change_24h FLOAT
  * market_cap_change_percentage_24h DECIMAL
  * circulating_supply FLOAT
  * total_supply FLOAT
  * max_supply FLOAT
  * ath FLOAT
  * ath_change_percentage DECIMAL
  * ath_date VARCHAR
  * atl FLOAT
  * atl_change_percentage DECIMAL
  * atl_date VARCHAR
  * roi VARCHAR
  * last_updated VARCHAR
  * price_change_percentage_24h_in_currency DECIMAL
  * price_change_percentage_30d_in_currency DECIMAL
  * price_change_percentage_7d_in_currency DECIMAL

CoinPrice:
  * id VARCHAR PRIMARY KEY
  * date DATE
  * price FLOAT
  * volume FLOAT
  





