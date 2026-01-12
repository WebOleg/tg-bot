import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime

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
    if len(values) < 2:
        return np.zeros(days)
    
    X = np.arange(len(values)).reshape(-1, 1)
    y = np.array(values)
    
    model = LinearRegression()
    model.fit(X, y)
    
    future_X = np.arange(len(values), len(values) + days).reshape(-1, 1)
    return model.predict(future_X)

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
