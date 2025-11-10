# Configuración de Seguridad

## ⚠️ Archivos Sensibles

Este proyecto utiliza un archivo `.gitignore` completo para proteger información sensible. Los siguientes archivos **NUNCA** deben ser subidos a GitHub:

### Archivos de Configuración
- `application.properties` - Contiene credenciales de base de datos
- `application.yml` - Configuración alternativa
- Cualquier archivo `application-*.properties` o `application-*.yml`
- Archivos `.env` con variables de entorno

### Credenciales y Certificados
- Archivos `.key`, `.pem`, `.p12`, `.jks`, `.keystore`
- `credentials.json`, `secrets.json`
- Cualquier archivo que contenga contraseñas, tokens o API keys

## 📝 Configuración Inicial

### Para Desarrolladores

1. **Copiar el archivo de ejemplo**:
   ```bash
   cd "Back/ToDo API/src/main/resources"
   cp application.properties.example application.properties
   ```

2. **Configurar credenciales locales**:
   Editar `application.properties` y reemplazar:
   ```properties
   spring.datasource.password=${MYSQL_PASSWORD:your_password_here}
   ```
   Por tu contraseña real de MySQL:
   ```properties
   spring.datasource.password=${MYSQL_PASSWORD:tu_contraseña_real}
   ```

3. **Crear la base de datos**:
   ```bash
   mysql -u root -p
   CREATE DATABASE IF NOT EXISTS db_todo_api;
   exit;
   ```

4. **Importar el esquema** (opcional, si quieres datos de ejemplo):
   ```bash
   mysql -u root -p db_todo_api < db_todo_api.sql
   ```

## 🔒 Mejores Prácticas

### Variables de Entorno (Recomendado)

En lugar de hardcodear las contraseñas, usa variables de entorno:

1. **Linux/Mac**:
   ```bash
   export MYSQL_USER=root
   export MYSQL_PASSWORD=tu_contraseña
   ```

2. **Windows (CMD)**:
   ```cmd
   set MYSQL_USER=root
   set MYSQL_PASSWORD=tu_contraseña
   ```

3. **Windows (PowerShell)**:
   ```powershell
   $env:MYSQL_USER="root"
   $env:MYSQL_PASSWORD="tu_contraseña"
   ```

### En el IDE (IntelliJ IDEA)

1. Click en el nombre del proyecto en la barra superior
2. Seleccionar "Edit Configurations..."
3. En "Environment variables" agregar:
   - `MYSQL_USER=root`
   - `MYSQL_PASSWORD=tu_contraseña`

## 🚫 Qué NO hacer

❌ **NUNCA** hagas commit de:
- Contraseñas en texto plano
- Archivos `application.properties` con credenciales reales
- Tokens de API o claves secretas
- Certificados o keystores

✅ **SIEMPRE** usa:
- Archivos `.example` para compartir la estructura
- Variables de entorno para credenciales
- `.gitignore` para proteger archivos sensibles

## 📦 Archivos Incluidos en .gitignore

El proyecto incluye `.gitignore` en dos niveles:

1. **Raíz del proyecto** (`/.gitignore`):
   - Archivos del sistema operativo
   - Configuraciones de IDEs
   - Archivos temporales
   - Credenciales y variables de entorno

2. **Backend** (`/Back/ToDo API/.gitignore`):
   - Archivos compilados de Java
   - Directorio `target/`
   - Archivos `application.properties`
   - Configuraciones específicas del IDE

## 🔍 Verificar antes de hacer Commit

Antes de hacer commit, verifica que no estás incluyendo archivos sensibles:

```bash
git status
git diff
```

Si accidentalmente agregaste un archivo sensible:

```bash
# Removerlo del stage
git reset HEAD archivo_sensible.properties

# O removerlo del historial si ya hiciste commit
git rm --cached archivo_sensible.properties
git commit -m "Remove sensitive file"
```

## 📞 Contacto

Si encuentras algún archivo sensible expuesto en el repositorio, por favor contacta inmediatamente al equipo de desarrollo.
