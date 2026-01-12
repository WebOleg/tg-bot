import numpy as np
from sklearn.linear_model import LinearRegression

def forecast_series(values, days):
    if len(values) < 2:
        return np.zeros(days)

    X = np.arange(len(values)).reshape(-1, 1)
    y = np.array(values)

    model = LinearRegression()
    model.fit(X, y)

    future_X = np.arange(len(values), len(values) + days).reshape(-1, 1)
    return model.predict(future_X)
