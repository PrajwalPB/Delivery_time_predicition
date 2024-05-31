# Create a Virtual Enviornment 
This is my first Data Science project.
conda create -p deliveryvenv python==3.8

# Activate virtual enviornment

conda activate delivery venv


# Installing all the libraries-requirements
pip install -r requirements.txt
# fro setup.py
python setup.py install     



sql Query
create databse delivery
create table testdata
(
 Delivery_person_Age INT,
 Delivery_person_Ratings FLOAT, 
 Restaurant_latitude FLOAT,
 Restaurant_longitude FLOAT,
 Delivery_location_latitude FLOAT,
 Delivery_location_longitude FLOAT,
 Vehicle_Condition INT,
 multiple_deliveries INT,
 Weather_conditions VARCHAR (20),
 Road_traffic_density VARCHAR (20),
 Type_of_order VARCHAR (20),
 Type_of_vehicle VARCHAR (20),
 Festival VARCHAR (5),
 City VARCHAR (20),
 results INT
 );