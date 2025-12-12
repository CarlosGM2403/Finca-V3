# ---------------------- LIBRERÍAS FLASK ----------------------
from sqlite3 import Cursor
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_mail import Mail, Message
from flask_login import current_user
from functools import wraps
from datetime import datetime, timedelta
import os
import base64
import uuid




# ---------------------- UTILIDADES ----------------------
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash
import os

from datetime import datetime
# ---------------------- IMPORTACIONES ADICIONALES ----------------------
from datetime import timedelta
from io import BytesIO
from flask import send_file
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ ReportLab no está instalado. Instala con: pip install reportlab")

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

# ---------------------- FUNCIONES DE NOTIFICACIÓN ----------------------

def crear_notificacion_admin(tipo, usuario_id, mensaje, referencia_id, cultivo_id):
    """
    Crea una notificación para todos los administradores
    """
    try:
        cur = db.connection.cursor()
        
        # Insertar notificación general para administradores
        cur.execute("""
            INSERT INTO notificaciones_generales 
            (tipo, usuario_id, mensaje, referencia_id, cultivo_id, fecha_creacion, leida)
            VALUES (%s, %s, %s, %s, %s, NOW(), 0)
        """, (tipo, usuario_id, mensaje, referencia_id, cultivo_id))
        
        db.connection.commit()
        cur.close()
        return True
        
    except Exception as e:
        print(f"Error al crear notificación admin: {str(e)}")
        db.connection.rollback()
        return False


def crear_notificacion_insumo(solicitud_id, usuario_id, tipo_insumo, cantidad, mensaje, tipo_notificacion):
    """
    Crea una notificación personal para un usuario específico
    """
    try:
        cur = db.connection.cursor()
        
        # Insertar notificación personal
        cur.execute("""
            INSERT INTO notificaciones 
            (usuario_id, solicitud_id, tipo_insumo, cantidad, mensaje, tipo, fecha_creacion, leida)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), 0)
        """, (usuario_id, solicitud_id, tipo_insumo, cantidad, mensaje, tipo_notificacion))
        
        db.connection.commit()
        cur.close()
        return True
        
    except Exception as e:
        print(f"Error al crear notificación de insumo: {str(e)}")
        db.connection.rollback()
        return False
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

        try:
            cur = db.connection.cursor()

            # Consulta con campos de seguridad - AGREGAR CAMPO 'estado'
            cur.execute(
                """
                SELECT id, password, must_change_password, rol, fullname, 
                       intentos_login, bloqueado_hasta, bloqueos_permanentes, estado
                FROM user WHERE username=%s
            """,
                (username,),
            )
            row = cur.fetchone()

            if not row:
                flash("Usuario o contraseña incorrectos", "error")
                return redirect(url_for("login"))

            (
                user_id,
                hashed_password,
                must_change_password,
                rol,
                fullname,
                intentos_login,
                bloqueado_hasta,
                bloqueos_permanentes,
                estado,
            ) = row

            # VERIFICAR ESTADO DEL USUARIO - NUEVA VALIDACIÓN
            if estado.lower() != "habilitado":
                flash("Usuario inhabilitado. Contacta al administrador.", "error")
                cur.close()
                return render_template("auth/login.html")

            # CONFIGURACIÓN DE SEGURIDAD
            MAX_INTENTOS = 3
            TIEMPO_BLOQUEO = 15  # minutos
            BLOQUEO_PERMANENTE_AFTER = 5

            # Verificar bloqueo permanente
            if (
                bloqueos_permanentes
                and bloqueos_permanentes >= BLOQUEO_PERMANENTE_AFTER
            ):
                flash(
                    "Cuenta bloqueada permanentemente. Contacta al administrador.",
                    "error",
                )
                cur.close()
                return render_template("auth/login.html")

            # Verificar bloqueo temporal
            if bloqueado_hasta and bloqueado_hasta > datetime.now():
                tiempo_restante = bloqueado_hasta - datetime.now()
                minutos_restantes = max(1, int(tiempo_restante.total_seconds() / 60))
                flash(
                    f"Cuenta bloqueada temporalmente. Intenta en {minutos_restantes} minutos",
                    "error",
                )
                cur.close()
                return render_template("auth/login.html")

            # Verificar contraseña
            if check_password_hash(hashed_password, password):
                # LOGIN EXITOSO - Resetear contadores de seguridad
                cur.execute(
                    """
                    UPDATE user 
                    SET intentos_login = 0, bloqueado_hasta = NULL
                    WHERE id = %s
                """,
                    (user_id,),
                )
                db.connection.commit()

                # Iniciar sesión
                user = ModelUser.get_by_id(db, user_id)
                login_user(user)
                session["user_id"] = user_id
                session["rol"] = rol
                session["fullname"] = fullname

                # REGISTRO DEL INICIO DE SESIÓN
                try:
                    ip = request.remote_addr
                    navegador = request.user_agent.string
                    cur.execute(
                        """
                        INSERT INTO registro_sesiones (id_usuario, direccion_ip, navegador, exito)
                        VALUES (%s, %s, %s, 1)
                    """,
                        (user_id, ip, navegador),
                    )
                    db.connection.commit()
                except Exception as e:
                    print(f"Error al registrar inicio de sesión: {e}")

                cur.close()

                if must_change_password == 1:
                    return redirect(url_for("cambiar_password"))

                next_page = request.args.get("next")
                flash(f"¡Bienvenido, {fullname}!", "success")
                return redirect(next_page or url_for("home"))

            else:
                # CONTRASEÑA INCORRECTA - Manejar intentos
                nuevos_intentos = (intentos_login or 0) + 1

                # Registrar intento fallido
                try:
                    ip = request.remote_addr
                    navegador = request.user_agent.string
                    cur.execute(
                        """
                        INSERT INTO registro_sesiones (id_usuario, direccion_ip, navegador, exito)
                        VALUES (%s, %s, %s, 0)
                    """,
                        (user_id, ip, navegador),
                    )
                except Exception as e:
                    print(f"Error al registrar intento fallido: {e}")

                if nuevos_intentos >= MAX_INTENTOS:
                    # BLOQUEAR CUENTA
                    bloqueado_hasta = datetime.now() + timedelta(minutes=TIEMPO_BLOQUEO)
                    nuevos_bloqueos = (bloqueos_permanentes or 0) + 1

                    cur.execute(
                        """
                        UPDATE user 
                        SET intentos_login = %s, bloqueado_hasta = %s,
                            bloqueos_permanentes = %s
                        WHERE id = %s
                    """,
                        (nuevos_intentos, bloqueado_hasta, nuevos_bloqueos, user_id),
                    )

                    db.connection.commit()
                    cur.close()

                    flash(
                        f"Demasiados intentos fallidos. Cuenta bloqueada por {TIEMPO_BLOQUEO} minutos",
                        "error",
                    )
                else:
                    # INCREMENTAR INTENTOS
                    cur.execute(
                        """
                        UPDATE user 
                        SET intentos_login = %s 
                        WHERE id = %s
                    """,
                        (nuevos_intentos, user_id),
                    )

                    db.connection.commit()
                    cur.close()

                    intentos_restantes = MAX_INTENTOS - nuevos_intentos
                    flash(
                        f"Contraseña incorrecta. Te quedan {intentos_restantes} intentos",
                        "error",
                    )

                return redirect(url_for("login"))

        except Exception as e:
            flash(f"Error en el sistema: {str(e)}", "error")
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




def obtener_notificaciones_unificadas(usuario_id, rol, cur):
    """
    Obtiene todas las notificaciones según el rol del usuario
    """
    notificaciones = []
    
    # Si es administrador, obtener notificaciones generales
    if rol == "administrador":
        cur.execute("""
            SELECT id, tipo, mensaje, leida, fecha_creacion, referencia_id
            FROM notificaciones_generales
            ORDER BY fecha_creacion DESC
        """)
        generales = cur.fetchall()
        
        for row in generales:
            notificaciones.append({
                "id": row[0],
                "tipo_notif": "general",
                "tipo": row[1],
                "mensaje": row[2],
                "leida": row[3],
                "fecha": row[4],
                "referencia_id": row[5]
            })
        
        print(f"✓ Admin tiene {len(generales)} notificaciones generales")  # Debug
    
    # Notificaciones personales (todos los usuarios)
    cur.execute("""
        SELECT id, tipo, mensaje, leida, fecha_creacion, solicitud_id
        FROM notificaciones
        WHERE usuario_id = %s
        ORDER BY fecha_creacion DESC
    """, (usuario_id,))
    personales = cur.fetchall()
    
    for row in personales:
        notificaciones.append({
            "id": row[0],
            "tipo_notif": "personal",
            "tipo": row[1],
            "mensaje": row[2],
            "leida": row[3],
            "fecha": row[4],
            "solicitud_id": row[5]
        })
    
    print(f"✓ Usuario {usuario_id} tiene {len(personales)} notificaciones personales")  # Debug
    
    return notificaciones


