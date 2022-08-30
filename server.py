from flask import Flask, flash, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
# from os.path import exists

import os
import json

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
from calendar import monthrange
import locale
locale.setlocale(locale.LC_TIME, 'es_MX')

from PIL import Image, ImageOps

import pathlib
from pathlib import Path

#######################
# variables de tiempo #
#######################

mes = datetime.today().strftime('%m') 
meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', \
            'junio', 'julio', 'agosto', 'septiembre', 'octubre', \
            'noviembre', 'diciembre']

#menos = hoy - relativedelta(months=-1)

#mes_actual = meses[int(mes)-1] # mes actual en español, lo checa en la lista -1 elementos, el array empieza en 0
dias_espanol  = ['domingo','lunes','martes','miércoles','jueves','viernes','sábado']
today = datetime.now()
dia = today.strftime('%A %d-%m-%Y-%H:%M')
mes = today.strftime('%m')
anio = today.strftime('%Y') 
primerdiames = datetime(int(anio),int(mes),1) 
primerdiamessemana = primerdiames.strftime('%w') #dia de la semana en que cae el primer dia del mes en numero
diasmes = calendar.monthrange(today.year, today.month)[1]

musicos = {
    1:  { 'nombre': 'Allen Vladimir Gómez', 'puesto' : 'dirección'},
    2:  { 'nombre':'Roberto Carlos Hernández Estrada' , 'puesto': 'bibliotecario y administrativo' },
    3:  { 'nombre': 'Diana Carolina Laguna Rivas' , 'puesto' : 'violín' },
    4:  { 'nombre': 'Francisco Vidal Rivera González' , 'puesto': 'violín' },
    5:  { 'nombre': 'Paris Ayala Buenrostro' , 'puesto' : 'violín' },
    6:  { 'nombre': 'Ramón Lemus Bravo' , 'puesto' : 'violín' },
    7:  { 'nombre': 'Sergio Rodríguez Barrón' , 'puesto': 'violín' },
    8:  { 'nombre': 'Robert Carl Nelson' , 'puesto': 'viola' },
    9:  { 'nombre': 'René Eduardo Nuño Guzmán' , 'puesto': 'viola' },
    10: { 'nombre': 'Deni González Miniashkin' , 'puesto': 'contrabajo' },
    11: { 'nombre': 'Jorge Alfonso González Jiménez' , 'puesto': 'violoncello' },
    12: { 'nombre': 'Yalissa Cruz Espino' , 'puesto': 'violoncello' },
    13: { 'nombre': 'Alfonso Chen Arellano' , 'puesto': 'clarinete' },
    14: { 'nombre': 'David Alejandro Padilla Guerrero' , 'puesto': 'oboe' } ,
    15: { 'nombre': 'Eva Alexandra Nogueira Rodrigues' , 'puesto': 'flauta' },
    16: { 'nombre': 'María Monserrat Velázquez Gómez' , 'puesto': 'fagot' },
    17: { 'nombre': 'Ana Silvia Guerrero González' , 'puesto': 'piano' },
    18: { 'nombre': 'Jorge Eduardo Aceves Cisneros' , 'puesto': 'percusiones' }
}
docs = ['32d', 'ecuenta','sitfiscal', 'factura', 'xmlfactura', 'complementodepago','xmlcomplemento', 'foto1','foto2','foto3','foto4']


#############
#APP y RUTAS#
#############

app = Flask(__name__)
app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024

path = os.getcwd() # Get current path
UPLOAD_FOLDER   = os.path.join(path, 'static/files/') # file Upload
#filename        = os.path.join(app.static_folder, 'calendarios', 'calendario' + mes_actual + '.json')
#filefiles       = os.path.join(app.static_folder, 'files', 'registro_uploads' + mes_actual + '.json')

# Make directory if uploads is not exists
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set([ 'pdf', 'xml', 'jpg', 'jpeg', 'png', 'gif']) # Allowed extension you can set your own
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

###################
###  FUNCIONES  ###
###################


def lee_archivos(docs):
    """
    lee los archivos existentes y regresa una lista con los nombres
    de los mismos
    """
    pati        = {}
    archivos    = {}
    for doc in docs:
