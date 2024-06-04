import streamlit as st
import pandas as pd
import joblib
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Cargar el modelo
model = joblib.load('/Users/cescrosello/Desktop/Bootcamp - WIP/DataScience-Mar2024/PROYECTO ML/model/my_model.pkl')

# Función para predecir el precio de la vivienda
def predict_price(input_data):
    data = pd.DataFrame(input_data, index=[0])
    prediction = model.predict(data)
    return prediction[0]

# Función para obtener coordenadas a partir de una dirección
def get_coordinates(address, timeout=10):
    geolocator = Nominatim(user_agent="house_price_prediction")
    try:
        location = geolocator.geocode(address, timeout=timeout)
        if location:
            return location.latitude, location.longitude
        else:
            st.error("No se encontraron coordenadas para la dirección proporcionada.")
            return None, None
    except GeocoderTimedOut:
        st.error("La solicitud de geocodificación ha excedido el tiempo de espera.")
        return None, None

# Inicializar variables de latitud y longitud en el estado de sesión
if 'latitud' not in st.session_state:
    st.session_state['latitud'] = None
if 'longitud' not in st.session_state:
    st.session_state['longitud'] = None
if 'predicted_price' not in st.session_state:
    st.session_state['predicted_price'] = None
if 'min_price' not in st.session_state:
    st.session_state['min_price'] = None
if 'max_price' not in st.session_state:
    st.session_state['max_price'] = None

# Crear el formulario de entrada
st.title("Predicción del Precio de la Vivienda")

# Dirección y número
st.header("Ubicación de la Vivienda")
direccion = st.text_input("Dirección", help="Ingrese la dirección de la vivienda.")
numero = st.text_input("Número", help="Ingrese el número de la vivienda.")
poblacion = "Valencia"  # Población por defecto

if st.button("Obtener Coordenadas"):
    if direccion and numero:
        address = f"{direccion} {numero}, {poblacion}"
        latitud, longitud = get_coordinates(address)
        if latitud and longitud:
            st.session_state['latitud'] = latitud
            st.session_state['longitud'] = longitud
            st.success(f"Coordenadas obtenidas: Latitud = {latitud}, Longitud = {longitud}")
    else:
        st.error("Por favor, ingrese tanto la dirección como el número.")

# Entradas predeterminadas
st.header("Características de la Vivienda")
col1, col2, col3 = st.columns(3)

with col1:
    metros_construidos = st.number_input("Metros Construidos", min_value=0, help="Ingrese los metros construidos de la vivienda.")
    habitaciones = st.number_input("Habitaciones", min_value=0, help="Ingrese el número de habitaciones.")
    banos = st.number_input("Baños", min_value=0, help="Ingrese el número de baños.")

with col2:
    terraza = st.number_input("Terraza", min_value=0, help="Ingrese el número de terrazas.")
    ascensor = st.number_input("Ascensor", min_value=0, help="Ingrese el número de ascensores.")
    aire_acondicionado = st.number_input("Aire Acondicionado", min_value=0, help="Ingrese el número de aires acondicionados.")

with col3:
    garaje = st.number_input("Garaje", min_value=0, help="Ingrese el número de garajes.")
    trastero = st.number_input("Trastero", min_value=0, help="Ingrese el número de trasteros.")
    piscina = st.number_input("Piscina", min_value=0, help="Ingrese el número de piscinas.")
    conserje = st.number_input("Conserje", min_value=0, help="Ingrese el número de conserjes.")
    ano_construccion = st.number_input("Año de Construcción", min_value=1800, max_value=2024, help="Ingrese el año de construcción.")

