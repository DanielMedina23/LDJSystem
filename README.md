# LDJSystem
Sistema web en Django para la gestión interactiva de mesas, planos de salón mediante SVG, reservas de clientes y configuración de horarios comerciales.

Estructura del repositorio:
- `ldjsystem/`: configuración principal del proyecto Django.
- Apps de dominio (`negocio`, `reservas`, etc.): lógica de negocio, modelos de mesas, horarios y gestión de reservas.
- `docker-compose.yml`, `Dockerfile`: entorno local con Docker.

## Flujo Principal
1. **Configuración del Negocio y Horarios:** El administrador define la información institucional del local (`negocio`) y establece los bloques horarios de atención por día de la semana (`horario`).

2. **Distribución de Mesas:** Se configuran las mesas y su disposición espacial o identificadores lógicos en el sistema de planos para el control de aforo y selección de asientos.

3. **Reserva Interactiva:** El cliente interactúa con la interfaz web para seleccionar una mesa disponible dentro del rango operativo, completando sus datos y aceptando los términos legales de privacidad.

4. **Validación y Notificación:** El sistema procesa la reserva, genera los tokens de verificación correspondientes y despacha notificaciones automáticas mediante SMTP (como correos de confirmación).

5. **Gestión Interna:** El personal autorizado supervisa, edita o da seguimiento operativo a las reservas y estados de las mesas desde el panel de control interno.

## Funcionalidades y Arquitectura Técnica
- **Dominio de Negocio y Horarios (`negocio`):**
  - Modelo relacional para la entidad `Negocio` (datos fiscales, metadatos institucionales y canales de contacto).
  - Gestión de franjas horarias con validación por día de la semana (`Horario`), desacopladas para renderizado adaptativo tanto en el panel de administración como en la capa de presentación pública (estilo listado vertical con filtrado de unicidad).

- **Infraestructura Espacial y Mesas (`plano`, `mesa`):**
  - Módulo de representación y gestión de aforo mediante coordenadas y distribuciones espaciales en el salón.
  - Relación directa entre la disponibilidad física del mobiliario y los motores de asignación de reservas.

- **Ciclo de Vida de Reservas (`reservas`):**
  - Orquestación de peticiones de reserva mediante validadores de formularios (`forms.py`), control de estados operativos y restricciones temporales basadas en los horarios comerciales vigentes.
  - Sistema de encriptación de tokens para la verificación de correos y despacho asíncrono/síncrono de notificaciones transaccionales a través del backend SMTP de Django.

- **Cumplimiento Normativo y Privacidad (`legales`):**
  - Middleware y componentes de cumplimiento RGPD incrustados en los flujos de entrada de datos (banners de cookies, avisos legales, políticas de privacidad y validación de casillas de consentimiento obligatorio en formularios).

- **Seguridad y Control de Acceso (`usuarios`):**
  - Sistema de autenticación basado en el ORM de Django con diferenciación de privilegios mediante decoradores y flags de permisos (`is_staff`, superusuarios).
  - Protección de rutas administrativas y puntos de API internos frente a accesos no autorizados.

## Instalacion Local
Requisitos previos:
- Python (versión 3.10 o superior recomendada)
- Git

Pasos para la puesta en marcha:

1. Clona el repositorio y sitúate en la raíz del proyecto:
git clone [https://github.com/DanielMedina23/LDJSystem.git]
cd LDJSystem

2. Montar el entorno virtual:
python -m venv venv

3. Activar el entorno virtual
# En Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# En Linux/macOS:
source venv/bin/activate

4. Configura las variables de entorno creando un archivo .env en la raíz (ajustando credenciales de base de datos, DEBUG, etc.).

5. Aplica las migraciones de base de datos y arranca el servidor de desarrollo:

-python manage.py migrate
-python manage.py runserver

6. Luego abre en tu navegador:
    http://127.0.0.1:8000

## Variables de Entorno Importantes
Crea un archivo `.env` en la raíz del proyecto basándote en los siguientes parámetros de configuración:

- `DEBUG`: Modo de depuración (`True` para desarrollo local, `False` para producción).
- `SECRET_KEY`: Clave secreta de encriptación de Django.
- `DB_NAME`: Nombre de la base de datos (ej. `ldjsystem`).
- `DB_USER`: Usuario del sistema gestor de base de datos.
- `DB_PASSWORD`: Contraseña de acceso a la base de datos.
- `DB_HOST`: Host de conexión (ej. `localhost` o IP del servidor).
- `DB_PORT`: Puerto del servicio de base de datos (ej. `5432` para PostgreSQL).
- `EMAIL_HOST_USER`: Dirección de correo electrónico utilizada para el envío de notificaciones y confirmaciones SMTP.
- `EMAIL_HOST_PASSWORD`: Contraseña de aplicación o credencial SMTP del servicio de correo.
- `GOOGLE_MAPS_REVIEW_URL`: Enlace de redirección para reseñas o ubicación en Google Maps integrado en el sistema de reservas.

## Notas de Integridad de Datos y Operativa
- **Unicidad de Horarios:** El sistema valida y renderiza los bloques horarios asegurando un único registro por día de la semana para evitar duplicidades en la vista pública.

- **Gestión de Mesas y Planos:** Las reservas interactúan directamente con los identificadores espaciales y de aforo, manteniendo la consistencia entre la selección gráfica y el backend.

- **Tokens y Verificación por Correo:** Las confirmaciones de reserva implementan verificación mediante tokens y envío SMTP con parámetros previamente delimitados.

## Listo Para Produccion
Antes de desplegar la aplicación en un entorno de producción, es recomendable revisar el siguiente checklist:

- Configurar `DEBUG=False` y utilizar una `SECRET_KEY` robusta y única.
- Asegurar las variables de conexión a una base de datos de producción (PostgreSQL) con políticas de respaldo activas.
- Configurar correctamente los dominios permitidos en `ALLOWED_HOSTS`.
- Establecer un servicio SMTP real (`EMAIL_HOST_*`) para el despacho fiable de los correos de confirmación.
- Ejecutar la recolección de archivos estáticos:
  ```bash:
  python manage.py collectstatic
