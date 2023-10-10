from flask import Flask,request,render_template,jsonify
from src.pipeline.prediction_pipeline import CustomData,PredictPipeline
from src.logger import logging
from src.utils import to_database
from src.utils import to_mongodb
from src.exception import CustomException
from src.exception import MySQLDatabaseError
from src.exception import MongoDBError




application = Flask(__name__)

app = application

# MySQL database error handler
@app.errorhandler(MySQLDatabaseError)
def handle_mysql_database_error(error):
    return render_template('mysql_error.html', error=error), 500

# MongoDB error handler
@app.errorhandler(MongoDBError)
def handle_mongodb_error(error):
    return render_template('mongodb_error.html', error=error), 500

@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/predict',methods = ['GET','POST'])
def predict_datapoint():
    if request.method == 'GET':
        return render_template('form.html')
    else:
        data = CustomData(
             Delivery_person_Age = int(request.form.get('Delivery_person_Age')),
             Delivery_person_Ratings = float(request.form.get('Delivery_person_Ratings')),
             Restaurant_latitude  = float(request.form.get('Restaurant_latitude')),
             Restaurant_longitude = float(request.form.get('Restaurant_longitude')),
             Delivery_location_latitude  = float(request.form.get('Delivery_location_latitude')),
             Delivery_location_longitude = float(request.form.get('Delivery_location_longitude')),
             Vehicle_condition = int(request.form.get('Vehicle_condition')),
             multiple_deliveries = int(request.form.get('multiple_deliveries')),
             Weather_conditions = request.form.get('Weather_conditions'),
             Road_traffic_density = request.form.get('Road_traffic_density'),
             Type_of_order = request.form.get('Type_of_order'),
             Type_of_vehicle  =  request.form.get('Type_of_vehicle'),
             Festival = request.form.get('Festival'),
             City = request.form.get('City')
        )

    

    final_new_data = data.get_data_as_dataframe()
    logging.info(f'Input Pred data gathered {final_new_data.to_string}')
    print(final_new_data)
    pred_pipeline = PredictPipeline()
    pred = pred_pipeline.predict(final_new_data)
    results = round(pred[0],2)
    #print(results)
    to_database(final_new_data,results)
    data_dict = final_new_data.iloc[0].to_dict()
    data_dict['predicted_result'] = results
    #print(data_dict)
    to_mongodb(data_dict)





    return render_template('result.html',final_result = results)












if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)