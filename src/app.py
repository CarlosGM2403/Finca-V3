# ---------------------- LIBRERÍAS FLASK ----------------------
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_mail import Mail, Message

# ---------------------- UTILIDADES ----------------------
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os

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

# ---------------------- CONFIGURAR CORREO ----------------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'estebangallego757@gmail.com'   
app.config['MAIL_PASSWORD'] = 'wsmc lowl twbu ovci'   # Contraseña de aplicación
app.config['MAIL_DEFAULT_SENDER'] = ('Soporte', 'estebangallego757@gmail.com')

mail = Mail(app)

# ---------------------- CONFIGURAR UPLOADS ----------------------
# Carpeta para subir imágenes (ruta absoluta)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

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
        cur.execute("SELECT id, password, must_change_password FROM user WHERE username=%s", (username,))
        row = cur.fetchone()
        cur.close()

        if row and check_password_hash(row[1], password):
            user = ModelUser.get_by_id(db, row[0])
            login_user(user)
            session['user_id'] = row[0]

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
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')


# ---------------------- ERRORES ----------------------
def status_401(error):
    return redirect(url_for('login'))

def status_404(error):
    return "<h1>Página no encontrada</h1>", 404


# ---------------------- FUNCIONALIDADES EXTRA ----------------------
@app.route('/forgot_password')
def forgot_password():
    return render_template('auth/forgot_password.html')


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
        sql = """INSERT INTO user
                 (username, password, fullname, must_change_password, rol, estado, fecha_registro) 
                 VALUES (%s, %s, %s, %s, %s, %s, NOW())"""
        values = (username, password_hashed, fullname, 1, rol, "Habilitado")
        cur.execute(sql, values)
        db.connection.commit()
        cur.close()

        # -------- Enviar correo con credenciales --------
        try:
            msg = Message(" MFG - Cuenta creada en el sistema", recipients=[username])
            msg.body = f"""
            Hola {fullname}, somos el sistema de la finca guerrero.

            Tu cuenta ha sido creada exitosamente, inicia sesion con las siguientes credenciales.

            Usuario: {username}
            Contraseña provisional: {password_plain}

            Recuerda que deberás cambiar la contraseña en tu primer acceso.

            Saludos.
            No responda este mensaje
            """
            mail.send(msg)
            flash("Usuario registrado y correo enviado con éxito", "success")
        except Exception as e:
            flash(f"Usuario registrado pero error al enviar el correo: {str(e)}", "warning")

        flash("Usuario registrado con éxito")
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


@app.route('/cambiar_estado/<int:id>')
@login_required
def cambiar_estado(id):
    cur = db.connection.cursor()
    cur.execute("SELECT estado FROM user WHERE id=%s", (id,))
    estado = cur.fetchone()[0]
    nuevo_estado = "Inhabilitado" if estado == "Habilitado" else "Habilitado"
    cur.execute("UPDATE user SET estado=%s WHERE id=%s", (nuevo_estado, id))
    db.connection.commit()
    cur.close()

    flash(f"Estado del usuario cambiado a {nuevo_estado}", "success")
    return redirect(url_for('usuarios'))


@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


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
        fullname = request.form['fullname']
        rol = request.form['rol']
        estado = request.form['estado']

        cursor.execute("""
            UPDATE user 
            SET fullname = %s, rol = %s, estado = %s
            WHERE id = %s
        """, (fullname, rol, estado, session['user_id']))

        db.connection.commit()
        cursor.close()

        flash("Perfil actualizado con éxito", "success")
        return redirect(url_for('perfil'))

    cursor.execute("SELECT id, username, fullname, rol, estado FROM user WHERE id = %s", (session['user_id'],))
    usuario = cursor.fetchone()
    cursor.close()

    return render_template('auth/editar_perfil.html', usuario=usuario)


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
        sql = """
            INSERT INTO cultivos (nombre, tipo, id_usuario)
            VALUES (%s, %s, %s)
        """
        cur.execute(sql, (nombre, tipo, id_usuario))
        db.connection.commit()
        cur.close()

        flash("Cultivo registrado con éxito", "success")
        return redirect(url_for('cultivos'))

    return render_template('auth/registrar_cultivo.html')


@app.route('/cambiar_estado_cultivo/<int:id>', methods=['POST'])
@login_required
def cambiar_estado_cultivo(id):
    cur = db.connection.cursor()
    cur.execute("SELECT estado FROM cultivos WHERE id_cultivo=%s", (id,))
    estado = cur.fetchone()[0]

    nuevo_estado = "Inhabilitado" if estado == "Habilitado" else "Habilitado"
    cur.execute("UPDATE cultivos SET estado=%s WHERE id_cultivo=%s", (nuevo_estado, id))
    db.connection.commit()
    cur.close()

    flash(f"Estado del cultivo cambiado a {nuevo_estado}", "success")
    return redirect(url_for('cultivos'))


# ---------------------- ACTIVIDADES + EVIDENCIAS ----------------------
@app.route('/registrar_actividad', methods=['GET', 'POST'])
@login_required
def registrar_actividad():
    if request.method == 'POST':
        actividad = request.form['actividad']
        insumos = request.form['insumos']
        observaciones = request.form['observaciones']

        evidencia = None
        if 'evidencia' in request.files:
            file = request.files['evidencia']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                evidencia = filename

        cur = db.connection.cursor()
        cur.execute("""
        INSERT INTO actividades (id_usuario, actividad, insumos, observaciones, evidencia, fecha)
        VALUES (%s, %s, %s, %s, %s, NOW())
        """, (session['user_id'], actividad, insumos, observaciones, evidencia))
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

