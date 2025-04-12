import pandas as pd
import joblib

MODEL_PATH = 'model/gbr_discount_model.pkl'

FEATURE_ORDER = [
    'x2_passenger_count',
    'x3_vehicle_count',
    'x4_weather_condition',
    'x5_day_type',
    'occupancy_rate',
    'x1_hour',
    'dayofweek'
]


def load_model():
    return joblib.load(MODEL_PATH)

def preprocess_input(data):
    df = pd.DataFrame([data])

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['x1_hour'] = df['timestamp'].dt.hour
    df['dayofweek'] = df['timestamp'].dt.dayofweek
    df = df.drop(columns=['timestamp'], errors='ignore')

    print("[Processed columns]", df.columns.tolist())
    print("[Expected order]", FEATURE_ORDER)

    df = df[FEATURE_ORDER]
    print("✅ Final preprocessed DataFrame:\n", df)
    return df
