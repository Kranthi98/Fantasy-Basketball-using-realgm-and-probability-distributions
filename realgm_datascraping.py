# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 18:50:22 2023

@author: SHIVA
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd

def realgm_pbl_stats(url):     
    # url = "https://basketball.realgm.com/international/league/21/Polish-EBL/team/2541/Rawlplug-Sokol-Lancut/schedule"
    soup = BeautifulSoup(requests.get(url).text)
    
    links = ["https://basketball.realgm.com"+x.get("href") for x in soup.findAll("a") if "boxscore" in x.get("href")]
    print(links)
    final_df1 = pd.DataFrame()
    for i in links:
        tms = i.split("/")[-2].split("-at-")
        df = pd.read_html(i)
        tm1 = df[3].dropna().assign(Team = tms[0]).replace({"Starter":1,"Bench":0})
        tm2 = df[4].dropna().assign(Team = tms[1]).replace({"Starter":1,"Bench":0})
        final_df1 = pd.concat([final_df1, tm1, tm2])
        print(final_df1.columns)
        player_df = final_df1.assign(Duration = 
        (final_df1.Min.str.split(":",expand = True)
         .assign(Duration = lambda df : df[0].astype("int")+df[1].astype("int")/60)
         .drop(columns = [0,1]))).drop(columns = ['#', 'Pos',"PF", 'FGM-A', '3PM-A', 'FTM-A', 'FIC',
                'Off', 'Def', ])
    
    return player_df.query(f"Team == '{url.split('/')[-2]}'")
    

url = "https://basketball.realgm.com/nba/teams/Golden-State-Warriors/9/Schedule"
url1 = "https://basketball.realgm.com/nba/teams/Phoenix-Suns/23/Schedule"

samara = realgm_pbl_stats(url)
astana = realgm_pbl_stats(url1)

pd.concat([
samara.query("Duration > 10"),
astana.query("Duration > 10")]).to_excel("Israel_game_13032023.xlsx", index = False)


final_df = pd.concat([nz.query("Team == 'New-Zealand'"),syd.query("Team == 'Sydney'")])
final_df.assign(FP = lambda df : df.PTS-df.TO+1.2*df.Reb+1.5*df.Ast+3*(df.STL+df.BLK)).to_excel("NBL_stats.xlsx", index = False)
