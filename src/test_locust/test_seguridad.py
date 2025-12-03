from locust import HttpUser, task, between
class SeguridadUser(HttpUser):
    # Tiempo de espera entre tareas (simula usuarios reales que no hacen requests continuas)
    wait_time = between(1, 2)


    # URL base del sistema que estamos probando
    host = "http://127.0.0.1:5000"


    @task
    def probar_ruta_protegida(self):
        """
        Prueba 1: Acceso a ruta protegida sin autenticación.
        ----------------------------------------------------
        Este test intenta acceder a la ruta /admin sin enviar
        ningún tipo de token o cabecera de autenticación.


        ¿Qué se espera?
        - Que el servidor responda con un código de error (401 o 403).
        - Esto ayuda a comprobar si existe un control de acceso adecuado.
        """
        self.client.get("/admin", headers={})


    @task
    def intento_sql_injection(self):
        """
        Prueba 2: Intento de SQL Injection.
        -----------------------------------
        Esta prueba intenta "romper" la seguridad del backend enviando
        un parámetro malicioso en la URL.


        Ejemplo del ataque enviado:
        /buscar?query=' OR '1'='1


        ¿Qué se espera?
        - Que el servidor NO ejecute la consulta.
        - Que devuelva un mensaje de error controlado o un resultado vacío.
        - Nunca debe devolver datos sensibles o fallar por completo.
        """
        self.client.get("/buscar?query=' OR '1'='1")
