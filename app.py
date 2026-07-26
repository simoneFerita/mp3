# app.py - IL MOTORE PYTHON COMPLETO E FINALE (Versione SICURA)
from flask import Flask, request, jsonify, send_from_directory
import subprocess
import os 
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy 
import mysql.connector 

# =====================================================
# 1. CONFIGURAZIONE DATABASE (SICURA)
# =====================================================

app = Flask(__name__)
CORS(app) 

# -------------------------------------------------
# TRUCCO DI SICUREZZA: Legge i dati dall'ambiente operativo (NON dal codice)
# -------------------------------------------------
try:
    # Recupera le variabili d'ambiente fornite da Render
    db_user = os.environ.get('DATABASE_USER')
    db_pass = os.environ.get('DATABASE_PASSWORD')
    db_name = os.environ.get('DATABASE_NAME')
    db_host = os.environ.get('DATABASE_HOST')
    
    if not db_user or not db_pass or not db_name or not db_host:
        raise ValueError("ERRORE: Le variabili di ambiente del database non sono state impostate!")

    # Costruisce l'URI di connessione
    DATABASE_URI = f'mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}'
except ValueError as e:
    print(e)
    # Blocca l'avvio se le credenziali non sono state impostate
    exit()


app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELLO DEL DATABASE ---
class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    artist = db.Column(db.String(128), nullable=False)
    filename = db.Column(db.String(128), unique=True, nullable=False)
    youtube_url = db.Column(db.String(512))


# Esegui questa parte UNA SOLA VOLTA per creare la tabella
with app.app_context():
    db.create_all()
    print("\n=====================================================")
    print("✅ Database e Tabelle MySQL creati con successo!")
    print("=====================================================")


# =====================================================
# 2. FUNZIONE DI ESTRAZIONE E CONVERSIONE (IL MOTORE)
# =====================================================
# ... (Il resto di questa funzione non cambia) ...
# (Copia l'intera funzione 'extract_audio_from_youtube' da cui sopra)
def extract_audio_from_youtube(youtube_url):
    # ... (INCOLLA QUI L'INTERA FUNZIONE) ...
    output_template = "%(title)s.%(ext)s" 
    try:
        command = [
            'yt-dlp', 
            '--extract-audio', 
            '-x',                
            '--audio-format', 'mp3', 
            '-o', output_template, 
            youtube_url
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)
        
        filename_found = [f for f in os.listdir('.') if f.endswith('.mp3')]
        
        if filename_found:
            final_filename = filename_found[0] 
            
            base_name = os.path.splitext(final_filename)[0]
            parts = base_name.split(' - ')
            
            if len(parts) >= 2:
                artist_name = parts[0].strip()
                title_name = parts[1].strip()
            else:
                artist_name = "Sconosciuto"
                title_name = base_name
            
            return {
                "success": True, 
                "filename": final_filename, 
                "title": title_name, 
                "artist": artist_name
            }
        else:
            return {"success": False, "error": "Conversione avvenuta, ma il file .mp3 non è stato trovato."}

    except Exception as e:
        return {"success": False, "error": f"ERRORE: Controlla yt-dlp e ffmpeg! Dettagli: {e}"}


# ------------------------------------------------
# API ENDPOINT 1: INIZIA IL LAVORO E SALVA NEL DB
# ------------------------------------------------
@app.route('/api/download-audio', methods=['POST'])
def handle_download_request():
    # ... (Il resto della logica rimarrà identica) ...
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"success": False, "error": "URL non fornito"}), 400

    youtube_url = data['url']
    
    extraction_result = extract_audio_from_youtube(youtube_url)

    if extraction_result['success']:
        filename = extraction_result['filename']
        
        try:
            song_record = Song(
                title=extraction_result['title'],
                artist=extraction_result['artist'],
                filename=filename,
                youtube_url=youtube_url
            )
            db.session.add(song_record)
            db.session.commit()
            
            return jsonify({"success": True, "filename": filename})
        except Exception as e:
             return jsonify({"success": False, "error": f"Errore al salvataggio nel database: {e}"})
    else:
        return jsonify(extraction_result), 500 


# ------------------------------------------------
# API ENDPOINT 2: SERVISIONE DEL FILE (IL DOWNLOAD)
# ------------------------------------------------
@app.route('/download/<filename>')
def serve_file(filename):
    # Questo carica il file MP3 dal tuo disco!
    return send_from_directory('.', filename)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
