# -*- coding: utf-8 -*-
"""Data Imputation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MNgD2721bvBkyP2a2-fa9y8ACs4IJmr0
"""

from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
import scipy.signal as signal
import matplotlib.dates as mdates
import seaborn as sns
from scipy import interpolate
from tqdm import tqdm

"""# Data

* 미국 국채 - Price: dgs{} / Return: dgs{}_log
* 회사채 - Price: D{}AA / Return: D{}AA_log
* Emerging - Price: emerging / Return: emerging_log
* US - Price: us / Return: us_log
* Commodity - Price: com / Return: com_log
* Gold - Price: gold / Return: gold_log
"""

# DGS

t = [1, 2, 3, 5, 10, 20, 30]

for i in t:
  dgs = pd.read_csv('/content/drive/MyDrive/FR/머신러닝 프로젝트/DGS{}.csv'.format(i))
  dgs['DATE'] = pd.to_datetime(dgs.DATE)
  dgs.set_index('DATE', inplace = True)
  dgs_log = np.log(dgs).diff(1)
  dgs_log.rename(columns={'DGS{} Price'.format(i):'DGS{} Log'.format(i)}, inplace=True)
  globals()['dgs{}'.format(i)] = dgs
  globals()['dgs{}_log'.format(i)] = dgs_log

# 회사채

d = ['A', 'B']

for i in d:
  daa = pd.read_csv('/content/drive/MyDrive/FR/머신러닝 프로젝트/D{}AA.csv'.format(i))
  daa['DATE'] = pd.to_datetime(daa.DATE)
  daa.set_index('DATE', inplace = True)
  daa['D{}AA Price'.format(i)] = daa['D{}AA Price'.format(i)].astype(float, errors='raise')
  daa_log = np.log(daa).diff(1)
  daa_log.rename(columns={'D{}AA Price'.format(i):'D{}AA Log'.format(i)}, inplace=True)
  globals()['D{}AA'.format(i)] = daa
  globals()['D{}AA_log'.format(i)] = daa_log

# Emerging

emerging = pd.read_csv('/content/drive/MyDrive/FR/머신러닝 프로젝트/iShares MSCI Emerging Markets ETF 2003-04-13.csv')
emerging = emerging[['Date', 'Adj Close']]
emerging['Date'] = pd.to_datetime(emerging.Date)
emerging.set_index('Date', inplace = True)
emerging.rename(columns={'Adj Close':'Emerging'}, inplace = True)

emerging_log = np.log(emerging).diff(1)
emerging_log.rename(columns={'Emerging':'Emerging Log'}, inplace=True)

# US

us = pd.read_csv('/content/drive/MyDrive/FR/머신러닝 프로젝트/Wilshire 5000 1970-12-31.csv')
us = us.replace('.', np.NaN)
us['DATE'] = pd.to_datetime(us.DATE)
us.set_index('DATE', inplace = True)
us.rename(columns={'WILL5000IND':'US'}, inplace = True)
us['US'] = us['US'].astype(float, errors='raise')

us_log = np.log(us).diff(1)
us_log.rename(columns={'US':'US Log'}, inplace=True)

# Commodity

com = pd.read_csv('/content/drive/MyDrive/FR/머신러닝 프로젝트/S&P GSCI Commodity Total Return Data 1979-12-27_PP.csv', thousands = ',')
com = com[['Date', 'Price']]
com['Date'] = pd.to_datetime(com.Date)
com.set_index('Date', inplace = True)
com.rename(columns={'Price':'Commodity'}, inplace = True)

com_log = np.log(com).diff(1)
com_log.rename(columns={'Commodity':'Commodity Log'}, inplace=True)

# Gold

gold = pd.read_csv('/content/drive/MyDrive/FR/머신러닝 프로젝트/Gold Futures Data 1979-12-27_PP.csv', thousands = ',')
gold = gold[['Date', 'Price']]
gold['Date'] = pd.to_datetime(gold.Date)
gold.set_index('Date', inplace = True)
gold.rename(columns={'Price':'Gold'}, inplace = True)

gold_log = np.log(gold).diff(1)
gold_log.rename(columns={'Gold':'Gold Log'}, inplace=True)

price_list = [DAAA, DBAA, dgs1, dgs2, dgs3, dgs5, dgs10, dgs20, dgs30, gold, emerging, com, us] 
ret_list = [DAAA_log, DBAA_log, dgs1_log, dgs2_log, dgs3_log, dgs5_log, dgs10_log, dgs20_log, dgs30_log, gold_log, emerging_log, com_log, us_log]

price = pd.concat(price_list, axis=1)
price

ret = pd.concat(ret_list, axis=1)
ret

ret = ret['1979-12-30':'2022-02-28']
ret

# Cumulative sum for log returns
cumreto = ret.cumsum()

plt.figure(figsize=(20,8))
sns.lineplot(data=cumreto, dashes=False)

for j in tqdm(range(14)): # Number of NAs: 0 to 13

  na = ret.copy()

  # Drop the row when the number of NA is more than j
  for i in na.index:
    if na.loc[i].isnull().sum() <= j:
      continue
    else:
      na.drop(i, inplace = True)       

  # Imputation
  imp = IterativeImputer(imputation_order='arabic', sample_posterior=True)
  imp.fit(na)
  ar_imp = imp.transform(na)

  # Array > DataFrame
  df_imp = pd.DataFrame(ar_imp, columns = na.columns, index = na.index)

  # Cumulative sum of log returns after imputation
  cumret = df_imp.cumsum()

  plt.figure(figsize=(20,8))
  sns.lineplot(data=cumret, dashes=False).set_title('NaN = {}'.format(j))

for j in tqdm(range(14)):

  na = ret.copy()

  for i in na.index:
    if na.loc[i].isnull().sum() <= j:
      continue
    else:
      na.drop(i, inplace = True)

  # Interpolation
  na = na.interpolate()

  # Imputation
  imp = IterativeImputer(imputation_order='arabic', sample_posterior=True)
  imp.fit(na)
  ar_imp = imp.transform(na)

  df_imp = pd.DataFrame(ar_imp, columns = na.columns, index = na.index)

  cumret = df_imp.cumsum()

  plt.figure(figsize=(20,8))
  sns.lineplot(data=cumret, dashes=False).set_title('NaN = {}'.format(j))

