# Sistema de Monitoreo de PC

Una aplicación de escritorio basada en Python para monitorear y gestionar información de hardware de computadoras, almacenar datos en una base de datos MySQL y generar etiquetas imprimibles para los equipos.

## Descripción general

El Sistema de Monitoreo de PC está diseñado para recopilar, mostrar y almacenar especificaciones de hardware de computadoras. Se integra con OpenHardwareMonitor para obtener datos de hardware en tiempo real, permite guardar esta información en una base de datos MySQL y genera etiquetas PDF para documentación de los equipos. La aplicación cuenta con una interfaz gráfica amigable construida con Tkinter y permite imprimir etiquetas directamente en una impresora especificada.

## Características

- **Monitoreo de hardware**: Recopila información del sistema como CPU, RAM, placa base, GPU, almacenamiento, unidades ópticas y dispositivos de audio usando OpenHardwareMonitor y WMI.
- **Integración con base de datos**: Almacena y recupera datos de hardware en una base de datos MySQL.
- **Funcionalidad de búsqueda**: Permite buscar equipos por número de serie.
- **Impresión de etiquetas**: Genera etiquetas en PDF con detalles del hardware y las envía a una impresora designada (por ejemplo, "LABEL_IMAXIS").
- **Interfaz modo oscuro**: Interfaz moderna en modo oscuro para mejor usabilidad.
- **Datos personalizables**: Permite agregar campos de modelo y comentario en los registros de equipos.

## Requisitos previos

- **Python 3.12+**
- **Servidor MySQL**: Un servidor MySQL en funcionamiento con una base de datos configurada.
- **OpenHardwareMonitor**: Incluido en el directorio `OpenHardwareMonitor`.
- **PDFtoPrinter.exe**: Incluido para impresión de etiquetas PDF.
- **Librerías de Python requeridas**:
  - `mysql-connector-python`
  - `wmi`
  - `psutil`
  - `Pillow`
  - `reportlab`
  - `pywin32`

Instala las dependencias usando:
```bash
pip install mysql-connector-python wmi psutil Pillow reportlab pywin32
```

## Instalación

