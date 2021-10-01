import pandas as pd
import polars as pl # Make sure you have this library installed.
# It is faster than pandas.
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
import math
from math import e
import os
from bs4 import BeautifulSoup
from urllib.request import urlopen
import sys
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

# As we know howis the csv file, we only need these columns
cols_to_use = ["Fecha_Hora", "T1","Isc1","Voc1","Vmpp1","Impp1","Pmpp1","T2","Isc2","Voc2","Vmpp2","Impp2","Pmpp2",
           "T3","Isc3","Voc3","Vmpp3","Impp3","Pmpp3","T4","Isc4","Voc4","Vmpp4","Impp4","Pmpp4",
           "T5","Isc5","Voc5","Vmpp5","Impp5","Pmpp5","T6","Isc6","Voc6","Vmpp6","Impp6","Pmpp6",
           "T7","Isc7","Voc7","Vmpp7","Impp7","Pmpp7","T8","Isc8","Voc8","Vmpp8","Impp8","Pmpp8" ]

# For the correction and filtering of the data, we only need the previous columns
# without the date and time
cols_to_correct = cols_to_use[1:]

def leer_polars(csv_file, cols=cols_to_use):
    # With this function we can read the csv document and delete the null values
    # from the dataframe
    # We use polars instead of pandas because it is quite faster.
    # '''
    # Inputs:
    #     csv_file: directory of the csv_file
    #     cols: columns to use for the DataFrame
    # Output:
    #     data_polars: Polars DataFrame with no NaN values
    # '''

    data_polars = pl.read_csv(csv_file,sep="\t", columns=cols)
    # Replace null values with the minimum value.
    data_polars = data_polars.fill_none('min')
    return data_polars

def leer_csv(csv_file, cols=cols_to_use):
    # With this function we can read the csv document and delete the null values
    # from the dataframe
    # We use polars instead of pandas because it is quite faster.
    # '''
    # Inputs:
    #     csv_file: directory of the csv_file
    #     cols: columns to use for the DataFrame
    # Output:
    #     data_polars: Polars DataFrame with no NaN values
    # '''

    data = pd.read_csv(csv_file,sep="\t", columns=cols)
    return data



def corregir_datos(df, cols=cols_to_correct):
    # With this function we correct most of the wrong values of the csv
    # '''
    # Inputs:
    #     polars_df: DataFrame that has to be corrected
    #     cols: columns to use for the DataFrame
    # Output:
    #     polars_df: Corrected Polars DataFrame
    # '''
    for i in range(len(df)):
        for j in range(len(cols)):
            if i > 0  and i < (len(df)-1):
                if df[cols[j]][i] <= 0 and df[cols[j]][i-1] > 0 and df[cols[j]][i+1] > 0:
                    df[cols[j]][i] = (df[cols[j]][i-1] + df[cols[j]][i+1])/2
    return df


def polars_to_pandas(polars_df):
    # With this function we transform the polars dataframe to a pandas dataframe
    # so it is more comfortable to work with.
    # '''
    # Inputs:
    #     polars_df: polars DataFrame that must be transformed into pandas
    # Output:
    #     df: Pandas DataFrame ready to work with.
    # '''
    df = polars_df.to_pandas()
    df = df.set_index('Fecha_Hora')
    return df

def get_dataframe(csv_file):
    # With this function we get the pandas dataframe prepared to use in this project
    # It is the sum of the previous functions.
    # It takes a while (about 2-3 mins) to correct all of the data.
    # '''
    # Inputs:
    #     csv_file: directory of the csv_file
    # Output:
    #     df: Pandas DataFrame ready to work with.
    # '''
    data_polars = leer_polars(csv_file)
    corrected_data = corregir_datos(data_polars)
    df = polars_to_pandas(corrected_data)
    return df

def get_dataframe_no_polars(csv_file):
    data = leer_csv(csv_file)
    corrected_data = corregir_datos(data)
    df = corrected_data
    return corrected_data


