"""
SQL statements to create tables, insert data into them, perform analysis and more.
"""
import configparser


# CONFIG -------------------------------------------------------------------

config = configparser.ConfigParser()
config.read('aws.cfg')

COIN_LIST_DATA = config.get('S3', 'COIN_LIST_DATA')
COIN_PRICE_DATA = config.get('S3', 'COIN_PRICE_DATA')
ARN = config.get('IAM_ROLE', 'ARN')


#Drop existing tables in redshift
coinListTableDrop = "DROP TABLE IF EXISTS coinlisttable CASCADE;"
coinPriceTableDrop = "DROP TABLE IF EXISTS coinpricetable;"



#Create table containing list of all coins
createCoinListTable = ("""
CREATE TABLE IF NOT EXISTS coinlisttable(
id VARCHAR PRIMARY KEY,
symbol VARCHAR,
name VARCHAR,
image VARCHAR,
current_price FLOAT,
market_cap BIGINT,
market_cap_rank INT,
fully_diluted_valuation FLOAT,
total_volume DECIMAL(12,1),
high_24h FLOAT,
low_24h FLOAT,
price_change_24h FLOAT,
price_change_percentage_24h DECIMAL(8,2),
market_cap_change_24h FLOAT,
market_cap_change_percentage_24h DECIMAL(8,2),
circulating_supply FLOAT,
total_supply FLOAT,
max_supply FLOAT,
ath FLOAT,
ath_change_percentage DECIMAL(8,2),
ath_date VARCHAR,
atl FLOAT,
atl_change_percentage DECIMAL(8,2),
atl_date VARCHAR,
roi VARCHAR,
last_updated VARCHAR,
price_change_percentage_24h_in_currency DECIMAL(8,2),
price_change_percentage_30d_in_currency DECIMAL(8,2),
price_change_percentage_7d_in_currency DECIMAL(8,2)
);
""")

#Create table containing list of daily prices for coins over a period of time
createCoinPriceTable = ("""
CREATE TABLE IF NOT EXISTS coinpricetable(
date DATE,
price FLOAT,
id VARCHAR PRIMARY KEY,
volume FLOAT,
FOREIGN KEY (id) REFERENCES coinlisttable(id)
);
""")

# copy data from s3 into redshift tables
coinListCopyToRedshift = f"""
COPY coinListTable FROM {COIN_LIST_DATA}
IAM_ROLE '{ARN}'
CSV
IGNOREHEADER 1
COMPUPDATE OFF
ROUNDEC;
"""

coinPriceCopyToRedshift = f"""
COPY coinPriceTable FROM {COIN_PRICE_DATA}
IAM_ROLE '{ARN}'
CSV
IGNOREHEADER 1
COMPUPDATE OFF;
"""

deleteQueries = (coinListTableDrop , coinPriceTableDrop)
createQueries = (createCoinListTable, createCoinPriceTable)
loadQueries = (coinListCopyToRedshift, coinPriceCopyToRedshift)