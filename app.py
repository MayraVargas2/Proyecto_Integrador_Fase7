from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId  # Importante para identificar registros de MongoDB
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

# CONFIGURACIÓN Y CONEXIÓN CON LA BASE DE DATOS DE MONGODB
MONGO_URI = "mongodb+srv://admin_catequesis:catequesis1234@cluster0.nd6sk3l.mongodb.net/iglesia_db?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client['iglesia_db']
    coleccion = db['catequizandos']
    client.admin.command('ping')
    print("¡CONEXIÓN EXITOSA A MONGODB ATLAS!")
except Exception as e:
    print(f"ERROR CRÍTICO: No se pudo conectar a Atlas: {e}")

# RUTA DE INICIO Y LISTADO
@app.route('/')
def inicio():
    try:
        registros_db = list(coleccion.find())
    except Exception as e:
        print(f"Error al leer datos: {e}")
        registros_db = []
    return render_template('index.html', registros=registros_db)

# RUTA PARA INGRESAR AL FORMULARIO
@app.route('/formulario')
def formulario():
    return render_template('formulario.html')

# ACCION GUARDAR
app.secret_key = "clave_secreta_iglesia"
@app.route('/guardar', methods=['POST'])
def guardar():
    datos_catequizando = {
        "cedula": request.form.get('cedula'),
        "nombre": request.form.get('nombre'),
        "apellido": request.form.get('apellido'),
        "sexo": request.form.get('sexo'),
        "fecha_nacimiento": request.form.get('fecha_nacimiento'),
        "edad": request.form.get('edad'),
        "fecha_inscripcion": request.form.get('fecha_inscripcion'),
        "telefono": request.form.get('telefono'),
        "email": request.form.get('email'),
        "parroquia": request.form.get('parroquia'),
        "direccion": request.form.get('direccion')
    }
    # CONDICIONES DE VALDIACIÓN
    try:
        coleccion.insert_one(datos_catequizando)
        flash("¡Registro guardado con éxito!", "success")
        return redirect(url_for('inicio'))
    except Exception as e:
        # Si MongoDB rechaza el dato por el ARCHIVO DE VALIDACIÓN
        print(f"Error de validación: {e}")
        flash("Error: Los datos no cumplen con los requisitos (Cédula de 10 dígitos, email válido, etc.)", "danger")
        return redirect(url_for('formulario'))

# BOTON ELIMINAR
@app.route('/eliminar/<id>')
def eliminar(id):
    try:
        coleccion.delete_one({'_id': ObjectId(id)})
        print(f"Registro {id} eliminado.")
    except Exception as e:
        print(f"Error al eliminar: {e}")
    return redirect(url_for('inicio'))

# --- NUEVA RUTA: VER DETALLE ---
@app.route('/ver/<id>')
def ver(id):
    try:
        catequizando = coleccion.find_one({'_id': ObjectId(id)})
        return render_template('detalle.html', c=catequizando)
    except Exception as e:
        print(f"Error al ver detalle: {e}")
        return redirect(url_for('inicio'))

# BOTON DE CONSULTA POR: NOMBRE, APELIDO O CEDULA
@app.route('/buscar', methods=['GET'])
def buscar():
    query = request.args.get('criterio')
    resultados = list(coleccion.find({
        "$or": [
            {"cedula": {"$regex": query, "$options": "i"}},
            {"nombre": {"$regex": query, "$options": "i"}},
            {"apellido": {"$regex": query, "$options": "i"}}
        ]
    }))
    return render_template('index.html', registros=resultados)

if __name__ == '__main__':
    app.run(debug=True)