from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import tensorflow as tf
from PIL import Image
import io
import base64
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Shoe Recognition API")

# Разрешаем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модель для запроса
class PredictionRequest(BaseModel):
    image: str  # base64-encoded image (возможно с data URL prefix)

# Классы обуви (в том же порядке, что и в выходных нейронах модели)
CLASS_NAMES = ["boots", "sneakers", "shoes"]  # ← ПОМЕНЯЙ ПОРЯДОК, ЕСЛИ НУЖНО!

# Загрузка модели
try:
    model = tf.keras.models.load_model('keras_model_cross.h5')
    logger.info("✅ Модель обуви успешно загружена")
except Exception as e:
    logger.error(f"❌ Ошибка загрузки модели: {e}")
    model = None

def preprocess_image(image_data: str) -> np.ndarray:
    try:
        logger.info("Начало предобработки изображения")

        # Убираем data URL prefix, если есть
        if ',' in image_data:
            image_data = image_data.split(',')[1]

        # Декодируем base64
        image_bytes = base64.b64decode(image_data)
        logger.info("Base64 декодирован")

        # Открываем и конвертируем в RGB (важно для цветных моделей!)
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        logger.info("Изображение открыто и конвертировано в RGB")

        # Изменяем размер до 224x224 (или того, что ожидает модель)
        image = image.resize((224, 224))
        image_array = np.array(image)
        logger.info(f"Размер изображения после ресайза: {image_array.shape}")

        # Нормализуем пиксели к диапазону [0, 1] (если модель обучена так)
        image_array = image_array.astype('float32') / 255.0

        # Добавляем batch dimension
        image_array = np.expand_dims(image_array, axis=0)  # shape: (1, 224, 224, 3)
        logger.info(f"Финальный размер для модели: {image_array.shape}")

        return image_array

    except Exception as e:
        logger.error(f"Ошибка в preprocess_image: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Ошибка обработки изображения: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Shoe Recognition API is running!"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "classes": CLASS_NAMES,
        "message": "API готов к работе"
    }

@app.post("/predict")
async def predict_shoe(request: PredictionRequest):
    """Эндпоинт для предсказания типа обуви"""
    try:
        logger.info("Получен запрос на /predict")

        if model is None:
            raise HTTPException(status_code=500, detail="Модель не загружена")

        image_data = request.image
        if not image_data:
            raise HTTPException(status_code=400, detail="No image data provided")

        # Предобработка
        processed_image = preprocess_image(image_data)

        # Предсказание
        logger.info("Начало предсказания...")
        predictions = model.predict(processed_image, verbose=0)
        logger.info("Предсказание завершено")

        # Получаем индекс с максимальной вероятностью
        predicted_idx = int(np.argmax(predictions[0]))
        predicted_class = CLASS_NAMES[predicted_idx]
        confidence = float(np.max(predictions[0]))

        # Вероятности для всех классов
        probabilities = {
            CLASS_NAMES[i]: float(predictions[0][i]) for i in range(len(CLASS_NAMES))
        }

        logger.info(f"Предсказанный класс: {predicted_class}, уверенность: {confidence:.4f}")

        return {
            "success": True,
            "predicted_class": predicted_class,
            "confidence": confidence,
            "probabilities": probabilities
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка в predict_shoe: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Тестовый эндпоинт (можно удалить)
@app.post("/predict_test")
async def predict_test():
    return {
        "success": True,
        "predicted_class": "sneakers",
        "confidence": 0.92,
        "probabilities": {"boots": 0.03, "sneakers": 0.92, "shoes": 0.05},
        "message": "Тестовый ответ"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)