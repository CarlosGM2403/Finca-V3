# ---------------------- LIBRERÍAS FLASK ----------------------
from sqlite3 import Cursor
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_mail import Mail, Message
from flask_login import current_user
import os
import base64
import uuid

# ---------------------- UTILIDADES ----------------------
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash
import os

from datetime import datetime

# ---------------------- CONFIGURACIÓN ----------------------


from config import config


# ---------------------- MODELOS ----------------------
from models.ModelUser import ModelUser

# ---------------------- ENTIDADES ----------------------
from models.entities.User import User

# ---------------------- CONFIGURACIÓN DE LA APP ----------------------
app = Flask(__name__)
app.config.from_object(config['development'])
app.secret_key = "cambia_esta_clave"
# Crea el serializador usando tu SECRET_KEY
s = URLSafeTimedSerializer(app.secret_key)

# ---------------------- CONFIGURAR CORREO ----------------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'estebangallego757@gmail.com'   
app.config['MAIL_PASSWORD'] = 'wsmc lowl twbu ovci'   # Contraseña de aplicación
app.config['MAIL_DEFAULT_SENDER'] = ('Soporte', 'estebangallego757@gmail.com')
app.config['UPLOAD_FOLDER'] = 'static/uploads'

mail = Mail(app)

# ---------------------- CONFIGURAR UPLOADS ----------------------
# Carpeta para subir imágenes (ruta absoluta)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
app.config['UPLOAD_FOLDER'] = os.path.join("static", "uploads")
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB límite

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Debug: imprime la ruta absoluta
print("UPLOAD_FOLDER configurado en:", UPLOAD_FOLDER)

# ---------------------- BASE DE DATOS ----------------------
db = MySQL(app)

# ---------------------- LOGIN MANAGER ----------------------
login_manager_app = LoginManager(app)
login_manager_app.login_view = 'login'

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)

# ---------------------- RUTAS PRINCIPALES ----------------------

@app.route('/')
def index():
    return redirect(url_for('login'))


# ---------------------- AUTENTICACIÓN ----------------------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = db.connection.cursor()
        cur.execute("SELECT id, password, must_change_password, rol FROM user WHERE username=%s", (username,))
        row = cur.fetchone()
        cur.close()

        if row and check_password_hash(row[1], password):
            user = ModelUser.get_by_id(db, row[0])
            login_user(user)
            session['user_id'] = row[0]
            session['rol'] = row[3]

            if row[2] == 1:  
                return redirect(url_for('cambiar_password'))

            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        else:
            flash("Usuario o contraseña incorrectos", "error")
    return render_template("auth/login.html")


@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))


# ---------------------- HOME ----------------------
@app.route('/home')
def home():
    rol = session.get("rol")
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html', rol=rol)


# ---------------------- ERRORES ----------------------
def status_401(error):
    return redirect(url_for('login'))

def status_404(error):
    return "<h1>Página no encontrada</h1>", 404


# ---------------------- FUNCIONALIDADES EXTRA ----------------------
# Paso 1: Usuario pide reset
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        cur = db.connection.cursor()
        cur.execute("SELECT id FROM user WHERE username=%s", (email,))
        user = cur.fetchone()

        if user:
            token = s.dumps(email, salt='password-reset-salt')
            link = url_for('reset_password', token=token, _external=True)

            msg = Message('Restablecer contraseña',
                          sender='tucorreo@gmail.com',
                          recipients=[email])
            msg.body = f"Para restablecer tu contraseña haz clic en el siguiente enlace:\n{link}"
            mail.send(msg)

            flash('Se ha enviado un enlace a tu correo.', 'success')
        else:
            flash('El correo no está registrado.', 'danger')

    return render_template('auth/forgot_password.html')

