<template>
  <div class="container">
    <div class="header">
      <h1>Поле Чудес: Угадай цифру!</h1>
      <div class="api-status">
        <span v-if="isLoading" class="loading">⏳ Отправляем Якубовичу...</span>
        <span v-else-if="apiConnected" class="connected">✅ Связь с Якубовичем установлена</span>
        <span v-else class="disconnected">❌ Якубович не отвечает</span>
      </div>
    </div>
    
    <div class="main-content">
      <div class="left-panel">
        <div class="canvas-container">
          <h3>Нарисуйте цифру:</h3>
          <canvas 
            ref="canvas"
            width="280"
            height="280"
            @mousedown="startDrawing"
            @mousemove="draw"
            @mouseup="stopDrawing"
            @mouseleave="stopDrawing"
            @touchstart="handleTouchStart"
            @touchmove="handleTouchMove"
            @touchend="stopDrawing"
          ></canvas>
          <div class="canvas-controls">
            <button @click="clearCanvas" class="btn-clear">Очистить</button>
            <button @click="predictDigit" :disabled="isLoading || !apiConnected" class="btn-predict">
              {{ isLoading ? 'Угадываем...' : 'Что за цифра?' }}
            </button>
          </div>
        </div>

        <div class="connection-info">
          <h3>Статус подключения:</h3>
          <div class="status-card">
            <div class="status-item">
              <span class="status-label">Сервер:</span>
              <span class="status-value">{{ apiStatus.server }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">Модель:</span>
              <span class="status-value">{{ apiStatus.model }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">Последняя проверка:</span>
              <span class="status-value">{{ apiStatus.lastCheck }}</span>
            </div>
          </div>
          <button @click="testConnection" class="btn-refresh" :disabled="isLoading">
            🔄 Проверить связь
          </button>
        </div>
      </div>
      
      <div class="right-panel">
        <div class="yakubovich-container">
          <img src="https://gamestracker.org/_ld/215/21528.jpg" alt="Якубович" class="yakubovich">
          <div class="speech-bubble" v-if="prediction !== null">
            {{ predictionText }}
          </div>
          <div class="speech-bubble error" v-if="error">
            {{ error }}
          </div>
          <div class="speech-bubble info" v-if="!apiConnected && !isLoading">
            Проверяю связь с сервером...
          </div>
        </div>

        <div class="history" v-if="predictionHistory.length > 0">
          <h3>История предсказаний:</h3>
          <div class="history-items">
            <div 
              v-for="(item, index) in predictionHistory" 
              :key="index" 
              class="history-item"
            >
              <span class="digit">{{ item.digit }}</span>
              <span class="confidence">({{ (item.confidence * 100).toFixed(1) }}%)</span>
              <span class="timestamp">{{ formatTime(item.timestamp) }}</span>
            </div>
          </div>
          <button @click="clearHistory" class="btn-clear-history">Очистить историю</button>
        </div>

        <div class="instructions" v-else>
          <h3>Как играть:</h3>
          <ol class="instructions-list">
            <li>Нарисуйте цифру от 0 до 9 в белом поле</li>
            <li>Нажмите "Что за цифра?" для распознавания</li>
            <li>Якубович скажет, что это за цифра и насколько он уверен</li>
          </ol>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Arial', sans-serif;
  background: linear-gradient(135deg, #8B4513, #D2691E);
  min-height: 100vh;
  color: white;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  font-size: 2.5em;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
  color: #FFD700;
}

.api-status {
  margin-top: 10px;
  font-weight: bold;
}

.loading {
  color: #FFD700;
}

.connected {
  color: #90EE90;
}

.disconnected {
  color: #FF6B6B;
}

.main-content {
  display: flex;
  gap: 40px;
  align-items: flex-start;
  justify-content: center;
  flex-wrap: wrap;
}

.left-panel {
  flex: 1;
  min-width: 300px;
}

.right-panel {
  flex: 1;
  min-width: 300px;
}

.canvas-container {
  background: rgba(255, 255, 255, 0.1);
  padding: 20px;
  border-radius: 15px;
  text-align: center;
  backdrop-filter: blur(10px);
  margin-bottom: 20px;
}

canvas {
  border: 3px solid #FFD700;
  border-radius: 10px;
  background: white;
  cursor: crosshair;
  margin: 10px 0;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

.canvas-controls {
  margin-top: 15px;
  display: flex;
  gap: 10px;
  justify-content: center;
}

.btn-clear, .btn-predict, .btn-refresh, .btn-clear-history {
  padding: 10px 20px;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-clear {
  background: #DC143C;
  color: white;
}

.btn-clear:hover:not(:disabled) {
  background: #B22222;
  transform: scale(1.05);
}

.btn-predict {
  background: #32CD32;
  color: white;
}

.btn-predict:hover:not(:disabled) {
  background: #228B22;
  transform: scale(1.05);
}

.btn-predict:disabled {
  background: #666;
  cursor: not-allowed;
  transform: none;
}

.btn-refresh {
  background: #1E90FF;
  color: white;
  width: 100%;
  margin-top: 10px;
}

.btn-refresh:hover:not(:disabled) {
  background: #0066CC;
  transform: scale(1.05);
}

.btn-refresh:disabled {
  background: #666;
  cursor: not-allowed;
}

.btn-clear-history {
  background: #FF8C00;
  color: white;
  width: 100%;
  margin-top: 10px;
  font-size: 14px;
}

.btn-clear-history:hover {
  background: #FF6B00;
  transform: scale(1.05);
}

.connection-info {
  background: rgba(255, 255, 255, 0.1);
  padding: 20px;
  border-radius: 15px;
  backdrop-filter: blur(10px);
}

.status-card {
  background: rgba(255, 255, 255, 0.1);
  padding: 15px;
  border-radius: 10px;
  margin-bottom: 10px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding: 5px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.status-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.status-label {
  font-weight: bold;
  color: #FFD700;
}

.status-value {
  font-weight: normal;
  color: white;
}

.yakubovich-container {
  position: relative;
  text-align: center;
  margin-bottom: 30px;
}

.yakubovich {
  width: 100%;
  max-width: 300px;
  border-radius: 15px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.4);
}

.speech-bubble {
  position: absolute;
  top: -80px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  color: #8B4513;
  padding: 15px 20px;
  border-radius: 20px;
  font-size: 1.2em;
  font-weight: bold;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  max-width: 250px;
  animation: bounce 0.5s ease;
}

.speech-bubble.error {
  background: #FF6B6B;
  color: white;
}

.speech-bubble.info {
  background: #1E90FF;
  color: white;
}

.speech-bubble::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  border-width: 10px 10px 0;
  border-style: solid;
  border-color: white transparent transparent;
}

.speech-bubble.error::after {
  border-color: #FF6B6B transparent transparent;
}

.speech-bubble.info::after {
  border-color: #1E90FF transparent transparent;
}

@keyframes bounce {
  0% { transform: translateX(-50%) scale(0); }
  70% { transform: translateX(-50%) scale(1.1); }
  100% { transform: translateX(-50%) scale(1); }
}

.history {
  background: rgba(255, 255, 255, 0.1);
  padding: 20px;
  border-radius: 15px;
  backdrop-filter: blur(10px);
}

.history-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 10px;
  margin-bottom: 15px;
  max-height: 300px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
}

.digit {
  font-size: 1.2em;
  font-weight: bold;
  color: #FFD700;
  min-width: 30px;
}

.confidence {
  font-size: 0.9em;
  color: #CCC;
  min-width: 70px;
  text-align: right;
}

.timestamp {
  font-size: 0.8em;
  color: #AAA;
  min-width: 80px;
  text-align: right;
}

.instructions {
  background: rgba(255, 255, 255, 0.1);
  padding: 20px;
  border-radius: 15px;
  backdrop-filter: blur(10px);
}

.instructions-list {
  padding-left: 20px;
  text-align: left;
}

.instructions-list li {
  margin-bottom: 10px;
  line-height: 1.4;
}

.instructions-list li:last-child {
  margin-bottom: 0;
}

@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
  }
  
  .yakubovich {
    max-width: 250px;
  }
  
  .history-item {
    flex-direction: column;
    gap: 5px;
    text-align: center;
  }
  
  .digit, .confidence, .timestamp {
    min-width: auto;
    text-align: center;
  }
}
</style>

