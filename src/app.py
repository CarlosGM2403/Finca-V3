# ---------------------- LIBRERÍAS FLASK ----------------------
from sqlite3 import Cursor
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_mail import Mail, Message
from flask_login import current_user
from functools import wraps
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
app.config.from_object(config["development"])
app.secret_key = "cambia_esta_clave"
# Crea el serializador usando tu SECRET_KEY
s = URLSafeTimedSerializer(app.secret_key)

# ---------------------- CONFIGURAR CORREO ----------------------
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "estebangallego757@gmail.com"
app.config["MAIL_PASSWORD"] = "wsmc lowl twbu ovci"  # Contraseña de aplicación
app.config["MAIL_DEFAULT_SENDER"] = ("Soporte", "estebangallego757@gmail.com")
app.config["UPLOAD_FOLDER"] = "static/uploads"

mail = Mail(app)

# ---------------------- CONFIGURAR UPLOADS ----------------------
# Carpeta para subir imágenes (ruta absoluta)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB límite

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Debug: imprime la ruta absoluta
print("UPLOAD_FOLDER configurado en:", UPLOAD_FOLDER)

# ---------------------- BASE DE DATOS ----------------------
db = MySQL(app)

# ---------------------- LOGIN MANAGER ----------------------
login_manager_app = LoginManager(app)
login_manager_app.login_view = "login"


@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)


# ----------------------- LOGIN REQUIRED ----------------------


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


