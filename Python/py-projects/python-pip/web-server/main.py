import store
from fastapi import FastApi
from fastapi.responses import HTMLResponse

app= FastApi()# Creamos nuestra primera instacia

@app.get('/') # Agregamos decorador de ruta
def get_list():
    return[1,2,3]

#Segunda ruta
@app.get('/contact', response_class=HTMLResponse)
def get_list():
    return'''
        <h1> Soy un sitio web </h1>
        <p>Soy un parrafo

'''



def run():
    store.get_razas()
    

if __name__=="__main__":
    run()