import os
import sys
import pickle
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score,mean_absolute_error,mean_squared_error
import mysql.connector as conn
from sqlalchemy import create_engine


from src.exception import CustomException
from src.logger import logging






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
    


# Function for putting the Input of user and the prediction result into the mysql Database
def to_database(pred_input,results):
    try:
        pred_input['results']=results
        engine = create_engine("mysql+pymysql://{user}:{pw}@database-1.cfaegq7desqu.us-east-1.rds.amazonaws.com/{db}".format(user="admin",pw="12345678",db="delivery"))
        pred_input.to_sql('testdata',con=engine,if_exists='append',chunksize=1000,index=False)
        pred_input['results']=results
        logging.info("Data loggeg into testdata")
        engine.dispose()

    except Exception as e:
        logging.info("Error Occured at databse stage")
        raise CustomException(e,sys)

    