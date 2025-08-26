from flask import Flask, render_template, request, redirect, url_for, flash, session
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

# Login

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur =db.connection.cursor()
        cur.execute("SELECT id, password, must_change_password FROM user WHERE username=%s", (username,))
        row = cur.fetchone()
        cur.close()

        if row and check_password_hash(row[1], password):
            session['user_id'] = row[0]

            # Verificamos si debe cambiar contraseña
            if row[2] == 1:  
                return redirect(url_for('cambiar_password'))
            
            return redirect(url_for('home'))
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


if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(401,status_401)
    app.register_error_handler(404,status_404)
    app.run()