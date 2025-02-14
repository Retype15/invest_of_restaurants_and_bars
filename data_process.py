import json
import pandas as pd
import os
from collections import Counter

lista_municipios = ["Habana del Este", "Centro Habana", "Regla", "Plaza de la Revolucion", "La Habana Vieja", "Cerro", "Diez de Octubre", "Guanabacoa", "San Miguel del Padron", "Playa", "Arroyo Naranjo", "Boyeros", "Marianao", "Cotorro", "La Lisa"]

#Cargar todos los archivos de la carpeta dnd estan los jsons
def load_datas(dir):
    datas = []
    for root, _, files in os.walk(dir):
        for filename in files:
            if filename.endswith(".json"):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        loaded = json.load(f)
                        loaded['_location'] = filepath
                        datas.append(loaded)
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
        flat_item['level'] = item.get('level', 'medium') or 'medium'
        flat_item['fb'] = item.get('fb')
        flat_item['ig'] = item.get('ig')
        flat_item['tw'] = item.get('twitter')

        types_of_menus = ['breakfast', 'appetizer', 'starters', 'mains', 'pizza', 'pasta', 'seafood', 'sandwich', 'sides', 'salads', 'soups', 'desserts', 'cocktails', 'wines', 'alcoholic_drinks', 'non_alcoholic_drinks', 'infusions', 'water', 'others']
        
        ls_menu = {}
        for menu in types_of_menus:
            ls_menu[f'menu_{menu}'] = []

        menu_types = item.get('menu',[])
        flat_item['menu_types'] = []

        for menu in menu_types:
            try:
                if menu['price']:
                    ls_menu[f'menu_{menu['type']}'].append(float(menu['price']))
                menu_type = menu['type']
                if menu_type and not menu_type in flat_item['menu_types']:
                    flat_item['menu_types'].append(menu_type)
                    

            except Exception as e:
                print('AAAAAAAAAAAAAAA --- ',menu, flat_item['name'], 'in: ', item['_location'])

        #print(ls_menu)

        total_mean = []
        total_min = []
        total_max = []
        total_count = []
        total_sum = []
        total_median = []
        total_mode = []

        for k,v in ls_menu.items():
            #print(k,v)
            val_mean = sum(v)/len(v) if len(v) > 0 else None
            flat_item[f'{k}_mean'] = val_mean
            if val_mean: total_mean.append(val_mean)
            val_min = min(v) if len(v) > 0 else None
            flat_item[f'{k}_min'] = val_min
            if val_min: total_min.append(val_min) 
            val_max = max(v) if len(v) > 0 else None
            flat_item[f'{k}_max'] = val_max
            if val_max: total_max.append(val_max)
            val_count = len(v)
            flat_item[f'{k}_count'] = val_count
            if val_count: total_count.append(val_count)
            val_sum = sum(v)
            flat_item[f'{k}_sum'] = val_sum
            if val_sum: total_sum.append(val_sum)
            val_median = pd.Series(v).median() if len(v) > 0 else None
            flat_item[f'{k}_median'] = val_median
            if val_median: total_median.append(val_median)
            val_mode = pd.Series(v).mode()[0] if len(v) > 0 else None
            flat_item[f'{k}_mode'] = val_mode
            if val_mode: total_mode.append(val_mode)

        flat_item['menu_mean'] = sum(total_mean)/len(total_mean) if len(total_mean) > 0 else None
        flat_item['menu_min'] = min(total_min) if len(total_min) > 0 else None
        flat_item['menu_max'] = max(total_max) if len(total_max) > 0 else None
        flat_item['menu_count'] = sum(total_count) if len(total_count) > 0 else None
        flat_item['menu_sum'] = sum(total_sum) if len(total_sum) > 0 else None
        flat_item['menu_median'] = pd.Series(total_median).median() if len(total_median) > 0 else None
        flat_item['menu_mode'] = pd.Series(total_mode).mode()[0] if len(total_mode) > 0 else None 

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

if __name__ == '__main__':
    flatten_data(load_datas('db'))