#revisa lista de documentos
        if not os.path.isdir( './static/files/' + doc ):
#si no está crea el directorio
            os.mkdir( './static/files/' + doc )
        archivos[doc] = os.listdir( './static/files/' + doc )
        
    return archivos

def lee_fechas( archivos, docs):
    """
    lee las fechas en las que fueron subidas los archivos y regresa un dictionary
    con el nombre de archivo y la fecha en la que fue subida a la plataforma
    """
    fechas_dict = {} #diccionario donde se agregan los archivos con la fecha en la que se agrega el archivo
    for d in docs:
        path = './static/files/' + d
        for x in os.listdir(path):
        #para cada archivo extraer cuando fue creado
            time = os.path.getmtime(path + '/' + x)
            #time = datetime.utcfromtimestamp(time).strftime('%A %d-%B-%Y %H:%M')
            #se convierte de unixtimestamp y se guarda en la variable time para cada archivo
            time = datetime.utcfromtimestamp(time)
            #se le restan 5 horas porque el server está 5 horas adelante
            time = time - timedelta(hours=5)
            time = time.strftime('%A %d-%B-%Y %H:%M')
            #se agrega la fecha al diccionario de fechas_dict, donde viene la fecha en que se suben todos los archivos
            fechas_dict[x] = time
    return fechas_dict

def abreCal(mes_actual):
    """
    revisa si hay calendario, de otra forma hace el archivo del mes correspondiente vacío y lo regresa
    """
    filename = os.path.join(app.static_folder, 'calendarios', 'calendario' + mes_actual + '.json')
    try:
        with open(filename) as test_file:
            data = json.load(test_file)
        return data
    except:
        with open(filename, 'w+') as test_file:
            data = test_file.write( json.dumps( { } ) )
        return data

"""
def abre_file_log():
    try:
        with open(filefiles) as fl:
            data_log = json.load(fl)
            return data_log
    except:
        open( filefiles, 'a+' ).close()
"""

###################################
#### Funciones para calendario ####
###################################

def get_meses():
#regresa un array con el mes en curso en letras y dos meses anteriores
    meses_array = []
    for x in range(0,3):
       mesesito = datetime.today() - relativedelta(months=x)
       mesesito = mesesito.strftime('%B')
       meses_array.append( mesesito )
    return meses_array


def get_fechas( anio, mes ):
    """
    con el año y el mes elegido regresa un array con lo siguiente:
    fechas [ primer dia de la semana del mes seleccionado en número, total de dias del mes del mes seleccionado]
    """
    fechas = [] 
    mes = meses.index( mes )
#al calcular el primer dia del mes se le suma 1 porque el array de meses comienza en cero
    primerdiames = datetime( int( anio ) , int( mes + 1 ), 1) 
    primerdiamessemana = primerdiames.strftime( '%w' )
    fechas.append( int(primerdiamessemana) )

    dias_mes=  monthrange(int(anio),int(mes+1))[1]
    fechas.append( int(dias_mes) )
    return fechas

###################
###   RUTAS     ###
###################

@app.route('/main')
def main():
    mes_actual = request.args.get('mes_selected')
    #mes_actual = datetime.today().strftime('%B') 

    #funcion para leer archivos de carpetas
    archivos = lee_archivos(docs)
    #data_log = abre_file_log()
    fechas_dict = lee_fechas( archivos, docs )
    return render_template('main.html', musicos = musicos , mes = mes_actual, anio = anio, \
                            docs = docs, archivos = archivos,  fechas_dict = fechas_dict )
    #data_log = data_log,
    

@app.route('/')
def index():
#get lista de meses para elegir
    mes_select = get_meses()
    return render_template('index.html', musicos = musicos,   mes_select = mes_select)

@app.route('/instrucciones')
def instrucciones():
    mes_actual = request.args.get('mes_selected')
    return render_template('instrucciones.html', mes_actual = mes_actual)