# Paso 2: Usuario abre el enlace
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600) # 1 hora
    except:
        flash('El enlace ha expirado o no es válido.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form['password']
        hashed_pw = generate_password_hash(new_password)

        cur = db.connection.cursor()
        cur.execute("UPDATE user SET password=%s WHERE username=%s", (hashed_pw, email))
        db.connection.commit()
        flash('Tu contraseña se actualizó con éxito.', 'success')
        return redirect(url_for('login'))

    return render_template('auth/reset_password.html', token=token)


@app.route('/cambiar_password', methods=['GET','POST'])
def cambiar_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nueva = request.form['nueva']
        confirmar = request.form['confirmar']

        if nueva == confirmar:
            hashed = generate_password_hash(nueva)

            cur = db.connection.cursor()
            cur.execute("""
                UPDATE user 
                SET password=%s, must_change_password=0 
                WHERE id=%s
            """, (hashed, session['user_id']))
            db.connection.commit()
            cur.close()

            session.clear()
            flash("Contraseña actualizada con éxito. Vuelve a iniciar sesión.", "success")
            return redirect(url_for('login'))

        flash("Las contraseñas no coinciden", "error")

    return render_template("cambiar_password.html")


# ---------------------- USUARIOS ----------------------
@app.route('/Registrar_usuarios', methods=['GET', 'POST'])
def registrar_usuario():
    if request.method == 'POST':
        username = request.form['username']
        password_plain = request.form['password']
        fullname = request.form['fullname']
        rol = request.form['rol']

        password_hashed = generate_password_hash(password_plain)

        cur = db.connection.cursor()
        try:
            sql = """INSERT INTO user
                     (username, password, fullname, must_change_password, rol, estado, fecha_registro) 
                     VALUES (%s, %s, %s, %s, %s, %s, NOW())"""
            values = (username, password_hashed, fullname, 1, rol, "Habilitado")
            cur.execute(sql, values)
            db.connection.commit()

            # -------- Enviar correo con credenciales --------
            try:
                msg = Message(" MFG - Cuenta creada en el sistema", recipients=[username])
                msg.body = f"""
                Hola {fullname}, somos el sistema de la finca guerrero.

                Tu cuenta ha sido creada exitosamente, inicia sesión con las siguientes credenciales:

                Usuario: {username}
                Contraseña provisional: {password_plain}

                Recuerda que deberás cambiar la contraseña en tu primer acceso.

                Saludos.
                No responda este mensaje.
                """
                mail.send(msg)
                flash("Usuario registrado y correo enviado con éxito", "success")
            except Exception as e:
                flash(f"Usuario registrado pero error al enviar el correo: {str(e)}", "warning")

        except Exception as e:
            # Aquí atrapamos el error si ya existe
            db.connection.rollback()
            flash("El usuario ya existe, no se puede registrar de nuevo.", "danger")

        finally:
            cur.close()

        return redirect(url_for('registrar_usuario'))

    return render_template('auth/Registrar_usuarios.html')


@app.route('/usuarios')
@login_required
def usuarios():
    cur = db.connection.cursor()
    cur.execute("SELECT id, fullname, rol, estado, fecha_registro FROM user")
    usuarios = cur.fetchall()
    cur.close()
    return render_template('auth/usuarios.html', usuarios=usuarios)


@app.route('/cambiar_estado/<int:id>', methods=['GET', 'POST'])
def cambiar_estado(id):
    # --- Obtener datos del usuario ---
    cur = db.connection.cursor()
    cur.execute("SELECT id, fullname, estado FROM user WHERE id=%s", (id,))
    row = cur.fetchone()
    cur.close()

    usuario = {
        "id": row[0],
        "fullname": row[1],
        "estado": row[2].strip().lower() if row[2] else None
    }

    if request.method == "POST":
        print("Datos recibidos desde el formulario:", request.form)
        nuevo_estado = request.form.get('estado')
        print(f"Valor que Flask recibió para estado: '{nuevo_estado}'")

        # --- Actualizar estado ---
        cur = db.connection.cursor()
        cur.execute("UPDATE user SET estado=%s WHERE id=%s", (nuevo_estado, id))
        db.connection.commit()
        cur.close()

        flash("Estado actualizado correctamente", "success")
        return redirect(url_for('usuarios'))

    return render_template('auth/cambiar_estado.html', usuario=usuario)


@app.route('/perfil')
def perfil():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cur = db.connection.cursor()
    cur.execute(""" 
        SELECT id, username, fullname, rol, estado, fecha_registro
        FROM user WHERE id=%s
    """, (session['user_id'],))
    usuario = cur.fetchone()
    cur.close()

    return render_template('auth/perfil.html', usuario=usuario)


@app.route('/editar_perfil', methods=['GET', 'POST'])
def editar_perfil():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = db.connection.cursor()

    if request.method == 'POST':
        fullname = request.form.get('fullname')  # Usamos .get() para evitar errores

        # Solo actualizamos el nombre
        cursor.execute("""
            UPDATE user 
            SET fullname = %s
            WHERE id = %s
        """, (fullname, session['user_id']))

        db.connection.commit()
        cursor.close()

        flash("Perfil actualizado con éxito", "success")
        return redirect(url_for('perfil'))

    # Obtener datos actuales del usuario
    cursor.execute("SELECT id, username, fullname, rol, estado FROM user WHERE id = %s", (session['user_id'],))
    usuario = cursor.fetchone()
    cursor.close()

    return render_template('auth/editar_perfil.html', usuario=usuario)



@app.route('/cambiar_contraseña', methods=['GET','POST'])
def cambiar_contraseña():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nueva = request.form['nueva']
        confirmar = request.form['confirmar']

        if nueva == confirmar:
            hashed = generate_password_hash(nueva)

            cur = db.connection.cursor()
            cur.execute("""
                UPDATE user 
                SET password=%s, must_change_password=0 
                WHERE id=%s
            """, (hashed, session['user_id']))
            db.connection.commit()
            cur.close()

            session.clear()
            flash("Contraseña actualizada con éxito. Vuelve a iniciar sesion", "success")
            return redirect(url_for('login'))

        flash("Las contraseñas no coinciden", "error")

    return render_template("auth/cambiar_contraseña.html")

# ---------------------- CULTIVOS ----------------------
@app.route('/cultivos')
@login_required
def cultivos():
    rol = session.get("rol")
    cur = db.connection.cursor()
    query = """
        SELECT c.id_cultivo, c.nombre, c.tipo, u.fullname, c.fecha_registro, c.estado, u.rol
        FROM cultivos c
        JOIN user u ON c.id_usuario = u.id
    """
    cur.execute(query)
    cultivos = cur.fetchall()
    cur.close()
    return render_template('auth/cultivos.html', cultivos=cultivos, rol=rol)


@app.route('/registrar_cultivo', methods=['GET', 'POST'])
@login_required
def registrar_cultivo():
    if request.method == 'POST':
        nombre = request.form['nombre']
        tipo = request.form['tipo']
        id_usuario = session['user_id']

        cur = db.connection.cursor()
        # Verificar si ya existe un cultivo con ese nombre
        cur.execute("SELECT id_cultivo FROM cultivos WHERE nombre=%s", (nombre,))
        existe = cur.fetchone()

        if existe:
            flash("Ya existe un cultivo con ese nombre.", "danger")
            cur.close()
            return redirect(url_for('registrar_cultivo'))

        cur.execute(
            "INSERT INTO cultivos (nombre, tipo, id_usuario) VALUES (%s, %s, %s)",
            (nombre, tipo, id_usuario)
        )
        db.connection.commit()
        cur.close()
        flash("Cultivo registrado con éxito.", "success")
        return redirect(url_for('registrar_cultivo'))

    return render_template('auth/registrar_cultivo.html')



# ---------------------- ACTIVIDADES + EVIDENCIAS ----------------------



@app.route('/registrar_actividad', methods=['GET', 'POST'])
@login_required
def registrar_actividad():
    if request.method == 'POST':
        actividad = request.form['actividad']
        insumos = request.form['insumos']
        observaciones = request.form['observaciones']
        evidencia_base64 = request.form['evidencia']

        print("DEBUG - Datos recibidos:")
        print("Actividad:", actividad)
        print("Insumos:", insumos)
        print("Observaciones:", observaciones)
        print("Evidencia:", len(evidencia_base64) if evidencia_base64 else "No llegó")

        filename = None

        if evidencia_base64:
            try:
                if "," in evidencia_base64:
                    evidencia_base64 = evidencia_base64.split(",")[1]

                image_data = base64.b64decode(evidencia_base64)
                filename = f"{uuid.uuid4().hex}.jpg"
                filepath = os.path.join(UPLOAD_FOLDER, filename)  # 👈 Ruta absoluta

                with open(filepath, "wb") as f:
                    f.write(image_data)

            except Exception as e:
                print("Error al guardar imagen:", e)
                flash(f"Error al guardar la imagen: {str(e)}", "danger")
                return redirect(url_for("registrar_actividad"))

        try:
            print(f"Actividad recibida: '{actividad}'")
            cursor = db.connection.cursor()
            cursor.execute("""
                INSERT INTO actividades (id_usuario, actividad, insumos, observaciones, evidencia, fecha)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (session['user_id'], actividad, insumos, observaciones, filename))
            db.connection.commit()
            cursor.close()

            flash("Actividad registrada correctamente", "success")
            return redirect(url_for('ver_fotos'))

        except Exception as e:
            db.connection.rollback()
            print("Error al guardar en la BD:", e)
            import traceback
            traceback.print_exc()
            flash(f"Error al registrar actividad: {str(e)}", "danger")

    return render_template("registrar_actividad.html")



@app.route("/ver_fotos")
@login_required
def ver_fotos():
    cursor = db.connection.cursor()

    # Consulta actualizada según tus tablas
    query = """
        SELECT a.evidencia, a.fecha, u.fullname, a.actividad, a.insumos, a.observaciones
        FROM actividades a
        JOIN user u ON a.id_usuario = u.id
        WHERE u.id = %s
    """
    cursor.execute(query, (session['user_id'],))
    rows = cursor.fetchall()

    fotos = []
    usuario = None  # Evitar el error de variable no definida

    for row in rows:
        if usuario is None:
            usuario = row[2]  # Capturamos el nombre completo solo una vez
        fotos.append({
            'ruta': url_for('static', filename='uploads/' + row[0]),
            'fecha': row[1],
            'usuario': row[2],
            'actividad': row[3],
            'insumos': row[4],
            'observaciones': row[5]
        })

    cursor.close()

    # Si no hay fotos, aún obtenemos el nombre del usuario
    if usuario is None:
        cursor = db.connection.cursor()
        cursor.execute("SELECT fullname FROM user WHERE id = %s", (session['user_id'],))
        result = cursor.fetchone()
        usuario = result[0] if result else "Usuario desconocido"
        cursor.close()

    return render_template("ver_fotos.html", fotos=fotos, usuario=usuario)

# ---------------------- SOLICITUD INSUMOS ----------------------
@app.route('/solicitud_insumos', methods=['GET', 'POST'])
@login_required
def solicitud_insumos():
    cur = db.connection.cursor()

    # Obtener tipos únicos de insumos sin filtrar por id
    cur.execute("SELECT DISTINCT tipo_insumo FROM solicitud_insumo")
    tipos = [row[0] for row in cur.fetchall()]

    if request.method == 'POST':
        tipo_insumo = request.form.get('tipo_insumo')  # Cambiado a .get() para evitar errores
        cantidad = request.form.get('cantidad')
        observaciones = request.form.get('observaciones', '')

        if not tipo_insumo or not cantidad:
            flash("Por favor, complete los campos obligatorios", "error")
            return redirect(url_for('solicitud_insumos'))

        fecha = datetime.now()

        # Insertar nueva solicitud
        cur.execute("""
            INSERT INTO solicitudes_insumos (fecha, tipo_insumo, cantidad, observaciones)
            VALUES (%s, %s, %s, %s)
        """, (fecha, tipo_insumo, cantidad, observaciones))
        db.connection.commit()
        cur.close()

        flash("Solicitud de insumo registrada con éxito", "success")
        return redirect(url_for('solicitud_insumos'))

    cur.close()
    return render_template('auth/solicitud_insumo.html', tipos=tipos)





@app.route("/registrar_ventas", methods=["GET", "POST"])
def registrar_ventas():
    cur = db.connection.cursor()

    # Traer cultivos para el selector
    cur.execute("SELECT Id_cultivo, nombre FROM Cultivos")
    cultivos = cur.fetchall()

    if request.method == "POST":
        cod_cultivo = request.form["cultivo"]
        fecha = request.form["fecha"]
        cantidad_bultos = request.form["cantidad_bultos"]
        precio = request.form["precio"]
        descripcion = request.form["descripcion"]

        # Insertar en la tabla ventas
        cur.execute("""
            INSERT INTO ventas (cod_cultivo, fecha_venta, cantidad_bultos, precio, descripcion)
            VALUES (%s, %s, %s, %s, %s)
        """, (cod_cultivo, fecha, cantidad_bultos, precio, descripcion))

        db.connection.commit()
        return redirect(url_for("ventas_registradas"))

    return render_template("auth/registrar_ventas.html", cultivos=cultivos)


@app.route("/ventas_registradas")
def ventas_registradas():
    cur = db.connection.cursor()
    cur.execute("""
        SELECT v.id_venta, c.nombre AS cultivo, v.fecha_venta, 
               v.cantidad_bultos, v.precio, v.descripcion
        FROM ventas v
        JOIN cultivos c ON v.cod_cultivo = c.id_cultivo
        ORDER BY v.fecha_venta DESC
    """)
    ventas = cur.fetchall()
    return render_template("auth/ventas_registradas.html", ventas=ventas)


@app.route("/eliminar_venta/<int:id>")
def eliminar_venta(id):
    cur = db.connection.cursor()
    cur.execute("DELETE FROM ventas WHERE id_venta = %s", (id,))
    db.connection.commit()
    return redirect(url_for("ventas_registradas"))

# ---------------------- REGISTRAR SIEMBRA ----------------------
@app.route("/Registrar_siembra", methods=["GET", "POST"])
@login_required
def registrar_siembra():
    cur = db.connection.cursor()
    cur.execute("SELECT Id_cultivo, nombre FROM Cultivos WHERE estado = 'Habilitado'")
    cultivos = cur.fetchall()

    if request.method == "POST":
        fecha = request.form["fecha"]
        detalle = request.form["detalle"]
        cod_cultivos = request.form["cultivo"]

        cur.execute("""
            INSERT INTO siembra (fecha_siembra, detalle, cod_cultivos)
            VALUES (%s, %s, %s)
        """, (fecha, detalle, cod_cultivos))
        db.connection.commit()
        return redirect(url_for("registrar_siembra"))

    return render_template("registrar_siembra.html", cultivos=cultivos)

# ---------------------- SIEMBRA REGISTRADA ----------------------
@app.route("/Siembra_registrada")
def siembra_registrada():
    cur = db.connection.cursor()
    cur.execute("""
        SELECT s.fecha_siembra, s.detalle, c.nombre AS cultivo_nombre
        FROM siembra s
        JOIN Cultivos c ON s.cod_cultivos = c.Id_cultivo
    """)
    registros = cur.fetchall()
    return render_template("siembra_registrada.html", registros=registros)


# ---------------------- SOLICITUD DE INSUMO ----------------------

@app.route('/solicitar_insumo', methods=['GET', 'POST'])
@login_required
def solicitar_insumo():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        tipo_insumo = request.form.get('tipo_insumo')
        cantidad = request.form.get('cantidad')
        observaciones = request.form.get('observaciones')

        try:
            cur = db.connection.cursor()
            cur.execute("""
                INSERT INTO solicitud_insumo (usuario_id, tipo_insumo, cantidad, observaciones, fecha_solicitud)
                VALUES (%s, %s, %s, %s, NOW())
            """, (session['user_id'], tipo_insumo, cantidad, observaciones))
            db.connection.commit()
            cur.close()

            flash("Solicitud de insumo registrada con éxito", "success")
            return redirect(url_for('solicitar_insumo'))

        except Exception as e:
            db.connection.rollback()
            flash(f"Error al registrar la solicitud: {str(e)}", "danger")

    return render_template('solicitud_insumo.html')

# ---------------------- SOLICITUDES REALIZADAS ----------------------

@app.route('/solicitudes', methods=['GET'])
def ver_solicitudes():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cur = db.connection.cursor()
    cur.execute("""
        SELECT s.id, u.fullname, s.tipo_insumo, s.cantidad, s.observaciones, s.fecha_solicitud
        FROM solicitud_insumo s
        JOIN user u ON s.usuario_id = u.id
        ORDER BY s.fecha_solicitud
    """)
    solicitudes = cur.fetchall()
    cur.close()

    print(solicitudes)  
    return render_template('ver_solicitudes.html', solicitudes=solicitudes)


# ---------------------- EN CONSTRUCCIÓN ----------------------

@app.route('/en_construccion')
def en_construccion():
    return "<h1>🚧 Esta sección está en construcción 🚧</h1>"

# ---------------------- SEGUIMIENTO DE CULTIVO ----------------------

@app.route('/seguimiento_cultivo', methods=['GET', 'POST'])
@login_required
def seguimiento_cultivo():
    cur = db.connection.cursor()
    cur.execute("SELECT Id_cultivo, nombre FROM Cultivos WHERE estado = 'Habilitado'")
    cultivos = cur.fetchall()

    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        cultivo_id = request.form.get('cultivo')  # 👈 coincide con el HTML
        tratamiento = request.form.get('tratamiento')
        problema = request.form.get('problema')
        prioridad = request.form.get('prioridad')
        insumos = request.form.get('insumos')

        try:
            # Traer el nombre del cultivo a partir del Id_cultivo
            cur.execute("SELECT nombre FROM Cultivos WHERE Id_cultivo = %s", (cultivo_id,))
            cultivo_nombre = cur.fetchone()

            if cultivo_nombre:
                cultivo_nombre = cultivo_nombre[0]  # Tomamos el valor del nombre

                # Insertar en la tabla tratamientos
                cur.execute("""
                    INSERT INTO tratamientos (cultivo, tratamiento, problema, prioridad, insumos, fecha_registro)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                """, (cultivo_nombre, tratamiento, problema, prioridad, insumos))
                db.connection.commit()

                flash("Seguimiento registrado con éxito", "success")
                return redirect(url_for('seguimiento_cultivo'))
            else:
                flash("El cultivo seleccionado no existe.", "danger")

        except Exception as e:
            db.connection.rollback()
            flash(f"Error al registrar el seguimiento: {str(e)}", "danger")

    cur.close()
    return render_template('auth/seguimiento_cultivo.html', cultivos=cultivos)

# ---------------------- TRATAMIENTOS REGISTRADOS ----------------------

@app.route('/tratamientos_registrados')
@login_required
def tratamientos_registrados():
    try:
        cur = db.connection.cursor()
        cur.execute("""
            SELECT id_tratamiento, cultivo, tratamiento, problema, prioridad, insumos, fecha_registro
            FROM tratamientos
            ORDER BY fecha_registro DESC
        """)
        tratamientos = cur.fetchall()
        cur.close()
        return render_template('auth/tratamientos_registrados.html', tratamientos=tratamientos)

    except Exception as e:
        flash(f"Error al cargar los tratamientos: {str(e)}", "danger")
        return redirect(url_for('home'))

# ---------------------- ELIMINAR TRATAMIENTO ----------------------

@app.route('/eliminar_tratamiento/<int:id>', methods=['GET'])
@login_required
def eliminar_tratamiento(id):
    try:
        cur = db.connection.cursor()
        cur.execute("DELETE FROM tratamientos WHERE id_tratamiento = %s", (id,))
        db.connection.commit()
        cur.close()
        flash("Tratamiento eliminado correctamente", "success")
    except Exception as e:
        db.connection.rollback()
        flash(f"Error al eliminar el tratamiento: {str(e)}", "danger")

    return redirect(url_for('tratamientos_registrados'))


# ---------------------- MAIN ----------------------
if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run()
