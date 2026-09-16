import flet as ft
import sqlite3
import pickle
import time

from database_config import DB_PATH

try:
    import cv2
    import face_recognition
    import numpy as np

    IA_DISPONIBLE = True
except ImportError:
    IA_DISPONIBLE = False

def inicializar_bd():
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            usuario TEXT PRIMARY KEY,
            password TEXT,
            nombre_completo TEXT,
            correo TEXT,
            sexo TEXT,
            telefono TEXT,
            direccion TEXT,
            rostro BLOB
        )
    ''')
    conexion.commit()
    conexion.close()

inicializar_bd()

def registrar_rostro_camara():
    if not IA_DISPONIBLE:
        return None
    cap = cv2.VideoCapture(0)
    encoding_rostro = None
    cuadros_consecutivos = 0
    UMBRAL_DETECCION = 20

    time.sleep(1)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        frame_pequeno = cv2.resize(rgb_frame, (0, 0), fx=0.5, fy=0.5)
        localizaciones = face_recognition.face_locations(frame_pequeno)

        alto, ancho, _ = frame.shape

        if len(localizaciones) == 1:
            cuadros_consecutivos += 1
            top, right, bottom, left = [coord * 2 for coord in localizaciones[0]]

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, "Mantente quieto...", (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            progreso = int((cuadros_consecutivos / UMBRAL_DETECCION) * 300)
            cv2.rectangle(frame, (50, alto - 40), (50 + progreso, alto - 20), (0, 255, 0), -1)
            cv2.rectangle(frame, (50, alto - 40), (350, alto - 20), (255, 255, 255), 2)

            if cuadros_consecutivos >= UMBRAL_DETECCION:
                cv2.putText(frame, "¡ESCANEO EXITOSO!", (left, bottom + 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 200, 0), 2)
                cv2.imshow("Escaneando Biometria Facial...", frame)
                cv2.waitKey(1000)

                encodings = face_recognition.face_encodings(rgb_frame, [(top, right, bottom, left)])
                if len(encodings) > 0:
                    encoding_rostro = encodings[0]
                    break
        else:
            cuadros_consecutivos = 0
            mensaje = "Mirando a la camara..." if len(localizaciones) == 0 else "Multiples rostros detectados."
            cv2.putText(frame, mensaje, (50, alto - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow("Escaneando Biometria Facial...", frame)
        if cv2.waitKey(30) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    return encoding_rostro


def iniciar_sesion_camara(rostros_registrados):
    if not IA_DISPONIBLE:
        return None

    cap = cv2.VideoCapture(0)
    usuario_encontrado = None
    tiempo_inicio = time.time()

    time.sleep(1)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        frame_pequeno = cv2.resize(rgb_frame, (0, 0), fx=0.5, fy=0.5)
        localizaciones = face_recognition.face_locations(frame_pequeno)

        if len(localizaciones) == 1:
            top, right, bottom, left = [coord * 2 for coord in localizaciones[0]]
            cv2.rectangle(frame, (left, top), (right, bottom), (255, 200, 0), 2)
            cv2.putText(frame, "Identificando...", (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 2)

            encodings = face_recognition.face_encodings(rgb_frame, [(top, right, bottom, left)])
            if len(encodings) > 0:
                rostro_vivo = encodings[0]
                for usuario, db_encoding in rostros_registrados.items():
                    coincidencias = face_recognition.compare_faces([db_encoding], rostro_vivo, tolerance=0.5)
                    if coincidencias[0]:
                        usuario_encontrado = usuario

                        cv2.putText(frame, f"HOLA {usuario.upper()}", (left, bottom + 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                        cv2.imshow("Autenticacion Face ID", frame)
                        cv2.waitKey(1500)
                        break

                if usuario_encontrado:
                    break
        else:
            cv2.putText(frame, "Ubica tu rostro en la camara...", (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # Timeout de 10 segundos para dar error visual
        if time.time() - tiempo_inicio > 10:
            alto, ancho, _ = frame.shape
            cv2.putText(frame, "FACE ID INVALIDO", (ancho // 2 - 150, alto // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            cv2.imshow("Autenticacion Face ID", frame)
            cv2.waitKey(1500)  # Muestra el error un momento antes de cerrar
            break

        cv2.imshow("Autenticacion Face ID", frame)
        if cv2.waitKey(30) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    return usuario_encontrado

class VistaLogin(ft.Column):
    def __init__(self, page: ft.Page, on_auth_success=None):
        super().__init__()
        self.main_page = page
        self.on_auth_success = on_auth_success
        self.usuario_autenticado = None
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.construir_menu_principal()

    def notificar_autenticacion(self, usuario):
        self.usuario_autenticado = usuario
        if self.on_auth_success:
            self.on_auth_success(usuario)

    def mostrar_mensaje(self, texto, color):
        self.main_page.snack_bar = ft.SnackBar(ft.Text(texto), bgcolor=color)
        self.main_page.snack_bar.open = True
        self.main_page.update()

    def limpiar_vista(self):
        self.controls.clear()

    def actualizar_pantalla(self):
        try:
            self.update()
        except RuntimeError:
            pass

    # --- 0. MENÚ PRINCIPAL ---
    def construir_menu_principal(self):
        self.limpiar_vista()
        btn_pass = ft.FilledButton("Ingresar con Usuario y Contraseña",
                                   on_click=lambda _: self.construir_vista_password(), width=300,
                                   icon=ft.Icons.PASSWORD)
        btn_faceid = ft.FilledButton("Ingresar con Face ID", on_click=lambda _: self.construir_vista_faceid(),
                                     width=300, icon=ft.Icons.FACE)
        btn_huella = ft.FilledButton("Ingresar con Huella Digital", on_click=lambda _: self.construir_vista_huella(),
                                     width=300, icon=ft.Icons.FINGERPRINT)

        btn_crear = ft.TextButton("¿No tienes cuenta? Créala aquí", on_click=lambda _: self.construir_vista_registro())
        btn_recuperar = ft.TextButton("¿Olvidaste tu contraseña?", on_click=lambda _: self.construir_vista_recuperar())

        self.controls.extend([
            ft.Text("GamerGear", size=35, weight=ft.FontWeight.BOLD),
            ft.Text("Selecciona un método para iniciar sesión", size=15, color=ft.Colors.GREY_400),
            ft.Container(height=20),
            btn_pass, btn_faceid, btn_huella,
            ft.Container(height=20),
            ft.Container(width=300, content=ft.Divider(color=ft.Colors.GREY_800)),
            btn_crear, btn_recuperar
        ])
        self.actualizar_pantalla()

    # --- 1A. INICIO CON CONTRASEÑA ---
    def construir_vista_password(self):
        self.limpiar_vista()
        self.user_input = ft.TextField(label="Usuario", width=300, prefix_icon=ft.Icons.PERSON)
        self.pass_input = ft.TextField(label="Contraseña", width=300, password=True, can_reveal_password=True,
                                       prefix_icon=ft.Icons.LOCK)
        btn_iniciar = ft.FilledButton("Entrar", on_click=self.procesar_login_normal, width=300)
        btn_volver = ft.TextButton("Volver", on_click=lambda _: self.construir_menu_principal())

        self.controls.extend([
            ft.Text("Credenciales", size=30, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            self.user_input, self.pass_input,
            ft.Container(height=10),
            btn_iniciar, btn_volver
        ])
        self.actualizar_pantalla()

    def procesar_login_normal(self, e):
        u, p = self.user_input.value, self.pass_input.value
        if not u or not p:
            self.mostrar_mensaje("Por favor, llena ambos campos", ft.Colors.RED)
            return

        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre_completo FROM usuarios WHERE usuario=? AND password=?", (u, p))
        resultado = cursor.fetchone()
        conexion.close()

        if resultado:
            self.mostrar_mensaje(f"Confirmación: Bienvenido {resultado[0]}", ft.Colors.GREEN)
            self.notificar_autenticacion(u)
        else:
            self.mostrar_mensaje("Usuario o contraseña incorrectos", ft.Colors.RED)

    def construir_vista_faceid(self):
        self.limpiar_vista()
        icono_face = ft.Icon(ft.Icons.FACE_RETOUCHING_NATURAL, size=100, color=ft.Colors.PURPLE_400)
        btn_escanear = ft.FilledButton("Activar Escáner Facial", on_click=self.procesar_login_faceid, width=300)
        btn_volver = ft.TextButton("Volver", on_click=lambda _: self.construir_menu_principal())

        self.controls.extend([
            ft.Text("Face ID", size=30, weight=ft.FontWeight.BOLD),
            ft.Text("Mire fijamente a la cámara para autenticarse", color=ft.Colors.GREY_400),
            ft.Container(height=30), icono_face, ft.Container(height=30),
            btn_escanear, btn_volver
        ])
        self.actualizar_pantalla()

    def procesar_login_faceid(self, e):
        if not IA_DISPONIBLE:
            self.mostrar_mensaje("Librerías de reconocimiento no disponibles", ft.Colors.RED)
            return

        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        cursor.execute("SELECT usuario, rostro FROM usuarios WHERE rostro IS NOT NULL")
        filas = cursor.fetchall()
        conexion.close()

        rostros_registrados = {}
        for fila in filas:
            usuario = fila[0]
            datos_binarios = fila[1]
            rostros_registrados[usuario] = pickle.loads(datos_binarios)

        if not rostros_registrados:
            self.mostrar_mensaje("No hay usuarios con Face ID registrados", ft.Colors.ORANGE)
            return

        self.mostrar_mensaje("Escaneando rostro en vivo...", ft.Colors.BLUE)
        usuario_match = iniciar_sesion_camara(rostros_registrados)

        if usuario_match:
            self.mostrar_mensaje(f"Confirmación: Face ID aceptado. ¡Bienvenido {usuario_match}!", ft.Colors.GREEN)
            self.notificar_autenticacion(usuario_match)
        else:
            self.mostrar_mensaje("Face ID inválido. El rostro no pertenece a ningún usuario.", ft.Colors.RED)

    def construir_vista_huella(self):
        self.limpiar_vista()
        icono_huella = ft.Icon(ft.Icons.FINGERPRINT, size=100, color=ft.Colors.BLUE_400)
        btn_simular = ft.FilledButton("Simular Lectura de Huella",
                                      on_click=lambda _: self.mostrar_mensaje("Confirmación: Huella validada con éxito",
                                                                              ft.Colors.GREEN), width=300)
        btn_volver = ft.TextButton("Volver", on_click=lambda _: self.construir_menu_principal())

        self.controls.extend([
            ft.Text("Huella Digital", size=30, weight=ft.FontWeight.BOLD),
            ft.Container(height=30), icono_huella, ft.Container(height=30),
            btn_simular, btn_volver
        ])
        self.actualizar_pantalla()

    def construir_vista_registro(self):
        self.limpiar_vista()

        self.reg_nombre = ft.TextField(label="Nombre y Apellido", width=300, prefix_icon=ft.Icons.BADGE)
        self.reg_correo = ft.TextField(label="Correo Electrónico", width=300, prefix_icon=ft.Icons.EMAIL)
        self.reg_sexo = ft.Dropdown(
            label="Sexo",
            width=300,
            options=[ft.dropdown.Option("Masculino"), ft.dropdown.Option("Femenino"), ft.dropdown.Option("Otro")]
        )
        self.reg_telefono = ft.TextField(label="Teléfono", width=300, prefix_icon=ft.Icons.PHONE)
        self.reg_direccion = ft.TextField(label="Dirección de Entrega", width=300, prefix_icon=ft.Icons.LOCATION_ON)

        self.reg_user = ft.TextField(label="Usuario", width=300, prefix_icon=ft.Icons.PERSON_ADD)
        self.reg_pass = ft.TextField(label="Contraseña", width=300, password=True, can_reveal_password=True,
                                     prefix_icon=ft.Icons.LOCK)

        self.usar_face_id = ft.Switch(label="Registrar Face ID (Cámara)", value=False)

        btn_guardar = ft.FilledButton("Crear Cuenta", on_click=self.guardar_cuenta, width=300)
        btn_volver = ft.TextButton("Volver al Inicio", on_click=lambda _: self.construir_menu_principal())

        lista_formulario = ft.ListView(
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Text("Crear Cuenta", size=28, weight=ft.FontWeight.BOLD),
                        self.reg_nombre,
                        self.reg_correo,
                        self.reg_sexo,
                        self.reg_telefono,
                        self.reg_direccion,
                        ft.Container(width=300, content=ft.Divider(color=ft.Colors.GREY_800)),
                        self.reg_user,
                        self.reg_pass,
                        ft.Container(height=5),
                        self.usar_face_id,
                        ft.Container(height=10),
                        btn_guardar,
                        btn_volver
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                )
            ],
            height=500,
            width=350,
        )

        self.controls.append(lista_formulario)
        self.actualizar_pantalla()

    def guardar_cuenta(self, e):
        nom = self.reg_nombre.value
        cor = self.reg_correo.value
        sex = self.reg_sexo.value
        tel = self.reg_telefono.value
        dir = self.reg_direccion.value
        usr = self.reg_user.value
        pwd = self.reg_pass.value

        if not all([nom, cor, sex, tel, dir, usr, pwd]):
            self.mostrar_mensaje("Complete todos los campos del formulario", ft.Colors.RED)
            return

        rostro_datos = None
        if self.usar_face_id.value:
            if not IA_DISPONIBLE:
                self.mostrar_mensaje("Error: Librerías de visión artificial no disponibles", ft.Colors.RED)
                return

            self.mostrar_mensaje("Iniciando escaneo... Mire a la cámara", ft.Colors.BLUE)
            encoding_rostro = registrar_rostro_camara()

            if encoding_rostro is None:
                self.mostrar_mensaje("Escaneo cancelado o no completado", ft.Colors.RED)
                return

            rostro_datos = pickle.dumps(encoding_rostro)

        try:
            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO usuarios (usuario, password, nombre_completo, correo, sexo, telefono, direccion, rostro) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (usr, pwd, nom, cor, sex, tel, dir, rostro_datos)
            )
            conexion.commit()
            conexion.close()

            self.mostrar_mensaje("Confirmación: ¡Cuenta creada y guardada exitosamente!", ft.Colors.GREEN)
            self.construir_menu_principal()

        except sqlite3.IntegrityError:
            self.mostrar_mensaje("Error: El nombre de usuario ya existe", ft.Colors.RED)

    def construir_vista_recuperar(self):
        self.limpiar_vista()
        self.rec_correo = ft.TextField(label="Correo Registrado", width=300, prefix_icon=ft.Icons.EMAIL)
        btn_recuperar = ft.FilledButton("Recuperar Datos", on_click=self.recuperar_cuenta, width=300)
        btn_volver = ft.TextButton("Volver", on_click=lambda _: self.construir_menu_principal())

        self.controls.extend([
            ft.Text("Recuperar Cuenta", size=30, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            self.rec_correo,
            ft.Container(height=10),
            btn_recuperar,
            btn_volver
        ])
        self.actualizar_pantalla()

    def recuperar_cuenta(self, e):
        c = self.rec_correo.value
        if not c:
            return
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        cursor.execute("SELECT usuario, password FROM usuarios WHERE correo=?", (c,))
        res = cursor.fetchone()
        conexion.close()

        if res:
            self.mostrar_mensaje(f"Confirmación: Credenciales enviadas a {c} (Usuario: {res[0]})", ft.Colors.BLUE)
        else:
            self.mostrar_mensaje("Correo no registrado", ft.Colors.RED)

def main(page: ft.Page):
    page.title = "GamerGear - Módulo de Login"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window_width = 450
    page.window_height = 680
    page.add(VistaLogin(page))


if __name__ == "__main__":
    ft.run(main)