# Crear el diccionario de datos de entrada
input_data = {
    'Metros_Construidos': metros_construidos,
    'Habitaciones': habitaciones,
    'Baños': banos,
    'Terraza': terraza,
    'Ascensor': ascensor,
    'Aire_Acondicionado': aire_acondicionado,
    'Garaje': garaje,
    'Trastero': trastero,
    'Piscina': piscina,
    'Conserje': conserje,
    'Año_construcción': ano_construccion,
    'Servicios': 0,
    'Armarios': 0,
    'Jardín': 0,
    'Duplex': 0,
    'Estudio': 0,
    'Ático': 0,
    'Calidad_suelo': 0,
    'Plantas_máximas': 0,
    'Número_viviendas': 0,
    'Calidad_catastral': 0,
    'Distancia_centro': 0.0,
    'Distancia_metro': 0.0,
    'Distancia_Blasco': 0.0,
    'Latitud': st.session_state['latitud'],
    'Longitud': st.session_state['longitud'],
    'Orientación_Este': 0,
    'Orientación_Norte': 0,
    'Orientación_Oeste': 0,
    'Orientación_Sur': 0
}

# Distribuir en dos columnas: Tasación del inmueble a la izquierda y valoración del activo a la derecha
col_izquierda, col_derecha = st.columns(2)

# Opción 1: Tasa la vivienda
with col_izquierda:
    st.header("Tasación del Inmueble")
    if st.button("Tasa la vivienda"):
        if st.session_state['latitud'] is not None and st.session_state['longitud'] is not None:
            input_data['Latitud'] = st.session_state['latitud']
            input_data['Longitud'] = st.session_state['longitud']
            predicted_price = predict_price(input_data)
            st.session_state['predicted_price'] = predicted_price
            st.session_state['min_price'] = predicted_price - 25000
            st.session_state['max_price'] = predicted_price + 25000
            st.markdown(f"### Valor estimado de venta")
            st.markdown(f"**{predicted_price:,.0f}€**")
            st.markdown(f"*mínimo {st.session_state['min_price']:,.0f}€ - máximo {st.session_state['max_price']:,.0f}€*")
        else:
            st.error("Por favor, obtenga las coordenadas primero.")

# Opción 2: Valora el activo
with col_derecha:
    st.header("Valoración del Activo")
    precio_ingresado = st.number_input("Precio de la vivienda a considerar", min_value=0, help="Ingrese el precio de la vivienda que desea valorar.")

    if st.button("Valora el activo"):
        if st.session_state['latitud'] is not None and st.session_state['longitud'] is not None:
            input_data['Latitud'] = st.session_state['latitud']
            input_data['Longitud'] = st.session_state['longitud']
            predicted_price = predict_price(input_data)
            st.session_state['predicted_price'] = predicted_price
            st.session_state['min_price'] = predicted_price - 25000
            st.session_state['max_price'] = predicted_price + 25000
            
            # Calcular el porcentaje de diferencia
            diferencia = precio_ingresado - st.session_state['predicted_price']
            porcentaje = (diferencia / st.session_state['predicted_price']) * 100
            
            if precio_ingresado < st.session_state['min_price']:
                st.success(f"El precio ingresado de {precio_ingresado:,.0f}€ está por debajo del mercado. Este inmueble tiene un valor aproximado de {st.session_state['predicted_price']:,.0f}€. El precio que indicas está un {porcentaje:.2f}% por debajo del mercado. Es una buena opción de inversión.")
            elif precio_ingresado > st.session_state['max_price']:
                st.error(f"El precio ingresado de {precio_ingresado:,.0f}€ está por encima del mercado. Este inmueble tiene un valor aproximado de {st.session_state['predicted_price']:,.0f}€. El precio que indicas está un {porcentaje:.2f}% por encima del mercado. Es una mala opción de inversión.")
            else:
                st.info(f"El precio ingresado de {precio_ingresado:,.0f}€ está dentro del rango de mercado. Este inmueble tiene un valor aproximado de {st.session_state['predicted_price']:,.0f}€. El precio que indicas está un {porcentaje:.2f}% dentro del rango de mercado.")
        else:
            st.error("Por favor, obtenga las coordenadas primero.")

# Mostrar algunos detalles adicionales en la página principal
st.write("""
Este dashboard permite predecir el precio de una vivienda basada en sus características.
Complete el formulario en la barra horizontal y presione el botón para obtener el precio predicho.
""")
