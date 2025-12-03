from locust import HttpUser, task, between


# --------------------------------------------------------------
# Clase que define un usuario virtual para realizar PRUEBAS
# DE RENDIMIENTO (performance testing).
#
# En este tipo de pruebas queremos observar:
# - cuántas solicitudes por segundo soporta el servidor
# - cuánto tardan los endpoints en responder (latencia)
# - si el servidor se cae bajo carga (errores o fallos)
# - si el tiempo de respuesta aumenta cuando hay muchos usuarios
# --------------------------------------------------------------
class RendimientoUser(HttpUser):


    # Tiempo de espera MUY corto entre solicitudes (0.5 a 1 segundo).
    # Esto permite generar alta carga sobre el servidor y medir su límite.
    wait_time = between(0.5, 1)


    # Dirección del servidor que queremos probar.
    # Aquí es tu servidor local con FastAPI.
    host = "http://127.0.0.1:5000"


    # ----------------------------------------------------------
    # PRUEBA DE RENDIMIENTO – Endpoint bajo estrés
    # ----------------------------------------------------------
    @task
    def stress_endpoint(self):
        # Esta solicitud GET al endpoint "/items" se repetirá
        # cientos o miles de veces dependiendo de la cantidad de
        # usuarios simulados en Locust.
        #
        # LO QUE MEDIMOS AQUÍ:
        # ✔ Tiempo promedio de respuesta
        # ✔ Tiempos mínimos y máximos
        # ✔ Percentiles (95%ile, 99%ile)
        # ✔ Fallos bajo alta concurrencia
        # ✔ Requests per second (RPS)
        #
        # Este tipo de prueba permite detectar:
        # - Cuellos de botella en base de datos
        # - Código ineficiente o lento
        # - Problemas de escalabilidad
        # - Caídas del servidor cuando hay muchos usuarios
        self.client.get("/items")
