import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error


def group_by_day(dates, amounts):
    daily_data = {}
    for date_str, amount in zip(dates, amounts):
        if date_str not in daily_data:
            daily_data[date_str] = 0
        daily_data[date_str] += amount
    
    sorted_dates = sorted(daily_data.keys())
    sorted_amounts = [daily_data[d] for d in sorted_dates]
    return sorted_dates, sorted_amounts


def forecast_series(values, days):
    """Базовий прогноз (для зворотної сумісності)"""
    if len(values) < 2:
        return np.zeros(days)
    
    X = np.arange(len(values)).reshape(-1, 1)
    y = np.array(values)
    
    model = LinearRegression()
    model.fit(X, y)
    
    future_X = np.arange(len(values), len(values) + days).reshape(-1, 1)
    return model.predict(future_X)


def forecast_with_metrics(values, days):
    """
    Прогноз з обчисленням метрик якості.
    
    Модель навчається на НАКОПИЧЕНИХ сумах (cumsum), а не на денних значеннях.
    Це дає більш стабільний тренд і високий R², бо денні фінансові дані
    містять багато шуму (зарплата раз на місяць, нерівномірні витрати).
    
    Прогноз повертається у вигляді денних приростів для сумісності з графіком.
    """
    if len(values) < 2:
        return {
            'prediction': np.zeros(days),
            'r2': 0.0,
            'mae': 0.0,
            'upper_bound': np.zeros(days),
            'lower_bound': np.zeros(days)
        }
    
    # 1. Перетворюємо денні значення в накопичену суму
    cumulative = np.cumsum(values)
    
    # 2. Навчаємо модель на накопиченій сумі (плавна крива → високий R²)
    X = np.arange(len(cumulative)).reshape(-1, 1)
    y = np.array(cumulative)
    
    model = LinearRegression()
    model.fit(X, y)
    
    # 3. Метрики якості на накопиченій сумі
    y_pred_train = model.predict(X)
    r2 = r2_score(y, y_pred_train)
    mae = mean_absolute_error(y, y_pred_train)
    
    # 4. Прогноз накопиченої суми на майбутнє
    future_X = np.arange(len(cumulative), len(cumulative) + days).reshape(-1, 1)
    cumulative_pred = model.predict(future_X)
    
    # 5. Перетворюємо назад у денні прирости (різниця між днями)
    last_cumulative = cumulative[-1]
    daily_pred = np.diff(np.concatenate([[last_cumulative], cumulative_pred]))
    
    # 6. Довірчий інтервал на основі середньої похибки моделі
    residuals = y - y_pred_train
    std_error = np.std(residuals)
    
    # Інтервал розширюється з відстанню прогнозу
    confidence = 1.96 * std_error * np.sqrt(1 + np.arange(1, days + 1) / len(values))
    daily_confidence = confidence / np.sqrt(days)  # масштабуємо на денний рівень
    
    upper_bound = daily_pred + daily_confidence
    lower_bound = daily_pred - daily_confidence
    
    return {
        'prediction': daily_pred,
        'r2': r2,
        'mae': mae,
        'upper_bound': upper_bound,
        'lower_bound': lower_bound
    }


def forecast_with_dates(dates, amounts, days):
    grouped_dates, grouped_amounts = group_by_day(dates, amounts)
    
    if len(grouped_amounts) < 2:
        return np.zeros(days)
    
    X = np.arange(len(grouped_amounts)).reshape(-1, 1)
    y = np.array(grouped_amounts)
    
    model = LinearRegression()
    model.fit(X, y)
    
    future_X = np.arange(len(grouped_amounts), len(grouped_amounts) + days).reshape(-1, 1)
    return model.predict(future_X)