def contar_notificaciones_unificadas(usuario_id, rol, cur):
    """
    Cuenta el total de notificaciones no leídas
    """
    total = 0

    # Contar generales si es administrador
    if rol == "administrador":
        cur.execute("SELECT COUNT(*) FROM notificaciones_generales WHERE leida = 0")
        total += cur.fetchone()[0]

    # Contar personales
    cur.execute("SELECT COUNT(*) FROM notificaciones WHERE usuario_id = %s AND leida = 0", (usuario_id,))
    total += cur.fetchone()[0]

    return total

# ---------------------- HOME ----------------------
@app.route("/home")
@login_required
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    cur = db.connection.cursor()
    
    # Obtener el rol del usuario
    cur.execute("SELECT rol FROM user WHERE id = %s", (session["user_id"],))
    user = cur.fetchone()
    rol = user[0] if user else None
    
    # Obtener foto de perfil
    cur.execute("SELECT foto_perfil FROM user WHERE id = %s", (session["user_id"],))
    foto = cur.fetchone()
    foto_perfil_url = (
        url_for("static", filename="uploads/" + foto[0])
        if foto and foto[0]
        else url_for("static", filename="img/default_profile.png")
    )
    
    cur.close()
    
    return render_template("home.html", rol=rol, foto_perfil_url=foto_perfil_url)

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
            msg.body = f"Para restablecer tu contraseña haz clic en el siguiente enlace:\n{link}\n Recuerda que tu contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula, un número y un símbolo"
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

                Recuerda que deberás cambiar la contraseña en tu primer acceso y esta debe tener al menos 8 caracteres, una mayúscula, una minúscula, un número y un símbolo.

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
            return redirect(url_for("home"))

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

# ---------------------- iNVENTARIO ----------------------

@app.route("/inventario")
@login_required
def inventario():
    # Verificar que sea administrador
    if session.get('rol') != 'administrador':
        flash('No tienes permisos para ver el inventario', 'danger')
        return redirect(url_for('home'))
    
    try:
        cur = db.connection.cursor()
        cur.execute("""
            SELECT 
                c.id_cultivo,
                c.nombre as cultivo,
                c.tipo,
                COALESCE(i.total_producido, 0) as total_producido,
                COALESCE(i.total_vendido, 0) as total_vendido,
                COALESCE(i.stock_actual, 0) as stock_actual,
                i.ultima_produccion,
                i.ultima_venta
            FROM cultivos c
            LEFT JOIN inventario i ON c.id_cultivo = i.id_cultivo
            WHERE c.estado = 'Habilitado'
            ORDER BY c.nombre ASC
        """)
        
        resultados = cur.fetchall()
        cur.close()
        
        # Formatear las fechas en Python
        inventario_data = []
        for row in resultados:
            # Formatear ultima_produccion
            ultima_prod = row[6].strftime('%d/%m/%Y') if row[6] else 'Sin registro'
            # Formatear ultima_venta
            ultima_venta = row[7].strftime('%d/%m/%Y') if row[7] else 'Sin registro'
            
            # Crear nueva tupla con fechas formateadas
            inventario_data.append((
                row[0],  # id_cultivo
                row[1],  # nombre
                row[2],  # tipo
                row[3],  # total_producido
                row[4],  # total_vendido
                row[5],  # stock_actual
                ultima_prod,  # ultima_produccion formateada
                ultima_venta  # ultima_venta formateada
            ))
        
        return render_template("auth/inventario.html", inventario=inventario_data)
        
    except Exception as e:
        flash(f"Error al cargar el inventario: {str(e)}", "danger")
        return redirect(url_for("home"))

