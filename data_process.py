import json
import pandas as pd
import os
from collections import Counter

lista_municipios = ["Habana del Este", "Centro Habana", "Regla", "Plaza de la Revolucion", "La Habana Vieja", "Cerro", "Diez de Octubre", "Guanabacoa", "San Miguel del Padron", "Playa", "Arroyo Naranjo", "Boyeros", "Marianao", "Cotorro", "La Lisa"]

#Cargar todos los archivos de la carpeta dnd estan los jsons
def load_datas(directory):
    datas = []
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith(".json"):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        datas.append(json.load(f))
                except Exception as e:
                        print(f"Error en: {filepath}, {e}")
    return datas

    #aplanar los datos para poder ser convertidos a DataFrame
def flatten_data(data_list):
    flat_data = []
    contador = 0
    for item in data_list:
        flat_item = {}

        # Top-level attributes
        flat_item['name'] = item.get('name')
        flat_item['phone'] = item.get('phone')
        flat_item['email'] = item.get('email')
        flat_item['web'] = item.get('web')
        flat_item['est_type'] = item.get('est_type')
        flat_item['bus_type'] = item.get('bus_type')
        flat_item['cuisine'] = item.get('cuisine')
        flat_item['cap'] = item.get('cap', 12) or 12
        flat_item['promo'] = item.get('promo', False) or False
        flat_item['rating'] = item.get('rating', 4.0) or 4.0
        flat_item['reviews'] = item.get('reviews', 0) or 0
        flat_item['level'] = item.get('level')
        flat_item['fb'] = item.get('fb')
        flat_item['ig'] = item.get('ig')
        flat_item['tw'] = item.get('twitter')

        types_of_menus = ['breakfast', 'appetizer', 'starters', 'mains', 'pizza', 'pasta', 'seafood', 'sandwich', 'sides', 'salads', 'soups', 'desserts', 'cocktails', 'wines', 'alcoholic_drinks', 'non_alcoholic_drinks', 'infusions', 'water', 'others']
        
        for tipo in types_of_menus:
            flat_item[f"menu_{tipo}"] = 0
        menu_items = item.get('menu', [])
        menu_types = [data.get('type') for data in menu_items if data and data.get('type')]
        type_counts = Counter(menu_types)
        for tipo, cantidad in type_counts.items():
            flat_item[f"menu_{tipo}"] = cantidad
        
        # aplanar las hours
        hours = item.get('hours', {})
        flat_item['hours_open'] = hours.get('open')
        flat_item['hours_close'] = hours.get('close')
        flat_item['hours_days'] = hours.get('days')

        # aplanar reservations, delivery, payment, amenities como datso booleanos
        reservations = item.get('reservations', []) or []
        for res in ["online", "phone", "in_person", "others"]:
            flat_item[f'reservation_{res}'] = True if res in reservations  else False


        delivery = item.get('delivery', []) or []
        for delivery_type in ["home", "takeaway", "on_site", "others"]:
            flat_item[f'delivery_{delivery_type}'] = True if delivery_type in delivery  else False

        payment = item.get('payment', []) or []
        for pay in ["cash", "card", "transfer", "others"]:
            flat_item[f'payment_{pay}'] = True if pay in payment  else False

        amenities = item.get('amenities', []) or []
        for amenity in ["wifi", "accessible", "live_music", "outdoor", "pet_friendly"]:
            flat_item[f'amenities_{amenity}'] = True if amenity in amenities  else False

        # aplanar la location
        loc = item.get('location', {})
        flat_item['loc_street'] = loc.get('street')
        flat_item['loc_council'] = loc.get('council')
        flat_item['loc_municipe'] = loc.get('municipe')
        flat_item['loc_province'] = loc.get('province')
        flat_item['loc_zip'] = loc.get('zip')
        flat_item['loc_country'] = loc.get('country')
        loc_x = loc.get('coords_x')
        loc_y = loc.get('coords_y')
        try:
            if isinstance(loc_x, float):
                flat_item['loc_x'] = float(loc_x)
            if isinstance(loc_y, float):
                flat_item['loc_y'] = float(loc_y)
        except Exception as e:
            print(f"Error en las locs de:{flat_item['name']}, loc_x:{loc_x}, loc_y: {loc_y}")
        
        contador += 1
        flat_data.append(flat_item)
    
    print(contador)
    return flat_data

def extract_menu(df):
    menu_data = []
    for index, row in df.iterrows():
        if isinstance(row['menu'], list):
            for item in row['menu']:
                menu_data.append({
                    "restaurant_id": index,  # ID del restaurante (o su índice)
                    "restaurant_name": row["name"],  # Nombre del restaurante
                    "dish_name": item.get("name", "Unknown"),  # Nombre del plato
                    "dish_price": item.get("price", 0),  # Precio del plato
                    "dish_type": item.get("type", "Unknown")  # Tipo de plato (ej. Starter, Main)
                })
    return pd.DataFrame(menu_data)

    
