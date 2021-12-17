#!/usr/bin/env python3

import time
import psycopg2
import pymongo


wait_db = True

while wait_db:
    try:
        connection = psycopg2.connect(
            dbname="mega_data", user="postgres", password="postgres", host="mega-postgres", port="5432")
        # connection.close()
        print("Postgres is up - continue")
        #client = pymongo.MongoClient('noa-mongo', serverSelectionTimeoutMS=1000)
        #client.server_info()
        #print("Mongo is up - continue")
        time.sleep(3)
        wait_db = False
    except psycopg2.OperationalError:
        print("Postgres is unavailable - waiting")
        wait_db = True
        time.sleep(1)
    except pymongo.errors.ServerSelectionTimeoutError:
        print("Mongo is unavailable - waiting")
        wait_db = True
        time.sleep(1)
