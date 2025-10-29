from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import tensorflow as tf
from PIL import Image
import io
import base64
import logging
import re

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Digit Recognition API")

# Разрешаем CORS для веб-приложения
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модель для запроса
class PredictionRequest(BaseModel):
    image: str

# Загрузка модели
try:
    model = tf.keras.models.load_model('digit_model.h5')
    logger.info("✅ Модель успешно загружена")
except Exception as e:
    logger.error(f"❌ Ошибка загрузки модели: {e}")
    model = None

def preprocess_image(image_data: str) -> np.ndarray:
    """Предобработка изображения для модели"""
    try:
        logger.info("Начало предобработки изображения")
        
        # Убираем префикс data:image/png;base64, если есть
        if ',' in image_data:
            image_data = image_data.split(',')[1]
            logger.info("Убран префикс data URL")
        
        # Декодируем base64
        image_bytes = base64.b64decode(image_data)
        logger.info("Base64 декодирован")
        
        # Открываем изображение
        image = Image.open(io.BytesIO(image_bytes)).convert('L')
        logger.info("Изображение открыто и конвертировано в grayscale")
        
        # Преобразуем в numpy array
        image_array = np.array(image)
        logger.info(f"Размер изображения после загрузки: {image_array.shape}")
        
        # Инвертируем цвета (белый на черном -> черный на белом)
        # В MNIST цифры белые на черном фоне, у нас обычно черные на белом
        image_array = 255 - image_array
        logger.info("Цвета инвертированы")
        
        # Нормализуем пиксели к диапазону [0, 1]
        image_array = image_array.astype('float32') / 255.0
        logger.info("Изображение нормализовано")
        
        # Добавляем размерности для модели (batch_size, height, width, channels)
        image_array = image_array.reshape(1, 28, 28, 1)
        logger.info(f"Финальный размер для модели: {image_array.shape}")
        
        return image_array
        
    except Exception as e:
        logger.error(f"Ошибка в preprocess_image: {str(e)}")
        raise

@app.get("/")
async def root():
    return {"message": "Digit Recognition API is running!"}

@app.get("/health")
async def health_check():
    """Проверка здоровья API"""
    return {
        "status": "healthy", 
        "model_loaded": model is not None,
        "message": "API готов к работе"
    }

@app.post("/predict")
async def predict_digit(request: PredictionRequest):
    """Основной эндпоинт для предсказания цифры"""
    try:
        logger.info("Получен запрос на /predict")
        
        if model is None:
            raise HTTPException(status_code=500, detail="Модель не загружена")
        
        image_data = request.image
        if not image_data:
            raise HTTPException(status_code=400, detail="No image data provided")
        
        logger.info(f"Длина image_data: {len(image_data)}")
        
        # Предобработка изображения
        processed_image = preprocess_image(image_data)
        
        # Предсказание
        logger.info("Начало предсказания...")
        predictions = model.predict(processed_image, verbose=0)
        logger.info("Предсказание завершено")
        
        # Получаем предсказанную цифру и уверенность
        predicted_digit = int(np.argmax(predictions[0]))
        confidence = float(np.max(predictions[0]))
        
        # Вероятности для всех цифр
        probabilities = {
            str(i): float(predictions[0][i]) for i in range(10)
        }
        
        logger.info(f"Предсказанная цифра: {predicted_digit}, уверенность: {confidence:.4f}")
        
        return {
            "success": True,
            "predicted_digit": predicted_digit,
            "confidence": confidence,
            "probabilities": probabilities
        }
        
    except Exception as e:
        logger.error(f"Ошибка в predict_digit: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Альтернативный эндпоинт для тестирования
@app.post("/predict_test")
async def predict_test():
    """Тестовый эндпоинт"""
    return {
        "success": True,
        "predicted_digit": 5,
        "confidence": 0.95,
        "probabilities": {str(i): 0.1 for i in range(10)},
        "message": "Тестовый ответ"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)