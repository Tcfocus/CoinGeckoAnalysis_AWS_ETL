
import configparser
import psycopg2
from sqlQueries import deleteQueries, createQueries, loadQueries

def delete_tables(cur, conn):
    """Running SQL scripts that delete existing redshift tables
       Arguments:
       curr -- The database cursor object for accessing data
       conn -- the connection to the database
       """
    for query in deleteQueries:
        try:
            cur.execute(query)
            conn.commit()
            print(f"\nRunning: {query}")
        except psycopg2.Error:
            print("Error: Copying into staging tables")
            raise

def create_tables(cur, conn):
    """Running SQL scripts that create tables in Redshit
       Arguments:
       curr -- The database cursor object for accessing data
       conn -- the connection to the database
       """
    for query in createQueries:
        try:
            cur.execute(query)
            conn.commit()
            print(f"\nRunning: {query}")
        except psycopg2.Error:
            print("Error: Copying into staging tables")
            raise

def load_tables(cur, conn):
    """Running SQL scripts that load data from s3 into redshift tables
       Arguments:
       curr -- The database cursor object for accessing data
       conn -- the connection to the database
       """
    for query in loadQueries:
        try:
            cur.execute(query)
            conn.commit()
            print(f"\nRunning: {query}")
        except psycopg2.Error:
            print("Error: Copying into staging tables")
            raise


def main():
    """
    - Configuration file is read.

    - Establishes connection with the coingeckodatabase and gets
    cursor to it.

    - Runs queries in Redshift to delete existing tables, create new tables, and load data from S3.

    - Closes the connection at the end.
    """

    # read config
    config = configparser.ConfigParser()
    config.read('aws.cfg')

    # set process status
    success = False
    conn = None
    try:
        # connect database
        conn = psycopg2.connect("host={} dbname={} user={} password={} \
                                port={}".format(*config['CLUSTER'].values()))
        # create cursor
        cur = conn.cursor()

        #delete existing tables
        delete_tables(cur, conn)

        #create new tables
        create_tables(cur, conn)

        # copy data into tables
        load_tables(cur, conn)

        # change process status
        success = True
        print("SQL queries run successfully.")
    except psycopg2.Error as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()
            print("Connection Closed")
        if success:
            print('Process succeeded')
        else:
            print('Process failed')


if __name__ == "__main__":
    main()