import pandas as pd

df = pd.read_csv('accounts.csv')

print(((df.isnull().sum()/len(df))*100).round(2))