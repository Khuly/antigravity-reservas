# Sistema de Gestión de Reservas Multi-Plataforma

Sistema profesional de producción que integra **Instagram Messaging API**, **Facebook Messenger API** y **WhatsApp Cloud API** para gestionar reservas de manera unificada mediante una aplicación desktop.

## 🎯 Características Principales

- ✅ **Aplicación Desktop** con interfaz Tkinter
- ✅ **Servidor Local FastAPI** para recibir webhooks de Meta
- ✅ **Integración Unificada** de Instagram + Messenger + WhatsApp
- ✅ **Detección Automática** de intenciones de reserva con NLP básico
- ✅ **Sistema de Notificaciones** con campana y contador
- ✅ **Gestión de Estados** (Pendiente → Confirmado/Rechazado)
- ✅ **Historial Completo** de conversaciones
- ✅ **Función "Llamar al Agente"** vía WhatsApp

## 📋 Requisitos

- Python 3.11+
- Cuenta de Meta Developer
- App de Facebook configurada
- Página de Facebook/Instagram
- WhatsApp Business Account
- ngrok o Cloudflare Tunnel (para exponer localhost)

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Khuly/antigravity-reservas.git
cd antigravity-reservas
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copiar el archivo de ejemplo y configurar las credenciales:

```bash
copy .env.example .env
```

Editar `.env` con tus credenciales de Meta.

## 🔧 Configuración de Meta Apps

Ver documentación completa en el README original para configurar webhooks y obtener tokens de acceso.

## 🏃 Ejecución

### Iniciar el servidor FastAPI

```bash
python main.py
```

El servidor estará disponible en `http://localhost:8000`

### Iniciar la interfaz web Streamlit

```bash
streamlit run streamlit_app.py
```

## 📁 Estructura del Proyecto

```
antigravity-reservas/
├── main.py                      # Servidor FastAPI
├── streamlit_app.py             # Punto de entrada Streamlit
├── requirements.txt             # Dependencias
├── .env.example                 # Template de variables
│
├── config/                      # Configuración
├── routers/                     # Webhooks
├── services/                    # Lógica de negocio
├── database/                    # Modelos y ORM
├── ui/                          # Interfaz Streamlit
└── utils/                       # Utilidades
```

## 🔐 Seguridad

- ✅ Validación de firma HMAC SHA256 en todos los webhooks
- ✅ Verify token personalizado
- ✅ Variables de entorno para credenciales
- ✅ `.gitignore` configurado para no subir secretos

## 📄 Licencia

Proyecto privado - Todos los derechos reservados

## ✨ Autor

Desarrollado como sistema profesional de producción para gestión de reservas multi-plataforma.