@app.route("/detalle_inventario/<int:id_cultivo>")
@login_required
def detalle_inventario(id_cultivo):
    # Verificar que sea administrador
    if session.get('rol') != 'administrador':
        return jsonify({'success': False, 'error': 'No tienes permisos'}), 403
    
    try:
        cur = db.connection.cursor()
        
        # Obtener historial de producción
        cur.execute("""
            SELECT 
                DATE_FORMAT(p.fecha, '%%d/%%m/%%Y') as fecha,
                p.cantidad_bultos,
                u.fullname as registrado_por
            FROM produccion p
            JOIN user u ON p.id_usuario = u.id
            WHERE p.id_cultivo = %s
            ORDER BY p.fecha DESC
            LIMIT 10
        """, (id_cultivo,))
        producciones = cur.fetchall()
        
        # Obtener historial de ventas
        cur.execute("""
            SELECT 
                DATE_FORMAT(v.fecha_venta, '%%d/%%m/%%Y') as fecha,
                v.cantidad_bultos,
                v.precio,
                v.descripcion
            FROM ventas v
            WHERE v.cod_cultivo = %s
            ORDER BY v.fecha_venta DESC
            LIMIT 10
        """, (id_cultivo,))
        ventas = cur.fetchall()
        
        cur.close()
        
        # Convertir a listas de diccionarios
        producciones_list = [
            {'fecha': p[0], 'cantidad': p[1], 'registrado_por': p[2]}
            for p in producciones
        ]
        
        ventas_list = [
            {'fecha': v[0], 'cantidad': v[1], 'precio': float(v[2]), 'descripcion': v[3]}
            for v in ventas
        ]
        
        return jsonify({
            'success': True,
            'producciones': producciones_list,
            'ventas': ventas_list
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def actualizar_inventario(id_cultivo):
    """
    Actualiza el inventario de un cultivo específico
    calculando totales desde las tablas produccion y ventas
    """
    try:
        cur = db.connection.cursor()
        
        # Calcular total producido
        cur.execute("""
            SELECT COALESCE(SUM(cantidad_bultos), 0) 
            FROM produccion 
            WHERE id_cultivo = %s
        """, (id_cultivo,))
        total_producido = int(cur.fetchone()[0])
        
        # Calcular total vendido
        cur.execute("""
            SELECT COALESCE(SUM(cantidad_bultos), 0) 
            FROM ventas 
            WHERE cod_cultivo = %s
        """, (id_cultivo,))
        total_vendido = int(cur.fetchone()[0])
        
        # Calcular stock actual (RESTA, no suma)
        stock_actual = total_producido - total_vendido
        
        # Obtener última fecha de producción
        cur.execute("""
            SELECT MAX(fecha) 
            FROM produccion 
            WHERE id_cultivo = %s
        """, (id_cultivo,))
        ultima_produccion = cur.fetchone()[0]
        
        # Obtener última fecha de venta
        cur.execute("""
            SELECT MAX(fecha_venta) 
            FROM ventas 
            WHERE cod_cultivo = %s
        """, (id_cultivo,))
        ultima_venta = cur.fetchone()[0]
        
        # Verificar si ya existe registro en inventario
        cur.execute("SELECT id_inventario FROM inventario WHERE id_cultivo = %s", (id_cultivo,))
        existe = cur.fetchone()
        
        if existe:
            # Actualizar registro existente
            cur.execute("""
                UPDATE inventario 
                SET total_producido = %s,
                    total_vendido = %s,
                    stock_actual = %s,
                    ultima_produccion = %s,
                    ultima_venta = %s
                WHERE id_cultivo = %s
            """, (total_producido, total_vendido, stock_actual, 
                  ultima_produccion, ultima_venta, id_cultivo))
            
            print(f"✓ INVENTARIO ACTUALIZADO")
        else:
            # Insertar nuevo registro
            cur.execute("""
                INSERT INTO inventario 
                (id_cultivo, total_producido, total_vendido, stock_actual, 
                 ultima_produccion, ultima_venta)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_cultivo, total_producido, total_vendido, stock_actual,
                  ultima_produccion, ultima_venta))
            
            print(f"✓ INVENTARIO CREADO")
        
        db.connection.commit()
        
        # IMPRIMIR VALORES (estos son los prints de los que hablaba)
        print(f"=====================================")
        print(f"CULTIVO ID: {id_cultivo}")
        print(f"Total Producido: {total_producido}")
        print(f"Total Vendido: {total_vendido}")
        print(f"Stock Actual: {stock_actual} (debe ser {total_producido} - {total_vendido})")
        print(f"=====================================")
        
        cur.close()
        return True
        
    except Exception as e:
        db.connection.rollback()
        print(f"✗ ERROR al actualizar inventario: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
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

        flash("Cultivo registrado con éxito.", "success")
        return redirect(url_for("registrar_cultivo"))

    return render_template("auth/registrar_cultivo.html")


# ---------------------- ACTIVIDADES + EVIDENCIAS ----------------------


@app.route("/registrar_actividad", methods=["GET", "POST"])
@login_required
def registrar_actividad():
    if request.method == "POST":
        actividad = request.form.get("actividad")
        insumos_lista = request.form.getlist("insumos")
        insumos_str = ", ".join(insumos_lista) if insumos_lista else None
        observaciones = request.form.get("observaciones")
        evidencia_base64 = request.form.get("evidencia")

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
                flash(f"Error al guardar la imagen: {str(e)}", "danger")
                return redirect(url_for("registrar_actividad"))

        try:
            cursor = db.connection.cursor()
            
            # Insertar actividad
            cursor.execute("""
                INSERT INTO actividades (id_usuario, actividad, insumos, observaciones, evidencia, fecha)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (session["user_id"], actividad, insumos_str, observaciones, filename))
            
            actividad_id = cursor.lastrowid
            
            # Obtener nombre del usuario
            cursor.execute("SELECT fullname FROM user WHERE id = %s", (session["user_id"],))
            usuario_info = cursor.fetchone()
            usuario_nombre = usuario_info[0] if usuario_info else "Usuario"
            
            db.connection.commit()
            
            # 🔔 NOTIFICACIÓN PARA ADMINISTRADORES
            mensaje = f"{usuario_nombre} registró una actividad: {actividad}"
            crear_notificacion_admin(
                'nueva_actividad',
                session["user_id"],
                mensaje,
                actividad_id,
                None
            )
            
            cursor.close()
            flash("Actividad registrada correctamente", "success")
            return render_template("registrar_actividad.html")

        except Exception as e:
            db.connection.rollback()
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
@login_required
def registrar_ventas():
    if session.get('rol') != 'administrador':
        flash('No tienes permisos para registrar ventas', 'danger')
        return redirect(url_for('home'))
    
    cur = db.connection.cursor()
    cur.execute("""
        SELECT c.id_cultivo, c.nombre, 
               COALESCE(i.stock_actual, 0) as stock_disponible
        FROM cultivos c
        LEFT JOIN inventario i ON c.id_cultivo = i.id_cultivo
        WHERE c.estado = 'Habilitado'
        ORDER BY c.nombre
    """)
    cultivos = cur.fetchall()

    if request.method == "POST":
        cod_cultivo = request.form["cultivo"]
        fecha = request.form["fecha"]
        cantidad_bultos = int(request.form["cantidad_bultos"])
        precio = request.form["precio"]
        descripcion = request.form["descripcion"]

        cur.execute("""
            SELECT COALESCE(stock_actual, 0) as stock
            FROM inventario
            WHERE id_cultivo = %s
        """, (cod_cultivo,))
        
        resultado_stock = cur.fetchone()
        stock_disponible = resultado_stock[0] if resultado_stock else 0
        
        if cantidad_bultos > stock_disponible:
            flash(f'No hay suficientes unidades en stock. Disponibles: {stock_disponible} bultos', 'danger')
            return render_template("auth/registrar_ventas.html", cultivos=cultivos)
        
        if stock_disponible == 0:
            flash('No hay unidades disponibles en el stock para este cultivo', 'danger')
            return render_template("auth/registrar_ventas.html", cultivos=cultivos)

        try:
            # Obtener nombre del cultivo
            cur.execute("SELECT nombre FROM cultivos WHERE id_cultivo = %s", (cod_cultivo,))
            cultivo_info = cur.fetchone()
            cultivo_nombre = cultivo_info[0] if cultivo_info else "Cultivo"
            
            # Obtener nombre del usuario
            cur.execute("SELECT fullname FROM user WHERE id = %s", (session["user_id"],))
            usuario_info = cur.fetchone()
            usuario_nombre = usuario_info[0] if usuario_info else "Administrador"
            
            # Insertar venta
            cur.execute("""
                INSERT INTO ventas (cod_cultivo, fecha_venta, cantidad_bultos, precio, descripcion)
                VALUES (%s, %s, %s, %s, %s)
            """, (cod_cultivo, fecha, cantidad_bultos, precio, descripcion))
            
            venta_id = cur.lastrowid
            db.connection.commit()
            
            # Actualizar inventario
            actualizar_inventario(cod_cultivo)
            
            # 🔔 NOTIFICACIÓN PARA ADMINISTRADORES
            mensaje = f"{usuario_nombre} registró venta de {cultivo_nombre}: {cantidad_bultos} bultos por ${precio}"
            crear_notificacion_admin(
                'nueva_venta',
                session["user_id"],
                mensaje,
                venta_id,
                None
            )
            
            flash("Venta registrada e inventario actualizado con éxito", "success")
            return redirect(url_for("ventas_registradas"))
            
        except Exception as e:
            db.connection.rollback()
            flash(f"Error al registrar venta: {str(e)}", "danger")

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
@login_required
def eliminar_venta(id):
    # Verificar que sea administrador
    if session.get('rol') != 'administrador':
        flash('No tienes permisos para eliminar ventas', 'danger')
        return redirect(url_for('home'))
    
    cur = db.connection.cursor()
    
    # Obtener el id_cultivo antes de eliminar
    cur.execute("SELECT cod_cultivo FROM ventas WHERE id_venta = %s", (id,))
    resultado = cur.fetchone()
    
    if resultado:
        cod_cultivo = resultado[0]
        
        # Eliminar la venta
        cur.execute("DELETE FROM ventas WHERE id_venta = %s", (id,))
        db.connection.commit()
        
        # Actualizar inventario
        actualizar_inventario(cod_cultivo)
        
        flash("Venta eliminada e inventario actualizado", "success")
    else:
        flash("Venta no encontrada", "danger")
    
    cur.close()
    return redirect(url_for("ventas_registradas"))


# ---------------------- REGISTRAR SIEMBRA ----------------------
@app.route("/Registrar_siembra", methods=["GET", "POST"])
@login_required
def registrar_siembra():
    cur = db.connection.cursor()
    cur.execute("SELECT Id_cultivo, nombre FROM Cultivos WHERE estado = 'Habilitado'")
    cultivos = cur.fetchall()

    if request.method == "POST":
        try:
            # Obtener datos del formulario
            fecha = request.form["fecha"]
            detalle = request.form["detalle"]
            cod_cultivos = request.form["cultivo"]
            
            # Obtener nombre del cultivo
            cur.execute("SELECT nombre FROM Cultivos WHERE Id_cultivo = %s", (cod_cultivos,))
            cultivo_info = cur.fetchone()
            cultivo_nombre = cultivo_info[0] if cultivo_info else "Cultivo"
            
            # Obtener nombre del usuario
            cur.execute("SELECT fullname FROM user WHERE id = %s", (session["user_id"],))
            usuario_info = cur.fetchone()
            usuario_nombre = usuario_info[0] if usuario_info else "Usuario"
            
            # Insertar siembra
            cur.execute(
                """
                INSERT INTO siembra (fecha_siembra, detalle, cod_cultivos)
                VALUES (%s, %s, %s)
            """,
                (fecha, detalle, cod_cultivos),
            )
            
            siembra_id = cur.lastrowid
            db.connection.commit()
            
            # 🔔 NOTIFICACIÓN PARA ADMINISTRADORES
            mensaje = f"{usuario_nombre} registró una siembra de {cultivo_nombre} - Fecha: {fecha}"
            crear_notificacion_admin(
                'nueva_siembra',
                session["user_id"],
                mensaje,
                siembra_id,
                cod_cultivos
            )
            
            flash("Registro exitoso", "success")
            
        except Exception as e:
            db.connection.rollback()
            flash(f"Error al registrar siembra: {str(e)}", "danger")
        finally:
            cur.close()
            
        return redirect(url_for("registrar_siembra"))
    
    cur.close()
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
        try:
            insumos_values = request.form.getlist("insumo_value[]")
            insumos_nombres = request.form.getlist("insumo_nombre[]")
            
            if not insumos_values:
                flash("Debes agregar al menos un insumo para hacer la solicitud", "error")
                return redirect(url_for("solicitar_insumo"))
            
            cur = db.connection.cursor()
            
            # Obtener nombre del usuario
            cur.execute("SELECT fullname FROM user WHERE id = %s", (session["user_id"],))
            usuario_info = cur.fetchone()
            usuario_nombre = usuario_info[0] if usuario_info else "Usuario"
            
            for i, insumo_value in enumerate(insumos_values):
                cantidad = request.form.get(f"cantidad_{insumo_value}")
                unidad = request.form.get(f"unidad_{insumo_value}")
                observaciones = request.form.get(f"observaciones_{insumo_value}")
                insumo_nombre = insumos_nombres[i]
                
                if not cantidad or not unidad:
                    flash(f"El insumo {insumo_nombre} requiere cantidad y unidad", "error")
                    continue
                
                tipo_insumo_completo = f"{insumo_nombre}"
                cantidad_completa = f"{cantidad} {unidad}"
                obs_final = observaciones if observaciones and observaciones.strip() else "Sin observaciones"
                
                # Insertar solicitud
                cur.execute("""
                    INSERT INTO solicitud_insumo (usuario_id, tipo_insumo, cantidad, observaciones, fecha_solicitud, estado)
                    VALUES (%s, %s, %s, %s, NOW(), 'Pendiente')
                """, (session["user_id"], tipo_insumo_completo, cantidad_completa, obs_final))
                
                solicitud_id = cur.lastrowid
                
                # 🔔 NOTIFICACIÓN PARA EL EMPLEADO
                mensaje_empleado = f"Tu solicitud de {tipo_insumo_completo} ({cantidad_completa}) ha sido enviada y está pendiente de revisión."
                crear_notificacion_insumo(
                    solicitud_id, 
                    session["user_id"], 
                    tipo_insumo_completo, 
                    cantidad_completa, 
                    mensaje_empleado, 
                    'pendiente'
                )
                
                # 🔔 NOTIFICACIÓN PARA ADMINISTRADORES
                mensaje_admin = f"{usuario_nombre} solicitó {tipo_insumo_completo} ({cantidad_completa})"
                crear_notificacion_admin(
                    'solicitud_insumo',
                    session["user_id"],
                    mensaje_admin,
                    solicitud_id,
                    None
                )
            
            db.connection.commit()
            cur.close()
            
            flash("Solicitud de insumos registrada con éxito", "success")
            return redirect(url_for("solicitar_insumo"))
            
        except Exception as e:
            db.connection.rollback()
            flash(f"Error al registrar la solicitud: {str(e)}", "error")
            return redirect(url_for("solicitar_insumo"))

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

    # Solo solicitudes pendientes
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
    cur.close()

    return render_template(
        "ver_solicitudes.html",
        solicitudes_pendientes=solicitudes_pendientes
    )

# ---------------------- ACTUALIZAR SOLICITUD CON OBSERVACIONES ----------------------
@app.route("/actualizar_solicitud/<int:id>/<string:accion>", methods=["POST"])
@login_required
def actualizar_solicitud(id, accion):
    observacion_supervisor = request.form.get("observacion_supervisor", "")
    nuevo_estado = "Aceptada" if accion == "aceptar" else "Rechazada"

    if nuevo_estado:
        try:
            cur = db.connection.cursor()
            
            # Actualizar estado
            cur.execute("""
                UPDATE solicitud_insumo
                SET estado = %s, observacion_supervisor = %s
                WHERE id = %s
            """, (nuevo_estado, observacion_supervisor, id))

            # Obtener información de la solicitud
            cur.execute("""
                SELECT usuario_id, tipo_insumo, cantidad
                FROM solicitud_insumo
                WHERE id = %s
            """, (id,))
            solicitud_info = cur.fetchone()

            if solicitud_info:
                usuario_id, tipo_insumo, cantidad = solicitud_info

                # Crear mensaje de notificación para el empleado
                if nuevo_estado == "Aceptada":
                    mensaje = f"Tu solicitud de {tipo_insumo} (Cantidad: {cantidad}) ha sido ACEPTADA."
                    if observacion_supervisor:
                        mensaje += f" Observaciones: {observacion_supervisor}"
                    tipo_notif = "aceptada"
                else:
                    mensaje = f"Tu solicitud de {tipo_insumo} (Cantidad: {cantidad}) ha sido RECHAZADA."
                    if observacion_supervisor:
                        mensaje += f" Motivo: {observacion_supervisor}"
                    tipo_notif = "rechazada"

                # Insertar notificación para el empleado
                crear_notificacion_insumo(
                    id, 
                    usuario_id, 
                    tipo_insumo, 
                    cantidad, 
                    mensaje, 
                    tipo_notif
                )

            db.connection.commit()
            cur.close()
            flash(f"Solicitud {nuevo_estado.lower()} correctamente", "success")

        except Exception as e:
            db.connection.rollback()
            flash(f"Error al actualizar la solicitud: {str(e)}", "danger")

    return redirect(url_for("ver_solicitudes"))


# ---------------------- SOLICITUDES PROCESADAS ----------------------
@app.route("/solicitudes_procesadas", methods=["GET", "POST"])
@login_required
def solicitudes_procesadas():
    """
    Muestra las solicitudes Aceptadas y Rechazadas
    Permite buscar por número de solicitud y marcar como Entregada
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    cur = db.connection.cursor()
    
    # Variable para almacenar la solicitud buscada
    solicitud_buscada = None
    numero_busqueda = None

    # Si es una búsqueda POST
    if request.method == "POST":
        numero_busqueda = request.form.get("numero_solicitud", "").strip()
        
        if numero_busqueda:
            cur.execute(
                """
                SELECT s.id, u.fullname, s.tipo_insumo, s.cantidad, 
                       s.observaciones, s.fecha_solicitud, s.estado, 
                       s.observacion_supervisor
                FROM solicitud_insumo s
                JOIN user u ON s.usuario_id = u.id
                WHERE s.id = %s AND s.estado IN ('Aceptada', 'Rechazada', 'Entregada')
            """,
                (numero_busqueda,),
            )
            solicitud_buscada = cur.fetchone()

    # Todas las solicitudes procesadas
    cur.execute(
        """
        SELECT s.id, u.fullname, s.tipo_insumo, s.cantidad, s.observaciones, 
               s.fecha_solicitud, s.estado, s.observacion_supervisor
        FROM solicitud_insumo s
        JOIN user u ON s.usuario_id = u.id
        WHERE s.estado IN ('Aceptada', 'Rechazada', 'Entregada')
        ORDER BY s.fecha_solicitud DESC
    """
    )
    solicitudes_procesadas = cur.fetchall()
    cur.close()

    return render_template(
        "solicitudes_procesadas.html",
        solicitudes_procesadas=solicitudes_procesadas,
        solicitud_buscada=solicitud_buscada,
        numero_busqueda=numero_busqueda,
    )


@app.route("/marcar_entregada/<int:id>", methods=["POST"])
@login_required
def marcar_entregada(id):
    """
    Marca una solicitud Aceptada como Entregada
    """
    try:
        cur = db.connection.cursor()

        # Verificar que la solicitud esté en estado "Aceptada"
        cur.execute(
            "SELECT estado FROM solicitud_insumo WHERE id = %s", (id,)
        )
        solicitud = cur.fetchone()

        if not solicitud:
            flash("Solicitud no encontrada", "error")
            return redirect(url_for("solicitudes_procesadas"))

        if solicitud[0] != "Aceptada":
            flash(
                "Solo se pueden marcar como entregadas las solicitudes aceptadas",
                "error",
            )
            return redirect(url_for("solicitudes_procesadas"))

        # Actualizar estado a "Entregada"
        cur.execute(
            """
            UPDATE solicitud_insumo
            SET estado = 'Entregada'
            WHERE id = %s
        """,
            (id,),
        )

        db.connection.commit()
        cur.close()

        flash(f"Solicitud #{id} marcada como entregada correctamente", "success")

    except Exception as e:
        db.connection.rollback()
        flash(f"Error al marcar como entregada: {str(e)}", "error")

    return redirect(url_for("solicitudes_procesadas"))

# ---------------------- EVIDENCIAS ----------------------


# Ruta para ver evidencias 
@app.route("/ver_evidencias")
@login_required
def ver_evidencias():
    cursor = db.connection.cursor()

    # Consulta simple 
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
        tratamientos = request.form.getlist("tratamiento")
        problemas = request.form.getlist("problema")
        prioridades = request.form.getlist("prioridad")
        insumos = request.form.getlist("insumos")

        tratamiento_str = ", ".join(tratamientos) if tratamientos else None
        problema_str = ", ".join(problemas) if problemas else None
        prioridad_str = ", ".join(prioridades) if prioridades else None
        insumo_str = ", ".join(insumos) if insumos else None

        try:
            # Obtener el nombre del cultivo
            cur.execute("SELECT nombre FROM Cultivos WHERE Id_cultivo = %s", (cultivo_id,))
            cultivo_nombre_row = cur.fetchone()

            if cultivo_nombre_row:
                cultivo_nombre = cultivo_nombre_row[0]
                usuario_id = session.get("user_id")
                
                # Obtener nombre del usuario
                cur.execute("SELECT fullname FROM user WHERE id = %s", (usuario_id,))
                usuario_info = cur.fetchone()
                usuario_nombre = usuario_info[0] if usuario_info else "Usuario"

                # Insertar tratamiento
                cur.execute("""
                    INSERT INTO tratamientos (cultivo, tratamiento, problema, prioridad, insumos, fecha_registro, usuario_id)
                    VALUES (%s, %s, %s, %s, %s, NOW(), %s)
                """, (cultivo_nombre, tratamiento_str, problema_str, prioridad_str, insumo_str, usuario_id))

                tratamiento_id = cur.lastrowid
                db.connection.commit()
                
                # 🔔 NOTIFICACIÓN PARA ADMINISTRADORES
                mensaje = f"{usuario_nombre} registró un tratamiento para {cultivo_nombre} - Prioridad: {prioridad_str}"
                crear_notificacion_admin(
                    'nuevo_tratamiento',
                    usuario_id,
                    mensaje,
                    tratamiento_id,
                    None
                )
                
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
# Ruta para ver tratamientos con sus observaciones
@app.route("/tratamientos_registrados")
@login_required
def tratamientos_registrados():
    try:
        cur = db.connection.cursor()
        
        # Obtener el rol del usuario desde la sesión
        rol = session.get("rol", "")
        user_id = session.get("user_id")
        
        # Si es administrador, ve TODOS los tratamientos
        if rol == "administrador":
            cur.execute(
                """
                SELECT t.id_tratamiento, t.cultivo, t.tratamiento, t.problema, 
                       t.prioridad, t.insumos, t.fecha_registro,
                       COUNT(o.id_observacion) as total_observaciones
                FROM tratamientos t
                LEFT JOIN observaciones_tratamiento o ON t.id_tratamiento = o.id_tratamiento
                GROUP BY t.id_tratamiento
                ORDER BY t.fecha_registro DESC
                """
            )
        else:

            cur.execute("""
                            SELECT t.id_tratamiento,t.cultivo,t.tratamiento,t.problema,t.prioridad,t.insumos,t.fecha_registro,u.fullname AS usuario_nombre, COUNT(o.id_observacion) AS total_observaciones
                            FROM tratamientos t
                            JOIN user u ON t.usuario_id = u.id
                            LEFT JOIN observaciones_tratamiento o 
                                ON t.id_tratamiento = o.id_tratamiento
                            WHERE t.usuario_id = %s
                            GROUP BY t.id_tratamiento
                            ORDER BY t.fecha_registro DESC
                        """, (user_id,))
        
        tratamientos = cur.fetchall()
        cur.close()
        
        return render_template(
            "auth/tratamientos_registrados.html", 
            tratamientos=tratamientos, 
            rol=rol
        )

    except Exception as e:
        flash(f"Error al cargar los tratamientos: {str(e)}", "danger")
        return redirect(url_for("home"))


# Ruta para obtener observaciones de un tratamiento (AJAX)
@app.route("/obtener_observaciones/<int:id_tratamiento>")
@login_required
def obtener_observaciones(id_tratamiento):
    try:
        cur = db.connection.cursor()
        cur.execute(
            """
            SELECT o.id_observacion, o.observacion, o.usuario_nombre, 
                   DATE_FORMAT(o.fecha_registro, '%%d/%%m/%%Y %%H:%%i') as fecha_formateada
            FROM observaciones_tratamiento o
            WHERE o.id_tratamiento = %s
            ORDER BY o.fecha_registro DESC
            """,
            (id_tratamiento,),
        )
        observaciones = cur.fetchall()
        cur.close()

        # Convertir a lista de diccionarios para JSON
        observaciones_list = []
        for obs in observaciones:
            observaciones_list.append(
                {
                    "id": obs[0],
                    "observacion": obs[1],
                    "usuario": obs[2],
                    "fecha": obs[3],
                }
            )

        return jsonify({"success": True, "observaciones": observaciones_list})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Ruta para agregar observación
@app.route("/agregar_observacion", methods=["POST"])
@login_required
def agregar_observacion():
    try:
        # Verificar que el usuario sea supervisor o administrador
        rol = session.get("rol", "")
        if rol not in ["administrador", "supervisor"]:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "No tienes permisos para agregar observaciones",
                    }
                ),
                403,
            )

        # Obtener datos del formulario
        id_tratamiento = request.form.get("id_tratamiento")
        observacion = request.form.get("observacion", "").strip()

        # Validar que la observación tenga al menos 5 caracteres
        if len(observacion) < 5:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "La observación debe tener al menos 5 caracteres",
                    }
                ),
                400,
            )

        # Verificar que el tratamiento existe
        cur = db.connection.cursor()
        cur.execute(
            "SELECT id_tratamiento FROM tratamientos WHERE id_tratamiento = %s",
            (id_tratamiento,),
        )
        tratamiento = cur.fetchone()

        if not tratamiento:
            cur.close()
            return jsonify({"success": False, "error": "El tratamiento no existe"}), 404

        # Obtener información del usuario
        usuario_id = session.get("user_id")

        # Obtener el nombre del usuario desde la base de datos
        cur.execute("SELECT fullname FROM user WHERE id = %s", (usuario_id,))
        usuario_info = cur.fetchone()
        usuario_nombre = usuario_info[0] if usuario_info else "Usuario Desconocido"

        # Insertar la observación
        cur.execute(
            """
            INSERT INTO observaciones_tratamiento 
            (id_tratamiento, observacion, usuario_id, usuario_nombre)
            VALUES (%s, %s, %s, %s)
            """,
            (id_tratamiento, observacion, usuario_id, usuario_nombre),
        )

        db.connection.commit()
        cur.close()

        return jsonify(
            {"success": True, "message": "Observación agregada correctamente"}
        )

    except Exception as e:
        db.connection.rollback()
        return (
            jsonify(
                {"success": False, "error": f"Error al agregar observación: {str(e)}"}
            ),
            500,
        )


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
                flash(f"Error al guardar la imagen: {str(e)}", "danger")
                return redirect(url_for("registrar_problema"))

        try:
            cursor = db.connection.cursor()
            
            # Obtener nombre del usuario
            cursor.execute("SELECT fullname FROM user WHERE id = %s", (session["user_id"],))
            usuario_info = cursor.fetchone()
            usuario_nombre = usuario_info[0] if usuario_info else "Usuario"
            
            # Insertar problema
            cursor.execute("""
                INSERT INTO problemas_cultivo (id_usuario, tipo_problema, descripcion, evidencia, fecha_registro)
                VALUES (%s, %s, %s, %s, NOW())
            """, (session["user_id"], tipo, descripcion, filename))
            
            problema_id = cursor.lastrowid
            db.connection.commit()
            
            # 🔔 NOTIFICACIÓN PARA ADMINISTRADORES
            mensaje = f"{usuario_nombre} reportó un problema: {tipo} - {descripcion[:50]}..."
            crear_notificacion_admin(
                'nuevo_problema',
                session["user_id"],
                mensaje,
                problema_id,
                None
            )
            
            cursor.close()
            flash("Problema registrado correctamente", "success")
            return redirect(url_for("ver_problemas"))

        except Exception as e:
            db.connection.rollback()
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
    if session.get('rol') != 'administrador':
        flash('No tienes permisos para registrar producción', 'danger')
        return redirect(url_for('home'))
    
    cursor = db.connection.cursor()
    cursor.execute("SELECT id_cultivo, nombre FROM cultivos WHERE estado = 'Habilitado'")
    cultivos = cursor.fetchall()

    if request.method == "POST":
        id_cultivo = request.form["cultivo"]
        fecha = request.form["fecha"]
        cantidad = request.form["cantidad"]

        try:
            # Obtener nombre del cultivo
            cursor.execute("SELECT nombre FROM cultivos WHERE id_cultivo = %s", (id_cultivo,))
            cultivo_info = cursor.fetchone()
            cultivo_nombre = cultivo_info[0] if cultivo_info else "Cultivo"
            
            # Obtener nombre del usuario
            cursor.execute("SELECT fullname FROM user WHERE id = %s", (session["user_id"],))
            usuario_info = cursor.fetchone()
            usuario_nombre = usuario_info[0] if usuario_info else "Administrador"
            
            # Insertar producción
            cursor.execute("""
                INSERT INTO produccion (id_usuario, id_cultivo, fecha, cantidad_bultos)
                VALUES (%s, %s, %s, %s)
            """, (session["user_id"], id_cultivo, fecha, cantidad))
            
            produccion_id = cursor.lastrowid
            db.connection.commit()
            
            # Actualizar inventario
            actualizar_inventario(id_cultivo)
            
            # 🔔 NOTIFICACIÓN PARA ADMINISTRADORES
            mensaje = f"{usuario_nombre} registró producción de {cultivo_nombre}: {cantidad} bultos"
            crear_notificacion_admin(
                'nueva_produccion',
                session["user_id"],
                mensaje,
                produccion_id,
                None
            )
            
            flash("Producción registrada e inventario actualizado correctamente", "success")
            return redirect(url_for("produccion_registrada"))
            
        except Exception as e:
            db.connection.rollback()
            flash(f"Error al registrar producción: {str(e)}", "danger")

    return render_template("registrar_produccion.html", cultivos=cultivos)

# ---------------------- NOTIFICACIONES ----------------------

@app.route("/mis_notificaciones")
@login_required
def mis_notificaciones():
    rol = session.get("rol")
    usuario_id = session.get("user_id")

    cur = db.connection.cursor()
    notificaciones = obtener_notificaciones_unificadas(usuario_id, rol, cur)
    no_leidas = contar_notificaciones_unificadas(usuario_id, rol, cur)
    cur.close()

    print(f"✓ Mostrando {len(notificaciones)} notificaciones para {rol}")  # Debug
    print(f"✓ Total no leídas: {no_leidas}")  # Debug

    return render_template(
        "mis_notificaciones.html",
        notificaciones=notificaciones,
        no_leidas=no_leidas,
        rol=rol
    )


@app.route("/marcar_notificacion_leida/<int:id>", methods=["POST"])
@login_required
def marcar_notificacion_leida(id):
    rol = session.get("rol")
    usuario_id = session.get("user_id")
    tipo = request.form.get("tipo_notif", "personal")

    cur = db.connection.cursor()

    try:
        if tipo == "general" and rol == "administrador":
            # Marcar notificación general
            cur.execute("UPDATE notificaciones_generales SET leida = 1 WHERE id = %s", (id,))
            print(f"✓ Notificación general {id} marcada como leída")
        else:
            # Marcar notificación personal
            cur.execute("""
                UPDATE notificaciones
                SET leida = 1
                WHERE id = %s AND usuario_id = %s
            """, (id, usuario_id))
            print(f"✓ Notificación personal {id} marcada como leída")

        db.connection.commit()
        flash("Notificación marcada como leída", "success")
        
    except Exception as e:
        db.connection.rollback()
        print(f"✗ Error al marcar notificación: {str(e)}")
        flash("Error al marcar la notificación", "error")
    
    cur.close()
    return redirect(url_for("mis_notificaciones"))



@app.route("/contar_notificaciones_pendientes")
@login_required
def contar_notificaciones_pendientes():
    cur = db.connection.cursor()
    total = contar_notificaciones_unificadas(session["user_id"], session["rol"], cur)
    cur.close()
    return {"count": total}




# ---------------------- PRODUCTIVIDAD DE EMPLEADOS ----------------------

@app.route("/productividad_empleados")
@login_required
def productividad_empleados():
    """
    Dashboard principal de productividad de empleados
    Solo accesible para administradores y supervisores
    Usa la VISTA para obtener métricas en tiempo real
    """
    rol = session.get("rol", "")
    
    if rol not in ["administrador", "supervisor"]:
        flash("No tienes permisos para ver esta sección", "danger")
        return redirect(url_for("home"))
    
    try:
        cur = db.connection.cursor()
        
        # Definir período actual (últimos 15 días)
        periodo_fin = datetime.now().date()
        periodo_inicio = periodo_fin - timedelta(days=14)
        
        # USAR LA VISTA directamente para obtener métricas en tiempo real
        # Filtrar por fecha en Python después de obtener los datos
        cur.execute("""
            SELECT 
                u.id,
                u.fullname,
                u.rol,
                -- Actividades del período
                COUNT(DISTINCT CASE 
                    WHEN DATE(a.fecha) BETWEEN %s AND %s 
                    THEN a.id 
                END) as total_actividades,
                -- Actividades con evidencia del período
                COUNT(DISTINCT CASE 
                    WHEN DATE(a.fecha) BETWEEN %s AND %s 
                        AND a.evidencia IS NOT NULL AND a.evidencia != '' 
                    THEN a.id 
                END) as actividades_con_evidencia,
                -- Problemas del período
                COUNT(DISTINCT CASE 
                    WHEN DATE(pc.fecha_registro) BETWEEN %s AND %s 
                    THEN pc.id_problema 
                END) as total_problemas,
                -- Solicitudes del período
                COUNT(DISTINCT CASE 
                    WHEN DATE(si.fecha_solicitud) BETWEEN %s AND %s 
                    THEN si.id 
                END) as total_solicitudes,
                -- Tratamientos del período
                COUNT(DISTINCT CASE 
                    WHEN DATE(t.fecha_registro) BETWEEN %s AND %s 
                    THEN t.id_tratamiento 
                END) as total_tratamientos,
                -- Siembras del período
                COUNT(DISTINCT CASE 
                    WHEN s.fecha_siembra BETWEEN %s AND %s 
                    THEN s.id_siembra 
                END) as total_siembras,
                -- Puntuación calculada del período
                ROUND(
                    (COUNT(DISTINCT CASE WHEN DATE(a.fecha) BETWEEN %s AND %s THEN a.id END) * 2) +
                    (COUNT(DISTINCT CASE WHEN DATE(a.fecha) BETWEEN %s AND %s AND a.evidencia IS NOT NULL THEN a.id END) * 3) +
                    (COUNT(DISTINCT CASE WHEN DATE(pc.fecha_registro) BETWEEN %s AND %s THEN pc.id_problema END) * 1.5) +
                    (COUNT(DISTINCT CASE WHEN DATE(si.fecha_solicitud) BETWEEN %s AND %s AND si.estado = 'Aceptada' THEN si.id END) * 2.5) +
                    (COUNT(DISTINCT CASE WHEN DATE(t.fecha_registro) BETWEEN %s AND %s THEN t.id_tratamiento END) * 2) +
                    (COUNT(DISTINCT CASE WHEN s.fecha_siembra BETWEEN %s AND %s THEN s.id_siembra END) * 1.5)
                , 2) as puntuacion_productividad
            FROM user u
            LEFT JOIN actividades a ON u.id = a.id_usuario
            LEFT JOIN problemas_cultivo pc ON u.id = pc.id_usuario
            LEFT JOIN solicitud_insumo si ON u.id = si.usuario_id
            LEFT JOIN tratamientos t ON u.id = t.usuario_id
            LEFT JOIN siembra s ON u.id = s.id_usuario
            WHERE u.estado = 'habilitado'
                AND u.rol IN ('empleado', 'cuidador', 'supervisor')
            GROUP BY u.id, u.fullname, u.rol
            ORDER BY puntuacion_productividad DESC, u.fullname ASC
        """, (
            periodo_inicio, periodo_fin,  # total_actividades
            periodo_inicio, periodo_fin,  # actividades_con_evidencia
            periodo_inicio, periodo_fin,  # total_problemas
            periodo_inicio, periodo_fin,  # total_solicitudes
            periodo_inicio, periodo_fin,  # total_tratamientos
            periodo_inicio, periodo_fin,  # total_siembras
            periodo_inicio, periodo_fin,  # puntuación - actividades
            periodo_inicio, periodo_fin,  # puntuación - evidencias
            periodo_inicio, periodo_fin,  # puntuación - problemas
            periodo_inicio, periodo_fin,  # puntuación - solicitudes aceptadas
            periodo_inicio, periodo_fin,  # puntuación - tratamientos
            periodo_inicio, periodo_fin   # puntuación - siembras
        ))
        
        empleados = cur.fetchall()
        
        # Obtener fecha del último reporte guardado (para info solamente)
        cur.execute("""
            SELECT MAX(periodo_fin) 
            FROM reportes_productividad
        """)
        ultimo_reporte = cur.fetchone()[0]
        
        # Calcular próxima fecha de reporte (cada 15 días)
        if ultimo_reporte:
            proxima_fecha = ultimo_reporte + timedelta(days=15)
            dias_restantes = (proxima_fecha - datetime.now().date()).days
        else:
            proxima_fecha = None
            dias_restantes = None
        
        cur.close()
        
        return render_template(
            "productividad_empleados.html",
            empleados=empleados,
            periodo_inicio=periodo_inicio,
            periodo_fin=periodo_fin,
            proxima_fecha=proxima_fecha,
            dias_restantes=dias_restantes,
            ultimo_reporte=ultimo_reporte
        )
        
    except Exception as e:
        flash(f"Error al cargar productividad: {str(e)}", "danger")
        import traceback
        traceback.print_exc()
        return redirect(url_for("home"))


@app.route("/calcular_productividad", methods=["POST"])
@login_required
def calcular_productividad():
    """
    Guarda un snapshot de las métricas actuales en la tabla metricas_productividad
    y registra el reporte
    """
    rol = session.get("rol", "")
    
    if rol not in ["administrador", "supervisor"]:
        return jsonify({"success": False, "error": "No tienes permisos"}), 403
    
    try:
        cur = db.connection.cursor()
        
        # Definir período de cálculo (últimos 15 días)
        periodo_fin = datetime.now().date()
        periodo_inicio = periodo_fin - timedelta(days=14)
        
        # Llamar al procedimiento almacenado para guardar el snapshot
        cur.execute("""
            CALL calcular_metricas_productividad(%s, %s, NULL)
        """, (periodo_inicio, periodo_fin))
        
        # Registrar la generación del reporte
        cur.execute("""
            INSERT INTO reportes_productividad (periodo_inicio, periodo_fin, generado_por)
            VALUES (%s, %s, %s)
        """, (periodo_inicio, periodo_fin, session["user_id"]))
        
        db.connection.commit()
        cur.close()
        
        flash("✓ Productividad calculada y guardada correctamente", "success")
        return redirect(url_for("productividad_empleados"))
        
    except Exception as e:
        db.connection.rollback()
        flash(f"Error al calcular productividad: {str(e)}", "danger")
        import traceback
        traceback.print_exc()
        return redirect(url_for("productividad_empleados"))


@app.route("/descargar_reporte_productividad")
@login_required
def descargar_reporte_productividad():
    """
    Genera y descarga un reporte PDF de productividad usando datos en tiempo real
    """
    rol = session.get("rol", "")
    
    if rol not in ["administrador", "supervisor"]:
        flash("No tienes permisos para descargar reportes", "danger")
        return redirect(url_for("home"))
    
    if not REPORTLAB_AVAILABLE:
        flash("ReportLab no está instalado. Contacta al administrador.", "danger")
        return redirect(url_for("productividad_empleados"))
    
    try:
        cur = db.connection.cursor()
        
        # Definir período del reporte
        periodo_fin = datetime.now().date()
        periodo_inicio = periodo_fin - timedelta(days=14)
        
        # Obtener datos usando la misma consulta que la vista principal
        cur.execute("""
            SELECT 
                u.fullname,
                u.rol,
                COUNT(DISTINCT CASE WHEN DATE(a.fecha) BETWEEN %s AND %s THEN a.id END),
                COUNT(DISTINCT CASE WHEN DATE(a.fecha) BETWEEN %s AND %s AND a.evidencia IS NOT NULL THEN a.id END),
                COUNT(DISTINCT CASE WHEN DATE(pc.fecha_registro) BETWEEN %s AND %s THEN pc.id_problema END),
                COUNT(DISTINCT CASE WHEN DATE(si.fecha_solicitud) BETWEEN %s AND %s THEN si.id END),
                COUNT(DISTINCT CASE WHEN DATE(t.fecha_registro) BETWEEN %s AND %s THEN t.id_tratamiento END),
                COUNT(DISTINCT CASE WHEN s.fecha_siembra BETWEEN %s AND %s THEN s.id_siembra END),
                ROUND(
                    (COUNT(DISTINCT CASE WHEN DATE(a.fecha) BETWEEN %s AND %s THEN a.id END) * 2) +
                    (COUNT(DISTINCT CASE WHEN DATE(a.fecha) BETWEEN %s AND %s AND a.evidencia IS NOT NULL THEN a.id END) * 3) +
                    (COUNT(DISTINCT CASE WHEN DATE(pc.fecha_registro) BETWEEN %s AND %s THEN pc.id_problema END) * 1.5) +
                    (COUNT(DISTINCT CASE WHEN DATE(si.fecha_solicitud) BETWEEN %s AND %s AND si.estado = 'Aceptada' THEN si.id END) * 2.5) +
                    (COUNT(DISTINCT CASE WHEN DATE(t.fecha_registro) BETWEEN %s AND %s THEN t.id_tratamiento END) * 2) +
                    (COUNT(DISTINCT CASE WHEN s.fecha_siembra BETWEEN %s AND %s THEN s.id_siembra END) * 1.5)
                , 2)
            FROM user u
            LEFT JOIN actividades a ON u.id = a.id_usuario
            LEFT JOIN problemas_cultivo pc ON u.id = pc.id_usuario
            LEFT JOIN solicitud_insumo si ON u.id = si.usuario_id
            LEFT JOIN tratamientos t ON u.id = t.usuario_id
            LEFT JOIN siembra s ON u.id = s.id_usuario
            WHERE u.estado = 'habilitado'
                AND u.rol IN ('empleado', 'cuidador', 'supervisor')
            GROUP BY u.id, u.fullname, u.rol
            ORDER BY 9 DESC, u.fullname ASC
        """, (
            periodo_inicio, periodo_fin,  # actividades
            periodo_inicio, periodo_fin,  # evidencias
            periodo_inicio, periodo_fin,  # problemas
            periodo_inicio, periodo_fin,  # solicitudes
            periodo_inicio, periodo_fin,  # tratamientos
            periodo_inicio, periodo_fin,  # siembras
            periodo_inicio, periodo_fin,  # punt - actividades
            periodo_inicio, periodo_fin,  # punt - evidencias
            periodo_inicio, periodo_fin,  # punt - problemas
            periodo_inicio, periodo_fin,  # punt - solicitudes
            periodo_inicio, periodo_fin,  # punt - tratamientos
            periodo_inicio, periodo_fin   # punt - siembras
        ))
        
        datos = cur.fetchall()
        cur.close()
        
        # Crear PDF en memoria
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elementos = []
        
        # Estilos
        styles = getSampleStyleSheet()
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=1
        )
        
        # Título
        titulo = Paragraph(
            f"<b>Reporte de Productividad de Empleados</b><br/>"
            f"<font size=12>Período: {periodo_inicio.strftime('%d/%m/%Y')} - {periodo_fin.strftime('%d/%m/%Y')}</font>",
            titulo_style
        )
        elementos.append(titulo)
        elementos.append(Spacer(1, 0.3*inch))
        
        # Crear tabla
        datos_tabla = [
            ['Empleado', 'Rol', 'Actividades', 'Evidencias', 'Problemas', 
             'Solicitudes', 'Tratamientos', 'Siembras', 'Puntuación']
        ]
        
        for fila in datos:
            datos_tabla.append([
                fila[0],  # Nombre
                fila[1],  # Rol
                str(fila[2]),  # Actividades
                str(fila[3]),  # Evidencias
                str(fila[4]),  # Problemas
                str(fila[5]),  # Solicitudes
                str(fila[6]),  # Tratamientos
                str(fila[7]),  # Siembras
                f"{fila[8]:.1f}"  # Puntuación
            ])
        
        tabla = Table(datos_tabla, colWidths=[1.2*inch, 0.8*inch, 0.7*inch, 0.7*inch, 
                                               0.7*inch, 0.7*inch, 0.8*inch, 0.7*inch, 0.7*inch])
        
        # Estilo de la tabla
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elementos.append(tabla)
        
        # Pie de página
        elementos.append(Spacer(1, 0.5*inch))
        pie = Paragraph(
            f"<i>Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}</i><br/>"
            f"<i>Por: {session.get('fullname', 'Sistema')}</i>",
            styles['Normal']
        )
        elementos.append(pie)
        
        # Construir PDF
        doc.build(elementos)
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'reporte_productividad_{periodo_inicio}_{periodo_fin}.pdf'
        )
        
    except Exception as e:
        flash(f"Error al generar reporte: {str(e)}", "danger")
        import traceback
        traceback.print_exc()
        return redirect(url_for("productividad_empleados"))


@app.route("/detalle_productividad/<int:user_id>")
@login_required
def detalle_productividad(user_id):
    """
    Muestra el detalle completo de productividad de un empleado específico
    """
    rol = session.get("rol", "")
    
    if rol not in ["administrador", "supervisor"]:
        return jsonify({"success": False, "error": "No tienes permisos"}), 403
    
    try:
        cur = db.connection.cursor()
        
        # Obtener información del empleado
        cur.execute("SELECT fullname, rol FROM user WHERE id = %s", (user_id,))
        empleado = cur.fetchone()
        
        if not empleado:
            return jsonify({"success": False, "error": "Empleado no encontrado"}), 404
        
        # Definir período
        periodo_fin = datetime.now().date()
        periodo_inicio = periodo_fin - timedelta(days=14)
        
        # Obtener actividades recientes
        cur.execute("""
            SELECT actividad, DATE_FORMAT(fecha, '%%d/%%m/%%Y'), insumos
            FROM actividades
            WHERE id_usuario = %s 
                AND DATE(fecha) BETWEEN %s AND %s
            ORDER BY fecha DESC
            LIMIT 10
        """, (user_id, periodo_inicio, periodo_fin))
        actividades = cur.fetchall()
        
        # Obtener problemas reportados
        cur.execute("""
            SELECT tipo_problema, descripcion, DATE_FORMAT(fecha_registro, '%%d/%%m/%%Y')
            FROM problemas_cultivo
            WHERE id_usuario = %s 
                AND DATE(fecha_registro) BETWEEN %s AND %s
            ORDER BY fecha_registro DESC
            LIMIT 5
        """, (user_id, periodo_inicio, periodo_fin))
        problemas = cur.fetchall()
        
        # Obtener tratamientos
        cur.execute("""
            SELECT cultivo, tratamiento, prioridad, DATE_FORMAT(fecha_registro, '%%d/%%m/%%Y')
            FROM tratamientos
            WHERE usuario_id = %s 
                AND DATE(fecha_registro) BETWEEN %s AND %s
            ORDER BY fecha_registro DESC
            LIMIT 5
        """, (user_id, periodo_inicio, periodo_fin))
        tratamientos = cur.fetchall()
        
        # Obtener siembras
        cur.execute("""
            SELECT c.nombre, s.detalle, DATE_FORMAT(s.fecha_siembra, '%%d/%%m/%%Y')
            FROM siembra s
            JOIN cultivos c ON s.cod_cultivos = c.id_cultivo
            WHERE s.id_usuario = %s 
                AND s.fecha_siembra BETWEEN %s AND %s
            ORDER BY s.fecha_siembra DESC
            LIMIT 5
        """, (user_id, periodo_inicio, periodo_fin))
        siembras = cur.fetchall()
        
        cur.close()
        
        return jsonify({
            "success": True,
            "empleado": {
                "nombre": empleado[0],
                "rol": empleado[1]
            },
            "actividades": [
                {
                    "actividad": a[0],
                    "fecha": a[1],
                    "insumos": a[2]
                } for a in actividades
            ],
            "problemas": [
                {
                    "tipo": p[0],
                    "descripcion": p[1],
                    "fecha": p[2]
                } for p in problemas
            ],
            "tratamientos": [
                {
                    "cultivo": t[0],
                    "tratamiento": t[1],
                    "prioridad": t[2],
                    "fecha": t[3]
                } for t in tratamientos
            ],
            "siembras": [
                {
                    "cultivo": s[0],
                    "detalle": s[1],
                    "fecha": s[2]
                } for s in siembras
            ]
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

# ---------------------- INSUMOS DE EMPLEADOS ----------------------
@app.route("/insumos_empleados", methods=["GET", "POST"])
@login_required
def insumos_empleados():
    """
    Muestra todos los insumos con estado 'Entregada'
    Permite filtrar por usuario específico
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    cur = db.connection.cursor()
    
    # Obtener todos los usuarios para el filtro
    cur.execute(
        """
        SELECT DISTINCT u.id, u.fullname
        FROM user u
        INNER JOIN solicitud_insumo s ON u.id = s.usuario_id
        WHERE s.estado = 'Entregada'
        ORDER BY u.fullname
    """
    )
    usuarios = cur.fetchall()
    
    # Variable para almacenar el usuario seleccionado
    usuario_seleccionado = None
    insumos_filtrados = []
    
    # Si hay filtro por usuario
    if request.method == "POST":
        usuario_id = request.form.get("usuario_id")
        if usuario_id:
            usuario_seleccionado = usuario_id
            cur.execute(
                """
                SELECT s.id, u.fullname, s.tipo_insumo, s.cantidad,
                       s.observaciones, s.observacion_supervisor,
                       s.fecha_solicitud, s.estado
                FROM solicitud_insumo s
                JOIN user u ON s.usuario_id = u.id
                WHERE s.estado = 'Entregada' AND u.id = %s
                ORDER BY s.fecha_solicitud DESC
            """,
                (usuario_id,),
            )
            insumos_filtrados = cur.fetchall()
    
    # Todos los insumos entregados (para mostrar por defecto)
    cur.execute(
        """
        SELECT s.id, u.fullname, s.tipo_insumo, s.cantidad,
               s.observaciones, s.observacion_supervisor,
               s.fecha_solicitud, s.estado
        FROM solicitud_insumo s
        JOIN user u ON s.usuario_id = u.id
        WHERE s.estado = 'Entregada'
        ORDER BY s.fecha_solicitud DESC
    """
    )
    todos_insumos = cur.fetchall()
    
    cur.close()
    
    return render_template(
        "insumos_empleados.html",
        usuarios=usuarios,
        insumos_filtrados=insumos_filtrados,
        todos_insumos=todos_insumos,
        usuario_seleccionado=usuario_seleccionado,
    )


# ---------------------- MAIN ----------------------
if __name__ == "__main__":
    app.config.from_object(config["development"])
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)


    app.run()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    app.run()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))


