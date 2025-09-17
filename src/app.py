# ---------------------- LIBRERÍAS FLASK ----------------------
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_mail import Mail, Message

import os
import base64
import datetime

# ---------------------- UTILIDADES ----------------------
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash
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
app.config['MAIL_PASSWORD'] = 'wsmc lowl twbu ovci'
app.config['MAIL_DEFAULT_SENDER'] = ('Soporte', 'estebangallego757@gmail.com')

mail = Mail(app)

# ---------------------- CONFIGURAR UPLOADS ----------------------
# Usaremos static/evidencias para las fotos de actividades
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EVIDENCIAS_FOLDER = os.path.join(BASE_DIR, "static", "evidencias")
app.config["EVIDENCIAS_FOLDER"] = EVIDENCIAS_FOLDER

# Crear carpeta si no existe
os.makedirs(EVIDENCIAS_FOLDER, exist_ok=True)

# Limitar tamaño máximo de request (ej. 16 MB) — ajústalo si quieres
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# Debug: imprime la ruta absoluta
print("EVIDENCIAS_FOLDER configurado en:", EVIDENCIAS_FOLDER)

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
    cur = db.connection.cursor()
    query = """
        SELECT c.id_cultivo, c.nombre, c.tipo, u.fullname, c.fecha_registro, c.estado
        FROM cultivos c
        JOIN user u ON c.id_usuario = u.id
    """
    cur.execute(query)
    cultivos = cur.fetchall()
    cur.close()
    return render_template('auth/cultivos.html', cultivos=cultivos)

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
        # Validaciones mínimas
        actividad = request.form.get('actividad')
        insumos = request.form.get('insumos')
        observaciones = request.form.get('observaciones')
        nombre_foto_usuario = request.form.get('nombreFoto', None)  # opcional nombre proporcionado por usuario
        evidencia_b64 = request.form.get('evidencia')

        # Validar campos obligatorios
        if not actividad or not insumos:
            flash("Actividad e Insumos son obligatorios.", "danger")
            return redirect(url_for('registrar_actividad'))

        evidencia_filename = None
        if evidencia_b64:
            try:
                # Separar encabezado (data:image/jpeg;base64,... o data:image/png;base64,...)
                if "," in evidencia_b64:
                    header, encoded = evidencia_b64.split(',', 1)
                else:
                    encoded = evidencia_b64

                data = base64.b64decode(encoded)

                # Generar nombre único: usar el nombre del usuario si lo dio, sino timestamp
                ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                if nombre_foto_usuario:
                    base = secure_filename(nombre_foto_usuario)
                    filename = f"{base}_{ts}.jpg"
                else:
                    filename = f"actividad_{ts}.jpg"

                file_path = os.path.join(app.config['EVIDENCIAS_FOLDER'], filename)

                # Guardar archivo
                with open(file_path, "wb") as f:
                    f.write(data)

                evidencia_filename = filename
            except Exception as e:
                flash(f"Error al guardar la foto: {e}", "danger")
                evidencia_filename = None

        # Insertar registro en BD (guardamos solo el nombre del archivo en 'evidencia')
        cur = db.connection.cursor()
        cur.execute("""
            INSERT INTO actividades (id_usuario, actividad, insumos, observaciones, evidencia, fecha)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (session['user_id'], actividad, insumos, observaciones, evidencia_filename))
        db.connection.commit()
        cur.close()

        flash("Actividad registrada con éxito ", "success")
        return redirect(url_for('registrar_actividad'))

    return render_template("auth/registrar_actividad.html")

@app.route('/ver_fotos')
@login_required
def ver_fotos():
    cursor = db.connection.cursor()
    query = """
        SELECT a.evidencia, a.fecha, u.fullname
        FROM actividades a
        JOIN user u ON a.id_usuario = u.id
        WHERE u.id = %s
        ORDER BY a.fecha DESC
    """
    cursor.execute(query, (session['user_id'],))
    resultados = cursor.fetchall()

    fotos = [
        {"nombre_archivo": row[0], "fecha": row[1], "usuario": row[2]}
        for row in resultados if row[0]
    ]

    usuario = fotos[0]["usuario"] if fotos else "Sin evidencias"
    cursor.close()

    return render_template("ver_fotos.html", fotos=fotos, usuario=usuario)



# ---------------------- MAIN ----------------------
if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run()
