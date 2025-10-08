def key():
    return open('key.txt','r').read()

def historical(ticker, from_date='2025-05-01'):
    return f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?from={from_date}&apikey={key()}"

# array = np.ctypeslib.as_array(ptr, shape=(n,)) lib.free_array(ptr) free(ptr) malloc(n * sizeof(double)) x_c = (ctypes.c_double * n)(*x)

stocks = ['AAPL','MSFT','META','NVDA','ORCL','AMZN']

import requests
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ctypes
import time

quant = ctypes.CDLL("./stoch.so")
quant.SimulatePortfolio.argtypes = [ctypes.POINTER(ctypes.c_double) for _ in range(4)] + [ctypes.c_int, ctypes.c_int, ctypes.c_double]
quant.SimulatePortfolio.restype = ctypes.POINTER(ctypes.c_double)

quant.free_all.argtypes = [ctypes.POINTER(ctypes.c_double)]
quant.free_all.restype = None

def LoadData():
    data = {}
    for stock in stocks:
        resp = requests.get(historical(stock)).json()
        df = pd.DataFrame(resp['historical'])['adjClose'][::-1].values
        data[stock] = df
        time.sleep(0.6)
        print('This stock has loaded: ', stock)
    return data 

def KellyCriterion(X):
    m, n = X.shape
    ror = X[1:]/X[:-1] - 1.0
    mu = np.mean(ror, axis=0)
    cv = np.cov(ror.T)
    sd = np.sqrt(np.diagonal(cv))
    weights = np.linalg.inv(cv).dot(mu)
    ones = np.ones(n).dot(weights)
    return weights / ones, mu, sd


dataset = LoadData()
n = len(stocks)

X = np.array([dataset[stock] for stock in stocks]).T

S = X[-1]
W, Drift, Volt = KellyCriterion(X)

S = (ctypes.c_double * n)(*S)
W = (ctypes.c_double * n)(*W)
Drift = (ctypes.c_double * n)(*Drift)
Volt = (ctypes.c_double * n)(*Volt)


u = 15000

fig = plt.figure()
ax = [fig.add_subplot(2, 2, e+1) for e in range(4)]

for i, uz in enumerate((1/365.0, 7/365.0, 14/365.0, 30/365.0)):
    res = quant.SimulatePortfolio(S, W, Drift, Volt, n, u, uz)

    final_boss = np.ctypeslib.as_array(res, shape=(u,))
    quant.free_all(res)

    final_boss = list(map(lambda ie: np.maximum(-1.0, 1.0 if ie > 1 else ie), final_boss))

    ax[i].set_title(f'Days Simulated: {uz*365.0}')
    ax[i].hist(final_boss, color='cyan', edgecolor='black')


plt.show()
