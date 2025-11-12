<template>
  <div class="container">
    <div class="header">
      <h1>Угадай обувь!</h1>
      <div class="api-status">
        <span v-if="isLoading" class="loading">Анализируем обувь...</span>
        <span v-else-if="apiConnected" class="connected">Связь с сервером установлена</span>
        <span v-else class="disconnected">Сервер не отвечает</span>
      </div>
    </div>
    
    <div class="main-content">
      <div class="left-panel">
        <div class="upload-container">
          <h3>Загрузите фото обуви:</h3>
          <div class="upload-area" 
               @drop="handleDrop"
               @dragover="handleDragOver"
               @click="triggerFileInput">
            <div class="upload-content">
              <div class="upload-icon">👟</div>
              <p>Перетащите фото сюда или нажмите для выбора</p>
              <p class="upload-hint">Поддерживаются: JPG, PNG, WebP</p>
            </div>
            <input 
              type="file" 
              ref="fileInput"
              @change="handleFileSelect"
              accept=".jpg,.jpeg,.png,.webp"
              style="display: none"
            >
          </div>
          
          <div class="image-preview" v-if="previewUrl">
            <img :src="previewUrl" alt="Предпросмотр обуви">
            <button @click="clearImage" class="btn-clear-preview">✕</button>
          </div>

          <div class="upload-controls">
            <button @click="clearImage" class="btn-clear" :disabled="!previewUrl">Очистить</button>
            <button @click="predictShoe" :disabled="isLoading || !apiConnected || !previewUrl || !modelLoaded" class="btn-predict">
              {{ isLoading ? 'Анализируем...' : 'Что за обувь?' }}
            </button>
          </div>

          <!-- Диагностическая информация -->
          <div class="diagnostics" v-if="!modelLoaded && apiConnected">
            <h4>Диагностика:</h4>
            <p class="diagnostic-warning">⚠️ Модель не загружена на сервере</p>
            <button @click="checkDiagnostics" class="btn-diagnostic">Проверить диагностику</button>
            <div v-if="diagnostics" class="diagnostic-info">
              <p><strong>Файл модели:</strong> {{ diagnostics.model_file_exists ? '✅ Найден' : '❌ Не найден' }}</p>
              <p><strong>Статус модели:</strong> {{ diagnostics.model_loaded ? '✅ Загружена' : '❌ Не загружена' }}</p>
            </div>
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
              <span class="status-label">Классы:</span>
              <span class="status-value">{{ apiStatus.classes }}</span>
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
        <div class="result-container">
          <div class="speech-bubble" v-if="prediction">
            {{ predictionText }}
          </div>
          <div class="speech-bubble error" v-if="error">
            {{ error }}
          </div>
          <div class="speech-bubble info" v-if="!apiConnected && !isLoading">
            Проверяю связь с сервером...
          </div>
          <div class="speech-bubble warning" v-if="apiConnected && !modelLoaded && !isLoading">
            ⚠️ Модель не загружена на сервере
          </div>
        </div>

        <!-- Блок вероятностей всех типов обуви -->
        <div class="probabilities">
          <h3>Вероятности всех типов:</h3>
          <div class="probabilities-grid">
            <div 
              v-for="(shoeType, index) in shoeTypes" 
              :key="index" 
              class="probability-item"
              :class="{ 'top-prediction': shoeType === prediction }"
            >
              <span class="type-label">{{ shoeType }}:</span>
              <div class="probability-bar-container">
                <div 
                  class="probability-bar" 
                  :style="{ width: (allProbabilities[shoeType] * 100) + '%' }"
                ></div>
              </div>
              <span class="probability-value">{{ (allProbabilities[shoeType] * 100).toFixed(2) }}%</span>
            </div>
          </div>
        </div>

        <div class="history" v-if="predictionHistory.length > 0">
          <h3>История распознаваний:</h3>
          <div class="history-items">
            <div 
              v-for="(item, index) in predictionHistory" 
              :key="index" 
              class="history-item"
            >
              <span class="type">{{ item.type }}</span>
              <span class="confidence">({{ (item.confidence * 100).toFixed(1) }}%)</span>
              <span class="timestamp">{{ formatTime(item.timestamp) }}</span>
            </div>
          </div>
          <button @click="clearHistory" class="btn-clear-history">Очистить историю</button>
        </div>

        <div class="instructions" v-else>
          <h3>Как использовать:</h3>
          <ol class="instructions-list">
            <li>Загрузите фото обуви (кроссовки, ботинки или сапоги)</li>
            <li>Нажмите "Что за обувь?" для распознавания</li>
            <li>Система определит тип обуви и покажет уверенность</li>
            <li>Посмотрите вероятности для всех типов в таблице ниже</li>
          </ol>
          <div class="shoe-examples">
            <h4>Примеры обуви:</h4>
            <div class="examples-grid">
              <div class="example-item">
                <span class="example-icon">👟</span>
                <span>Кроссовки</span>
              </div>
              <div class="example-item">
                <span class="example-icon">👢</span>
                <span>Ботинки</span>
              </div>
              <div class="example-item">
                <span class="example-icon">🥾</span>
                <span>Сапоги</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Стили остаются такими же, только добавляем новые для диагностики */
