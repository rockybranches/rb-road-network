# coding: utf-8
import pandas as pd
import sqlite3
import os
os.getenv('RB_DATA')
get_ipython().run_line_magic('ls', '/home/robertc/Documents/rb_data/')
get_ipython().run_line_magic('ls', '/home/robertc/Documents/rb_data/county_pop/')
os.getenv('RB_DATA') + '/county_pop.db'
os.path.join(os.getenv('RB_DATA'), 'county_pop.db')
db_fn = os.path.join(os.getenv('RB_DATA'), 'county_pop.db')
con = sqlite3.connect(db_fn)
con
cur = con.cursor()
pd.DataFrame.to_sql
help(pd.DataFrame.to_sql)
df_ga = pd.read_csv('/home/robertc/Documents/rb_data/county_pop/ga.csv')
df_ga
df_ga_new = pd.read_excel('/home/robertc/Downloads/population projection for dad/County Residential Population Projections, 2020-2060 (1).xlsx')
get_ipython().run_line_magic('pip', 'install openpyxl')
df_ga_new = pd.read_excel('/home/robertc/Downloads/population projection for dad/County Residential Population Projections, 2020-2060 (1).xlsx')
df_ga_new
df_ga_new = pd.read_excel('/home/robertc/Downloads/population projection for dad/County Residential Population Projections, 2020-2060 (1).xlsx', header=True)
df_ga_new = pd.read_excel('/home/robertc/Downloads/population projection for dad/County Residential Population Projections, 2020-2060 (1).xlsx', header=1)
df_ga_new
df_ga_new = pd.read_excel('/home/robertc/Downloads/population projection for dad/County Residential Population Projections, 2020-2060 (1).xlsx', header=2)
df_ga_new
df_ga_new.head()
df_ga_new.columns
df_ga_new.COUNTY
df_ga_new.head(159)
df_ga_new.COUNTY
df_ga_new.head(158)
df_ga_new.head(159)
df_ga_new = df_ga_new.head(159)
df_ga_new.COUNTY
df_ga
df_ga.columns
pd.merge(left=df_ga, right=df_ga_new, on='county')
df_ga['county'] = df_ga['County']
df_ga_new['county'] = df_ga_new['COUNTY']
pd.merge(left=df_ga, right=df_ga_new, on='county')
df_ga
df_ga_new
df_ga_new['county'].str.lower()
df_ga_new['county'].str.title()
df_ga_new['county'] = df_ga_new['county'].str.title()
df_ga_new
pd.merge(left=df_ga, right=df_ga_new, on='county')
df_ga.county.isin(df_ga_new.county)
df_ga.county.isin(df_ga_new.county).all()
df_ga.county.isin(df_ga_new.county).mask()
get_ipython().system('df_ga.county.isin(df_ga_new.county)')
( not df_ga.county.isin(df_ga_new.county) )
df_ga.county.isin(df_ga_new.county).apply(lambda d: not d)
df_ga.county.isin(df_ga_new.county).apply(lambda d: not d).where()
df_ga.county[!(df_ga.county.isin(df_ga_new.county))]
df_ga.county[df_ga.county.isin(df_ga_new.county)]
df_ga.county.isin(df_ga_new.county).sum()
df_ga.county.count()
df_ga.county.where(lambda d: d not in df_ga_new.county)
df_ga.county.where(lambda d: d not in df_ga_new.county.to_list())
[c for c in df_ga.county.to_list() if c not in df_ga_new.county.to_list()]
df_ga['county'] = df_ga.county.lower()
df_ga['county'] = df_ga.county.str.lower()
df_ga_new['county'] = df_ga_new.county.str.lower()
[c for c in df_ga.county.to_list() if c not in df_ga_new.county.to_list()]
pd.merge(left=df_ga, right=df_ga_new, on='county')
pd.merge(left=df_ga, right=df_ga_new, on='county').columns
pd.merge(left=df_ga, right=df_ga_new, on='county').head()
pd.merge(left=df_ga, right=df_ga_new, on='county')[['2020', '2020_x']].head()
pd.merge(left=df_ga, right=df_ga_new, on='county').columns
pd.merge(left=df_ga, right=df_ga_new, on='county', suffixes=('_old', None)).columns
df_final = pd.merge(left=df_ga, right=df_ga_new, on='county', suffixes=('_old', None))
df_merge = pd.merge(left=df_ga, right=df_ga_new, on='county', suffixes=('_old', None))
df_ga.to_csv('/home/robertc/Documents/rb_data/.backup-ga.csv')
df_merge.head()
df_ga.head()
df_merge.drop(columns=[c for c in df_merge.columns if '_old' in c]).head()
df_ga.head()
df_merge.drop(columns=[c for c in df_merge.columns if '_old' in c] + ['COUNTY', 'county']).head()
df_merge.drop(columns=[c for c in df_merge.columns if '_old' in c] + ['COUNTY', 'county'])
df_final = df_merge.drop(columns=[c for c in df_merge.columns if '_old' in c] + ['COUNTY', 'county'])
get_ipython().run_line_magic('matplotlib', '')
import matplotlib.pyplot as plt
plt.ion()
df_final.T
df_final.loc[df_final.County=='Fulton']
df_final.loc[df_final.County=='Fulton'].T
df_final.loc[df_final.County=='Fulton'].T.columns
df_final.loc[df_final.County=='Fulton']
df_final.loc[df_final.County=='Fulton'].groupby('County')
df_final.loc[df_final.County=='Fulton'].groupby('County').agg()
df_final.loc[df_final.County=='Fulton'].groupby('County').mean()
df_final.loc[df_final.County=='Fulton'].groupby('County').mean().T
df_final.loc[df_final.County=='Fulton']
df_final.loc[df_final.County=='Fulton', [c for c in df_final.columns if c not in ['County NS Code']]]
df_final.loc[df_final.County=='Fulton', [c for c in df_final.columns if c not in ['County NS Code']]].T
df_final.loc[df_final.County=='Fulton', [c for c in df_final.columns if c not in ['County NS Code']]].T.iloc[1:,:]
df_final.loc[df_final.County=='Fulton', [c for c in df_final.columns if c not in ['County NS Code']]].T.iloc[1:,:].plot()
ax = plt.gca()
ax.get_figure()
df_ga.loc[df_final.County=='Fulton', [c for c in df_final.columns if c not in ['County NS Code']]].T.iloc[1:,:].plot(ax=ax, color='r')
df_ga.loc[df_final.County=='Fulton', [c for c in df_ga.columns if c not in ['County NS Code']]].T.iloc[1:,:].plot(ax=ax, color='r')
df_ga.loc[df_final.County=='Fulton', [c for c in df_ga.columns if c not in ['County NS Code']]].T.iloc[1:,:]
df_ga.loc[df_final.County=='Fulton', [c for c in df_ga.columns if c not in ['County NS Code']]].T.iloc[:-1,:]
df_ga.loc[df_final.County=='Fulton', [c for c in df_ga.columns if c not in ['County NS Code']]].T.iloc[1:-1,:]
df_ga.loc[df_final.County=='Fulton', [c for c in df_ga.columns if c not in ['County NS Code']]].T.iloc[1:-1,:].plot(ax=ax, color='r')
df_final
df_final.to_csv("/home/robertc/Documents/rb_data/county_pop/ga.csv", index=False)
