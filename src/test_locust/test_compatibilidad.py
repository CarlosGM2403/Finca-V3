from locust import HttpUser, task, between


# --------------------------------------------------------------
# Clase que representa un "tipo de usuario" para pruebas de compatibilidad.
# En esta prueba queremos simular usuarios que acceden desde navegadores
# y dispositivos diferentes (Chrome, Firefox, Android).
# --------------------------------------------------------------
class CompatibilidadUser(HttpUser):


    # Tiempo de espera entre cada petición.
    # Esto evita bombardear al servidor sin pausas reales.
    wait_time = between(1, 2)


    # Dirección del servidor o API que vamos a probar.
    # En este caso tu aplicación local con FastAPI.
    host = "http://127.0.0.1:5000"


    # ----------------------------------------------------------
    # PRUEBA 1 – Simulación de usuario en Google Chrome
    # ----------------------------------------------------------
    @task
    def test_chrome(self):
        # Enviamos una solicitud GET al endpoint raíz "/"
        # Usando un USER-AGENT típico de Chrome.
        # Esto sirve para verificar si el sistema responde igual
        # cuando el usuario usa Chrome.
        self.client.get("/", headers={"User-Agent": "Mozilla/5.0 Chrome"})


    # ----------------------------------------------------------
    # PRUEBA 2 – Simulación de usuario en Mozilla Firefox
    # ----------------------------------------------------------
    @task
    def test_firefox(self):
        # Igual que el anterior, pero usando User-Agent de Firefox.
        self.client.get("/", headers={"User-Agent": "Mozilla/5.0 Firefox"})


    # ----------------------------------------------------------
    # PRUEBA 3 – Simulación de usuario en un dispositivo Android
    # ----------------------------------------------------------
    @task
    def test_android(self):
        # Aquí verificamos si la aplicación se comporta igual
        # cuando el usuario accede desde un celular Android.
        self.client.get("/", headers={"User-Agent": "Android Mobile"})
