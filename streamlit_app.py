
import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import json

# Cargar las credenciales de Firestore desde los secretos de Streamlit
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)

# Crear el cliente de Firestore con las credenciales
db = firestore.Client(credentials=creds, project="netflix02-3c210")

# Función para filtrar por título
def filter_by_name(name, data):
    return data[data['name'].str.contains(name, case=False, na=False)]

# Función para filtrar por director
def filter_by_director(director, data):
    return data[data['director'] == director]

# Mostrar los datos si el usuario selecciona la opción
if st.sidebar.checkbox('Mostrar todos los filmes'):
    st.subheader('Todos los filmes')

    # Recuperar los datos de Firestore (colección de filmes)
    films_ref = db.collection("films")  # Cambia "films" por el nombre de tu colección
    films = list(films_ref.stream())  # Recuperamos todos los documentos de la colección
    films_dict = [film.to_dict() for film in films]  # Convertir los documentos en un diccionario
    data = pd.DataFrame(films_dict)  # Convertir los diccionarios en un DataFrame

    st.dataframe(data)  # Mostrar todos los filmes

# Entrada de texto para buscar filmes
titulofilme = st.sidebar.text_input('Título del filme:')
btnBuscar = st.sidebar.button('Buscar filmes')

# Filtrar los filmes por título
if btnBuscar and titulofilme:
    if 'data' in locals() and not data.empty:
        data_filme = filter_by_name(titulofilme, data)
        count_row = data_filme.shape[0]  # Número de filas
        st.write(f"Total de filmes encontrados: {count_row}")
        if not data_filme.empty:
            st.dataframe(data_filme)
    else:
        st.warning("No se han cargado los datos aún.")

# Filtrar los filmes por director
selected_director = st.sidebar.selectbox("Seleccionar Director", data['director'].unique() if 'data' in locals() else [])
btnFilterbyDirector = st.sidebar.button('Filtrar por Director')

if btnFilterbyDirector and selected_director:
    if 'data' in locals() and not data.empty:
        filtered_by_director = filter_by_director(selected_director, data)
        count_row = filtered_by_director.shape[0]  # Número de filas
        st.write(f"Total de filmes de {selected_director}: {count_row}")
        if not filtered_by_director.empty:
            st.dataframe(filtered_by_director)
    else:
        st.warning("No se han cargado los datos aún.")

# Insertar un nuevo filme
with st.sidebar.form("insert_film_form"):
    st.header("Insertar un nuevo filme")
    new_name = st.text_input("Nombre:")
    new_genre = st.text_input("Género:")
    new_director = st.text_input("Director:")
    new_company = st.text_input("Compañía:")

    submit_button = st.form_submit_button("Insertar Filme")
    if submit_button:
        if new_name and new_genre and new_director and new_company:
            # Usar 'data' en lugar de 'df' para verificar si el filme ya existe
            existing_films = data[data['name'].str.contains(new_name, case=False, na=False)]
            if not existing_films.empty:
                st.warning(f"El filme '{new_name}' ya existe en la base de datos.")
            else:
                # Insertar el nuevo filme en Firestore
                new_film = {'name': new_name, 'genre': new_genre, 'director': new_director, 'company': new_company}
                db.collection('films').add(new_film)  # Asegúrate de que la colección se llama 'films'
                st.success(f"¡El filme '{new_name}' ha sido insertado exitosamente!")

                # Añadir el nuevo filme directamente a los datos cargados en session_state
                new_film_df = pd.DataFrame([new_film])
                st.session_state.data = pd.concat([data, new_film_df], ignore_index=True)
        else:
            st.error("Por favor completa todos los campos del formulario.")

# Mostrar los datos de Firestore (otra colección si es necesario)
names_ref = db.collection(u'names').stream()  # Recupera el stream de la colección 'names'
names_dict = list(map(lambda x: x.to_dict(), names_ref))  # Convierte los documentos a diccionario
names_dataframe = pd.DataFrame(names_dict)  # Convierte la lista de diccionarios a un DataFrame

st.dataframe(names_dataframe)  # Muestra el DataFrame