def dia(datos,año,mes,dia):
    # With this function we create 3 columns from the index, so we can choose any day to study
    # '''
    # Inputs:
    #     datos: DataFrame to separate by days
    #     año: year to study
    #     mes: month to study
    #     day: day to study
    # Output:
    #     datos_dia: Pandas DataFrame of the required day
    # '''

    datos["dia"] = datos.index.day
    datos["mes"] = datos.index.month
    datos["año"] = datos.index.year
    datos_dia = datos[(datos['dia'] == dia) & (datos['mes'] == mes) & (datos['año'] == año)]
    return(datos_dia)



def grafica_dia(parametro,df_dia):
    # With this function we plot the given parameters in the csv
    # '''
    # Inputs:
    #     parametro: parameter to plot (Isc, Voc, T, Pmpp)
    # Output:
    #     Plots the chosen parameter for each PV cell
    # '''
    if parametro == 'Isc':
        unit = ' [A]'
    elif parametro == 'Voc':
        unit = ' [V]'
    elif parametro == 'T':
        unit = ' [C]'
    elif parametro == 'Pmpp':
        unit = ' [W]'

    fig = make_subplots(rows=4, cols=2,
                        subplot_titles=(parametro+" módulo 1",parametro+" módulo 2",parametro+" módulo 3",parametro+" módulo 4",
                                        parametro+" módulo 5",parametro+" módulo 6",parametro+" módulo 7",parametro+" módulo 8",))
    fila=1
    columna=1
    for i in range (8):
        fig.add_trace(go.Scatter(x=df_dia.index,y=df_dia[parametro+str(i+1)]),row=fila, col=columna)
        fig.update_yaxes(title_text=parametro+unit, row=fila, col=columna)
        fig.update_xaxes(title_text='fecha y hora', row=fila, col=columna)
        if columna == 2:
            columna=0
            fila+=1
        columna+=1


        fig.update_layout(height=1500, width=1000, title_text="Analisis de "+ parametro + " para cada modulo",title_x=0.5,
                          showlegend=False)
    fig.show()


def grafica_dia2(parametro1,parametro2,df_dia):
    # With this function we plot 2 parameters in the same graph
    # '''
    # Inputs:
    #     parametro1: first parameter to plot (Isc, Voc, T, Pmpp)
    #     parametro2: second parameter to plot (Isc, Voc, T, Pmpp)
    # Output:
    #     Plots the chosen parameters for each PV cell
    # '''
    for i in range (8):
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=df_dia.index, y=df_dia[parametro1+str(i+1)], name=parametro1),secondary_y=False,)
        fig.add_trace(go.Scatter(x=df_dia.index, y=df_dia[parametro2+str(i+1)], name=parametro2),secondary_y=True,)
        fig.update_layout(title_text= parametro1 +" y "+ parametro2 +' del modulo ' + str(i+1),title_x=0.5)
        fig.update_xaxes(title_text="Hora")
        fig.update_yaxes(title_text=parametro1, secondary_y=False)
        fig.update_yaxes(title_text=parametro2, secondary_y=True)
        fig.show()



