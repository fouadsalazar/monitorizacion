#!/usr/bin/env python
# coding: utf-8

# In[11]:


import pandas as pd
import plotly.graph_objects as go
import requests
import json
import os

def corregir_datos(df):

    columna = ["T1","Isc1","Voc1","Vmpp1","Impp1","Pmpp1","T2","Isc2","Voc2","Vmpp2","Impp2","Pmpp2",
           "T3","Isc3","Voc3","Vmpp3","Impp3","Pmpp3","T4","Isc4","Voc4","Vmpp4","Impp4","Pmpp4",
           "T5","Isc5","Voc5","Vmpp5","Impp5","Pmpp5","T6","Isc6","Voc6","Vmpp6","Impp6","Pmpp6",
           "T7","Isc7","Voc7","Vmpp7","Impp7","Pmpp7","T8","Isc8","Voc8","Vmpp8","Impp8","Pmpp8"]
    
    for i in range(len(df)):
        for j in range(len(columna)):
            if i > 0  and i < (len(df)-1):
                if df[columna[j]][i] == 0 and df[columna[j]][i-1] > 0 and df[columna[j]][i+1] > 0:
                    df[columna[j]][i] = (df[columna[j]][i-1] + df[columna[j]][i+1])/2
    return (df)

def leer(datos):
    df = pd.read_csv(datos,sep="\t")
    
    # Elimino las columnas buffer del dataframe
    for i in range(8):
        del(df['Buffer{}'.format(i+1)])
        
    df.fillna(0,inplace=True)

    # Se añade una nueva columna al dataframe solo con la fecha para facilitar el filtrado de datos
    lista = []
    for i in range(len(df)):
        
        # Se crea una nueva columna solo con las fechas (se quitan las horas)
        fecha = df["Fecha_Hora"][i]
        fecha = fecha[0:10]
        lista.append(fecha)
        
    df["Fecha"] = lista
    
    return(df)

def dia(año,mes,dia):
    dia = '{}-{}-{}'.format(año,mes,dia)
    df_dia = df[(df['Fecha']==dia)]
    
    df_dia = corregir_datos(df_dia)
    return(df_dia)

def grafica_dia(parametro,df_dia):
    for i in range (8):
        fig = go.Figure(data=[
            go.Scatter(name=f'{"Modulo "+"{}".format(i+1)}',x=df_dia["Fecha_Hora"], y=df_dia[parametro+str(i+1)])])

        fig.update_layout(barmode='group', title=parametro + ' del modulo ' + str(i+1),
                           xaxis_title='Hora',
                           yaxis_title=parametro)
        fig.show()
        
def obtengo_clima(a1,m1,d1,a2,m2,d2):
    url = 'https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{}-{}-{}T00:00:00UTC/fechafin/{}-{}-{}T23:59:59UTC/estacion/C447A'.format(a1,m1,d1,a2,m2,d2)

    # Esta es personal a cada uno
    api_key = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhbHUwMTAxNDQ3MDU2QHVsbC5lZHUuZXMiLCJqdGkiOiIyMGNmNGJlMy02NDBhLTRlZTItYWU2ZS0yYjkzMDc0MTU0ZmUiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTYxNzEyMzg0MSwidXNlcklkIjoiMjBjZjRiZTMtNjQwYS00ZWUyLWFlNmUtMmI5MzA3NDE1NGZlIiwicm9sZSI6IiJ9.drkbNcv_jR5VFpS2yI5BVsjBbhLDPDMfZvhzdcR3F6g"
    querystring = {"api_key":api_key}

    headers = {
        'cache-control': "no-cache"
        }

    # Obtener código datos
    response = requests.request("GET", url, params=querystring)
    data = response.json()

    codigo = data['datos']

    response = requests.request("GET", codigo, params=querystring)
    data = response.json()
    
    dates = pd.DataFrame(data)
    return (dates)


# In[13]:


df = leer("datos.csv")

# Cambiar la fecha para escoger cualquier otro dia
df_dia = dia('2021','07','01')

# Cambiar el parametro si se quiere estudiar otro (Pmpp,Isc,Voc,T,Vmpp,Impp)
grafica_dia('Pmpp',df_dia)

# Se visualizan los datos del clima de ese dia 
clima = obtengo_clima('2021','07','01','2021','07','01')
clima


# In[ ]:


# Podriamos hacer otro codigo para buscar maximos en un año, de temperatura, potencia, lo que sea
# Tambien podria evaluarse la generacion con la radicion segun la fecha daDA PVGIS


# In[4]:


# Estaba probando automatizarlo asi, pero no me funciona a pesar de hago lo mismo que arriba, lo cual me parece raro


df = leer("datos.csv")

while True:
    print('A continuacion se estudiara un dia en concreto')
    año = str(input('Año = '))
    mes = str(input('Mes = '))
    dia = str(input('Dia = '))
    df_dia = dia(año,mes,dia)
    print()
    while True:
        print('A continuacion escriba cual parametro quiere estudiar (Pmpp,Isc,Voc,T,Vmpp,Impp)')
        parametro=str(input("Parametro = "))
        grafica_dia(parametro,df_dia)
        respuesta= str(input('¿Desea estudiar otro parametro?(s/n)'))
        if respuesta !='s':
            break
    respuesta= input('¿Desea estudiar otro dia?(s/n)')
    if respuesta !='s':
        break
    else:
        os.system('cls')


# In[ ]:





# In[ ]:




