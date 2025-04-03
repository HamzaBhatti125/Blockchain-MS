import joblib

# Load the pre-trained fare prediction model
model = joblib.load('models/fare_prediction_model.pkl')

def predict_fare(input_data):
    features = [input_data['x1_hour'], input_data['x2_passenger_count'], input_data['x3_vehicle_count'],
                input_data['x4_weather_condition'], input_data['x5_day_type'], input_data['occupancy_rate'],
                input_data['dayofweek']]
    
    predicted_fare = model.predict([features])
    return predicted_fare[0]
