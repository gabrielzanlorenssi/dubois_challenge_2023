#--------------------
#-- MODULES

import pandas as pd
import geopandas as gpd
import numpy as np
import zipfile
import os
import matplotlib.pyplot as plt
import matplotlib.colors as clr
from urllib import request
from skimpy import clean_columns
from unidecode import unidecode

#--------------------
#-- DOWNLOAD DATA

#-- Function to download data from ibge ftp
def ibge_extract(url, filename, fmt):
    '''download ibge data from ftp'''
    '''url is the location of the file,  filename is the file we want to download, fmt is the format of the file'''
    request.urlretrieve(url+filename+fmt, filename+fmt)
    if fmt == ".zip" :
      with zipfile.ZipFile(filename+fmt, 'r') as zip_ibge:
        zip_ibge.extractall(filename)

#-- Census
url_census = "https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/evolucao_da_divisao_territorial_do_brasil/evolucao_da_divisao_territorial_do_brasil_1872_2010/municipios_1872_1991/Documentacao/"
file_census = "pop_TUR_UF_1872_a_2010"
fmt_census = ".xls"

#-- Map
url_map = "https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/evolucao_da_divisao_territorial_do_brasil/evolucao_da_divisao_territorial_do_brasil_1872_2010/municipios_1872_1991/divisao_territorial_1872_1991/1872/"
file_map = "04_limite_de_provincia_1872" 
fmt_map = ".zip"

# run:
ibge_extract(url=url_census, filename=file_census, fmt=fmt_census)
ibge_extract(url=url_map, filename=file_map, fmt=fmt_map)

#--------------------
#--- PREPARING DATA

#-- 1872 POPULATION DATA

#- clean columns
censo = clean_columns(pd.read_excel("pop_TUR_UF_1872_a_2010.xls"))

#- generate 
censo = censo.groupby(['provincias_1872'], as_index=False)[["pop_total", "pop_escrava"]].sum()

#- lower case provinces column
censo['provincias_1872'] = censo.provincias_1872.str.lower().apply(unidecode)

#- enslaved percentage
censo["enslaved_perc"] = censo["pop_escrava"]/censo["pop_total"]

#-- 1872 MAP

#- read map
map1872 = gpd.read_file("04_limite_de_provincia_1872/04-limite de província 1872.shp")

#- lower case provinces
map1872['nome'] = map1872.nome.str.lower().apply(unidecode)

#--------------------
#--- PLOTTING

#-- MAP
#- merge map and data
map_final = map1872.merge(censo, left_on="nome", right_on="provincias_1872")

#- create categories
# map_final["enslaved_perc"].describe()
lbl = ["0-6%", "6-12%", "12-18%", "18-24%", "24%-37.4%"]

map_final["enslaved_cat"] = pd.cut(map_final["enslaved_perc"], 
                    bins=[0, 0.06, 0.12, 0.18, 0.24, np.inf],
                    labels=lbl)
#- custom colors
colors = ['#FFD700', '#FFC0CB', '#DC143C', '#654321', '#000000']
custom_pal = clr.ListedColormap(colors)

#- plotting
map_final.plot(column="enslaved_cat", cmap=custom_pal, linewidth=0.25, edgecolor="black", legend=True)

plt.show()
plt.savefig("dubois_brazil_1872.pdf")
plt.clf()

#--- Total enslaved
censo.pop_escrava.sum()  * 100 / censo.pop_total.sum()