def datos_aemet(years, months, days):
    # With this function we get data from the AEMET for a given date
    # '''
    # Inputs:
    #     years: list of beggining and ending years
    #     months: list of beggining and ending months
    #     days: list of beggining and ending days
    # Output:
    #     datos_meteo: DataFrame of meteorological data
    # '''

    api_key = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhbHUwMTAxNDQ3MDU2QHVsbC5lZHUuZXMiLCJqdGkiOiIyMGNmNGJlMy02NDBhLTRlZTItYWU2ZS0yYjkzMDc0MTU0ZmUiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTYxNzEyMzg0MSwidXNlcklkIjoiMjBjZjRiZTMtNjQwYS00ZWUyLWFlNmUtMmI5MzA3NDE1NGZlIiwicm9sZSI6IiJ9.drkbNcv_jR5VFpS2yI5BVsjBbhLDPDMfZvhzdcR3F6g"
    querystring = {"api_key":api_key}
    headers = {
        'cache-control': "no-cache"
        }
    tf_sur = 'C429I'
    url_base = 'https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/'
    estacion = f'estacion/{tf_sur}'
    # Creamos una lista de dataframes para luego juntarlos con los datos de los 5 días.
    dfs = []
    for i in range(len(years)):
        fecha_ini = f'fechaini/{years[i]}-{months[i]}-{days[i]}T00:00:00UTC/'
        fecha_fin = f'fechafin/{years[i]}-{months[i]}-{days[i]}T00:00:00UTC/'
        url = url_base + fecha_ini + fecha_fin + estacion

        # Obtener código datos
        response = requests.request('GET', url, params=querystring)
        data = response.json()

        codigo = data['datos']

        response = requests.request('GET', codigo, params=querystring)
        data = response.json()

        dates = pd.DataFrame(data, dtype=float)
        dfs.extend([dates])

    df = pd.concat(dfs)
    df = df.set_index('fecha') # Cambio el índice para poder usar el método resample

    datos_meteo = df[['tmed', 'velmedia', 'prec' ]]
    datos_meteo = datos_meteo.apply(lambda x: x.str.replace(',','.'))

    datos_meteo.tmed=pd.to_numeric(datos_meteo.tmed)
    datos_meteo.velmedia=pd.to_numeric(datos_meteo.velmedia)
    datos_meteo.prec=pd.to_numeric(datos_meteo.prec)

    datos_meteo.index = pd.to_datetime(datos_meteo.index, format = '%Y/%m/%d')

    return datos_meteo



def curva_i_v(df_dia):
    # This function allows us to plot the I-V curves for each module where Isc
    # # reaches its max value
    # '''
    # Inputs:
    #     df_dia: DataFrame of the day in study
    # Output:
    #     plots the I-V curve for each module
    # '''
    x=0
    for i in range(8):
        x+=1
        isc=df_dia["Isc"+str(x)].max()
        v=0
        corriente=[]
        voltaje=[]
        potencia=[]
        while True:
            i=isc-((1.7*(10**-8))*((math.exp(((1.6*(10**-19))*v/(((1.38*(10**-23))*300))))-1)))
            p=v*i
            corriente.append(i)
            voltaje.append(v)
            potencia.append(p)
            if i < 0:
                break
            v+=0.0001

        fig = go.Figure(data=[go.Scatter(name="Corriente(Amp)",x=voltaje, y=corriente)])

        fig.update_layout(barmode='group', title="Curva IV del modulo "+str(x),title_x=0.5,xaxis_title='Voltaje',yaxis_title="Corriente, Potencia")
        fig.add_trace(go.Scatter(name="Potencia(W)",x=voltaje, y=potencia))

        fig.show()


def irradiacion(mes):
    # This function allows us to get data from pvgis in order to determine the Fill Factor
    # '''
    # Inputs:
    #     mes: month to obtain the mean irradiation
    # Output:
    #     df: DataFrame of the mean irradiation
    # '''
    columns=["time(UTC)","G(i)"]
    df = pd.DataFrame(columns)
    url = "https://re.jrc.ec.europa.eu/api/DRcalc?lat=28.482&lon=+-16.321&raddatabase=PVGIS-SARAH&angle=30&aspect=180&browser=1&outputformat=csv&userhorizon=&usehorizon=1&js=1&select_database_daily=PVGIS-SARAH&month={}&localtime=0&global=1&dangle=30&daspect=180".format(mes)
    u = urlopen(url)
    try:
        html = u.read().decode('utf-8')
    finally:
        u.close()
    soup = BeautifulSoup(html, "html.parser")
    data = StringIO(str(soup))
    df = pd.read_csv(data, sep="\t",header=6,usecols=columns,skipfooter=6)
    return(df)

# If you have polars, then you can use this function
df = get_dataframe('datos.csv')
# If polars is not available for you, then you can use the following:
# df = get_dataframe_no_polars('datos.csv')
