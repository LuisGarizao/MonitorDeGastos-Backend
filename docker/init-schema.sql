-- Se ejecuta automáticamente solo la PRIMERA vez que se crea el volumen de datos.
-- Crea el esquema que tu settings.py espera vía "search_path=trackerdb".
CREATE SCHEMA IF NOT EXISTS trackerdb AUTHORIZATION CURRENT_USER;
