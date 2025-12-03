from locust import HttpUser, task, between


# --------------------------------------------------------------
# Clase que define un "usuario virtual" para pruebas funcionales.
# Aquí el objetivo NO es medir velocidad, sino verificar que
# los endpoints funcionan correctamente al ser llamados varias veces.
# --------------------------------------------------------------
class FuncionalidadUser(HttpUser):


    # Tiempo de espera entre cada tarea (1 a 3 segundos)
    # Esto simula un usuario real navegando la aplicación.
    wait_time = between(1, 3)


    # Dirección del servidor que vamos a probar.
    # Tu aplicación FastAPI local.
    host = "http://127.0.0.1:5000"


    # ----------------------------------------------------------
    # PRUEBA 1 – Verificar que la página principal funciona
    # ----------------------------------------------------------
    @task
    def test_home(self):
        # Se envía una solicitud GET a "/"
        # para comprobar que el endpoint responde correctamente.
        self.client.get("/")


    # ----------------------------------------------------------
    # PRUEBA 2 – Verificar que se pueden listar elementos
    # ----------------------------------------------------------
    @task
    def test_listar_items(self):
        # Llama al endpoint "/items" con un GET.
        # Esta prueba revisa que:
        # - la ruta exista
        # - retorne una lista válida
        # - no genere errores
        self.client.get("/items")


    # ----------------------------------------------------------
    # PRUEBA 3 – Verificar que se puede crear un elemento
    # ----------------------------------------------------------
    @task
    def test_crear_item(self):
        # Creamos un cuerpo JSON con los datos del nuevo item.
        payload = {"nombre": "Item de prueba", "precio": 100}


        # Enviamos un POST a "/items" con el JSON.
        # Esta prueba revisa que el servidor:
        # - reciba datos correctamente
        # - cree un nuevo recurso
        # - retorne un código válido (200, 201, etc.)
        self.client.post("/items", json=payload)
