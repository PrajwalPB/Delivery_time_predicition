import os
import sys
import pickle
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score,mean_absolute_error,mean_squared_error
import mysql.connector as conn
from sqlalchemy import create_engine
from pymongo import MongoClient
import pymysql

from src.exception import CustomException
from src.exception import MongoDBError
from src.exception import MySQLDatabaseError
from src.logger import logging
import boto3
from botocore.exceptions import ClientError
import json




def save_object(file_path,obj):
    try:

        dir_path = os.path.dirname(file_path)

        os.makedirs(dir_path,exist_ok=True)
        with open(file_path,"wb") as file_obj:
            pickle.dump(obj,file_obj)


    except Exception as e:
        logging.info("Error while dumping pickle file")
        raise CustomException(e,sys)
    



def evaluate_model(X_train,y_train,X_test,y_test,models):
    try:
        report = {}
        for i in range(len(models)):
            model = list(models.values())[i]

            model.fit(X_train,y_train)

            y_test_pred = model.predict(X_test)

            test_model_score = r2_score(y_test,y_test_pred)
            report[list(models.keys())[i]] =  test_model_score
            
        return report
    except Exception as e:
        logging.info('Exception occured during model training')
        raise CustomException(e,sys)
    




# Function for loading the pickle file
def load_object(file_path):
    try:
        with open(file_path,'rb') as file_obj:
            return pickle.load(file_obj)
        
    except Exception as e:
        logging.info('Exception Occured in load_object pickle file')
        raise CustomException(e,sys)
    
#fetching secrets from aws secrets manager test
def get_secret():

    secret_name = "prajwal/dev/key"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']
    return secret
    # Your code goes here.

# Function for putting the Input of user and the prediction result into the mysql Database
def to_database(pred_input,results):
    try:
        DB_HOST = os.getenv("DB_HOST")
        #DB_PORT = os.getenv("DB_PORT")
        DB_NAME = os.getenv("DB_NAME")
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        if None in [DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]:
            raise Exception("Database environment variables are not set properly")
        #secret_string=get_secret()
        #secret_dict = json.loads(secret_string)
        #mysql_username = secret_dict.get("username")
        #mysql_password = secret_dict.get("password")
        pred_input['results']=results
        #engine = create_engine("mysql+pymysql://root:1234@localhost/delivery")
        engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")
        pred_input.to_sql('testdata',con=engine,if_exists='append',chunksize=1000,index=False)
        pred_input['results']=results
        logging.info("Data loggeg into testdata")
        engine.dispose()

    except pymysql.MySQLError as e:
        logging.info("Error Occured at databse stage")
        raise MySQLDatabaseError(str(e))

    

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
def to_mongodb(pred_input):
    try:
        secret_string=get_secret()
        secret_dict = json.loads(secret_string)
        mongodb_username = secret_dict.get("mongodb_username")
        mongodb_password = secret_dict.get("mongodb_password")
        mongodb_database = secret_dict.get("mongodb_database")
        uri = f"mongodb+srv://{mongodb_username}:{mongodb_password}@{mongodb_database}.idegko8.mongodb.net/?retryWrites=true&w=majority"
        # Replace 'your_connection_string' with your actual MongoDB Atlas connection string
        #client = MongoClient(uri)
        client = MongoClient(uri, server_api=ServerApi('1'))
        
        # Replace 'your_database_name' and 'your_collection_name' with your database and collection names
        db = client['test']
        collection = db['delivery_collection']

        to_insert = pred_input

        # Insert data into the collection
        collection.insert_one(to_insert)
        print("Data inserted into MongoDB successfully!")

        # Close the connection
        client.close()
    except Exception as e:
        raise MongoDBError(str(e))
    
    