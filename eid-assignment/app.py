from flask import Flask, request, jsonify
from utils import load_model, preprocess_input
from train_model import train_and_save_model
import os

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        input_data = request.get_json()
        model = load_model()
        df = preprocess_input(input_data)
        prediction = model.predict(df)[0]
        return jsonify({'predicted_discount': round(prediction, 3)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/train', methods=['POST'])
def retrain():
    try:
        train_and_save_model()
        return jsonify({'message': 'Model retrained successfully.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return "🎯 Discount Prediction API is running."

if __name__ == '__main__':
    if not os.path.exists('model/gbr_discount_model.pkl'):
        train_and_save_model()
    app.run(debug=True)
