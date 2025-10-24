from flask import Flask, render_template, request, jsonify, url_for
import pandas as pd
import numpy as np
import soundfile as sf
import os

app = Flask(__name__)
# Carpeta temporal donde se guardarán los audios
UPLOAD_FOLDER = 'static/audios'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/procesar', methods=['POST'])
def procesar():
    if 'file' not in request.files:
        return jsonify({"error": "No se subió ningún archivo"})

    archivo = request.files['file']
    if archivo.filename == '':
        return jsonify({"error": "Archivo vacío"})

    try:
        df = pd.read_csv(archivo)
    except Exception as e:
        return jsonify({"error": f"Error al leer el CSV: {e}"})

    col_tiempo = next((c for c in df.columns if "tiempo" in c.lower()), None)
    if col_tiempo is None:
        return jsonify({"error": "No se encontró columna de tiempo (ejemplo: 'Tiempo (s)')"})

    tiempo = df[col_tiempo].to_numpy(dtype=np.float64)
    dt = np.mean(np.diff(tiempo))
    fs = 1.0 / dt
    fs_int = int(round(fs))

    columnas = ["Vertical", "Axial", "Horizontal"]
    archivos_generados = []

    for eje in columnas:
        if eje not in df.columns:
            continue
        señal = df[eje].to_numpy(dtype=np.float32)
        max_val = np.max(np.abs(señal))
        if max_val > 1.0:
            señal /= max_val

        nombre = f"{eje}.wav"
        ruta = os.path.join(UPLOAD_FOLDER, nombre)
        sf.write(ruta, señal, samplerate=fs_int, subtype='FLOAT', format='WAV')

        archivos_generados.append({"nombre": nombre, "url": url_for('static', filename=f'audios/{nombre}')})

    if not archivos_generados:
        return jsonify({"error": "No se encontraron columnas de vibración válidas."})

    return jsonify({
        "mensaje": f" Audios generados con fs = {fs_int} Hz",
        "archivos": archivos_generados
    })

if __name__ == '__main__':
    app.run(debug=True)
