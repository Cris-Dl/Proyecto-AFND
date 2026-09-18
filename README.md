# GamerGear - Proyecto AFND

Aplicación de escritorio desarrollada para el curso de **Lenguajes Formales y Autómatas**.

GamerGear simula una tienda de productos y utiliza un **Autómata Finito No Determinista (AFND)** para representar el proceso de compra, disponibilidad, seguimiento, entrega y cancelación de pedidos

## Integrantes

- Cristhian Estuardo de León Pérez - 1540225
- Marvin Antonio Vásquez Chán - 1558525
- Diego Angel Alberto Barrios Ajquill - 1557125
- Santiago Jefté Batz Rodríguez - 1548725

## Requisitos

Se recomienda utilizar:

- Python 3.13
- Git
- Windows
- Conexión a internet
- Cámara web para utilizar Face ID

## Descargar el proyecto

Clonar el repositorio:

```powershell
git clone https://github.com/Cris-Dl/Proyecto-AFND.git
cd Proyecto-AFND
```

El proyecto final se encuentra en la rama principal:

```powershell
git switch main
git pull
```

## Crear el entorno virtual

El entorno virtual sirve para instalar las librerías del proyecto de forma separada, sin afectar otras instalaciones de Python en la computadora.

Crear el entorno:

```powershell
py -3.13 -m venv .venv
```

No es obligatorio activarlo. Los siguientes comandos utilizan directamente el Python que se encuentra dentro de `.venv`.

## Instalar dependencias

Primero actualizar `pip`:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
```

Instalar las dependencias principales:

```powershell
.\.venv\Scripts\python.exe -m pip install "flet[desktop]==0.28.3" "flet-map==0.1.0" requests opencv-python numpy dlib-bin face-recognition-models "setuptools<81" Click Pillow
```

Instalar `face-recognition` por separado:

```powershell
.\.venv\Scripts\python.exe -m pip install --no-deps face-recognition==1.3.0
```

## Verificar la instalación

Para comprobar que las librerías principales estén instaladas correctamente:

```powershell
.\.venv\Scripts\python.exe -c "import flet, flet_map, cv2, numpy, dlib, face_recognition; print('GamerGear OK')"
```

Si todo está correcto debe aparecer:

```text
GamerGear OK
```

## Ejecutar el proyecto

```powershell
.\.venv\Scripts\python.exe app.py
```

La primera vez que se ejecute la aplicación se puede crear una cuenta desde la pantalla de registro