@app.route('/upload_docs', methods=['GET', 'POST'])
def upload_docs():
    idmusico    = request.args.get( 'idmusico' ) 
    doctype     = request.args.get( 'doctype' )
    mes_actual = request.args.get('mes_selected')
    dict_file   = {}
    if request.method == 'POST':
        mes_actual = request.form['mes_selected']
        if 'files[]' not in request.files:
            flash( 'No hay archivos para subir' )
            return redirect(request.url)
        files = request.files.getlist( 'files[]' )
        for file in files:
            idmusico    = request.form.get( 'idmusico' ) 
            doctype     = request.form.get( 'doctype' )
            if file and allowed_file( file.filename ):
                filename = secure_filename( file.filename )
                filename = str(idmusico) + '-' + str(doctype)+ '-' + mes_actual + '.' + filename[-3:]
                if doctype[0:4] == 'foto': #Si son fotos hace un resize y cambio de extension
                    # Nombres de archivo
                    filename = str(idmusico) + '-foto' + str(files.index(file)+1) + '-' + mes_actual + '.' + filename[-3:]
                    file.save( os.path.join( app.config[ 'UPLOAD_FOLDER' ], doctype + '/' + filename ))
                    image = Image.open('static/files/' + doctype+ '/' + filename)
                    image = image.convert('RGB')
                    # Manipulacion de imagenes, resizeo
                    dim     =   image.size #obtener tamaño de imagen
                    rwidth  =   float(300) #ancho deseado de imagen
                    width   =   float( dim[0] ) #obtener ancho
                    height  =   float( rwidth/width ) * float(dim[1]) #hacer la proporcion del alto con el ancho deseado
                    newsize =   ( int(rwidth), int(round(height)) ) #obtiene tamaño para resizear
                    imagenr =   image.resize( newsize ) #resizea la imagen y la guarda como imagenr
                    imagenr =   ImageOps.exif_transpose(imagenr)
                    # guardar foto 
                    filenametosave  = filename.split('.')[0] 
                    #Anteriormente se hacia esto
                    #imagenr.save( 'static/files/'+ 'foto' + str(files.index(file)+1) + '/' + filenametosave + '.jpg' )
                    nombrefoto      = 'static/files/'+ 'foto' + str(files.index(file)+1) + '/' + filenametosave + '.jpg' 
                    imagenr.save( nombrefoto )
                else: #Si son documentos los guarda solamente
                    file.save( os.path.join( app.config[ 'UPLOAD_FOLDER' ], doctype + '/' + filename ))
                    dict_file[filename] = dia
                    with open('static/files/'  + 'registro_uploads'  + mes_actual + '.json','a') as dp:
                        json.dump( dict_file, dp, indent=4 ) #escribe el json con las fechas enviadas
        flash( 'Archivos subidos con éxito ')
        return redirect( url_for( 'user', idmusico = idmusico, mes_selected= mes_actual ) )
    return render_template('upload_docs.html', musicos = musicos, idmusico = idmusico, mes = mes_actual, doctype = doctype, dia = dia)

#######################################
#### RUTAS DE REPORTE Y CALENDARIO ####
#######################################

@app.route('/crea_calendario', methods=['GET','POST'])
def crea_calendario():
#    mes_actual = request.form.get('mes_selected')
#    data = abreCal(mes_actual)

    
    fechasCalendario = {}
    multi_dict = request.form

    if request.method == 'POST':
        mes_actual = request.form['mes_selected']
        data = abreCal( mes_actual )
        anio = today.strftime( '%Y' )
        fechas = get_fechas( anio, mes_actual)
        primerdiamessemana = fechas[0] 
        diasmes = fechas[1]
        archivos = lee_archivos(docs)
        fechas_dict = lee_fechas( archivos, docs )

        for k in request.form:
            print(k)
            if multi_dict.get(k) != '':
                fechasCalendario[k] = multi_dict.get(k)
            else :
                pass
        calendario = 'calendario' + mes_actual #Pone nombre de calendario y mes actual para guardar como archivo json
        with open('static/calendarios/'+calendario+'.json','w') as fp:
            json.dump( fechasCalendario, fp, indent=4 ) #escribe el json con las fechas enviadas
        
        return render_template('main.html', musicos = musicos , mes = mes_actual, anio = anio, \
                                docs = docs, archivos = archivos,  fechas_dict = fechas_dict )

    return render_template('crea_calendario.html', diasmes=diasmes , dias_espanol = dias_espanol,\
                            primerdiamessemana=primerdiamessemana, mes_actual=mes_actual, anio=anio, data = data)



