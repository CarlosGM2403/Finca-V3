from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_mysqldb import MySQL
from flask_login import LoginManager,login_user,logout_user,login_required

from werkzeug.security import check_password_hash, generate_password_hash

from config import config

# Modelos:
from models.ModelUser import ModelUser

# Entidades:
from models.entities.User import User

app=Flask(__name__)
app.config.from_object(config['development'])  # <-- primero
app.secret_key = "cambia_esta_clave"

db = MySQL(app)
login_manager_app=LoginManager(app)
login_manager_app.login_view = 'login'

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)

@app.route('/')
def index():
    return redirect(url_for('login'))

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
            # Crear objeto User para Flask-Login
            user = ModelUser.get_by_id(db, row[0])
            login_user(user)  # Esto marca al usuario como logueado

            # También puedes mantener session si quieres
            session['user_id'] = row[0]

            # Verificamos si debe cambiar contraseña
            if row[2] == 1:  
                return redirect(url_for('cambiar_password'))

            # Redirigir al destino original si existe
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        else:
            flash("Usuario o contraseña incorrectos", "error")
    return render_template("auth/login.html")


    
# Logout

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

# Home
    
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

def status_401(error):
    return redirect(url_for('login'))

def status_404(error):
    return "<h1>Página no encontrada</h1>", 404

#olvide mi contraseña

@app.route('/forgot_password')
def forgot_password():
    return render_template('auth/forgot_password.html')


# Cambiar_password

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

            # Cerrar toda la sesión
            session.clear()

            flash("Contraseña actualizada con éxito. Vuelve a iniciar sesión.", "success")
            return redirect(url_for('login'))
        
        flash("Las contraseñas no coinciden", "error")

    return render_template("cambiar_password.html")


#registrar usuarios
@app.route('/Registrar_usuarios', methods=['GET', 'POST'])
def registrar_usuario():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        rol = request.form['rol']

        # encriptar contraseña
        password = generate_password_hash(password)

        # usar flask_mysqldb
        cur = db.connection.cursor()

        sql = """INSERT INTO user
                 (username, password, fullname, must_change_password, rol, estado, fecha_registro) 
                 VALUES (%s, %s, %s, %s, %s, %s, NOW())"""
        values = (username, password, fullname, 1, rol, "Habilitado")

        cur.execute(sql, values)
        db.connection.commit()
        cur.close()

        flash("Usuario registrado con éxito")
        return redirect(url_for('registrar_usuario'))

    return render_template('auth/Registrar_usuarios.html')


# Listar usuarios
@app.route('/usuarios')
@login_required
def usuarios():
    cur = db.connection.cursor()
    cur.execute("SELECT id, fullname, rol, estado, fecha_registro FROM user")
    usuarios = cur.fetchall()
    cur.close()
    return render_template('auth/usuarios.html', usuarios=usuarios)


# Cambiar estado de usuario
@app.route('/cambiar_estado/<int:id>')
@login_required
def cambiar_estado(id):
    cur = db.connection.cursor()
    # Obtener estado actual
    cur.execute("SELECT estado FROM user WHERE id=%s", (id,))
    estado = cur.fetchone()[0]
    nuevo_estado = "Inhabilitado" if estado == "Habilitado" else "Habilitado"

    # Actualizar estado
    cur.execute("UPDATE user SET estado=%s WHERE id=%s", (nuevo_estado, id))
    db.connection.commit()
    cur.close()

    flash(f"Estado del usuario cambiado a {nuevo_estado}", "success")
    return redirect(url_for('usuarios'))


#Borrar la caché y no dejar regresar
@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(401,status_401)
    app.register_error_handler(404,status_404)
    app.run()