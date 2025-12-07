# 🛰️ Drones GIS – Plataforma Web para Gestión de Vuelos y Fotografías Geolocalizadas
**Proyecto TFG – CFGS Desarrollo de Aplicaciones Web – San Valero**

---

## 📌 Introducción
**Drones GIS** es una plataforma web desarrollada como Trabajo Fin de Grado del ciclo **Desarrollo de Aplicaciones Web**.  
Permite gestionar vuelos de dron, almacenar fotografías geolocalizadas y visualizar todo en un visor GIS interactivo basado en **Leaflet** y **CesiumJS**.

El sistema integra:
- Datos GPS desde EXIF
- Rutas de vuelo en GeoJSON
- Zonas UAS (prohibidas / restringidas / simuladas)
- API REST completa
- Herramientas avanzadas en el visor (regla, heatmap, animación de vuelo)

---

## ✨ Características principales

### 📷 Gestión de fotografías
- Subida de imágenes con lectura EXIF automática (lat/lon)
- Asignación opcional a un vuelo
- Edición completa de meta-información
- Visualización en mapa con iconos, popups e información detallada
- Exportación GeoJSON de todas las fotos o por vuelo

### ✈️ Gestión de vuelos
- Crear, listar y eliminar vuelos
- Asociar fotos a vuelos
- Guardar y editar rutas de vuelo en formato GeoJSON
- Animación del dron recorriendo la ruta

### 🗺️ Visor GIS 2D
Basado en **Leaflet**, incluye:
- Fotos geolocalizadas
- Rutas de vuelo
- Zonas UAS (simuladas)
- Heatmap de fotos
- Selector de vuelos / filtros
- Regla de distancias interactiva
- Ajuste automático de zoom a los elementos

### 🌍 Visor 3D
Versión simplificada usando **CesiumJS** para visualizar vuelos en 3D.

### 🔌 API REST (DRF)
Endpoints principales:
- `/api/photos/`
- `/api/flights/`
- `/api/zones/`

---

## 🧱 Arquitectura del proyecto

```
drones-gis/
│
├── config/                # Configuración Django
├── core/                  # Modelos, views, API y lógica principal
├── templates/             # HTML base + frontend estilizado
├── static/                # Imágenes, CSS, JS, iconos
├── media/                 # Fotos subidas por el usuario
└── manage.py
```

---

## 🛠️ Instalación y ejecución

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Accede en:

```
http://127.0.0.1:8000/
```

---

## 🧭 Flujo de trabajo recomendado

1. **Crear un vuelo**  
   → Añadir nombre, dron usado y fecha.

2. **Subir fotografías**  
   → El EXIF detecta automáticamente lat/lon si existe.

3. **Visualizar en el mapa**  
   → Fotos, rutas, zonas, heatmap y animaciones disponibles.

4. **Exportar datos**  
   → Formatos abiertos GeoJSON para usar en QGIS/ArcGIS.

---

## 📤 Exportaciones disponibles

| Tipo | URL | Descripción |
|------|------|-------------|
| Fotos | `/export/photos.geojson` | Exporta todas las fotos o filtradas por vuelo |
| Vuelos | `/export/flights.geojson` | Exporta todas las rutas de vuelo |
| Un vuelo | `/flight/<id>/export/` | Exporta un vuelo concreto |

---

## 🔐 Zonas UAS
Las zonas incluidas son **simulaciones** para uso académico:  
- Aeropuertos  
- Áreas militares  
- Zonas prohibidas y restringidas  

El sistema permite sustituirlas por capas oficiales (ej. ENAIRE).

---

## 👤 Autor
**Gustavo Díaz**  
Proyecto TFG – 2025  
Centro San Valero (DAW)  
