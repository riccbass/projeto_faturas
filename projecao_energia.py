# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 09:10:23 2022

@author: ricar
"""

import pandas as pd

import seaborn as sns
import numpy as np

import xgboost as xgb
from sklearn.metrics import mean_squared_error
from neuralprophet import NeuralProphet

import matplotlib.pyplot as plt
color_pal = sns.color_palette()



from sklearn.model_selection import TimeSeriesSplit

df = pd.read_excel(r'C:\projeto_faturas\consumo_praia.xlsx')

df = df.set_index('DATA')

df.index = pd.to_datetime(df.index)

df.plot(style=".", 
        figsize=(15, 8), 
        color=color_pal[0])

df['CONSUMO'].plot(kind='hist', bins=20)

df.query('CONSUMO > 1_000').plot(style='.')

df = df.query('CONSUMO < 1_000').copy()

train = df.loc[df.index < '01-01-2022']
test = df.loc[df.index >= '01-01-2022']

fig, ax = plt.subplots(figsize=(15, 5))
train.plot(ax=ax, label='train')
test.plot(ax=ax, label='test')
ax.axvline('01-01-2022', color='black', ls='--')
ax.legend(['Training', 'Test'])


def create_features(df):

  df = df.copy()
  df['quarter'] = df.index.quarter
  df['month'] = df.index.month
  df['year'] = df.index.year

  return df

df = create_features(df)

def add_lags(df):


  df = df.copy()
  
  try:
      
      del df['lag1']
      
  except:
      pass
  
  df['yearmonth'] = df.index
  df['yearmonth'] = df['yearmonth'].dt.strftime('%Y%m').astype('int')
    
  df_ant = df.copy(deep=True)

  df_ant['yearmonth'] += 100    
  
  df_ant = df_ant[['yearmonth', 'CONSUMO']]
  
  df_ant.rename(columns={'CONSUMO':'lag1'},
                inplace=True)
  
  df['DATA'] = df.index
  
  df = df.merge(df_ant,
                how = 'inner',
                on = ['yearmonth'])
  
  df.drop(['yearmonth'], axis=1, inplace=True)


  df = df.set_index('DATA')

  df.index = pd.to_datetime(df.index)  

  return df

df = add_lags(df)

fig, ax = plt.subplots(figsize=(10, 8))
sns.boxplot(data=df,
            x='month',
            y='CONSUMO')

tss = TimeSeriesSplit(n_splits=2, test_size=9, gap=1)
df = df.sort_index() #needed for the split

fold = 0
preds = []
scores = []

for train_idx, val_idx in tss.split(df):

  train = df.iloc[train_idx]
  test = df.iloc[val_idx]

  train = create_features(train)
  test = create_features(test)

  features = [ 'quarter', 'month', 'year',
               'lag1']
               
  target = 'CONSUMO'

  X_train = train[features]
  y_train = train[target]

  X_test = test[features]
  y_test = test[target]

  reg = xgb.XGBRegressor(base_score=0.5,
                         booster='gbtree',
                         objective='reg:squarederror',
                         max_depth=3,
                         n_estimators=1_000, 
                         early_stopping_rounds=50, 
                         learning_rate=0.01)
  
  reg.fit(X_train, y_train,
          eval_set=[(X_train, y_train), (X_test, y_test)],
          verbose=100)
  
  y_pred = reg.predict(X_test)
  preds.append(y_pred)
  score = np.sqrt(mean_squared_error(y_test, y_pred))
  scores.append(score)


print(np.mean(scores))
print(scores)

fi = pd.DataFrame(data=reg.feature_importances_,
             index=X_train.columns,
             columns=['impo'])

fi.sort_values('impo').plot(kind='barh')

test['prediction'] = reg.predict(X_test)

 
X_train = df[features]
y_train = df[target]
 
reg = xgb.XGBRegressor(base_score=0.5,
                        booster='gbtree',
                        objective='reg:squarederror',
                        max_depth=3,
                        n_estimators=500, 
                        early_stopping_rounds=50, 
                        learning_rate=0.01)
  
reg.fit(X_train, y_train,
        eval_set=[(X_train, y_train)],
        verbose=100)


future = pd.date_range('2022-01-01', '2022-10-01', freq = '1m')
future_df = pd.DataFrame(index=future)

future_df['isFuture'] = True

df['isFuture'] = False

df_and_future = pd.concat([df, future_df])

df_and_future = create_features(df_and_future)
df_and_future = add_lags(df_and_future)

future_w_features = df_and_future.query('isFuture').copy()

future_w_features['pred'] = reg.predict(future_w_features[features])

ax = future_w_features[['pred']].plot(figsize=(15, 8))
ax.set_title('Raw Data')


df = df.merge(test[['prediction']],
              how='left',
              left_index=True,
              right_index=True)

ax = df[['CONSUMO']].plot(figsize=(15, 8))
df['prediction'].plot(ax=ax, style=".")
ax.set_title('Raw Data')