# ----------------------- EVITER CACHE -------------------------
@app.after_request
def disable_cache(response):
    response.headers["Cache-control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# ---------------------- RUTAS PRINCIPALES ----------------------


@app.route("/")
def index():
    return redirect(url_for("login"))


# ---------------------- AUTENTICACIÓN ----------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cur = db.connection.cursor()
        cur.execute(
            "SELECT id, password, must_change_password, rol, fullname FROM user WHERE username=%s",
            (username,),
        )
        row = cur.fetchone()
        cur.close()

        if row and check_password_hash(row[1], password):
            user = ModelUser.get_by_id(db, row[0])
            login_user(user)
            session["user_id"] = row[0]
            session["rol"] = row[3]
            session["fullname"] = row[4]

            # ===============================
            # REGISTRO DEL INICIO DE SESIÓN
            # ===============================
            try:
                cur = db.connection.cursor()
                ip = request.remote_addr
                navegador = request.user_agent.string
                cur.execute(
                    """
                    INSERT INTO registro_sesiones (id_usuario, direccion_ip, navegador)
                    VALUES (%s, %s, %s)
                    """,
                    (row[0], ip, navegador),
                )
                db.connection.commit()
                cur.close()
            except Exception as e:
                print(f"Error al registrar inicio de sesión: {e}")
            # ===============================

            if row[2] == 1:
                return redirect(url_for("cambiar_password"))

            next_page = request.args.get("next")
            flash(f"¡Bienvenido, {row[4]}!", "success")
            return redirect(next_page or url_for("home"))
        else:
            flash("Usuario o contraseña incorrectos", "error")
            return redirect(url_for("login"))

    return render_template("auth/login.html")


# ---------------------- PRODUCCIÓN REGISTRADA ----------------------


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    print("Sesión después de logout:", session)
    return redirect(url_for("login"))


# ---------------------- HOME ----------------------
@app.route("/home")
@login_required
def home():
    print("Accediendo a /home con sesión activa")
    rol = session.get("rol")
    nombre = session.get("fullname")

    if "user_id" not in session:
        return redirect(url_for("login"))

    # Obtener foto de perfil del usuario
    cur = db.connection.cursor()
    cur.execute("SELECT foto_perfil FROM user WHERE id=%s", (session["user_id"],))
    resultado = cur.fetchone()
    cur.close()

    # Construir URL de la foto de perfil
    if resultado and resultado[0]:  # Si tiene foto en la base de datos
        foto_perfil_url = url_for("static", filename="uploads/" + resultado[0])
    else:  # Si no tiene foto, usar la por defecto
        foto_perfil_url = url_for("static", filename="img/perfil.png")

    print(f"Foto de perfil URL: {foto_perfil_url}")

    return render_template(
        "home.html", rol=rol, nombre=nombre, foto_perfil_url=foto_perfil_url
    )


# ---------------------- ERRORES ----------------------
def status_401(error):
    return redirect(url_for("login"))


def status_404(error):
    return "<h1>Página no encontrada</h1>", 404


# ---------------------- FUNCIONALIDADES EXTRA ----------------------
# Paso 1: Usuario pide reset
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        cur = db.connection.cursor()
        cur.execute("SELECT id FROM user WHERE username=%s", (email,))
        user = cur.fetchone()

        if user:
            token = s.dumps(email, salt="password-reset-salt")
            link = url_for("reset_password", token=token, _external=True)

            msg = Message(
                "Restablecer contraseña",
                sender="tucorreo@gmail.com",
                recipients=[email],
            )
            msg.body = f"Para restablecer tu contraseña haz clic en el siguiente enlace:\n{link}"
            mail.send(msg)

            flash("Se ha enviado un enlace a tu correo.", "success")
        else:
            flash("El correo no está registrado.", "danger")

    return render_template("auth/forgot_password.html")


# Paso 2: Usuario abre el enlace
@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = s.loads(token, salt="password-reset-salt", max_age=3600)  # 1 hora
    except:
        flash("El enlace ha expirado o no es válido.", "danger")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        new_password = request.form["password"]
        hashed_pw = generate_password_hash(new_password)

        cur = db.connection.cursor()
        cur.execute("UPDATE user SET password=%s WHERE username=%s", (hashed_pw, email))
        db.connection.commit()
        flash("Tu contraseña se actualizó con éxito.", "success")
        return redirect(url_for("login"))

    return render_template("auth/reset_password.html", token=token)


@app.route("/cambiar_password", methods=["GET", "POST"])
def cambiar_password():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        nueva = request.form["nueva"]
        confirmar = request.form["confirmar"]

        if nueva == confirmar:
            hashed = generate_password_hash(nueva)

            cur = db.connection.cursor()
            cur.execute(
                """
                UPDATE user 
                SET password=%s, must_change_password=0 
                WHERE id=%s
            """,
                (hashed, session["user_id"]),
            )
            db.connection.commit()
            cur.close()

            session.clear()
            session["passwordChanged"] = True
            flash(
                "Contraseña actualizada con éxito. Vuelve a iniciar sesión.", "success"
            )
            return redirect(url_for("login"))

        flash("Las contraseñas no coinciden", "error")

    return render_template("cambiar_password.html")


# ---------------------- USUARIOS ----------------------
@app.route("/Registrar_usuarios", methods=["GET", "POST"])
def registrar_usuario():
    if request.method == "POST":
        username = request.form["username"]
        password_plain = request.form["password"]
        fullname = request.form["fullname"]
        rol = request.form["rol"]

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
                msg = Message(
                    " MFG - Cuenta creada en el sistema", recipients=[username]
                )
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
                flash(
                    f"Usuario registrado pero error al enviar el correo: {str(e)}",
                    "warning",
                )

        except Exception as e:
            # Aquí atrapamos el error si ya existe
            db.connection.rollback()
            flash("El usuario ya existe, no se puede registrar de nuevo.", "danger")

        finally:
            cur.close()
        flash("Registro exitoso", "success")
        return redirect(url_for("registrar_usuario"))

    return render_template("auth/Registrar_usuarios.html")


@app.route("/usuarios")
@login_required
def usuarios():
    cur = db.connection.cursor()
    cur.execute("SELECT id, fullname, rol, estado, fecha_registro FROM user")
    usuarios = cur.fetchall()
    cur.close()
    return render_template("auth/usuarios.html", usuarios=usuarios)


@app.route("/cambiar_estado/<int:id>", methods=["GET", "POST"])
@login_required
def cambiar_estado(id):
    # VERIFICAR ROL - Solo administradores pueden cambiar estados
    if session.get("rol") != "administrador":
        flash("No tienes permisos para esta acción", "error")
        return redirect(url_for("home"))

    cur = db.connection.cursor()
    # AGREGAR rol A LA CONSULTA
    cur.execute("SELECT id, fullname, estado, rol FROM user WHERE id=%s", (id,))
    row = cur.fetchone()

    if not row:
        flash("Usuario no encontrado", "error")
        cur.close()
        return redirect(url_for("usuarios"))

    cur.close()

    usuario = {
        "id": row[0],
        "fullname": row[1],
        "estado": row[2].strip().lower() if row[2] else None,
        "rol": row[3],  # ← AGREGAR ESTO
    }

    if request.method == "POST":
        print("Datos recibidos desde el formulario:", request.form)
        nuevo_estado = request.form.get("estado")
        nuevo_rol = request.form.get("rol")  # ← CAPTURAR EL ROL TAMBIÉN
        print(f"Valor que Flask recibió para estado: '{nuevo_estado}'")
        print(f"Valor que Flask recibió para rol: '{nuevo_rol}'")

        # Validar que el estado sea correcto
        if nuevo_estado not in ["habilitado", "inhabilitado"]:
            flash("Estado no válido", "error")
            return redirect(url_for("cambiar_estado", id=id))

        # Validar que el rol sea correcto
        if nuevo_rol not in ["administrador", "supervisor", "cuidador", "empleado"]:
            flash("Rol no válido", "error")
            return redirect(url_for("cambiar_estado", id=id))

        # --- Actualizar estado Y rol ---
        try:
            cur = db.connection.cursor()
            # ACTUALIZAR AMBOS CAMPOS
            cur.execute(
                "UPDATE user SET estado=%s, rol=%s WHERE id=%s",
                (nuevo_estado, nuevo_rol, id),
            )
            db.connection.commit()
            cur.close()

            flash("Usuario actualizado correctamente", "success")
            return redirect(url_for("usuarios"))

        except Exception as e:
            db.connection.rollback()
            flash(f"Error al actualizar usuario: {str(e)}", "error")
            return redirect(url_for("cambiar_estado", id=id))

    return render_template("auth/cambiar_estado.html", usuario=usuario)


@app.route("/perfil")
def perfil():
    if "user_id" not in session:
        return redirect(url_for("login"))

    cur = db.connection.cursor()
    cur.execute(
        """ 
        SELECT id, username, fullname, rol, estado, fecha_registro, foto_perfil
        FROM user WHERE id=%s
    """,
        (session["user_id"],),
    )
    usuario = cur.fetchone()
    cur.close()

    # Obtener URL de la foto
    foto_url = (
        url_for("static", filename="uploads/" + usuario[6])
        if usuario[6]
        else url_for("static", filename="img/default-avatar.png")
    )

    return render_template("auth/perfil.html", usuario=usuario, foto_url=foto_url)


@app.route("/editar_perfil", methods=["GET", "POST"])
def editar_perfil():
    if "user_id" not in session:
        return redirect(url_for("login"))

    cursor = db.connection.cursor()

    if request.method == "POST":
        fullname = request.form.get("fullname")
        foto_perfil = request.files.get("foto_perfil")  # Nuevo campo

        if foto_perfil and foto_perfil.filename != "":
            if allowed_file(foto_perfil.filename):
                # Generar nombre único
                filename = f"perfil_{session['user_id']}_{uuid.uuid4().hex}.jpg"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                foto_perfil.save(filepath)

                # Actualizar nombre Y foto
                cursor.execute(
                    """
                    UPDATE user 
                    SET fullname = %s, foto_perfil = %s
                    WHERE id = %s
                """,
                    (fullname, filename, session["user_id"]),
                )
            else:
                flash("Formato no permitido. Use JPG, PNG o JPEG.", "error")
                return redirect(url_for("editar_perfil"))
        else:
            # Solo actualizar nombre
            cursor.execute(
                """
                UPDATE user 
                SET fullname = %s
                WHERE id = %s
            """,
                (fullname, session["user_id"]),
            )

        db.connection.commit()
        cursor.close()
        flash("Perfil actualizado con éxito", "success")
        return redirect(url_for("perfil"))

    # Obtener datos actuales
    cursor.execute(
        "SELECT id, username, fullname, rol, estado, foto_perfil FROM user WHERE id = %s",
        (session["user_id"],),
    )
    usuario = cursor.fetchone()

    # Obtener URL de la foto actual
    foto_url = (
        url_for("static", filename="uploads/" + usuario[5])
        if usuario[5]
        else url_for("static", filename="img/default-avatar.png")
    )

    cursor.close()

    return render_template(
        "auth/editar_perfil.html", usuario=usuario, foto_url=foto_url
    )


@app.route("/cambiar_contraseña", methods=["GET", "POST"])
def cambiar_contraseña():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        actual = request.form["actual"]  # 🔹 contraseña actual
        nueva = request.form["nueva"]
        confirmar = request.form["confirmar"]

        # Obtener la contraseña actual desde la BD
        cur = db.connection.cursor()
        cur.execute("SELECT password FROM user WHERE id = %s", (session["user_id"],))
        usuario = cur.fetchone()

        # Confirmar que la contraseña anterior sea correcta
        if not usuario or not check_password_hash(usuario[0], actual):
            flash("La contraseña actual no es correcta", "error")
            cur.close()
            return redirect(url_for("cambiar_contraseña"))

        # Verificar que las nuevas contraseñas coincidan
        if nueva == confirmar:
            hashed = generate_password_hash(nueva)

            cur.execute(
                """
                UPDATE user 
                SET password=%s, must_change_password=0 
                WHERE id=%s
            """,
                (hashed, session["user_id"]),
            )
            db.connection.commit()
            cur.close()

            session.clear()
            flash(
                "Contraseña actualizada con éxito. Vuelve a iniciar sesión", "success"
            )
            return redirect(url_for("login"))

        flash("Las contraseñas nuevas no coinciden", "error")
        cur.close()

    return render_template("auth/cambiar_contraseña.html")


# ---------------------- CULTIVOS ----------------------
@app.route("/cultivos")
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
    return render_template("auth/cultivos.html", cultivos=cultivos, rol=rol)


@app.route("/cambiar_estado_cultivo/<int:id>", methods=["POST"])
def cambiar_estado_cultivo(id):
    cur = db.connection.cursor()
    cur.execute("SELECT nombre, estado FROM cultivos WHERE id_cultivo=%s", (id,))
    row = cur.fetchone()
    if row is None:
        flash("El cultivo no existe", "error")
        cur.close()
        return redirect(url_for("cultivos"))
    nombre = row[0]
    estado_actual = row[1]
    nuevo_estado = "Inhabilitado" if estado_actual == "Habilitado" else "Habilitado"
    cur.execute("UPDATE cultivos SET estado=%s WHERE id_cultivo=%s", (nuevo_estado, id))
    db.connection.commit()
    cur.close()
    flash(f"El cultivo '{nombre}' fue {nuevo_estado}", "success")
    return redirect(url_for("cultivos"))


@app.route("/registrar_cultivo", methods=["GET", "POST"])
@login_required
def registrar_cultivo():
    if request.method == "POST":
        nombre = request.form["nombre"]
        tipo = request.form["tipo"]
        id_usuario = session["user_id"]

        cur = db.connection.cursor()
        # Verificar si ya existe un cultivo con ese nombre
        cur.execute("SELECT id_cultivo FROM cultivos WHERE nombre=%s", (nombre,))
        existe = cur.fetchone()

        if existe:
            flash("Ya existe un cultivo con ese nombre.", "danger")
            cur.close()
            return redirect(url_for("registrar_cultivo"))

        cur.execute(
            "INSERT INTO cultivos (nombre, tipo, id_usuario) VALUES (%s, %s, %s)",
            (nombre, tipo, id_usuario),
        )
        db.connection.commit()
        cur.close()
        flash("Cultivo registrado con éxito.", "success")
        return redirect(url_for("registrar_cultivo"))

    return render_template("auth/registrar_cultivo.html")


# ---------------------- ACTIVIDADES + EVIDENCIAS ----------------------


@app.route("/registrar_actividad", methods=["GET", "POST"])
@login_required
def registrar_actividad():
    if request.method == "POST":
        actividad = request.form.get("actividad")
        # Obtener lista de insumos (multiple)
        insumos_lista = request.form.getlist("insumos")
        # Convertir a string para DB
        insumos_str = ", ".join(insumos_lista) if insumos_lista else None
        observaciones = request.form.get("observaciones")
        evidencia_base64 = request.form.get("evidencia")

        # --- DEBUG: imprimir en la consola de Flask (no en SQL) ---
        print("DEBUG - Datos recibidos:")
        print("Actividad:", actividad)
        print("INSUMOS RECIBIDOS (lista):", insumos_lista)
        print("INSUMOS STRING a guardar:", insumos_str)
        print("Observaciones:", observaciones)
        print(
            "Evidencia (len):",
            len(evidencia_base64) if evidencia_base64 else "No llegó",
        )
        # -----------------------------------------------------------

        # Validación: evitar insertar NULL si la columna es NOT NULL
        if not insumos_str:
            flash("Debes seleccionar al menos un insumo.", "danger")
            return redirect(url_for("registrar_actividad"))

        filename = None
        if evidencia_base64:
            try:
                if "," in evidencia_base64:
                    evidencia_base64 = evidencia_base64.split(",")[1]
                image_data = base64.b64decode(evidencia_base64)
                filename = f"{uuid.uuid4().hex}.jpg"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                with open(filepath, "wb") as f:
                    f.write(image_data)
            except Exception as e:
                print("Error al guardar imagen:", e)
                flash(f"Error al guardar la imagen: {str(e)}", "danger")
                return redirect(url_for("registrar_actividad"))

        try:
            cursor = db.connection.cursor()
            cursor.execute(
                """
                INSERT INTO actividades (id_usuario, actividad, insumos, observaciones, evidencia, fecha)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """,
                (session["user_id"], actividad, insumos_str, observaciones, filename),
            )
            db.connection.commit()
            cursor.close()

            flash("Actividad registrada correctamente", "success")
            return render_template("registrar_actividad.html")

        except Exception as e:
            db.connection.rollback()
            print("Error al guardar en la BD:", e)
            import traceback

            traceback.print_exc()
            flash(f"Error al registrar actividad: {str(e)}", "danger")
            return render_template("registrar_actividad.html")

    return render_template("registrar_actividad.html")


@app.route("/ver_fotos")
@login_required
def ver_fotos():
    try:
        cursor = db.connection.cursor()

        query = """
            SELECT a.evidencia, a.fecha, u.fullname, a.actividad, a.insumos, a.observaciones
            FROM actividades a
            JOIN user u ON a.id_usuario = u.id
            WHERE u.id = %s AND a.evidencia IS NOT NULL AND a.evidencia != ''
        """
        cursor.execute(query, (session["user_id"],))
        rows = cursor.fetchall()

        fotos = []
        usuario = None

        for row in rows:
            if usuario is None:
                usuario = row[2]

            # Construir ruta de forma segura
            nombre_archivo = row[0] if row[0] else ""
            ruta_imagen = f"uploads/{nombre_archivo}" if nombre_archivo else None

            fotos.append(
                {
                    "ruta": (
                        url_for("static", filename=ruta_imagen) if ruta_imagen else None
                    ),
                    "fecha": row[1],
                    "usuario": row[2],
                    "actividad": row[3],
                    "insumos": row[4],
                    "observaciones": row[5],
                }
            )

        cursor.close()

        if usuario is None:
            cursor = db.connection.cursor()
            cursor.execute(
                "SELECT fullname FROM user WHERE id = %s", (session["user_id"],)
            )
            result = cursor.fetchone()
            usuario = result[0] if result else "Usuario desconocido"
            cursor.close()

        return render_template("ver_fotos.html", fotos=fotos, usuario=usuario)

    except Exception as e:
        # Manejo de errores
        print(f"Error en ver_fotos: {str(e)}")
        return render_template(
            "ver_fotos.html", fotos=[], usuario="Usuario", error=str(e)
        )


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
        cur.execute(
            """
            INSERT INTO ventas (cod_cultivo, fecha_venta, cantidad_bultos, precio, descripcion)
            VALUES (%s, %s, %s, %s, %s)
        """,
            (cod_cultivo, fecha, cantidad_bultos, precio, descripcion),
        )

        db.connection.commit()
        flash("Venta registrada con éxito", "success")
        return redirect(url_for("ventas_registradas"))

    return render_template("auth/registrar_ventas.html", cultivos=cultivos)


@app.route("/ventas_registradas")
def ventas_registradas():
    cur = db.connection.cursor()
    cur.execute(
        """
        SELECT v.id_venta, c.nombre AS cultivo, v.fecha_venta, 
               v.cantidad_bultos, v.precio, v.descripcion
        FROM ventas v
        JOIN cultivos c ON v.cod_cultivo = c.id_cultivo
        ORDER BY v.fecha_venta DESC
    """
    )
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

        cur.execute(
            """
            INSERT INTO siembra (fecha_siembra, detalle, cod_cultivos)
            VALUES (%s, %s, %s)
        """,
            (fecha, detalle, cod_cultivos),
        )
        db.connection.commit()
        flash("Registro exitoso", "success")
        return redirect(url_for("registrar_siembra"))
    return render_template("registrar_siembra.html", cultivos=cultivos)


# ---------------------- SIEMBRA REGISTRADA ----------------------
@app.route("/Siembra_registrada")
def siembra_registrada():
    cur = db.connection.cursor()
    cur.execute(
        """
        SELECT s.fecha_siembra, s.detalle, c.nombre AS cultivo_nombre
        FROM siembra s
        JOIN Cultivos c ON s.cod_cultivos = c.Id_cultivo
    """
    )
    registros = cur.fetchall()
    return render_template("siembra_registrada.html", registros=registros)


# ---------------------- SOLICITUD DE INSUMO ----------------------


@app.route("/solicitar_insumo", methods=["GET", "POST"])
@login_required
def solicitar_insumo():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        # 🔹 getlist() para campos con selección múltiple
        tipos_insumo = request.form.getlist("tipo_insumo")
        cantidad = request.form.get("cantidad")
        observaciones = request.form.get("observaciones")

        # 🔹 Convertir la lista a texto separado por comas
        tipo_insumo_str = ", ".join(tipos_insumo) if tipos_insumo else None

        try:
            cur = db.connection.cursor()
            cur.execute(
                """
                INSERT INTO solicitud_insumo (usuario_id, tipo_insumo, cantidad, observaciones, fecha_solicitud, estado)
                VALUES (%s, %s, %s, %s, NOW(), 'Pendiente')
            """,
                (session["user_id"], tipo_insumo_str, cantidad, observaciones),
            )

            db.connection.commit()
            cur.close()

            flash("Solicitud de insumo registrada con éxito", "success")
            return redirect(url_for("solicitar_insumo"))

        except Exception as e:
            db.connection.rollback()
            flash(f"Error al registrar la solicitud: {str(e)}", "danger")

    return render_template("solicitud_insumo.html")


# ---------------------- SOLICITUDES REALIZADAS ----------------------


@app.route("/mis_solicitudes")
@login_required
def mis_solicitudes():
    cur = db.connection.cursor()
    cur.execute(
        """
        SELECT tipo_insumo, cantidad, observaciones, estado, 
               observacion_supervisor, fecha_solicitud
        FROM solicitud_insumo 
        WHERE usuario_id = %s
        ORDER BY fecha_solicitud DESC
    """,
        (session["user_id"],),
    )

    mis_solicitudes = cur.fetchall()
    cur.close()

    return render_template("mis_solicitudes.html", solicitudes=mis_solicitudes)


@app.route("/ver_solicitudes", methods=["GET"])
@login_required
def ver_solicitudes():
    if "user_id" not in session:
        return redirect(url_for("login"))

    cur = db.connection.cursor()

    # Solicitudes pendientes
    cur.execute(
        """
        SELECT s.id, u.fullname, s.tipo_insumo, s.cantidad, s.observaciones, s.fecha_solicitud, s.estado
        FROM solicitud_insumo s
        JOIN user u ON s.usuario_id = u.id
        WHERE s.estado = 'Pendiente'
        ORDER BY s.fecha_solicitud DESC
    """
    )
    solicitudes_pendientes = cur.fetchall()

    # Solicitudes procesadas (aceptadas o rechazadas) - AGREGAR observacion_supervisor
    cur.execute(
        """
        SELECT s.id, u.fullname, s.tipo_insumo, s.cantidad, s.observaciones, s.fecha_solicitud, s.estado, s.observacion_supervisor
        FROM solicitud_insumo s
        JOIN user u ON s.usuario_id = u.id
        WHERE s.estado IN ('Aceptada', 'Rechazada')
        ORDER BY s.fecha_solicitud DESC
    """
    )
    solicitudes_procesadas = cur.fetchall()
    cur.close()

    return render_template(
        "ver_solicitudes.html",
        solicitudes_pendientes=solicitudes_pendientes,
        solicitudes_procesadas=solicitudes_procesadas,
    )


# ---------------------- ACTUALIZAR SOLICITUD CON OBSERVACIONES ----------------------
@app.route("/actualizar_solicitud/<int:id>/<string:accion>", methods=["POST"])
@login_required
def actualizar_solicitud(id, accion):
    """
    Actualiza el estado de la solicitud: 'Aceptada' o 'Rechazada' con observaciones del supervisor
    """
    observacion_supervisor = request.form.get("observacion_supervisor", "")
    nuevo_estado = None

    if accion == "aceptar":
        nuevo_estado = "Aceptada"
    elif accion == "rechazar":
        nuevo_estado = "Rechazada"

    if nuevo_estado:
        try:
            cur = db.connection.cursor()

            # Verificar si la columna observacion_supervisor existe, si no, agregarla
            try:
                cur.execute(
                    """
                    UPDATE solicitud_insumo
                    SET estado = %s, observacion_supervisor = %s
                    WHERE id = %s
                """,
                    (nuevo_estado, observacion_supervisor, id),
                )
            except Exception as columna_error:
                # Si la columna no existe, crearla y luego actualizar
                if "Unknown column" in str(columna_error):
                    cur.execute(
                        "ALTER TABLE solicitud_insumo ADD COLUMN observacion_supervisor TEXT"
                    )
                    cur.execute(
                        """
                        UPDATE solicitud_insumo
                        SET estado = %s, observacion_supervisor = %s
                        WHERE id = %s
                    """,
                        (nuevo_estado, observacion_supervisor, id),
                    )
                else:
                    raise columna_error

            db.connection.commit()
            cur.close()
            flash(f"Solicitud {nuevo_estado.lower()} correctamente", "success")

        except Exception as e:
            db.connection.rollback()
            flash(f"Error al actualizar la solicitud: {str(e)}", "danger")

    return redirect(url_for("ver_solicitudes"))


# ---------------------- EVIDENCIAS ----------------------


# Ruta para ver evidencias (MUCHO más simple)
@app.route("/ver_evidencias")
@login_required
def ver_evidencias():
    cursor = db.connection.cursor()

    # Consulta simple - todo en una tabla
    query = """
        SELECT a.id, a.evidencia, a.fecha, u.fullname, a.actividad, 
               a.insumos, a.observaciones, a.comentarios_admin,
               admin.fullname as admin_nombre, a.fecha_comentario
        FROM actividades a
        JOIN user u ON a.id_usuario = u.id
        LEFT JOIN user admin ON a.admin_comentario_id = admin.id
        ORDER BY a.fecha DESC
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    evidencias = []
    for row in rows:
        # Construir la ruta de la imagen de forma segura
        ruta_imagen = None
        if row[1]:  # Si hay evidencia (no es NULL)
            ruta_imagen = url_for("static", filename="uploads/" + row[1])

        evidencias.append(
            {
                "id": row[0],
                "ruta": ruta_imagen,
                "fecha": (
                    row[2].strftime("%d/%m/%Y %H:%M")
                    if row[2]
                    else "Fecha no disponible"
                ),
                "usuario": row[3],
                "actividad": row[4],
                "insumos": row[5],
                "observaciones": row[6],
                "comentario_admin": row[7],  # Comentario del administrador
                "admin_nombre": row[8],  # Quién comentó
                "fecha_comentario": (
                    row[9].strftime("%d/%m/%Y %H:%M") if row[9] else None
                ),
            }
        )

    cursor.close()
    return render_template("ver_evidencias.html", evidencias=evidencias)


# Ruta para agregar/comentar evidencia (MUCHO más simple)
@app.route("/comentar_evidencia/<int:actividad_id>", methods=["POST"])
@login_required
def comentar_evidencia(actividad_id):
    if request.method == "POST":
        comentario = request.form.get("comentario")

        if not comentario or not comentario.strip():
            flash("El comentario no puede estar vacío", "error")
            return redirect(url_for("ver_evidencias"))

        try:
            cursor = db.connection.cursor()

            # Actualizar directamente la actividad
            cursor.execute(
                """
                UPDATE actividades 
                SET comentarios_admin = %s, 
                    admin_comentario_id = %s,
                    fecha_comentario = NOW()
                WHERE id = %s
            """,
                (comentario.strip(), session["user_id"], actividad_id),
            )

            db.connection.commit()
            cursor.close()

            flash("Comentario agregado correctamente", "success")

        except Exception as e:
            db.connection.rollback()
            flash(f"Error al agregar comentario: {str(e)}", "danger")

    return redirect(url_for("ver_evidencias"))


# ---------------------- EN CONSTRUCCIÓN ----------------------


@app.route("/en_construccion")
def en_construccion():
    return "<h1>🚧 Esta sección está en construcción 🚧</h1>"


# ---------------------- SEGUIMIENTO DE CULTIVO ----------------------


@app.route("/seguimiento_cultivo", methods=["GET", "POST"])
@login_required
def seguimiento_cultivo():
    cur = db.connection.cursor()
    cur.execute("SELECT Id_cultivo, nombre FROM Cultivos WHERE estado = 'Habilitado'")
    cultivos = cur.fetchall()

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        cultivo_id = request.form.get("cultivo")

        # 🔹 getlist() para los campos múltiples
        tratamientos = request.form.getlist("tratamiento")
        problemas = request.form.getlist("problema")
        prioridades = request.form.getlist("prioridad")
        insumos = request.form.getlist("insumos")

        # 🔹 Convertir las listas a texto separado por comas
        tratamiento_str = ", ".join(tratamientos) if tratamientos else None
        problema_str = ", ".join(problemas) if problemas else None
        prioridad_str = ", ".join(prioridades) if prioridades else None
        insumo_str = ", ".join(insumos) if insumos else None

        try:
            # Obtener el nombre del cultivo
            cur.execute(
                "SELECT nombre FROM Cultivos WHERE Id_cultivo = %s", (cultivo_id,)
            )
            cultivo_nombre = cur.fetchone()

            if cultivo_nombre:
                cultivo_nombre = cultivo_nombre[0]

                # Insertar en la tabla tratamientos
                cur.execute(
                    """
                    INSERT INTO tratamientos (cultivo, tratamiento, problema, prioridad, insumos, fecha_registro)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                """,
                    (
                        cultivo_nombre,
                        tratamiento_str,
                        problema_str,
                        prioridad_str,
                        insumo_str,
                    ),
                )

                db.connection.commit()
                flash("Seguimiento registrado con éxito", "success")
                return redirect(url_for("seguimiento_cultivo"))
            else:
                flash("El cultivo seleccionado no existe.", "danger")

        except Exception as e:
            db.connection.rollback()
            flash(f"Error al registrar el seguimiento: {str(e)}", "danger")

    cur.close()
    return render_template("auth/seguimiento_cultivo.html", cultivos=cultivos)


# ---------------------- TRATAMIENTOS REGISTRADOS ----------------------


@app.route("/tratamientos_registrados")
@login_required
def tratamientos_registrados():
    try:
        cur = db.connection.cursor()
        cur.execute(
            """
            SELECT id_tratamiento, cultivo, tratamiento, problema, prioridad, insumos, fecha_registro
            FROM tratamientos
            ORDER BY fecha_registro DESC
        """
        )
        tratamientos = cur.fetchall()
        cur.close()
        return render_template(
            "auth/tratamientos_registrados.html", tratamientos=tratamientos
        )

    except Exception as e:
        flash(f"Error al cargar los tratamientos: {str(e)}", "danger")
        return redirect(url_for("home"))
    

@app.route('/guardar_comentarios', methods=['POST'])
@login_required
def guardar_comentarios():
    if current_user.rol != 'administrador':
        flash('No tienes permiso para realizar esta acción', 'error')
        return redirect(url_for('tratamientos'))

    # Por ejemplo, si tienes los tratamientos en DB con id, y campo comentario:
    for key, value in request.form.items():
        if key.startswith('comentario_'):
            id_tratamiento = int(key.split('_')[1])
            comentario = value
            # Guardar comentario en DB, ejemplo:
            tratamiento = tratamiento.query.get(id_tratamiento)
            if tratamiento:
                tratamiento.comentario = comentario
                db.session.commit()

    flash('Comentarios guardados correctamente', 'success')
    return redirect(url_for('tratamientos'))



# ---------------------- ELIMINAR TRATAMIENTO ----------------------


@app.route("/eliminar_tratamiento/<int:id>", methods=["GET"])
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

    return redirect(url_for("tratamientos_registrados"))


# ---------------------- MAIN ----------------------
@app.route("/registrar_problema", methods=["GET", "POST"])
@login_required
def registrar_problema():
    tipos = ["Plaga", "Enfermedad", "Deficiencia nutricional", "Estrés hídrico", "Otro"]

    if request.method == "POST":
        tipo = request.form["tipo"]
        descripcion = request.form["descripcion"]
        evidencia_base64 = request.form["evidencia"]

        print("DEBUG - Datos recibidos:")
        print("Tipo:", tipo)
        print("Descripción:", descripcion)
        print("Evidencia:", len(evidencia_base64) if evidencia_base64 else "No llegó")

        filename = None

        if evidencia_base64:
            try:
                if "," in evidencia_base64:
                    evidencia_base64 = evidencia_base64.split(",")[1]

                image_data = base64.b64decode(evidencia_base64)
                filename = f"{uuid.uuid4().hex}.jpg"
                filepath = os.path.join(UPLOAD_FOLDER, filename)

                with open(filepath, "wb") as f:
                    f.write(image_data)

            except Exception as e:
                print("Error al guardar imagen:", e)
                flash(f"Error al guardar la imagen: {str(e)}", "danger")
                return redirect(url_for("registrar_problema"))

        try:
            cursor = db.connection.cursor()
            cursor.execute(
                """
                INSERT INTO problemas_cultivo (id_usuario, tipo_problema, descripcion, evidencia, fecha_registro)
                VALUES (%s, %s, %s, %s, NOW())
            """,
                (session["user_id"], tipo, descripcion, filename),
            )
            db.connection.commit()
            cursor.close()

            flash("Problema registrado correctamente", "success")
            return redirect(url_for("ver_problemas"))

        except Exception as e:
            db.connection.rollback()
            print("Error al guardar en la BD:", e)
            import traceback

            traceback.print_exc()
            flash(f"Error al registrar problema: {str(e)}", "danger")

    return render_template("/registrar_problema.html", tipos=tipos)


# ---------------------- PROBLEMAS REGISTRADOS ----------------------
@app.route("/problemas_registrados")
@login_required
def problemas_registrados():
    cursor = db.connection.cursor()
    query = """
        SELECT p.evidencia, p.fecha_registro, u.fullname, p.tipo_problema, p.descripcion
        FROM problemas_cultivo p
        JOIN user u ON p.id_usuario = u.id
        WHERE u.id = %s
    """
    cursor.execute(query, (session["user_id"],))
    resultados = cursor.fetchall()

    problemas = []
    for row in resultados:
        ruta = url_for("static", filename="uploads/" + row[0]) if row[0] else None
        problemas.append(
            {
                "ruta": ruta,
                "fecha": row[1],
                "usuario": row[2],
                "tipo": row[3],
                "descripcion": row[4],
            }
        )

    usuario = problemas[0]["usuario"] if problemas else "Sin registros"
    cursor.close()

    return render_template(
        "problemas_registrados.html", problemas=problemas, usuario=usuario
    )


@app.route("/produccion_registrada")
@login_required
def produccion_registrada():
    try:
        cur = db.connection.cursor()
        cur.execute(
            """
            SELECT p.fecha, p.cantidad_bultos, c.nombre as cultivo, u.fullname as registrado_por
            FROM produccion p
            JOIN cultivos c ON p.id_cultivo = c.id_cultivo
            JOIN user u ON p.id_usuario = u.id
            WHERE u.id = %s
            ORDER BY p.fecha DESC
        """,
            (session["user_id"],),
        )

        registros = cur.fetchall()  # Sin conversión a diccionarios
        cur.close()

        return render_template("produccion_registrada.html", registros=registros)

    except Exception as e:
        flash(f"Error al cargar la producción: {str(e)}", "danger")
        return redirect(url_for("home"))


@app.route("/registrar_produccion", methods=["GET", "POST"])
@login_required
def registrar_produccion():
    cursor = db.connection.cursor()
    cursor.execute(
        "SELECT Id_cultivo, nombre FROM Cultivos WHERE estado = 'Habilitado'"
    )
    cultivos = cursor.fetchall()

    if request.method == "POST":
        id_cultivo = request.form["cultivo"]
        fecha = request.form["fecha"]
        cantidad = request.form["cantidad"]

        try:
            cursor.execute(
                """
                INSERT INTO produccion (id_usuario, id_cultivo, fecha, cantidad_bultos)
                VALUES (%s, %s, %s, %s)
            """,
                (session["user_id"], id_cultivo, fecha, cantidad),
            )
            db.connection.commit()
            flash("Producción registrada correctamente", "success")
            return redirect(url_for("produccion_registrada"))
        except Exception as e:
            db.connection.rollback()
            flash(f"Error al registrar producción: {str(e)}", "danger")

    return render_template("registrar_produccion.html", cultivos=cultivos)


# ---------------------- MAIN ----------------------
if __name__ == "__main__":
    app.config.from_object(config["development"])
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run()