<script setup>
import { ref, onMounted, computed } from 'vue'

// Реактивные переменные
const canvas = ref(null)
const isDrawing = ref(false)
const prediction = ref(null)
const confidence = ref(null)
const isLoading = ref(false)
const apiConnected = ref(false)
const error = ref(null)
const predictionHistory = ref([])

// URL API скрыт внутри кода - подключение к localhost:8000
const API_CONFIG = {
  BASE_URL: 'http://localhost:8000',
  PREDICT_ENDPOINT: '/predict',
  HEALTH_ENDPOINT: '/health'
}

// Полные URL для API
const PREDICT_URL = API_CONFIG.BASE_URL + API_CONFIG.PREDICT_ENDPOINT
const HEALTH_URL = API_CONFIG.BASE_URL + API_CONFIG.HEALTH_ENDPOINT

// Статус API
const apiStatus = ref({
  server: 'Проверка...',
  model: 'Проверка...',
  lastCheck: 'Никогда'
})

let ctx = null

onMounted(() => {
  // Инициализация canvas
  ctx = canvas.value.getContext('2d')
  clearCanvas()
  ctx.strokeStyle = 'black'
  ctx.lineWidth = 15
  ctx.lineCap = 'round'
  
  // Автоматическая проверка соединения при загрузке
  testConnection()
})

