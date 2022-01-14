from pycoingecko import CoinGeckoAPI
from datetime import datetime
import pandas as pd
import time
import boto3
from io import StringIO
import configparser

# initialize the client
cg = CoinGeckoAPI()

# Get lists of all coins w market data->transform df then insert into one large df
def getCoinListData():
    """
    Purpose: Get JSON from coingecko api call, and convert into a dataframe
    """
    coinListdf = pd.DataFrame()
    i = 0
    while i < 1: #use 10
        coinsMarketListJSON = cg.get_coins_markets(vs_currency = 'usd',
                                                page = 20, #use 3
                                                per_page = 25, #use 250
                                                price_change_percentage = '24h,7d,30d')
        outputdf = pd.DataFrame(coinsMarketListJSON)
        coinListdf = coinListdf.append(outputdf)
        i+=1
    return coinListdf


# *********Get json of coin price data + get a df to convert to csv for uploading into s3



# Get complete json of coin price
def getCoinPriceData(coinListdf):
    """
    Purpose: Get JSON from coingecko api call
    Arguments:
    coinListdf -- The output df from getCoinLitData function
    """

    coinPriceListJson = []
    numberOfRequests = 0
    loops = 0

    for id in coinListdf['id']:
        coinData = cg.get_coin_market_chart_by_id(id=id, vs_currency='usd', days=90, interval='daily')
        numberOfRequests += 1
        # add the id from the coinsMarketList because it does not come with the id
        coinData['id'] = id
        coinPriceListJson.append(coinData)
        if numberOfRequests == 45:
            print("Waiting 90 seconds to not exceed request limit...")
            numberOfRequests = 0
            loops += 1
            time.sleep(90)

    return coinPriceListJson

# create df from the complete json



def coinListToDF(coinPriceListJson):
    """
    Purpose: Convert JSON list obtained from getCoinPriceData function into a dataframe
    Arguments:
    coinMarketDataJSON -- The output json from getCoinPriceData function
    """
    #Create an empty dataframe
    coinPriceDF = pd.DataFrame()

    for coin in coinPriceListJson:
        print(coin['id'])
        for price in coin['prices']:
            price[0] = datetime.fromtimestamp(price[0] / 1e3)
            price[0] = datetime.date(price[0])

        dfCoins = pd.DataFrame(coin['prices'], columns=['date', 'price'])

        # set a column to be the id of the coin
        dfCoins['Id'] = coin['id']

        # Get volume data: create a list of the volume data and join it to price data
        coinVolume = coin['total_volumes']
        volumeList = []
        for volume in coinVolume:
            volumeList.append(volume[1])

        dfCoins['volume'] = volumeList

        # append to final df
        coinPriceDF = coinPriceDF.append(dfCoins)

    return coinPriceDF

# **************************Insert into AWS s3 bucket***************************

# function for uploading the dfs
def copy_to_s3(client, df, bucket, filepath):
    """
    Purpose: Function for uploading the dataframes into an S3 bucket
    """
    csv_buf = StringIO()
    df.to_csv(csv_buf, header=True, index=False)
    csv_buf.seek(0)
    client.put_object(Bucket=bucket, Body=csv_buf.getvalue(), Key=filepath)
    print(f'Copy {df.shape[0]} rows to S3 Bucket {bucket} at {filepath}, Done!')

def main():
    config = configparser.ConfigParser()
    config.read('aws.cfg')

    s3 = boto3.client('s3',
                    aws_access_key_id=config.get('AWS', 'KEY'),
                    aws_secret_access_key=config.get('AWS', 'SECRET'))

    coinListdf = getCoinListData()

    coinMarketDataJSON = getCoinPriceData(coinListdf)

    coinPricedf = coinListToDF(coinMarketDataJSON)

    # upload the coinlist df by first converting into csv then uploading
    copy_to_s3(client=s3, df=coinListdf, bucket='coingeckobucket', filepath='coinListData')

    # upload coin price df by first converting into csv then uploading
    copy_to_s3(client=s3, df=coinPricedf, bucket='coingeckobucket', filepath='coinPriceData')

if __name__ == "__main__":
    main()







