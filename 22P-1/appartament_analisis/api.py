from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
import pickle
import uvicorn
from typing import Dict, Any
from datetime import date

# Создание приложения FastAPI
app = FastAPI(
    title="API для предсказания недвижимости",
    description="API для предсказания цены и типа недвижимости",
    version="1.0.0"
)

# Загрузка моделей
try:
    with open('xgb_reg.pkl', 'rb') as f:
        regressor_model = pickle.load(f)

    with open('bagging_clf.pkl', 'rb') as f:
        classifier_model = pickle.load(f)

    print("✅ Модели успешно загружены")

    # Получаем имена признаков из моделей
    try:
        regressor_features = regressor_model.feature_names_in_
        print(f"Признаки регрессора ({len(regressor_features)}): {list(regressor_features)}")
        print(regressor_features)
    except:
        regressor_features = None
        print("Не удалось получить признаки регрессора")

    try:
        classifier_features = classifier_model.feature_names_in_
        print(f"Признаки классификатора ({len(classifier_features)}): {list(classifier_features)}")
    except:
        classifier_features = None
        print("Не удалось получить признаки классификатора")

except Exception as e:
    print(f"Ошибка загрузки моделей: {e}")
    regressor_model = None
    classifier_model = None
    regressor_features = None
    classifier_features = None


# Модель данных для запроса
class PropertyFeatures(BaseModel):
    listing_type: int
    tom: int
    building_age: int
    total_floor_count: int
    floor_no: int
    room_count: int
    size: int
    heating_type: int  # Изменено с str на int
    price: float
    address_encoded: int = 0
    start_year: int = 0
    start_month: int = 0
    start_day: int = 0
    end_year: int = 0
    end_month: int = 0
    end_day:int = 0
    heating_type_ecnoded: int = 0
    sub_type_encoded: int = 0


# Корневой эндпоинт
@app.get("/")
async def root():
    return {
        "message": "API для предсказания недвижимости",
        "version": "1.0.0",
        "endpoints": {
            "POST /predict": "Предсказание цены и типа недвижимости"
        }
    }


# Эндпоинт для предсказаний
@app.post("/predict")
async def predict_price_and_type(features: PropertyFeatures) -> Dict[str, Any]:
    if not regressor_model or not classifier_model:
        return {
            "error": "Модели не загружены",
            "predicted_price": 0,
            "predicted_subtype": -1
        }

    
    # Создаем словарь со всеми признаками
    feature_dict = {
        'total_floor_count': features.total_floor_count,
        'listing_type': features.listing_type,
        'tom': features.tom,
        'building_age': features.building_age,
        'floor_no': features.floor_no,
        'room_count': features.room_count,
        'size': features.size,
        'heating_type': features.heating_type,
        'price': features.price,
        "address_encoded" : features.address_encoded,
        'start_day': features.start_day,
        'start_year': features.start_year,
        'start_month': features.start_month,
        'end_year': features.end_year,
        'end_month' : features.end_month,
        'end_day':  features.end_day,
        'heating_type_ecnoded':features.heating_type_ecnoded,
        'sub_type_encoded': features.sub_type_encoded
    }

    # Создаем DataFrame для регрессора
    if regressor_features is not None:
        regressor_data = {col: [feature_dict[col]] for col in regressor_features}
        regressor_df = pd.DataFrame(regressor_data)
    else:
        # Создаем DataFrame с правильными именами столбцов
        regressor_df = pd.DataFrame([[
            features.listing_type,
            features.tom,
            features.building_age,
            features.total_floor_count,
            features.floor_no,
            features.room_count,
            features.size,
            features.heating_type,
            features.price,
            features.address_encoded,
            features.start_year
        ]], columns=[
            'listing_type', 'tom', 'building_age', 'total_floor_count',
            'floor_no', 'room_count', 'size', 'heating_type', 'price', 'address_encoded', 'start_year',
            'start_day','start_month','end_year','end_month','end_day','heating_type_ecnoded',
            'sub_type_encoded'
        ])

    # Создаем DataFrame для классификатора (аналогично)
    if classifier_features is not None:
        classifier_data = {col: [feature_dict[col]] for col in classifier_features}
        classifier_df = pd.DataFrame(classifier_data)
    else:
        classifier_df = pd.DataFrame([[
            features.listing_type,
            features.tom,
            features.building_age,
            features.total_floor_count,
            features.floor_no,
            features.room_count,
            features.size,
            features.heating_type,
            features.price,
            features.address_encoded,
            features.start_year
        ]], columns=[
            'listing_type', 'tom', 'building_age', 'total_floor_count',
            'floor_no', 'room_count', 'size', 'heating_type', 'price', 'address_encoded', 'start_year',
            'start_day','start_month','end_year','end_month','end_day','heating_type_ecnoded',
            'sub_type_encoded'
        ])

    # Делаем предсказания
    price_prediction = regressor_model.predict(regressor_df)[0]
    subtype_prediction = classifier_model.predict(classifier_df)[0]

    return {
        "predicted_price": float(price_prediction),
        "predicted_subtype": (subtype_prediction),
        "status": "success"
    }




if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)