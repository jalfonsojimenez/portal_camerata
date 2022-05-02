from flask import Flask, render_template
# from os.path import exists
import os
from datetime import datetime

# variables de tiempo
mes = datetime.today().strftime('%m') 
meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', \
            'junio', 'julio', 'agosto', 'septiembre', 'octubre', \
            'noviembre', 'diciembre']
# mes actual en español, lo checa en la lista -1 elementos, el array empieza en 0
mes_actual = meses[int(mes)-1]

app = Flask(__name__)

musicos = {
    1 : {'nombre': 'Allen', 'puesto': 'director'},
    2 : {'nombre': 'Poncho', 'puesto': 'cello'},
    3 : {'nombre': 'Miguelin', 'puesto': 'violín'}
}

@app.route('/')
def index():
    # Checar el directorio de imágenes
    path = ('./static/img/')
    dir_list = os.listdir(path)

    return render_template('index.html', musicos = musicos , mes = mes_actual, archivos = dir_list)

@app.route('/user/<intid>', methods=['GET', 'POST'])
def method_name():
    pass

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
 