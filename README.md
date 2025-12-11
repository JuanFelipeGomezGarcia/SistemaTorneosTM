# 🏓 Sistema de Torneos - Tenis de Mesa

Sistema completo para la gestión de torneos de tenis de mesa con interfaz web desarrollada en Streamlit y base de datos PostgreSQL en Supabase.

## 🚀 Características

- **Sistema de Login**: Administradores y Competidores
- **Gestión de Torneos**: Crear, editar y finalizar torneos
- **Categorías**: Múltiples categorías por torneo
- **Cuadros**: Sistema de cuadros con resultados en tiempo real
- **Llaves Eliminatorias**: Generación automática de llaves
- **Base de Datos**: Persistencia completa con Supabase
- **Visualización en Vivo**: Los competidores pueden ver resultados en tiempo real

## 📋 Requisitos

- Python 3.8+
- Cuenta gratuita en Supabase
- Navegador web moderno

## 🛠️ Instalación

### 1. Clonar o descargar el proyecto

```bash
cd SistemaTorneos
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar Supabase

1. Ve a [supabase.com](https://supabase.com) y crea una cuenta gratuita
2. Crea un nuevo proyecto
3. Ve a Settings > API y copia:
   - Project URL
   - anon/public key

### 4. Configurar la base de datos

1. En tu proyecto de Supabase, ve a SQL Editor
2. Ejecuta el contenido del archivo `database/schema.sql`
3. Actualiza el archivo `database/supabase_config.py` con tus credenciales:

```python
SUPABASE_URL = "tu-project-url"
SUPABASE_KEY = "tu-anon-key"
```

### 5. Ejecutar la aplicación

```bash
streamlit run main.py
```

## 👥 Usuarios por Defecto

- **Administrador**: 
  - Usuario: `admin`
  - Contraseña: `admin123`

- **Competidor**: Acceso directo sin credenciales

## 📖 Guía de Uso

### Para Administradores

1. **Login**: Inicia sesión con credenciales de administrador
2. **Crear Torneo**: Desde el home, crea un nuevo torneo
3. **Agregar Categorías**: Define categorías con cuadros y participantes
4. **Gestionar Cuadros**: Ingresa resultados de partidos
5. **Generar Llaves**: Una vez completados los cuadros
6. **Finalizar Torneo**: Cuando todas las categorías tengan ganador

### Para Competidores

1. **Acceso**: Entra como competidor (sin credenciales)
2. **Ver Torneos**: Visualiza torneos disponibles
3. **Seguir Resultados**: Ve cuadros y llaves en tiempo real
4. **Solo Lectura**: No puede modificar resultados

## 🗂️ Estructura del Proyecto

```
SistemaTorneos/
├── main.py                 # Aplicación principal
├── requirements.txt        # Dependencias
├── README.md              # Este archivo
├── database/
│   ├── supabase_config.py # Configuración de Supabase
│   ├── db_operations.py   # Operaciones de base de datos
│   └── schema.sql         # Esquema de la base de datos
├── pages/
│   ├── vista_cuadros.py   # Página de cuadros
│   └── vista_llaves.py    # Página de llaves
└── utils/
    └── tournament_utils.py # Utilidades para torneos
```

## 🎯 Funcionalidades Principales

### Gestión de Torneos
- Crear torneos con nombre y fecha
- Estados: "En Curso" y "Finalizado"
- Historial completo de torneos

### Sistema de Categorías
- Múltiples categorías por torneo
- Configuración flexible de cuadros
- Gestión de participantes

### Cuadros de Competencia
- Distribución automática de participantes
- Ingreso de resultados (3-0, 3-1, 3-2, etc.)
- Validación de cuadros completos

### Llaves Eliminatorias
- Generación automática basada en ganadores
- Sistema de eliminación directa
- Selección de campeones

### Base de Datos
- Persistencia completa en Supabase
- Historial de todos los torneos
- Sincronización en tiempo real

## 🔧 Personalización

### Modificar Formatos de Resultado
Edita `utils/tournament_utils.py` para cambiar los formatos de resultado disponibles.

### Agregar Nuevas Funcionalidades
- Crea nuevas páginas en `pages/`
- Agrega operaciones de BD en `database/db_operations.py`
- Actualiza la navegación en `main.py`

## 🐛 Solución de Problemas

### Error de conexión a Supabase
- Verifica que las credenciales sean correctas
- Asegúrate de que el proyecto de Supabase esté activo

### Problemas con dependencias
```bash
pip install --upgrade streamlit supabase pandas
```

### La aplicación no carga
- Verifica que todas las tablas estén creadas en Supabase
- Revisa los logs de error en la consola

## 📞 Soporte

Para reportar problemas o sugerir mejoras, crea un issue en el repositorio del proyecto.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo LICENSE para más detalles.