.diagnostics {
  background: rgba(255, 193, 7, 0.2);
  padding: 15px;
  border-radius: 10px;
  margin-top: 15px;
  border: 1px solid #FFC107;
}

.diagnostic-warning {
  color: #FFC107;
  font-weight: bold;
  margin-bottom: 10px;
}

.btn-diagnostic {
  background: #FFC107;
  color: #333;
  border: none;
  padding: 8px 15px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  margin-bottom: 10px;
}

.btn-diagnostic:hover {
  background: #FFA000;
}

.diagnostic-info {
  font-size: 0.9em;
  text-align: left;
}

.diagnostic-info p {
  margin: 5px 0;
}

.speech-bubble.warning {
  background: #FFC107;
  color: #333;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Arial', sans-serif;
  background: linear-gradient(135deg, #667eea, #764ba2);
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

.upload-container {
  background: rgba(255, 255, 255, 0.1);
  padding: 20px;
  border-radius: 15px;
  text-align: center;
  backdrop-filter: blur(10px);
  margin-bottom: 20px;
}

.upload-area {
  border: 2px dashed #FFD700;
  border-radius: 10px;
  padding: 40px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.upload-area:hover {
  background: rgba(255, 215, 0, 0.1);
  transform: scale(1.02);
}

.upload-content {
  color: #FFD700;
}

.upload-icon {
  font-size: 3em;
  margin-bottom: 10px;
}

.upload-hint {
  font-size: 0.9em;
  color: #CCC;
  margin-top: 10px;
}

.image-preview {
  position: relative;
  margin: 20px 0;
  display: inline-block;
}

.image-preview img {
  max-width: 100%;
  max-height: 300px;
  border-radius: 10px;
  border: 3px solid #FFD700;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

.btn-clear-preview {
  position: absolute;
  top: -10px;
  right: -10px;
  background: #DC143C;
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-clear-preview:hover {
  background: #B22222;
  transform: scale(1.1);
}

.upload-controls {
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

.result-container {
  position: relative;
  text-align: center;
  margin-bottom: 30px;
  min-height: 100px;
}

.speech-bubble {
  background: white;
  color: #333;
  padding: 20px 25px;
  border-radius: 20px;
  font-size: 1.3em;
  font-weight: bold;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  max-width: 300px;
  margin: 0 auto;
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

@keyframes bounce {
  0% { transform: scale(0); }
  70% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

/* Стили для блока вероятностей */
.probabilities {
  background: rgba(255, 255, 255, 0.1);
  padding: 20px;
  border-radius: 15px;
  backdrop-filter: blur(10px);
  margin-bottom: 20px;
}

.probabilities-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 15px;
}

.probability-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px 15px;
  border-radius: 10px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.05);
}

.probability-item.top-prediction {
  background: rgba(255, 215, 0, 0.3);
  border: 2px solid #FFD700;
  transform: scale(1.02);
}

.type-label {
  min-width: 100px;
  font-weight: bold;
  color: #FFD700;
  font-size: 1.1em;
}

.probability-bar-container {
  flex: 1;
  height: 25px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  overflow: hidden;
}

.probability-bar {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #8BC34A);
  transition: width 0.8s ease;
  border-radius: 12px;
}

.probability-value {
  min-width: 70px;
  text-align: right;
  font-weight: bold;
  font-size: 1.1em;
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
  padding: 10px 15px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
}

.type {
  font-size: 1.2em;
  font-weight: bold;
  color: #FFD700;
  min-width: 100px;
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
  margin-bottom: 20px;
}

.instructions-list li {
  margin-bottom: 10px;
  line-height: 1.4;
}

.instructions-list li:last-child {
  margin-bottom: 0;
}

.shoe-examples {
  margin-top: 20px;
}

.examples-grid {
  display: flex;
  justify-content: space-around;
  margin-top: 15px;
}

.example-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.example-icon {
  font-size: 2em;
}

@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
  }
  
  .history-item {
    flex-direction: column;
    gap: 5px;
    text-align: center;
  }
  
  .type, .confidence, .timestamp {
    min-width: auto;
    text-align: center;
  }

  .probability-item {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .type-label {
    min-width: auto;
  }

  .examples-grid {
    flex-direction: column;
    gap: 15px;
  }
}
</style>

<script setup>
import { ref, onMounted, computed } from 'vue'

// перепутаны классы
const CLASS_MAPPING = {
  'sneakers': 'Туфли',
  'boots': 'Кроссовки',
  'shoes': 'Сапоги'
}

// Обратное сопоставление для отображения в интерфейсе
const RUSSIAN_CLASSES = Object.values(CLASS_MAPPING)
const ENGLISH_CLASSES = Object.keys(CLASS_MAPPING)

// Реактивные переменные
const fileInput = ref(null)
const previewUrl = ref('')
const prediction = ref(null) // будет хранить русское название: "кроссовки"
const confidence = ref(null)
const isLoading = ref(false)
const apiConnected = ref(false)
const modelLoaded = ref(false)
const error = ref(null)
const predictionHistory = ref([])
const diagnostics = ref(null)

// Инициализируем вероятности с русскими названиями
const allProbabilities = ref(
  RUSSIAN_CLASSES.reduce((acc, cls) => {
    acc[cls] = 0
    return acc
  }, {})
)

const shoeTypes = RUSSIAN_CLASSES

const API_CONFIG = {
  BASE_URL: 'http://localhost:8000',
  PREDICT_ENDPOINT: '/predict',
  HEALTH_ENDPOINT: '/health'
}

const PREDICT_URL = API_CONFIG.BASE_URL + API_CONFIG.PREDICT_ENDPOINT
const HEALTH_URL = API_CONFIG.BASE_URL + API_CONFIG.HEALTH_ENDPOINT

const apiStatus = ref({
  server: 'Проверка...',
  model: 'Проверка...',
  classes: 'Проверка...',
  lastCheck: 'Никогда'
})

onMounted(() => {
  testConnection()
})

// --- Функции загрузки файла (остаются без изменений) ---
const triggerFileInput = () => fileInput.value.click()

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) processFile(file)
}

const handleDrop = (event) => {
  event.preventDefault()
  const file = event.dataTransfer.files[0]
  if (file) processFile(file)
}

const handleDragOver = (event) => event.preventDefault()

const processFile = (file) => {
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
  if (!validTypes.includes(file.type)) {
    error.value = 'Пожалуйста, выберите файл изображения (JPG, PNG, WebP)'
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    error.value = 'Размер файла не должен превышать 5MB'
    return
  }
  previewUrl.value = URL.createObjectURL(file)
  error.value = null
  prediction.value = null
  confidence.value = null
  resetProbabilities()
}

const clearImage = () => {
  previewUrl.value = ''
  if (fileInput.value) fileInput.value.value = ''
  prediction.value = null
  confidence.value = null
  error.value = null
  resetProbabilities()
}

const resetProbabilities = () => {
  allProbabilities.value = RUSSIAN_CLASSES.reduce((acc, cls) => {
    acc[cls] = 0
    return acc
  }, {})
}

const clearHistory = () => predictionHistory.value = []

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// --- Проверка соединения ---
const testConnection = async () => {
  isLoading.value = true
  error.value = null
  try {
    const response = await fetch(HEALTH_URL)
    if (response.ok) {
      const data = await response.json()
      apiConnected.value = true
      modelLoaded.value = data.model_loaded

      // Преобразуем английские классы в русские для отображения
      const displayedClasses = data.classes
        ? data.classes.map(cls => CLASS_MAPPING[cls] || cls).join(', ')
        : 'Неизвестно'

      apiStatus.value = {
        server: 'Работает',
        model: data.model_loaded ? 'Загружена' : 'Не загружена',
        classes: displayedClasses,
        lastCheck: new Date().toLocaleTimeString('ru-RU')
      }
    } else {
      throw new Error(`HTTP ${response.status}`)
    }
  } catch (err) {
    apiConnected.value = false
    modelLoaded.value = false
    apiStatus.value = {
      server: 'Не доступен',
      model: 'Не доступна',
      classes: 'Не доступны',
      lastCheck: new Date().toLocaleTimeString('ru-RU')
    }
    error.value = `Ошибка соединения: ${err.message}`
  } finally {
    isLoading.value = false
  }
}

// --- Предсказание ---
const predictShoe = async () => {
  if (!apiConnected.value) {
    error.value = 'Нет соединения с сервером.'
    return
  }
  if (!modelLoaded.value) {
    error.value = 'Модель не загружена на сервере.'
    return
  }
  if (!previewUrl.value) {
    error.value = 'Пожалуйста, загрузите изображение обуви'
    return
  }

  isLoading.value = true
  error.value = null

  try {
    const file = fileInput.value.files[0]
    const imageBase64 = await fileToBase64(file)

    const response = await fetch(PREDICT_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: imageBase64 })
    })

    if (!response.ok) throw new Error(`HTTP ${response.status}`)

    const result = await response.json()

    if (result.success) {
      const englishClass = result.predicted_class
      const russianClass = CLASS_MAPPING[englishClass] || englishClass

      prediction.value = russianClass
      confidence.value = result.confidence

      // Обновляем вероятности с русскими названиями
      const updatedProbs = {}
      for (const eng of ENGLISH_CLASSES) {
        const rus = CLASS_MAPPING[eng]
        updatedProbs[rus] = result.probabilities?.[eng] || 0
      }
      allProbabilities.value = updatedProbs

      // Добавляем в историю
      predictionHistory.value.unshift({
        type: russianClass,
        confidence: result.confidence,
        timestamp: new Date()
      })
      if (predictionHistory.value.length > 10) {
        predictionHistory.value = predictionHistory.value.slice(0, 10)
      }
    } else {
      throw new Error(result.error || 'Неизвестная ошибка API')
    }
  } catch (err) {
    error.value = `Ошибка распознавания: ${err.message}`
    resetProbabilities()
  } finally {
    isLoading.value = false
  }
}

const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => resolve(reader.result)
    reader.onerror = error => reject(error)
  })
}

const predictionText = computed(() => {
  if (prediction.value === null) return ''
  return `Это: ${prediction.value}! (Уверенность: ${(confidence.value * 100).toFixed(2)}%)`
})
</script>