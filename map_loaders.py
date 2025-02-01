import json
import plotly.express as px
import pandas as pd

def plot_havana_map(df, hover_data, color="rating",size="rating",mapbox_style="open-street-map"):
    fig = px.scatter_mapbox(
        df,
        lat="loc_x",
        lon="loc_y",
        hover_name ="name",
        hover_data = hover_data,
        color=color,
        size=size,
        color_discrete_sequence=px.colors.qualitative.Set2, 
        zoom=10,
        height=600,
        size_max=20
    )
    fig.update_layout(
        mapbox_style=mapbox_style,
        mapbox_zoom=10,
        mapbox_center={"lat": df["loc_x"].mean(), "lon": df["loc_y"].mean()}
    )
    fig.show()

def load_json(ruta):
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(e)
        raise Exception("fallo en load_file,probablemente no se encuentra el geojson...")


municipios = {
    'loc_municipe': [ 'Plaza de la Revolucion', 'Playa', 'La Habana Vieja', 'Centro Habana', 'Cerro', 'Diez de Octubre', 'Marianao', 'Boyeros', 'Arroyo Naranjo', 'Cotorro', 'San Miguel del Padron', 'Regla', 'Guanabacoa', 'La Lisa', 'Habana del Este'],
    'municipe_id': [ '23.02', '23.01', '23.04', '23.03', '23.10', '23.09', '23.11', '23.13', '23.14', '23.15', '23.08', '23.05', '23.07', '23.12', '23.06']
}
df_municipios = pd.DataFrame(municipios)


def map_geojson_show(df):
    havana_geomap = load_json("maps/lha.geojson")
    #print(havana_geomap)
    promedio_r = df.groupby('loc_municipe')['rating'].mean().reset_index()
    df_merged = pd.merge(df_municipios, promedio_r, on='loc_municipe', how='left')
    df_count = df['loc_municipe'].value_counts().reset_index()
    df_count.columns = ['loc_municipe', 'cant_locals_evaluados'] # Cant. Munic. evaluados
    df_merged = pd.merge(df_merged, df_count, on='loc_municipe', how='left')
    df_merged['rating'] = df_merged['rating'].fillna(0)
    df_merged['cant_locals_evaluados'] = df_merged['cant_locals_evaluados'].fillna(0)
    df_merged.rename(columns={  
        'municipe_id': 'Municipio id',
        'loc_municipe': 'Municipio',
        'cant_locals_evaluados': 'Cantidad de locales evaluados',
        'rating': 'Puntuacion promedio',
    }, inplace=True)
    fig = px.choropleth(
        df_merged,
        geojson=havana_geomap,
        locations='Municipio id',
        featureidkey='properties.DPA_municipality_code',
        color='Puntuacion promedio',
        range_color=[0, 5],
        color_continuous_scale="Reds",
        hover_name='Municipio',
        hover_data={
            'Municipio': True,
            'Cantidad de locales evaluados': True,
            'Puntuacion promedio': True
        },
        title='Promedio de la puntuacion general (0=min - 5=max) por municipio en La Habana'
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.show()
    
    return df_merged