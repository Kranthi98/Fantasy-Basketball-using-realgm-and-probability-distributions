# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 19:51:27 2023

@author: SHIVA
"""

import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import easygui




def myround(x, base=6):
    return base * round(x/base)

df = pd.read_clipboard()
fp = pd.read_clipboard()

df = pd.read_excel(easygui.fileopenbox("Player details file"))
df.head()

fp = pd.read_excel(easygui.fileopenbox("Fantasy points file"))
fp["FP"] = fp.FP.apply(myround)





from itertools import combinations

combos = [x for x in combinations(df.Sel1.values,8)]
pos, _ = pd.factorize(df.Pos.values)
teams, _ = pd.factorize(df.Team.values)
Crs = df.Credits.values
selc1 = df.Sel.values
tm_min = np.array([3,3])
tm_max = np.array([5,5])

combos1 = [x for x in combos if len(set(pos[list(x)])) == 5 if sum(Crs[list(x)]) <= 100 if sum(Crs[list(x)]) >= 99
           if np.all(np.bincount(teams[list(x)], selc1[list(x)]) <= tm_max) == True if np.all(np.bincount(teams[list(x)], selc1[list(x)]) >= tm_min) == True]
team_combos = pd.DataFrame(combos1)



Plr_replace = df[["Player","Sel1"]].set_index("Sel1").to_dict()["Player"]
team_combos = team_combos.replace(Plr_replace)

v = team_combos.loc[0,:].values
fp_dict = {x:list() for x in fp.Player.unique()}
for i in fp_dict.keys():
    
    fp_dict[i] = list(fp.query(f"Player == '{i}'")["FP"].values)
    
from itertools import product
from functools import reduce

conv = lambda x, y: np.convolve(x, y, mode='full')

def multi_conv(*arrs, fun):
    return reduce(fun, arrs)

def percentiles_df(fp1, combos1):
    
    p50 = []
    p75 = []
    p95 = []
    p97 = []
    p99 = []
    arr = np.array(combos1)
    quantiles_list = []
    j = 0
    for i in arr:

        b1 = np.array([[x,fp1[i[0]].count(x)/len(fp1[i[0]])] for x in set(fp1[i[0]])])
        b2 = np.array([[x,fp1[i[1]].count(x)/len(fp1[i[1]])] for x in set(fp1[i[1]])])
        b3 = np.array([[x,fp1[i[2]].count(x)/len(fp1[i[2]])] for x in set(fp1[i[2]])])
        b4 = np.array([[x,fp1[i[3]].count(x)/len(fp1[i[3]])] for x in set(fp1[i[3]])])
        b5 = np.array([[x,fp1[i[4]].count(x)/len(fp1[i[4]])] for x in set(fp1[i[4]])])
        b6 = np.array([[x,fp1[i[5]].count(x)/len(fp1[i[5]])] for x in set(fp1[i[5]])])
        b7 = np.array([[x,fp1[i[6]].count(x)/len(fp1[i[6]])] for x in set(fp1[i[6]])])
        b8 = np.array([[x,fp1[i[7]].count(x)/len(fp1[i[7]])] for x in set(fp1[i[7]])])
        
        values = np.add.outer(np.add.outer(np.add.outer(np.add.outer(np.add.outer(np.add.outer(np.add.outer(b1[:,0], b2[:,0]), b3[:,0]), b4[:,0]), b5[:,0]), b6[:,0]),b7[:,0]), b8[:,0]).flatten()
        probs = np.multiply.outer(np.multiply.outer(np.multiply.outer(np.multiply.outer(np.multiply.outer(np.multiply.outer(np.multiply.outer(b1[:,1], b2[:,1]), b3[:,1]), b4[:,1]), b5[:,1]), b6[:,1]),b7[:,1]), b8[:,1]).flatten()
        
        
        import scipy.interpolate
        ordering = np.argsort(values)
        distribution = scipy.interpolate.interp1d(np.cumsum(probs[ordering]), values[ordering], bounds_error=False, fill_value='extrapolate')
        
        
        p50.append(distribution(0.5))
        p75.append(distribution(0.75))
        p95.append(distribution(0.95))
        p97.append(distribution(0.97))
        p99.append(distribution(0.99))
        print(j)
        j = j+1

       
    final_df = pd.concat([combos1, pd.DataFrame(zip(p50,p75,p95,p97,p99), columns = ["p50",'p75',"p95","p97","p99"])], axis = 1)
    
    return final_df

final_combos = percentiles_df(fp_dict, team_combos)
