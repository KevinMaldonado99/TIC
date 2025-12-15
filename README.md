# 🧬 TIC – Malware Classifier ( Ransomware vs Benign)

Sistema de análisis estático basado en Machine Learning para clasificar archivos PE en categorías de **Malware** (Trojan o Ransomware, según la rama seleccionada) y **Benignos**.

Este proyecto incluye:

- 🧠 Modelos entrenados para:
  - **Trojan vs Benign**
  - **Ransomware vs Benign**
- 🌐 Backend en **Flask**
- 💻 Frontend en **React + Vite**
- 📊 Reportes dinámicos y análisis forense
- 🔐 Validación estricta de estructura del CSV (75 características exactas)

Puedes ejecutar cualquiera de las variantes simplemente **cambiando de rama**.


## 📥 1. Clonar el repositorio

git clone https://github.com/EstherZumba/TIC.git

## 2 Cambiar de rama:
git checkout Trojan-Final
o
git checkout Ransomware-Final

## 3 Configurar y ejecutar el Backend (Flask)
cd backend
# 3.1 Crear entorno virtual
python -m venv env

# 3.2 Activar entorno
env\Scripts\activate

# 3.3 Ejecutar el servidor Flask
python app/app.py

> http://localhost:5000

## 3.4 Configurar y ejecutar el Frontend (React + Vite)
cd ../frontend

# 4. Instalar dependencias
npm install

# 4.1 Ejecutar la aplicación
npm run dev

> http://localhost:5173


## 📊 5. Uso del sistema

Con el backend y frontend ejecutándose:
1. Ejecuta el servidor flask (backend)
2. Abre la interfaz web en http://localhost:5173.
3. Haz clic en el círculo animado.
4. Selecciona un archivo CSV con las características del ejecutable.
5. El sistema realizará automáticamente:
  - Validación estricta de que el CSV tenga exactamente las 75 columnas del modelo.
  - Conversión y verificación de tipos numéricos.
  - Clasificación (Benign vs Trojan o Benign vs Ransomware según la rama).
  - Cálculo de confianza promedio.
  - Nivel de riesgo (Alto / Medio / Bajo).
  - Análisis forense (hashes, tiempo de análisis, top features).
  - Generación de enlace a reporte PDF.


### 🔍 5.1 Detalles importantes

- Cada rama contiene modelos distintos (`.pkl`) y archivos ajustados al tipo de malware.
- El frontend reconoce automáticamente si el resultado proviene de un modelo **Trojan** o **Ransomware**, ya que proviene del backend.
- El backend valida estrictamente que el CSV tenga las **75 columnas reales del modelo**.

## 🧠 6 . Explicación del modelo y entrenamiento

El sistema utiliza **Machine Learning basado en varios modelos**, entrenado con características estáticas extraídas de archivos PE:

- Tamaños de sección
- Flags del PE header
- DLL characteristics
- Permisos
- Cantidad de llamadas a API
- Métricas del import table
- Indicadores de comportamiento (lectura de registro, EntryPoint, SizeOfCode, SizeOfUninitializedData, etc.)

El flujo de entrenamiento fue:

1. **Extracción de características** con un script estático → genera CSV con ~75 columnas.
2. **Limpieza, normalización y verificación**.
3. Entrenamiento de:
   - Modelo 1: **Trojan vs Benign**
   - Modelo 2: **Ransomware vs Benign**
4. Validación cruzada (cross-validation)
5. Exportación del modelo con pickle.


### 🔐 7 Validación estricta del CSV

Durante la predicción, el backend verifica:

✔ Que el CSV contenga las 75 columnas exactas  
✔ Que todas sean numéricas  
✔ Que ninguna esté vacía  
✔ Que no existan columnas desconocidas  
✔ Que la confianza > 75% (para evitar muestras fuera del dominio)

Esto garantiza reproducibilidad y seguridad.


## 📝 8. Generación de reportes PDF

El sistema genera un **reporte forense** con:

- Hash MD5 / SHA256  
- Fecha del análisis  
- Tiempo de procesamiento  
- Clase detectada  
- Nivel de riesgo  
- Confianza promedio  
- Métricas sintéticas (Precision, Recall, F1-Score)  
- Top 8 características influyentes  
- Información técnica del dataset  


El PDF **no requiere bases de datos** y **no guarda información**.

### 🧪 Interfaz de carga
<img width="1528" height="769" alt="imagen" src="https://github.com/user-attachments/assets/322bd373-f030-4b5a-a773-09a53e0cfe38" />







