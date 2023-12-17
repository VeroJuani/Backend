from flask import Flask, render_template, request, send_from_directory, redirect,url_for,flash
from flask_mysqldb import MySQL
from datetime import datetime
import os
from flask import send_from_directory

app = Flask(__name__)
app.secret_key="ClaveSecreta"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sistema'

mysql = MySQL(app)



CARPETA = os.path.join('uploads')
app.config['CARPETA'] = CARPETA


def obtener_empleados():
    try:
        with mysql.connection.cursor() as cursor:
            sql = "SELECT * FROM `sistema`.`empleados`;"
            cursor.execute(sql)
            empleados = cursor.fetchall()
            return empleados
    except Exception as e:
        print(f"Error al obtener empleados: {e}")
        return []


def eliminar_foto_anterior(id):
    try:
        with mysql.connection.cursor() as cursor:
            cursor.execute("SELECT foto FROM `sistema`.`empleados` WHERE id=%s", (id,))
            fila = cursor.fetchall()
            if fila:
                foto_antigua = fila[0][0]
                os.remove(os.path.join(app.config['CARPETA'], foto_antigua))
    except Exception as e:
        print(f"Error al eliminar foto anterior: {e}")


def actualizar_empleado(id, nombre, correo, foto):
    try:
        with mysql.connection.cursor() as cursor:
            sql = "UPDATE `sistema`.`empleados` SET `nombre`=%s, `correo`=%s WHERE id=%s;"
            datos = (nombre, correo, id)
            cursor.execute(sql, datos)
            mysql.connection.commit()
    except Exception as e:
        print(f"Error al actualizar empleado: {e}")


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)

@app.route('/')
def index():
    empleados = obtener_empleados()
    return render_template('empleados/index.html', empleados=empleados)


@app.route('/destroy/<int:id>')
def destroy(id):
    try:
        with mysql.connection.cursor() as cursor:
            sql = "DELETE FROM `sistema`.`empleados` WHERE id=%s;"
            cursor.execute(sql, (id,))
            mysql.connection.commit()
        return redirect('/')
    except Exception as e:
        print(f"Error al eliminar empleado: {e}")
        return render_template('empleados/index.html', error='Error al eliminar el empleado')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    try:
        with mysql.connection.cursor() as cursor:
            sql = "SELECT * FROM `sistema`.`empleados` WHERE id = %s;"
            cursor.execute(sql, (id,))
            empleado = cursor.fetchone()
            return render_template('empleados/edit.html', empleado=empleado)
    except Exception as e:
        print(f"Error al editar empleado: {e}")
        return render_template('empleados/index.html', error='Error al editar el empleado')


@app.route('/update', methods=['POST'])
def update():
    try:
        _nombre = request.form['txtNombre']
        _correo = request.form['txtCorreo']
        _foto = request.files['txtFoto']
        id = request.form['txtID']

        if _foto.filename != '':
            now = datetime.now()
            tiempo = now.strftime("%Y%H%M%S")
            nuevo_nombre_foto = tiempo + _foto.filename
            _foto.save(os.path.join(app.config['CARPETA'], nuevo_nombre_foto))
            
            eliminar_foto_anterior(id)
            
            with mysql.connection.cursor() as cursor:
                cursor.execute("UPDATE `sistema`.`empleados` SET foto=%s WHERE id=%s;", (nuevo_nombre_foto, id))

        actualizar_empleado(id, _nombre, _correo, _foto.filename)
        return redirect('/')

    except Exception as e:
        print(f"Error al actualizar empleado: {e}")
        return render_template('empleados/index.html', error='Error al actualizar el empleado')


@app.route('/create')
def create():
    return render_template('empleados/create.html')


@app.route('/store', methods=['POST'])
def storage():
    try:
        _nombre = request.form['txtNombre']
        _correo = request.form['txtCorreo']
        _foto = request.files['txtFoto']
        if _nombre == '' or _correo == '' or _foto =='':
            flash('Recuerda llenar los datos de los campos')
            return redirect(url_for('create'))
        now = datetime.now()
        tiempo = now.strftime("%Y%H%M%S")

        if _foto.filename != '':
            nuevo_nombre_foto = tiempo + _foto.filename
            _foto.save(os.path.join(app.config['CARPETA'], nuevo_nombre_foto))

        sql = "INSERT INTO `sistema`.`empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s, %s);"
        datos = (_nombre, _correo, nuevo_nombre_foto)

        with mysql.connection.cursor() as cursor:
            cursor.execute(sql, datos)
            mysql.connection.commit()

        return redirect('/')

    except Exception as e:
        print(f"Error al agregar empleado: {e}")
        return render_template('empleados/index.html', error='Error al agregar el empleado')


if __name__ == '__main__':
    app.run(debug=True)