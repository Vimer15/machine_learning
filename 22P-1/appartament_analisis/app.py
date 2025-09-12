import streamlit as st
import requests
import pandas as pd
import numpy as np
from typing import Dict, Any
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Конфигурация страницы
st.set_page_config(
    page_title="RealEstatePredictor | Анализ недвижимости",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS стили
st.markdown("""
<style>
    .main-header {
        font-size: 3rem !important;
        color: #1f77b4 !important;
        text-align: center;

    }
    .sub-header {
        font-size: 1.2rem !important;
        color: #666 !important;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
    }
    .parameter-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .input-section {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 1rem;
        border-radius: 10px;
        font-size: 1.1rem;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
    }
</style>
""", unsafe_allow_html=True)

# Заголовок приложения
st.markdown("""
<div class="main-header">
    🏠 RealEstatePredictor
</div>
<div class="sub-header">
    Интеллектуальный анализ рынка недвижимости с использованием машинного обучения
</div>
""", unsafe_allow_html=True)

# URL API
API_URL = "http://localhost:8000"


# Функция для получения предсказаний от API
def get_predictions(data: Dict[str, Any]) -> Dict[str, Any]:
    
        response = requests.post(f"{API_URL}/predict", json=data, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Ошибка API: {response.status_code}"}


# Секция ввода параметров на главной странице
st.markdown("### Введите параметры недвижимости")

# Используем колонки для организации ввода
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🏢 Основное")
    size = st.number_input("**Площадь (м²)**", min_value=10, max_value=1000, value=80, step=5,
                           help="Общая площадь объекта недвижимости")
    room_count = st.selectbox("**Количество комнат**", [1, 2, 3, 4, 5, 6], index=1,
                              help="Количество жилых комнат")
    building_age = st.slider("**Возраст здания (лет)**", 0, 50, 5,
                                     help="Сколько лет зданию")

with col2:
    st.markdown("#### 📍 Расположение")
    floor_no = st.number_input("**Этаж**", min_value=-2, max_value=50, value=3, step=1,
                               help="На каком этаже расположен объект")
    total_floor_count = st.number_input("**Этажность здания**", min_value=1, max_value=50, value=5, step=1,
                                        help="Общее количество этажей в здании")
    tom = st.slider("**Дней на рынке**", 0, 365, 30,
                               help="Сколько дней объект находится в продаже")

with col3:
    st.markdown("#### ⚙️ Доп. параметры")
    heating_type = st.selectbox(
        "**Тип отопления**",
        options=[
            ("Нет", 0),
            ("Печь (Уголь)", 1),
            ("Печь (Газ)", 2),
            ("Котел (Уголь)", 3),
            ("Котел (Газ)", 4),
            ("Котел (Жидкое топливо)", 5),
            ("Газовый котел (настенный)", 6),
            ("Электрический котел", 7),
            ("Поквартирное отопление", 8),
            ("Центральная система", 9),
            ("Центральная система (счетчик тепла)", 10),
            ("Теплый пол", 11),
            ("Кондиционер/Обогреватель", 12),
            ("Фанкойл", 13),
            ("Солнечная энергия", 14),
            ("Геотермальная", 15)
        ],
        format_func=lambda x: x[0],
        index=9,
        help="Тип системы отопления в здании"
    )[1]

# Кнопка для получения предсказаний по центру
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    predict_button = st.button("Получить прогноз", use_container_width=True)

if predict_button:
    # Подготовка данных для отправки
    input_data = {
        "total_floor_count": total_floor_count,
        "floor_no": floor_no,
        "room_count": room_count,
        "size": size,
        "building_age": building_age,
        "tom": tom,
        "heating_type": heating_type,
        "listing_type": 1,
        'price': 0,
        "address_encoded": 0,
    }

    # Отображение введенных параметров
    st.markdown("### Введенные параметры")

    # Создаем контейнер для параметров
    params_container = st.container()

    with params_container:
        param_cols = st.columns(3)

        # Словарь для сопоставления кодов отопления с русскими названиями
        heating_types = {
            0: "Нет",
            1: "Печь (Уголь)",
            2: "Печь (Газ)",
            3: "Котел (Уголь)",
            4: "Котел (Газ)",
            5: "Котел (Жидкое топливо)",
            6: "Газовый котел (настенный)",
            7: "Электрический котел",
            8: "Поквартирное отопление",
            9: "Центральная система",
            10: "Центральная система (счетчик тепла)",
            11: "Теплый пол",
            12: "Кондиционер/Обогреватель",
            13: "Фанкойл",
            14: "Солнечная энергия",
            15: "Геотермальная"
        }

        params = [
            ("Площадь", f"{size} м²"),
            ("Комнаты", room_count),
            ("Этаж", f"{floor_no}/{total_floor_count}"),
            ("Возраст здания", f"{building_age} лет"),
            ("Дней на рынке", tom),
            ("Тип отопления", heating_types.get(heating_type, "Неизвестно"))
        ]

        for i, (param_name, param_value) in enumerate(params):
            with param_cols[i % 3]:
                st.markdown(f"**{param_name}:** {param_value}")

    # Отправка запроса к API
    with st.spinner("🔍 Анализируем данные с помощью ML моделей..."):
        predictions = get_predictions(input_data)
        print("ПРЕД:   ", predictions)

    if predictions:
        if "error" in predictions:
            st.error(f"❌ {predictions['error']}")
        else:
            # Основные результаты
            st.markdown("---")
            st.markdown("### Результаты анализа")

            # Метрики в карточках
            col1, col2 = st.columns(2)

            with col1:
                price = predictions.get("predicted_price", 0)
                st.markdown(f"""
                <div class="metric-card">
                    <h3>💰 Предсказанная цена</h3>
                    <h2>{price:,.0f} ₺</h2>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                subtype = predictions.get("predicted_subtype", -1)
                subtype_mapping = {
                    0: "Квартира", 1: "Жилой комплекс", 2: "Вилла",
                    3: "Индивидуальный дом", 4: "Кооператив", 5: "Комплекс зданий",
                    6: "Дача", 7: "Сборный дом", 8: "Особняк/Дворец",
                    9: "Фермерский дом", 10: "Водная квартира", 11: "Лофт"
                }
                subtype_name = subtype_mapping.get(subtype, "Неизвестно")
                st.markdown(f"""
                <div class="metric-card" 
                style="background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);">
                    <h3>🏷 Тип недвижимости</h3>
                    <h4>{subtype}</h4>
                </div>
                """, unsafe_allow_html=True)

            # Визуализация
            st.markdown("---")
            st.markdown("### Визуализация параметров")

            # График параметров
            fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'bar'}, {'type': 'pie'}]])

            # Bar chart
            param_names = ['Площадь', 'Комнаты', 'Этаж', 'Возраст']
            param_values = [size, room_count, floor_no, building_age]

            fig.add_trace(
                go.Bar(x=param_names, y=param_values, name="Параметры", marker_color='#1f77b4'),
                row=1, col=1
            )

            # Pie chart для распределения
            pie_labels = ['Площадь', 'Комнаты', 'Расположение', 'Возраст']
            pie_values = [40, 25, 20, 15]

            fig.add_trace(
                go.Pie(labels=pie_labels, values=pie_values, name=""),
                row=1, col=2
            )

            fig.update_layout(height=400, showlegend=False, title_text="Анализ параметров объекта")
            st.plotly_chart(fig, use_container_width=True)

            # Детальная информация
            with st.expander("Детальная информация о прогнозе"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Исходные данные:**")
                    st.json(input_data)
                with col2:
                    st.write("**Результаты модели:**")
                    st.json({k: v for k, v in predictions.items() if
                             k not in ['regressor_features_count', 'classifier_features_count']})

else:
    # Информационная панель когда кнопка еще не нажата
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
