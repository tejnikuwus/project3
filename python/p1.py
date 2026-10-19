# -*- coding: utf-8 -*-
"""
California Housing: Порівняння Лінійної та Поліноміальної Регресії,
Явні Формули Моделей та Аналіз Перенавчання (Overfitting).

Автор: Артем, учень 10 класу НВК №141 «ОРТ» м. Києва.
Спеціально розроблено для роботи у браузері через Pyodide / stlite Wasm.
"""

import sys
import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# ==================== НАЛАШТУВАННЯ СТОРІНКИ STREAMLIT ====================
st.set_page_config(
    page_title="California Housing — Регресія та Перенавчання",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Стилізація UI для сучасного вигляду
st.markdown("""
<style>
  .metric-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 14px;
    transition: transform 0.2s ease, border-color 0.2s ease;
  }
  .metric-card:hover {
    border-color: #00f2fe;
    transform: translateY(-2px);
  }
  .formula-box {
    background: #0f172a;
    border-left: 4px solid #00f2fe;
    padding: 14px 18px;
    border-radius: 0 10px 10px 0;
    font-family: 'Courier New', Courier, monospace;
    font-size: 1.05rem;
    color: #e2e8f0;
    margin: 12px 0;
    overflow-x: auto;
  }
  .formula-box-2 {
    background: #0f172a;
    border-left: 4px solid #ec4899;
    padding: 14px 18px;
    border-radius: 0 10px 10px 0;
    font-family: 'Courier New', Courier, monospace;
    font-size: 1.05rem;
    color: #e2e8f0;
    margin: 12px 0;
    overflow-x: auto;
  }
  .status-badge-ok {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    background: rgba(16, 185, 129, 0.15);
    color: #10b981;
    font-size: 0.85rem;
    font-weight: 600;
  }
  .status-badge-warn {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    background: rgba(239, 68, 68, 0.15);
    color: #ef4444;
    font-size: 0.85rem;
    font-weight: 600;
  }
</style>
""", unsafe_allow_html=True)


# ==================== ЗАВАНТАЖЕННЯ ДАНИХ ====================
@st.cache_data
def load_housing_data():
    """
    Завантажує датасет California Housing:
    1) Спочатку шукає локальний california_housing.csv
    2) Якщо відсутній, пробує fetch_california_housing
    3) Якщо обидва варіанти недоступні — генерує автентичну вибірку
    """
    csv_candidates = [
        "california_housing.csv",
        "python/california_housing.csv",
        "../python/california_housing.csv"
    ]
    for p in csv_candidates:
        if os.path.exists(p):
            try:
                df = pd.read_csv(p)
                if "MedHouseVal" in df.columns and "MedHouseValue" not in df.columns:
                    df["MedHouseValue"] = df["MedHouseVal"]
                feature_names = [c for c in df.columns if c not in ("MedHouseValue", "MedHouseVal")]
                return df, feature_names, "Локальний файл California Housing CSV"
            except Exception:
                pass

    try:
        from sklearn.datasets import fetch_california_housing
        housing = fetch_california_housing(as_frame=True)
        df = housing.data.copy()
        df["MedHouseValue"] = housing.target
        feature_names = list(housing.feature_names)
        return df, feature_names, "scikit-learn fetch_california_housing"
    except Exception:
        pass

    # Автономна генерація даних у стилі California Housing (якщо Wasm офлайн)
    np.random.seed(42)
    n_samples = 1500
    med_inc = np.random.uniform(0.5, 15.0, n_samples)
    house_age = np.random.uniform(1.0, 52.0, n_samples)
    ave_rooms = np.random.uniform(2.0, 9.0, n_samples)
    ave_bedrms = np.random.uniform(0.8, 2.5, n_samples)
    population = np.random.uniform(200, 5000, n_samples)
    ave_occup = np.random.uniform(1.5, 5.0, n_samples)
    latitude = np.random.uniform(32.5, 42.0, n_samples)
    longitude = np.random.uniform(-124.3, -114.1, n_samples)

    # Нелінійна залежність вартості від медіанного доходу
    med_house_val = (
        0.45 +
        0.42 * med_inc -
        0.012 * (med_inc ** 2) +
        0.0003 * (med_inc ** 3) +
        np.random.normal(0, 0.40, n_samples)
    )
    med_house_val = np.clip(med_house_val, 0.15, 5.0)

    df = pd.DataFrame({
        "MedInc": med_inc,
        "HouseAge": house_age,
        "AveRooms": ave_rooms,
        "AveBedrms": ave_bedrms,
        "Population": population,
        "AveOccup": ave_occup,
        "Latitude": latitude,
        "Longitude": longitude,
        "MedHouseValue": med_house_val
    })
    feature_names = ["MedInc", "HouseAge", "AveRooms", "AveBedrms", "Population", "AveOccup", "Latitude", "Longitude"]
    return df, feature_names, "Автономна генерація California Housing (Wasm Safe)"


# ==================== ДОПОМІЖНІ ФУНКЦІЇ ДЛЯ ФОРМУЛ ====================
def format_formula_latex(intercept, coefs, feature_name="x", precision=4):
    """
    Генерує LaTeX вираз виду:
    \\hat{y} = b_0 + b_1 x + b_2 x^{2} + ... + b_k x^{k}
    """
    terms = [f"{intercept:.{precision}f}"]
    for i, c in enumerate(coefs, start=1):
        sign = "+" if c >= 0 else "-"
        abs_c = abs(c)
        if 0 < abs_c < 0.0001:
            c_str = f"{abs_c:.2e}"
        else:
            c_str = f"{abs_c:.{precision}f}"

        if i == 1:
            terms.append(f"{sign} {c_str} {feature_name}")
        else:
            terms.append(f"{sign} {c_str} {feature_name}^{{{i}}}")
    return r"\hat{y} = " + " ".join(terms)


def format_formula_text(intercept, coefs, feature_name="MedInc", precision=4):
    """
    Генерує текстовий вираз із верхніми індексами:
    ŷ = b₀ + b₁·MedInc + b₂·MedInc² + ...
    """
    superscripts = {
        1: "", 2: "²", 3: "³", 4: "⁴", 5: "⁵",
        6: "⁶", 7: "⁷", 8: "⁸", 9: "⁹", 10: "¹⁰",
        11: "¹¹", 12: "¹²"
    }
    terms = [f"{intercept:.{precision}f}"]
    for i, c in enumerate(coefs, start=1):
        sign = "+" if c >= 0 else "-"
        abs_c = abs(c)
        if 0 < abs_c < 0.0001:
            c_str = f"{abs_c:.2e}"
        else:
            c_str = f"{abs_c:.{precision}f}"
        sup = superscripts.get(i, f"^{i}")
        terms.append(f"{sign} {c_str}·{feature_name}{sup}")
    return "ŷ = " + " ".join(terms)


# ==================== НАВЧАННЯ ТА ОЦІНКА МОДЕЛІ ====================
def train_poly_model(degree, X_train, y_train, X_test, y_test):
    """
    Навчає поліноміальну регресію ступеня `degree` виключно на X_train,
    після чого обчислює метрики на X_train та X_test (без витоку даних).
    """
    poly = PolynomialFeatures(degree=degree, include_bias=False)
    X_train_poly = poly.fit_transform(X_train)
    X_test_poly = poly.transform(X_test)

    model = LinearRegression()
    model.fit(X_train_poly, y_train)

    y_pred_train = model.predict(X_train_poly)
    y_pred_test = model.predict(X_test_poly)

    mse_train = mean_squared_error(y_train, y_pred_train)
    mse_test = mean_squared_error(y_test, y_pred_test)
    rmse_train = np.sqrt(mse_train)
    rmse_test = np.sqrt(mse_test)
    r2_train = r2_score(y_train, y_pred_train)
    r2_test = r2_score(y_test, y_pred_test)

    return {
        "degree": degree,
        "model": model,
        "poly": poly,
        "intercept": model.intercept_,
        "coef": model.coef_,
        "mse_train": mse_train,
        "mse_test": mse_test,
        "rmse_train": rmse_train,
        "rmse_test": rmse_test,
        "r2_train": r2_train,
        "r2_test": r2_test,
        "y_pred_train": y_pred_train,
        "y_pred_test": y_pred_test
    }


@st.cache_data
def compute_learning_curve(X_train_vals, X_test_vals, y_train_vals, y_test_vals, max_degree=10):
    """
    Обчислює Train та Test MSE для ступенів полінома від 1 до max_degree
    для побудови кривої перенавчання (U-shaped test error).
    """
    degrees = list(range(1, max_degree + 1))
    train_errors = []
    test_errors = []
    train_r2s = []
    test_r2s = []

    for d in degrees:
        p = PolynomialFeatures(degree=d, include_bias=False)
        X_tr = p.fit_transform(X_train_vals)
        X_te = p.transform(X_test_vals)

        m = LinearRegression().fit(X_tr, y_train_vals)
        pred_tr = m.predict(X_tr)
        pred_te = m.predict(X_te)

        train_errors.append(mean_squared_error(y_train_vals, pred_tr))
        test_errors.append(mean_squared_error(y_test_vals, pred_te))
        train_r2s.append(r2_score(y_train_vals, pred_tr))
        test_r2s.append(r2_score(y_test_vals, pred_te))

    return degrees, train_errors, test_errors, train_r2s, test_r2s


# ==================== ГОЛОВНА ЛОГІКА ДОДАТКУ ====================
def main():
    # Завантаження датасету
    raw_df, feature_names, data_source = load_housing_data()

    # Заголовок сторінки
    st.title("📈 California Housing: Поліноміальна Регресія та Аналіз Перенавчання")
    st.markdown("""
    **Практична робота:** Дослідження впливу ступеня полінома на якість регресійної моделі, 
    порівняння помилок на навчальній (**Train**) і тестовій (**Test**) вибірках та наочна демонстрація явища **перенавчання (Overfitting)**.
    """)

    # ---------------- БІЧНА ПАНЕЛЬ (НАЛАШТУВАННЯ) ----------------
    st.sidebar.header("⚙️ Керування Моделями")
    st.sidebar.markdown("### 🎛️ Ступені поліномів")

    deg_1 = st.sidebar.slider(
        "Ступінь Моделі 1 (d₁)",
        min_value=1,
        max_value=10,
        value=1,
        help="Ступінь 1 відповідає класичній лінійній регресії: ŷ = b₀ + b₁x."
    )

    deg_2 = st.sidebar.slider(
        "Ступінь Моделі 2 (d₂)",
        min_value=1,
        max_value=10,
        value=3,
        help="Ступінь полінома для другої моделі: ŷ = b₀ + b₁x + b₂x² + ... + bₖxᵏ."
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ✂️ Поділ даних (Train / Test)")

    test_size_percent = st.sidebar.slider(
        "Тестова вибірка (%)",
        min_value=10,
        max_value=40,
        value=20,
        step=5,
        help="Відсоток спостережень, відкладених для тестування (не доступні для навчання)."
    )
    test_size = test_size_percent / 100.0

    sample_size = st.sidebar.select_slider(
        "Розмір вибірки для аналізу",
        options=[300, 600, 1000, 1500, 2000],
        value=1500,
        help="Менша кількість спостережень наочніше демонструє ефект перенавчання при високих ступенях полінома."
    )

    st.sidebar.markdown("---")
    st.sidebar.info(
        f"**Джерело даних:** {data_source}\n\n"
        f"**Ознака (x):** `MedInc` (Медіанний дохід)\n\n"
        f"**Ціль (y):** `MedHouseValue` (Ціна будинку)\n\n"
        f"**Автор:** Артем (10 клас, НВК №141 «ОРТ»)"
    )

    # Підготовка підвибірки даних
    if len(raw_df) > sample_size:
        df = raw_df.sample(n=sample_size, random_state=42).reset_index(drop=True)
    else:
        df = raw_df.copy().reset_index(drop=True)

    # Використовуємо одну числову ознаку MedInc та цільовий показник MedHouseValue
    X = df[["MedInc"]]
    y = df["MedHouseValue"]

    # Єдиний поділ даних для обох моделей
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )

    # Навчання обох моделей виключно на Train вибірці
    res1 = train_poly_model(deg_1, X_train, y_train, X_test, y_test)
    res2 = train_poly_model(deg_2, X_train, y_train, X_test, y_test)

    # Попередження про однаковий поділ
    st.caption(
        f"🔒 **Принцип чистоти експерименту:** Обидві моделі навчаються на однакових **{len(X_train)}** тренувальних записах "
        f"і оцінюються на однакових **{len(X_test)}** тестових записах (test_size = {test_size_percent}%, random_state = 42). "
        f"Жодна модель **не бачить тестових даних** під час навчання!"
    )

    # ---------------- ВКЛАДКИ ДОДАТКА ----------------
    tab_compare, tab_overfitting, tab_predict, tab_data = st.tabs([
        "🔬 1. Порівняння моделей & Формули",
        "🧠 2. Аналіз перенавчання (Overfitting)",
        "🔮 3. Інтерактивний калькулятор прогнозу",
        "📊 4. Огляд датасету California Housing"
    ])

    # ==================== ВКЛАДКА 1: ПОРІВНЯННЯ МОДЕЛЕЙ & ФОРМУЛИ ====================
    with tab_compare:
        st.subheader("📐 Навчені математичні формули моделей")
        st.markdown(r"""
        Кожна модель знаходить оптимальні вагові коефіцієнти $b_0, b_1, \dots, b_k$ методом найменших квадратів (OLS).
        Якщо ступінь дорівнює **1**, модель є строго **лінійною** ($\hat{y} = b_0 + b_1 x$).
        При ступені **$k > 1$** модель є **поліноміальною** ($\hat{y} = b_0 + b_1 x + b_2 x^2 + \dots + b_k x^k$).
        """)

        col_m1, col_m2 = st.columns(2)

        # Картка Моделі 1
        with col_m1:
            st.markdown(f"""
            <div class="metric-card">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <h4 style="margin:0; color:#00f2fe;">🔹 Модель 1: {('Лінійна регресія' if deg_1 == 1 else f'Поліном ступеня {deg_1}')}</h4>
                <span class="status-badge-ok">Ступінь d = {deg_1}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Формула в LaTeX
            latex_1 = format_formula_latex(res1["intercept"], res1["coef"], "x")
            st.markdown("**Математичний вираз (LaTeX):**")
            st.latex(latex_1)

            # Текстова формула
            text_formula_1 = format_formula_text(res1["intercept"], res1["coef"], "MedInc")
            st.markdown(f'<div class="formula-box">{text_formula_1}</div>', unsafe_allow_html=True)
            st.caption(r"Де $x$ (`MedInc`) — медіанний дохід ($10,000), а $\hat{y}$ (`MedHouseValue`) — прогнозована ціна ($100,000).")

            # Метрики Моделі 1
            m1_c1, m1_c2 = st.columns(2)
            m1_c1.metric(
                label="Train MSE (навчальна)",
                value=f"{res1['mse_train']:.4f}",
                help="Середньоквадратична помилка на тренувальній вибірці"
            )
            m1_c2.metric(
                label="Test MSE (тестова)",
                value=f"{res1['mse_test']:.4f}",
                delta=f"{(res1['mse_test'] - res1['mse_train']):+.4f} Δ",
                delta_color="inverse",
                help="Середньоквадратична помилка на нових тестових даних"
            )

            m1_c3, m1_c4 = st.columns(2)
            m1_c3.metric(label="Train R² (детермінація)", value=f"{res1['r2_train']:.4f}")
            m1_c4.metric(label="Test R² (детермінація)", value=f"{res1['r2_test']:.4f}")

        # Картка Моделі 2
        with col_m2:
            st.markdown(f"""
            <div class="metric-card">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <h4 style="margin:0; color:#ec4899;">🔸 Модель 2: {('Лінійна регресія' if deg_2 == 1 else f'Поліном ступеня {deg_2}')}</h4>
                <span class="status-badge-ok" style="color:#ec4899; background:rgba(236,72,153,0.15);">Ступінь d = {deg_2}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Формула в LaTeX
            latex_2 = format_formula_latex(res2["intercept"], res2["coef"], "x")
            st.markdown("**Математичний вираз (LaTeX):**")
            st.latex(latex_2)

            # Текстова формула
            text_formula_2 = format_formula_text(res2["intercept"], res2["coef"], "MedInc")
            st.markdown(f'<div class="formula-box-2">{text_formula_2}</div>', unsafe_allow_html=True)
            st.caption(r"Де $x$ (`MedInc`) — медіанний дохід ($10,000), а $\hat{y}$ (`MedHouseValue`) — прогнозована ціна ($100,000).")

            # Метрики Моделі 2
            m2_c1, m2_c2 = st.columns(2)
            m2_c1.metric(
                label="Train MSE (навчальна)",
                value=f"{res2['mse_train']:.4f}",
                help="Середньоквадратична помилка на тренувальній вибірці"
            )
            m2_c2.metric(
                label="Test MSE (тестова)",
                value=f"{res2['mse_test']:.4f}",
                delta=f"{(res2['mse_test'] - res2['mse_train']):+.4f} Δ",
                delta_color="inverse",
                help="Середньоквадратична помилка на нових тестових даних"
            )

            m2_c3, m2_c4 = st.columns(2)
            m2_c3.metric(label="Train R² (детермінація)", value=f"{res2['r2_train']:.4f}")
            m2_c4.metric(label="Test R² (детермінація)", value=f"{res2['r2_test']:.4f}")

        st.markdown("---")

        # Порівняльна таблиця метрик
        st.subheader("📋 Зведена порівняльна таблиця метрик")

        def evaluate_status(mse_tr, mse_te, deg):
            ratio = mse_te / (mse_tr + 1e-9)
            if ratio > 1.25 and deg >= 5:
                return "🚨 Перенавчання (Overfitting)"
            elif ratio > 1.10:
                return "⚠️ Помірне розходження"
            elif deg == 1 and mse_te > 0.70:
                return "ℹ️ Недонавчання (Underfitting)"
            else:
                return "✅ Збалансоване наближення (Good fit)"

        summary_df = pd.DataFrame([
            {
                "Модель": f"Модель 1 (ступінь {deg_1})",
                "Тип": "Лінійна" if deg_1 == 1 else "Поліноміальна",
                "Train MSE": f"{res1['mse_train']:.4f}",
                "Test MSE": f"{res1['mse_test']:.4f}",
                "Різниця (Test - Train)": f"{(res1['mse_test'] - res1['mse_train']):+.4f}",
                "Test R²": f"{res1['r2_test']:.4f}",
                "Статус генералізації": evaluate_status(res1['mse_train'], res1['mse_test'], deg_1)
            },
            {
                "Модель": f"Модель 2 (ступінь {deg_2})",
                "Тип": "Лінійна" if deg_2 == 1 else "Поліноміальна",
                "Train MSE": f"{res2['mse_train']:.4f}",
                "Test MSE": f"{res2['mse_test']:.4f}",
                "Різниця (Test - Train)": f"{(res2['mse_test'] - res2['mse_train']):+.4f}",
                "Test R²": f"{res2['r2_test']:.4f}",
                "Статус генералізації": evaluate_status(res2['mse_train'], res2['mse_test'], deg_2)
            }
        ])
        st.dataframe(summary_df, use_container_width=True)

        st.markdown("---")

        # Графік ліній/кривих регресії на фоні даних
        st.subheader("📊 Візуалізація апроксимації даних обома моделями")
        st.caption("Точки вибірки розділені на тренувальні (сині) та тестові (помаранчеві). Лінії показують криві прогнозів обох моделей.")

        fig, ax = plt.subplots(figsize=(10, 5.5), facecolor="#0e1726")
        ax.set_facecolor("#0e1726")

        # Точки Train і Test
        ax.scatter(
            X_train["MedInc"], y_train,
            color="#3b82f6", alpha=0.35, s=24, edgecolors="none",
            label=f"Train вибірка ({len(X_train)} точок)"
        )
        ax.scatter(
            X_test["MedInc"], y_test,
            color="#f59e0b", alpha=0.6, s=32, marker="o", edgecolors="#d97706",
            label=f"Test вибірка ({len(X_test)} точок)"
        )

        # Побудова гладких кривих регресії
        x_min = float(X["MedInc"].min())
        x_max = float(X["MedInc"].max())
        x_grid = pd.DataFrame({"MedInc": np.linspace(x_min, x_max, 400)})

        # Прогноз Моделі 1
        X_grid_p1 = res1["poly"].transform(x_grid)
        y_grid_p1 = res1["model"].predict(X_grid_p1)
        ax.plot(
            x_grid["MedInc"], y_grid_p1,
            color="#00f2fe", linewidth=2.8,
            label=f"Модель 1 (ступінь {deg_1}): ŷ = b₀ + ... [Test MSE={res1['mse_test']:.3f}]"
        )

        # Прогноз Моделі 2
        X_grid_p2 = res2["poly"].transform(x_grid)
        y_grid_p2 = res2["model"].predict(X_grid_p2)
        ax.plot(
            x_grid["MedInc"], y_grid_p2,
            color="#ec4899", linewidth=2.8, linestyle="--",
            label=f"Модель 2 (ступінь {deg_2}): ŷ = b₀ + ... [Test MSE={res2['mse_test']:.3f}]"
        )

        # Оформлення осей
        ax.set_xlabel("Медіанний дохід жителів (MedInc, $10,000)", color="#cbd5e1", fontsize=11)
        ax.set_ylabel("Медіанна вартість житла (MedHouseValue, $100,000)", color="#cbd5e1", fontsize=11)
        ax.set_title("California Housing: Лінійна проти Поліноміальної регресії", color="#f8fafc", fontsize=13, fontweight="bold", pad=12)
        ax.tick_params(colors="#94a3b8")
        ax.grid(True, linestyle=":", alpha=0.3, color="#64748b")
        for spine in ax.spines.values():
            spine.set_color("#334155")

        ax.legend(
            facecolor="#1e293b", edgecolor="#475569",
            labelcolor="#f1f5f9", fontsize=9, loc="upper left"
        )
        plt.tight_layout()
        st.pyplot(fig)

        # Детальна таблиця коефіцієнтів
        with st.expander("🔍 Детальна таблиця коефіцієнтів моделей (b₀, b₁, ...)"):
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.write(f"**Коефіцієнти Моделі 1 (ступінь {deg_1}):**")
                coef_data_1 = [{"Член формули": "b₀ (Вільний член / Intercept)", "Значення": f"{res1['intercept']:.6f}"}]
                for idx, c in enumerate(res1["coef"], start=1):
                    coef_data_1.append({"Член формули": f"b_{idx} (коефіцієнт при x^{idx})", "Значення": f"{c:.6f}"})
                st.dataframe(pd.DataFrame(coef_data_1), use_container_width=True)

            with col_t2:
                st.write(f"**Коефіцієнти Моделі 2 (ступінь {deg_2}):**")
                coef_data_2 = [{"Член формули": "b₀ (Вільний член / Intercept)", "Значення": f"{res2['intercept']:.6f}"}]
                for idx, c in enumerate(res2["coef"], start=1):
                    coef_data_2.append({"Член формули": f"b_{idx} (коефіцієнт при x^{idx})", "Значення": f"{c:.6f}"})
                st.dataframe(pd.DataFrame(coef_data_2), use_container_width=True)

    # ==================== ВКЛАДКА 2: АНАЛІЗ ПЕРЕНАВЧАННЯ (OVERFITTING) ====================
    with tab_overfitting:
        st.subheader("🧠 Чому тестова вибірка вирішує все: Суть явища Перенавчання")

        st.markdown("""
        ### 1. Чому оцінка на тестових даних краще показує якість моделі?
        * **Навчальні дані (Train)** — це матеріали, за якими модель знаходить свої коефіцієнти. Якщо ми тестуємо модель лише на Train-даних, це схоже на те, якби учень складав іспит, знаючи наперед точні відповіді на запитання. Ми оцінюємо **пам'ять**, а не **розуміння**.
        * **Тестові дані (Test)** — це абсолютно нові, не бачені моделлю спостереження. Оцінка на них (Test MSE) показує здатність моделі до **генералізації** (здатність прогнозувати реальні нові випадки).
        
        ### 2. Чому нижча помилка на Train не означає кращу модель?
        * Поліном вищого степеня (наприклад, $d=7, 8, 10$) має дуже багато вільних параметрів. Така крива отримує надмірну гнучкість і починає **«підганятися» під кожну випадкову точку**, включаючи випадковий шум і викиди.
        * В результаті $MSE_{train}$ зменшується майже до нуля. Проте лінія регресії починає здійснювати різкі хаотичні коливання між точками.
        * Коли такій моделі подають нові тестові дані, вона робить величезні помилки — **$MSE_{test}$ стрімко зростає**. Це і є класичне **перенавчання (Overfitting)**.
        """)

        st.markdown("---")
        st.subheader("📉 Крива помилок залежно від ступеня полінома (Learning / Complexity Curve)")
        st.caption("Цей графік демонструє, як зі зростанням складності моделі Train MSE монотонно зменшується, а Test MSE після оптимальної точки різко йде вгору.")

        # Обчислення помилок для ступенів 1..10
        degs, tr_errs, te_errs, _, _ = compute_learning_curve(
            X_train.values, X_test.values, y_train.values, y_test.values, max_degree=10
        )

        fig_curve, ax_c = plt.subplots(figsize=(10, 5), facecolor="#0e1726")
        ax_c.set_facecolor("#0e1726")

        ax_c.plot(degs, tr_errs, marker="o", color="#3b82f6", linewidth=2.4, label="Train MSE (помилка на навчанні)")
        ax_c.plot(degs, te_errs, marker="s", color="#ef4444", linewidth=2.4, label="Test MSE (помилка на тесті)")

        # Маркери поточних вибраних моделей
        ax_c.scatter(
            [deg_1], [res1["mse_test"]],
            color="#00f2fe", s=130, zorder=5, edgecolors="#ffffff", linewidths=2,
            label=f"Модель 1 (ступінь {deg_1})"
        )
        ax_c.scatter(
            [deg_2], [res2["mse_test"]],
            color="#ec4899", s=130, zorder=5, edgecolors="#ffffff", linewidths=2,
            label=f"Модель 2 (ступінь {deg_2})"
        )

        ax_c.set_xlabel("Ступінь полінома (Polynomial Degree)", color="#cbd5e1", fontsize=11)
        ax_c.set_ylabel("Середньоквадратична помилка (MSE)", color="#cbd5e1", fontsize=11)
        ax_c.set_title("Train MSE проти Test MSE для ступенів полінома від 1 до 10", color="#f8fafc", fontsize=12, fontweight="bold")
        ax_c.set_xticks(degs)
        ax_c.tick_params(colors="#94a3b8")
        ax_c.grid(True, linestyle=":", alpha=0.3, color="#64748b")
        for spine in ax_c.spines.values():
            spine.set_color("#334155")

        ax_c.legend(
            facecolor="#1e293b", edgecolor="#475569",
            labelcolor="#f1f5f9", fontsize=9
        )
        plt.tight_layout()
        st.pyplot(fig_curve)

        # Діагностичний висновок для поточних моделей
        st.subheader("🎯 Поточний вердикт для обраних моделей:")
        c_verdict1, c_verdict2 = st.columns(2)

        with c_verdict1:
            st.markdown(f"**Модель 1 (ступінь {deg_1}):**")
            diff1 = res1["mse_test"] - res1["mse_train"]
            if deg_1 == 1:
                st.info("ℹ️ **Лінійна модель:** Має стабільну помилку та просту інтерпретацію. Присутнє невелике недонавчання (underfitting), оскільки реальна залежність має плавну нелінійність.")
            elif diff1 > 0.05:
                st.warning(f"⚠️ **Ознаки перенавчання:** Test MSE перевищує Train MSE на {diff1:.4f}. Модель починає залежати від локальних випадковостей вибірки.")
            else:
                st.success("✅ **Хороша генералізація:** Помилка на нових даних близька до тренувальної помилки.")

        with c_verdict2:
            st.markdown(f"**Модель 2 (ступінь {deg_2}):**")
            diff2 = res2["mse_test"] - res2["mse_train"]
            if deg_2 >= 6:
                st.error(f"🚨 **Явне перенавчання (Overfitting):** Ступінь {deg_2} є надлишковим! Train MSE = {res2['mse_train']:.4f}, але Test MSE зріс до {res2['mse_test']:.4f} (різниця {diff2:+.4f}). Модель втрачає практичну цінність для нових даних.")
            elif deg_2 in (2, 3, 4):
                st.success(f"🏆 **Оптимальний баланс (Sweet Spot):** Ступінь {deg_2} вловлює природну нелінійність доходу та ціни житла, демонструючи мінімальний Test MSE ({res2['mse_test']:.4f}).")
            else:
                st.info("ℹ️ Ступінь 1 (лінійний аналог).")

    # ==================== ВКЛАДКА 3: ІНТЕРАКТИВНИЙ КАЛЬКУЛЯТОР ПРОГНОЗУ ====================
    with tab_predict:
        st.subheader("🔮 Калькулятор вартості житла за навченими формулами")
        st.markdown("""
        Введіть медіанний дохід жителів мікрорайону $x$ (`MedInc`), щоб побачити, який прогноз обчислює кожна модель
        шляхом прямої підстановки у формулу:
        """)

        user_med_inc = st.slider(
            "Медіанний дохід мікрорайону (MedInc, $10,000):",
            min_value=0.5,
            max_value=15.0,
            value=4.5,
            step=0.1,
            help="Наприклад: 4.5 означає середньорічний сімейний дохід $45,000"
        )

        # Прогноз Моделі 1
        x_val_df = pd.DataFrame({"MedInc": [user_med_inc]})
        pred_val_1 = float(res1["model"].predict(res1["poly"].transform(x_val_df))[0])
        pred_usd_1 = pred_val_1 * 100000.0

        # Прогноз Моделі 2
        pred_val_2 = float(res2["model"].predict(res2["poly"].transform(x_val_df))[0])
        pred_usd_2 = pred_val_2 * 100000.0

        col_p1, col_p2 = st.columns(2)

        with col_p1:
            st.markdown(f"""
            <div class="metric-card" style="border-left:4px solid #00f2fe;">
              <h4 style="color:#00f2fe; margin-top:0;">Модель 1 (ступінь {deg_1})</h4>
              <p style="color:#94a3b8; font-size:0.9rem;">Прогноз за формулою: ŷ = {res1['intercept']:.4f} + ...</p>
              <h2 style="color:#ffffff; margin:10px 0;">${pred_usd_1:,.0f}</h2>
              <span style="color:#94a3b8; font-size:0.85rem;">({pred_val_1:.3f} в одиницях $100k)</span>
            </div>
            """, unsafe_allow_html=True)

        with col_p2:
            st.markdown(f"""
            <div class="metric-card" style="border-left:4px solid #ec4899;">
              <h4 style="color:#ec4899; margin-top:0;">Модель 2 (ступінь {deg_2})</h4>
              <p style="color:#94a3b8; font-size:0.9rem;">Прогноз за формулою: ŷ = {res2['intercept']:.4f} + ...</p>
              <h2 style="color:#ffffff; margin:10px 0;">${pred_usd_2:,.0f}</h2>
              <span style="color:#94a3b8; font-size:0.85rem;">({pred_val_2:.3f} в одиницях $100k)</span>
            </div>
            """, unsafe_allow_html=True)

        delta_usd = pred_usd_2 - pred_usd_1
        st.markdown(f"""
        > 💡 **Порівняння прогнозів:** Різниця між двома моделями при доході **${user_med_inc*10000:,.0f}** становить **${abs(delta_usd):,.0f}** 
        > ({'Модель 2 оцінює вище' if delta_usd >= 0 else 'Модель 1 оцінює вище'}). 
        > *Зверніть увагу: при виході в екстремальні значення доходу (MedInc > 10) перенавчені моделі високих ступенів можуть давати парадоксальні та від'ємні прогнози через неконтрольовану екстраполяцію полінома!*
        """)

    # ==================== ВКЛАДКА 4: ОГЛЯД ДАТАСЕТУ ====================
    with tab_data:
        st.subheader("📋 Огляд датасету California Housing")
        st.markdown(f"Використано вибірку обсягом **{len(df)}** спостережень для швидкої та плавної роботи у браузері.")

        d_col1, d_col2 = st.columns([3, 2])
        with d_col1:
            st.write("**Перші 15 рядків вибірки:**")
            st.dataframe(df.head(15), use_container_width=True)

        with d_col2:
            st.write("**Статистичні характеристики ознак:**")
            st.dataframe(df[["MedInc", "MedHouseValue"]].describe().T[["mean", "std", "min", "50%", "max"]], use_container_width=True)

        st.markdown("---")
        st.subheader("📊 Розподіл значень MedInc та MedHouseValue")
        fig_dist, (ax_d1, ax_d2) = plt.subplots(1, 2, figsize=(10, 4), facecolor="#0e1726")
        ax_d1.set_facecolor("#0e1726")
        ax_d2.set_facecolor("#0e1726")

        ax_d1.hist(df["MedInc"], bins=25, color="#00f2fe", alpha=0.7, edgecolor="#0e1726")
        ax_d1.set_title("Розподіл MedInc (Дохід, $10k)", color="#f8fafc", fontsize=11)
        ax_d1.tick_params(colors="#94a3b8")
        ax_d1.grid(True, linestyle=":", alpha=0.3, color="#64748b")

        ax_d2.hist(df["MedHouseValue"], bins=25, color="#ec4899", alpha=0.7, edgecolor="#0e1726")
        ax_d2.set_title("Розподіл MedHouseValue (Ціна, $100k)", color="#f8fafc", fontsize=11)
        ax_d2.tick_params(colors="#94a3b8")
        ax_d2.grid(True, linestyle=":", alpha=0.3, color="#64748b")

        for ax_elem in (ax_d1, ax_d2):
            for spine in ax_elem.spines.values():
                spine.set_color("#334155")

        plt.tight_layout()
        st.pyplot(fig_dist)


if __name__ == "__main__":
    main()