// Функции для рисования
const startDrawing = (e) => {
  isDrawing.value = true
  draw(e)
  error.value = null
}

const draw = (e) => {
  if (!isDrawing.value) return
  
  const rect = canvas.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  
  ctx.lineTo(x, y)
  ctx.stroke()
  ctx.beginPath()
  ctx.moveTo(x, y)
}

const stopDrawing = () => {
  isDrawing.value = false
  ctx.beginPath()
}

// Touch события для мобильных устройств
const handleTouchStart = (e) => {
  e.preventDefault()
  const touch = e.touches[0]
  const mouseEvent = new MouseEvent('mousedown', {
    clientX: touch.clientX,
    clientY: touch.clientY
  })
  canvas.value.dispatchEvent(mouseEvent)
}

const handleTouchMove = (e) => {
  e.preventDefault()
  const touch = e.touches[0]
  const mouseEvent = new MouseEvent('mousemove', {
    clientX: touch.clientX,
    clientY: touch.clientY
  })
  canvas.value.dispatchEvent(mouseEvent)
}

// Очистка canvas
const clearCanvas = () => {
  ctx.fillStyle = 'white'
  ctx.fillRect(0, 0, canvas.value.width, canvas.value.height)
  prediction.value = null
  confidence.value = null
  error.value = null
}

// Очистка истории
const clearHistory = () => {
  predictionHistory.value = []
}

// Форматирование времени
const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// Тестирование соединения с API
const testConnection = async () => {
  isLoading.value = true
  error.value = null
  
  try {
    const response = await fetch(HEALTH_URL, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      apiConnected.value = true
      apiStatus.value = {
        server: '✅ Работает',
        model: data.model_loaded ? '✅ Загружена' : '❌ Не загружена',
        lastCheck: new Date().toLocaleTimeString('ru-RU')
      }
    } else {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
  } catch (err) {
    apiConnected.value = false
    apiStatus.value = {
      server: '❌ Не доступен',
      model: '❌ Не доступна',
      lastCheck: new Date().toLocaleTimeString('ru-RU')
    }
    error.value = `Ошибка соединения: ${err.message}`
  } finally {
    isLoading.value = false
  }
}

// Предсказание цифры через API
const predictDigit = async () => {
  if (!apiConnected.value) {
    error.value = 'Нет соединения с сервером. Проверьте подключение.'
    return
  }
  
  isLoading.value = true
  error.value = null
  
  try {
    // Получаем изображение в base64
    const imageData = getImageAsBase64()
    
    // Отправляем запрос к API
    const response = await fetch(PREDICT_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image: imageData
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    
    // Обрабатываем ответ API
    if (result.success) {
      prediction.value = result.predicted_digit
      confidence.value = result.confidence
      
      // Добавляем в историю
      predictionHistory.value.unshift({
        digit: result.predicted_digit,
        confidence: result.confidence,
        timestamp: new Date()
      })
      
      // Ограничиваем историю 10 последними предсказаниями
      if (predictionHistory.value.length > 10) {
        predictionHistory.value = predictionHistory.value.slice(0, 10)
      }
      
    } else {
      throw new Error(result.error || 'Неизвестная ошибка API')
    }
    
  } catch (err) {
    error.value = `Ошибка предсказания: ${err.message}`
    apiConnected.value = false
  } finally {
    isLoading.value = false
  }
}

// Преобразование изображения в base64
const getImageAsBase64 = () => {
  // Создаем временный canvas для обработки изображения
  const tempCanvas = document.createElement('canvas')
  const tempCtx = tempCanvas.getContext('2d')
  
  // Устанавливаем размер 28x28 как в MNIST
  tempCanvas.width = 28
  tempCanvas.height = 28
  
  // Очищаем белым фоном
  tempCtx.fillStyle = 'white'
  tempCtx.fillRect(0, 0, 28, 28)
  
  // Рисуем основное изображение с изменением размера
  tempCtx.drawImage(canvas.value, 0, 0, 28, 28)
  
  // Конвертируем в base64
  return tempCanvas.toDataURL('image/png')
}

// Вычисляемое свойство для текста предсказания
const predictionText = computed(() => {
  if (prediction.value === null) return ''
  
  let text = `Это цифра: ${prediction.value}!`
  if (confidence.value) {
    text += ` (Уверенность: ${(confidence.value * 100).toFixed(1)}%)`
  }
  
  return text
})
</script>