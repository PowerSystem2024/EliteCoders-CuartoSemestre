import requests

def get_razas():
    r = requests.get("https://dog.ceo/api/breeds/list/all")
    print(r.status_code)
    print(r.text)
    print(type(r.text))
    # En este caso es un string por el texxt, pero aqui encontramos
    # un diccionario con listas
    razas = r.json()
    for raza in razas.values(): # utilizamos la funcion para los valores del diccionario
        print(f"Raza de los perritos: {raza[5]}") # recorremos los valores del dicionario








