import pandas as pd
import joblib
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import os

def train_and_save_model(csv_path='data/synthetic_fare_ai_dataset.csv', model_dir='model'):
    df = pd.read_csv(csv_path)

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['x1_hour'] = df['timestamp'].dt.hour
    df['dayofweek'] = df['timestamp'].dt.dayofweek
    df = df.drop(columns=['timestamp'])

    # X = df.drop(columns=['discount'])
    X = df[['x2_passenger_count', 'x3_vehicle_count', 'x4_weather_condition', 'x5_day_type', 'occupancy_rate', 'x1_hour', 'dayofweek']]
    y = df['discount']


    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = GradientBoostingRegressor()
    model.fit(X_train, y_train)

    print("Training columns:", X.columns.tolist())  # <-- Add this here


    y_pred = model.predict(X_test)
    print(f"MSE: {mean_squared_error(y_test, y_pred):.4f}")
    print(f"R2: {r2_score(y_test, y_pred):.4f}")

    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(model, os.path.join(model_dir, 'gbr_discount_model.pkl'))
    print("✅ Model trained and saved.")

if __name__ == "__main__":
    train_and_save_model()
