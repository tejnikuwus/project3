import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, root_mean_squared_error

# Налаштування сторінки Streamlit
st.set_page_config(
    page_title="California Housing — Лінійна Регресія",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data
def load_data():
    housing = fetch_california_housing(as_frame=True)
    df = housing.data.copy()
    df["MedHouseValue"] = housing.target
    return df, housing.feature_names, housing.DESCR


@st.cache_resource
def train_model(df, feature_names):
    X = df[feature_names]
    y = df["MedHouseValue"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LinearRegression()
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)

    mse = mean_squared_error(y_test, y_pred)
    rmse = root_mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    metrics = {"MSE": mse, "RMSE": rmse, "R2": r2}
    return model, scaler, X_test, y_test, y_pred, metrics


def main():
    st.title("🏠 Аналіз та Прогнозування Цін на Житло (California Housing)")
    st.markdown("""
    Цей інтерактивний веб-додаток демонструє роботу моделі **Лінійної Регресії** 
    для прогнозування медіанної вартості будинків у Каліфорнії.
    """)

    # Завантаження даних та навчання моделі
    df, feature_names, descr = load_data()
    model, scaler, X_test, y_test, y_pred, metrics = train_model(df, feature_names)

    # Бічна панель
    st.sidebar.header("⚙️ Налаштування та Інфо")
    st.sidebar.info("Датасет: California Housing\nМодель: Linear Regression")

    # Вкладки додатка
    tab1, tab2, tab3 = st.tabs([
        "📊 1. Набір даних", 
        "🤖 2. Як працює модель", 
        "🔮 3. Інтерактивний прогноз"
    ])

    # --- ВКЛАДКА 1: НАБІР ДАНИХ ---
    with tab1:
        st.subheader("📋 Огляд датасету")
        col1, col2 = st.columns([2, 1])

        with col1:
            st.dataframe(df.head(20), use_container_width=True)

        with col2:
            st.write("**Статистичний опис даних:**")
            st.dataframe(df.describe().T[["mean", "std", "min", "50%", "max"]], use_container_width=True)

        st.markdown("---")
        st.subheader("🗺 Карта розташування об'єктів та вартість")
        st.caption("Широта (Latitude) та довгота (Longitude) будинків у Каліфорнії")
        map_data = df[["Latitude", "Longitude", "MedHouseValue"]].rename(
            columns={"Latitude": "lat", "Longitude": "lon"}
        )
        st.map(map_data, zoom=5)

        st.subheader("🔥 Кореляційна матриця ознак")
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.heatmap(df.corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
        st.pyplot(fig)

    # --- ВКЛАДКА 2: ЯК ПРАЦЮЄ МОДЕЛЬ ---
    with tab2:
        st.subheader("🎯 Метрики якості моделі")
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric(label="R² Score (Коефіцієнт детермінації)", value=f"{metrics['R2']:.4f}")
        m_col2.metric(label="RMSE (Корінь середньоквадр. помилки)", value=f"${metrics['RMSE']*100:.2f}k")
        m_col3.metric(label="MSE (Середньоквадратична помилка)", value=f"{metrics['MSE']:.4f}")

        st.markdown("---")
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("📈 Фактичні значення проти Прогнозованих")
            fig_scat, ax_scat = plt.subplots(figsize=(6, 5))
            ax_scat.scatter(y_test, y_pred, alpha=0.3, color="crimson")
            ax_scat.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], "k--", lw=2)
            ax_scat.set_xlabel("Фактична ціна ($100k)")
            ax_scat.set_ylabel("Прогнозована ціна ($100k)")
            ax_scat.set_title("Actual vs Predicted")
            st.pyplot(fig_scat)

        with col_right:
            st.subheader("⚖️ Вагові коефіцієнти ознак")
            coef_df = pd.DataFrame({
                "Ознака": feature_names,
                "Коефіцієнт": model.coef_
            }).sort_values(by="Коефіцієнт", ascending=True)

            fig_bar, ax_bar = plt.subplots(figsize=(6, 5))
            ax_bar.barh(coef_df["Ознака"], coef_df["Коефіцієнт"], color="skyblue")
            ax_bar.axvline(0, color="black", linestyle="--", linewidth=0.8)
            ax_bar.set_title("Вплив ознак на ціну житла")
            ax_bar.set_xlabel("Значення коефіцієнта")
            st.pyplot(fig_bar)

    # --- ВКЛАДКА 3: ІНТЕРАКТИВНИЙ ПРОГНОЗ ---
    with tab3:
        st.subheader("🎛 Введіть параметри будинку для прогнозу ціни")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            med_inc = st.slider("Медіанний дохід (MedInc, $10k)", float(df.MedInc.min()), float(df.MedInc.max()), float(df.MedInc.mean()))
            house_age = st.slider("Вік будинку (HouseAge)", float(df.HouseAge.min()), float(df.HouseAge.max()), float(df.HouseAge.median()))
            ave_rooms = st.slider("Сер. кількість кімнат (AveRooms)", 1.0, 10.0, float(df.AveRooms.mean()))

        with c2:
            ave_bedrms = st.slider("Сер. спалень (AveBedrms)", 0.5, 5.0, float(df.AveBedrms.mean()))
            population = st.slider("Населення району (Population)", float(df.Population.min()), float(df.Population.max()), float(df.Population.mean()))
            ave_occup = st.slider("Сер. мешканців на будинок (AveOccup)", 1.0, 6.0, float(df.AveOccup.mean()))

        with c3:
            latitude = st.slider("Широта (Latitude)", float(df.Latitude.min()), float(df.Latitude.max()), float(df.Latitude.mean()))
            longitude = st.slider("Довгота (Longitude)", float(df.Longitude.min()), float(df.Longitude.max()), float(df.Longitude.mean()))

        # Підготовка даних для прогнозу
        input_data = pd.DataFrame([[
            med_inc, house_age, ave_rooms, ave_bedrms, population, ave_occup, latitude, longitude
        ]], columns=feature_names)

        input_scaled = scaler.transform(input_data)
        prediction = model.predict(input_scaled)[0]

        st.markdown("---")
        st.markdown(f"### 💰 Прогнозована медіанна вартість: **${prediction * 100000:,.2f}**")


if __name__ == "__main__":
    main()
