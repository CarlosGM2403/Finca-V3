from locust import HttpUser, task, between


class UsabilidadUser(HttpUser):
    # Tiempo de espera entre cada acción para simular un usuario real
    # Un usuario no ejecuta clics de manera inmediata, siempre hay pausas.
    wait_time = between(2, 4)


    # URL base del sistema bajo prueba
    host = "http://127.0.0.1:5000"


    @task
    def flujo_de_usuario(self):
        """
        Prueba: Flujo básico de usuario (Usabilidad)
        --------------------------------------------
        Esta prueba intenta simular un "recorrido" típico que haría un usuario
        dentro de la aplicación. Esto permite observar:


        - Si la navegación fluye sin errores.
        - Si los tiempos de respuesta son coherentes.
        - Si las acciones encadenadas no rompen el sistema.
        - Si un usuario puede completar tareas básicas sin problemas.


        ¿Qué representa cada paso?
        1. self.client.get("/")  
           -> El usuario entra al home o página principal.


        2. self.client.get("/items")  
           -> Navega al listado de elementos disponibles.


        3. self.client.post("/items", json={"nombre": "Flujo", "precio": 50})  
           -> Intenta crear un nuevo ítem (acción común en CRUDs).


        4. self.client.get("/items")  
           -> Revisa que la lista se haya actualizado o que todo siga funcionando.


        Este tipo de prueba es útil para ver cómo el sistema responde
        cuando un usuario real sigue una secuencia lógica de pasos.
        """
       
        # 1. Usuario abre la página principal
        self.client.get("/")


        # 2. Usuario entra al listado de ítems
        self.client.get("/items")


        # 3. Usuario crea un nuevo ítem (acción típica de un flujo CRUD)
        self.client.post("/items", json={"nombre": "Flujo", "precio": 50})


        # 4. Usuario revisa nuevamente la lista
        self.client.get("/items")