1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/tu-usuario/pc-monitor-system.git
   cd pc-monitor-system
   ```

2. **Configura la base de datos MySQL**:
   - Crea una base de datos MySQL llamada `monitor`.
   - Configura la conexión en `bd_ruta.py` con los datos de tu servidor MySQL (host, usuario, contraseña, puerto).
   - Asegúrate de que existan las siguientes tablas:
     ```sql
     CREATE TABLE equipo (
         id INT AUTO_INCREMENT PRIMARY KEY,
         serial VARCHAR(255) NOT NULL,
         modelo VARCHAR(255),
         comentario TEXT,
         fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
     );

     CREATE TABLE info_estatica (
         equipo_id INT PRIMARY KEY,
         sistema VARCHAR(255),
         cpu VARCHAR(255),
         placa_base VARCHAR(255),
         FOREIGN KEY (equipo_id) REFERENCES equipo(id)
     );

     CREATE TABLE ram (
         id INT AUTO_INCREMENT PRIMARY KEY,
         equipo_id INT,
         descripcion VARCHAR(255),
         FOREIGN KEY (equipo_id) REFERENCES equipo(id)
     );

     CREATE TABLE grafica (
         id INT AUTO_INCREMENT PRIMARY KEY,
         equipo_id INT,
         descripcion VARCHAR(255),
         FOREIGN KEY (equipo_id) REFERENCES equipo(id)
     );

     CREATE TABLE almacenamiento (
         id INT AUTO_INCREMENT PRIMARY KEY,
         equipo_id INT,
         descripcion VARCHAR(255),
         FOREIGN KEY (equipo_id) REFERENCES equipo(id)
     );

     CREATE TABLE opticas (
         id INT AUTO_INCREMENT PRIMARY KEY,
         equipo_id INT,
         descripcion VARCHAR(255),
         FOREIGN KEY (equipo_id) REFERENCES equipo(id)
     );

     CREATE TABLE audio (
         id INT AUTO_INCREMENT PRIMARY KEY,
         equipo_id INT,
         descripcion VARCHAR(255),
         FOREIGN KEY (equipo_id) REFERENCES equipo(id)
     );
     ```

3. **Instala las dependencias**:
   Ejecuta el comando `pip` indicado en la sección de Requisitos previos.

4. **Ubica los archivos necesarios**:
   - Asegúrate de que `OpenHardwareMonitor.exe` y las DLL relacionadas estén en el directorio `OpenHardwareMonitor`.
   - Asegúrate de que `PDFtoPrinter.exe` esté en el directorio raíz.
   - Coloca los íconos en el directorio `img-and-sounds` según la estructura del proyecto.

5. **Ejecuta la aplicación**:
   ```bash
   python monitor.py
   ```
   Alternativamente, usa el ejecutable precompilado `monitor.exe` para Windows.

## Uso

1. **Inicia la aplicación**:
   - Ejecuta `monitor.py` o `monitor.exe`.
   - Al iniciar, puedes elegir si deseas escanear el hardware del sistema actual.

2. **Interfaz principal**:
   - Muestra los detalles del hardware (CPU, RAM, placa base, etc.) con actualizaciones de temperatura en tiempo real.
   - Usa el menú "Archivo" para:
     - **Abrir**: Buscar y cargar datos de equipos por número de serie.
     - **Guardar**: Guardar los datos de hardware en la base de datos MySQL.
     - **Imprimir**: Generar e imprimir etiquetas del equipo.
     - **Salir**: Salir de la aplicación (solicita guardar si hay datos sin guardar).

3. **Guardar datos**:
   - Ingresa el modelo y comentario en el diálogo de guardado.
   - Los datos se almacenan en la base de datos MySQL y también se utiliza un archivo temporal JSON (`temp_guardar.json`) durante el proceso.

4. **Impresión de etiquetas**:
   - Selecciona un registro de la lista de equipos recientes.
   - Se genera un PDF (`equipo_etiqueta.pdf`) y se envía a la impresora "LABEL_IMAXIS".
   - Si la impresión falla, el PDF puede abrirse manualmente para imprimir.

## Estructura del proyecto

```
C:.
│   abrir.py              # Interfaz gráfica para buscar/cargar equipos por serie
│   bd_ruta.py            # Configuración de conexión a la base de datos
│   equipo_etiqueta.pdf   # Ejemplo de etiqueta PDF generada
│   guardar_mysql.py      # Lógica para guardar datos en MySQL
│   imprimir.py           # Lógica para generar/imprimir etiquetas PDF
│   monitor.exe           # Ejecutable para Windows
│   monitor.py            # Script principal de la aplicación
│   PDFtoPrinter.exe      # Utilidad para impresión de PDFs
│   py-to-exe.json        # Configuración para PyInstaller
│
├───equipos
│       SDFG4.txt
│       To be filled by O.E.M..txt
│
├───img-and-sounds
│       almacenamiento.png
│       audio.png
│       comentarios.png
│       cpu.png
│       device.png
│       grafica.png
│       icono.ico
│       placa-base.png
│       ram.png
│       sistema-operativo.png
│       unidades-opticas.png
│
├───OpenHardwareMonitor
│       Aga.Controls.dll
│       License.html
│       OpenHardwareMonitor.config
│       OpenHardwareMonitor.exe
│       OpenHardwareMonitorLib.dll
│       OpenHardwareMonitorLib.sys
│       OxyPlot.dll
│       OxyPlot.WindowsForms.dll
│
├───output
└───__pycache__
```

## Compilación del ejecutable

Para compilar la aplicación en un solo archivo ejecutable:

1. Instala PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Usa la configuración `py-to-exe.json` con `auto-py-to-exe` o ejecuta:
   ```bash
   pyinstaller --noconfirm --onefile --noconsole --icon=img-and-sounds/icono.ico    --add-data "img-and-sounds;img-and-sounds/"    --add-data "OpenHardwareMonitor;OpenHardwareMonitor/"    --add-data "abrir.py;."    --add-data "bd_ruta.py;."    --add-data "guardar_mysql.py;."    --add-data "imprimir.py;."    --add-data "monitor.py;."    --add-data "PDFtoPrinter.exe;."    --add-data "ruta_a_mysql_connector;mysql/connector"    monitor.py
   ```
   Sustituye `ruta_a_mysql_connector` por la ruta a tu directorio `mysql/connector`.

## Notas

- **Configuración de la base de datos**: Actualiza `bd_ruta.py` con los datos de tu servidor MySQL. La configuración predeterminada usa una instancia MySQL en la nube.
- **Configuración de impresora**: Asegúrate de tener disponible una impresora con "LABEL_IMAXIS" en su nombre para impresión automática.
- **OpenHardwareMonitor**: Requiere privilegios de administrador para ejecutarse. La aplicación maneja esto automáticamente.
- **Generación de PDFs**: Se utiliza ReportLab para crear etiquetas de equipos compactas y bien formateadas.

## Contribuciones

¡Se aceptan contribuciones! Por favor, envía un pull request o abre un issue para reportar errores, solicitar funciones o mejoras.

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## Agradecimientos

- [OpenHardwareMonitor](https://openhardwaremonitor.org/) por las capacidades de monitoreo de hardware.
- [ReportLab](https://www.reportlab.com/) por la generación de PDFs.
- [Tkinter](https://docs.python.org/3/library/tkinter.html) por el framework de la interfaz gráfica.