@app.route('/logincal', methods=['POST','GET'])
def logincal():
    mes_actual = request.args.get('mes_selected')
    data = abreCal(mes_actual)
    print( data )

    fechas = get_fechas( anio, mes_actual)
    primerdiamessemana = fechas[0] 
    diasmes = fechas[1]

    if request.method == 'POST':
        password = request.form['password']
        mes_actual = request.form['mes_selected']
        if password == 'camerata':
            return render_template('crea_calendario.html', diasmes=diasmes , dias_espanol = dias_espanol, \
                            primerdiamessemana=primerdiamessemana, mes_actual=mes_actual, anio=anio, data = data)
        else:
            flash( 'Password incorrecto, vuelve a intentar')
            return redirect( url_for('logincal', **request.args ))
    return render_template('logincal.html', mes_actual = mes_actual)


@app.route('/muestra_calendario/<idmusico>', methods=['GET'])
def muestra_calendario(idmusico):
    mes_actual = request.args.get('mes_selected')
    idmusico    = int( idmusico )
    data = abreCal(mes_actual)

    fechas = get_fechas( anio, mes_actual)
    primerdiamessemana = fechas[0] 
    diasmes = fechas[1]

    return render_template('muestra_calendario.html', idmusico=idmusico, data = data, diasmes=diasmes , dias_espanol = dias_espanol, \
                            primerdiamessemana=primerdiamessemana, mes_actual=mes_actual, anio=anio, musicos = musicos)


@app.route('/login/<idmusico>', methods=['GET', 'POST'])
def login(idmusico):
    mes_actual = request.args.get('mes_selected')
    idmusico = int( idmusico )
    data = abreCal(mes_actual)
    if idmusico in musicos: #checa si está en la lista para evitar hackeos
        if request.method == 'POST':
            mes_actual = request.form['mes_selected']
            password = request.form['password']
            if password == 'Camerata2017!':
                mes_actual = request.form['mes_selected']
                filenamedba = os.path.join(app.static_folder, 'cartas_musicos', 'cartas_musicos.json')
                with open(filenamedba) as f:
                    datos = json.load(f)
                return render_template('muestra_dba.html', idmusico = idmusico, musicos = musicos, \
                                        datos = datos, filenamedba = filenamedba, diasmes=diasmes, mes_actual=mes_actual, anio = anio)
            else: 
                flash( 'Password incorrecto, vuelve a intentar')
                return redirect( url_for('login', idmusico = idmusico, **request.args ))
    else:
        return redirect( '/')
    return render_template( 'login.html', idmusico = idmusico, musicos = musicos, mes_actual = mes_actual)



@app.route('/muestra_dba/', methods=['POST']) #Ruta para mostrar datos bancarios
def muestra_dba(idmusico):
    mes_actual = request.args.get('mes_selected')
    if request.method == 'POST':
        mes_actual = request.form['mes_selected']
    return render_template('muestra_calendario.html', idmusico=idmusico, datos = datos, diasmes=diasmes , dias_espanol = dias_espanol, \
                            primerdiamessemana=primerdiamessemana, mes_actual=mes_actual, anio=anio, musicos = musicos)


@app.route('/usuario', methods=['GET', 'POST'])
def user():
    archivos = lee_archivos( docs )
    #data_log = abre_file_log()
    fechas_dict = lee_fechas( archivos, docs )
    mes_actual = request.args.get('mes_selected')
    if request.method == 'POST':
        mes_actual = request.form['mes_selected']
        idmusico = int( request.form['idmusico'] ) 
        return render_template('usuario.html', idmusico = idmusico, musicos = musicos, docs = docs, mes = mes_actual,  archivos = archivos, fechas_dict = fechas_dict)
#data_log = data_log,
    else:
        idmusico = int(request.args.get('idmusico'))
        return render_template('usuario.html', idmusico = idmusico, musicos = musicos, docs = docs, mes = mes_actual,  archivos = archivos \
        , fechas_dict = fechas_dict) #data_log = data_log

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)

