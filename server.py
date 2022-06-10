from flask import Flask, flash, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
# from os.path import exists
import os
import json
#import datetime
from datetime import datetime
import calendar
from PIL import Image
import pathlib

#######################
# variables de tiempo #
#######################

mes = datetime.today().strftime('%m') 
meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', \
            'junio', 'julio', 'agosto', 'septiembre', 'octubre', \
            'noviembre', 'diciembre']

mes_actual = meses[int(mes)-1] # mes actual en español, lo checa en la lista -1 elementos, el array empieza en 0
dias_espanol  = ['domingo','lunes','martes','miércoles','jueves','viernes','sábado']
today = datetime.now()
mes = today.strftime('%m')
anio = today.strftime('%Y') 
primerdiames = datetime(int(anio),int(mes),1) 
primerdiamessemana = primerdiames.strftime('%w') #dia de la semana en que cae el primer dia del mes en numero
diasmes = calendar.monthrange(today.year, today.month)[1]

musicos = {
    1 : {'nombre': 'Allen Gómez', 'puesto': 'director'},
    2 : {'nombre': 'Jorge Alfonso González Jiménez', 'puesto': 'cello'},
    3 : {'nombre': 'Pedro Martinez', 'puesto': 'violín'},
    4 : {'nombre': 'Jorge Aceves', 'puesto' : 'percusiones'},
    5 : {'nombre': 'Ana Silvia Guerrero', 'puesto': 'piano'},
    6 : {'nombre': 'Montserrat', 'puesto': 'fagot'}
}
docs = ['32d', 'ecuenta', 'factura', 'dbancarios',  'sitfiscal', 'foto1','foto2','foto3','foto4']

#############
#APP y RUTAS#
#############

app = Flask(__name__)
app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

path = os.getcwd() # Get current path
UPLOAD_FOLDER = os.path.join(path, 'static/files/') # file Upload

# Make directory if uploads is not exists
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set([ 'pdf', 'xml', 'jpg', 'jpeg']) # Allowed extension you can set your own
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

###################
###  FUNCIONES  ###
###################
def lee_archivos(docs):
    pati        = []
    archivos    = {}
    for doc in docs:
        pati.append('./static/files/' + doc)
        archivos[doc] = os.listdir( './static/files/' + doc )
    return archivos

@app.route('/')
def index():

    archivos = lee_archivos(docs)

    return render_template('index.html', musicos = musicos , mes = mes_actual, anio = anio, \
                            docs = docs, archivos = archivos)

@app.route('/upload_docs', methods=['GET', 'POST'])
def upload_docs():
    idmusico    = request.args.get( 'idmusico' ) 
    doctype     = request.args.get( 'doctype' )

    if request.method == 'POST':
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

                    # Manipulacion de imagenes, resizeo
                    dim     =   image.size #obtener tamaño de imagen
                    rwidth  =   float(300) #ancho deseado de imagen
                    width   =   float( dim[0] ) #obtener ancho
                    height  =   float( rwidth/width ) * float(dim[1]) #hacer la proporcion del alto con el ancho deseado
                    newsize =   ( int(rwidth), int(round(height)) ) #obtiene tamaño para resizear
                    imagenr =   image.resize( newsize ) #resizea la imagen y la guarda como imagenr
                    
                    # guardar foto 
                    filenametosave = filename.split('.')[0] 
                    imagenr.save( 'static/files/'+ 'foto' + str(files.index(file)+1) + '/' + filenametosave + '.jpg' )

                else: #Si son documentos los guarda solamente
                    file.save( os.path.join( app.config[ 'UPLOAD_FOLDER' ], doctype + '/' + filename ))
            
        flash( 'Archivos subidos con éxito ')
        return redirect( '/' )


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


filename = os.path.join(app.static_folder, 'calendarios', 'calendario'+mes_actual+'.json')

@app.route('/muestra_calendario/<idmusico>', methods=['GET'])
def muestra_calendario(idmusico):
    #idmusico    = request.args.get('idmusico', type= int) 
    idmusico    =   idmusico 
    print(idmusico)
    with open(filename) as test_file:
        data = json.load(test_file)

    return render_template('muestra_calendario.html', idmusico=idmusico, data = data, diasmes=diasmes , dias_espanol = dias_espanol, \
                            primerdiamessemana=primerdiamessemana, mes_actual=mes_actual, anio=anio, musicos = musicos)

@app.route('/login/<idmusico>', methods=['GET', 'POST'])
def login(idmusico):
    idmusico = int( idmusico )
    if idmusico in musicos: #checa si está en la lista para evitar hackeos
        if request.method == 'POST':
            password = request.form['password']
            if password == '123':
                filenamedba = os.path.join(app.static_folder, 'cartas_musicos', 'cartas_musicos.json')
                with open(filenamedba) as f:
                    datos = json.load(f)
                return render_template('muestra_dba.html', idmusico = idmusico, musicos = musicos, \
                                        datos = datos, filenamedba = filenamedba, diasmes=diasmes, mes_actual=mes_actual, anio = anio)
                #return redirect('/muestra_dba')
            else:
                return redirect('/')
    else:
        return redirect('/')
    return render_template( 'login.html', idmusico = idmusico, musicos = musicos, mes_actual = mes_actual)


@app.route('/muestra_dba/', methods=['POST']) #Ruta para mostrar datos bancarios
def muestra_dba(idmusico):
    #idmusico    = request.args.get('idmusico', type= int) 

    return render_template('muestra_calendario.html', idmusico=idmusico, datos = datos, diasmes=diasmes , dias_espanol = dias_espanol, \
                            primerdiamessemana=primerdiamessemana, mes_actual=mes_actual, anio=anio, musicos = musicos)

@app.route('/usuario/<idmusico>', methods=['GET']) #Ruta para ver documentos por usuario
def user(idmusico):
    idmusico    = int(idmusico)
    
    archivos = lee_archivos( docs )
    return render_template('usuario.html', idmusico = idmusico, musicos = musicos, docs = docs, mes = mes_actual,  archivos = archivos)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)

