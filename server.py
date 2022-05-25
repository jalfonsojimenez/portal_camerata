from flask import Flask, flash, render_template, request, redirect, url_for
# from os.path import exists
import os
import json
#import datetime
from datetime import datetime
import calendar

# variables de tiempo
mes = datetime.today().strftime('%m') 
meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', \
            'junio', 'julio', 'agosto', 'septiembre', 'octubre', \
            'noviembre', 'diciembre']
# mes actual en español, lo checa en la lista -1 elementos, el array empieza en 0
mes_actual = meses[int(mes)-1]

dias_espanol  = ['domingo','lunes','martes','miércoles','jueves','viernes','sábado']
today = datetime.now()
mes = today.strftime('%m')
anio = today.strftime('%Y') 
primerdiames = datetime(int(anio),int(mes),1) 
primerdiamessemana = primerdiames.strftime('%w') #dia de la semana en que cae el primer dia del mes en numero
diasmes = calendar.monthrange(today.year, today.month)[1]

app = Flask(__name__)

musicos = {
    1 : {'nombre': 'Allen Gómez', 'puesto': 'director'},
    2 : {'nombre': 'Poncho Gonzalez', 'puesto': 'cello'},
    3 : {'nombre': 'Pedro Martinez', 'puesto': 'violín'},
    4 : {'nombre': 'Jorge Aceves', 'puesto' : 'percusiones'},
    5 : {'nombre': 'Ana Silvia Guerrero', 'puesto': 'piano'}
}

@app.route('/')
def index():
    # Checar el directorio de imágenes
    path = ('./static/img/')
    dir_list = os.listdir(path)

    return render_template('index.html', musicos = musicos , mes = mes_actual, archivos = dir_list)

@app.route('/upload_docs', methods=['GET', 'POST'])
def upload_docs():
    idmusico    = request.args.get('idmusico') 
    doctype     = request.args.get('doctype')
    print(type(idmusico))
    return render_template('upload_docs.html', musicos = musicos, idmusico = idmusico, mes = mes_actual, doctype = doctype)

@app.route('/crea_calendario', methods=['GET','POST'])
def crea_calendario():
    fechasCalendario = {}
    multi_dict = request.form
    if request.method == 'POST':
        for k in request.form:
            if multi_dict.get(k) != '':
                fechasCalendario[k] = multi_dict.get(k)
            else :
                pass
        calendario = 'calendario' + mes_actual #Pone nombre de calendario y mes actual para guardar como archivo json
        with open('static/calendarios/'+calendario+'.json','w') as fp:
            json.dump( fechasCalendario, fp, indent=4 ) #escribe el json con las fechas enviadas
        return redirect( '/'  )

    return render_template('crea_calendario.html', diasmes=diasmes , dias_espanol = dias_espanol, \
                            primerdiamessemana=primerdiamessemana, mes_actual=mes_actual, anio=anio)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
 
