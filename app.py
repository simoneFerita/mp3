# app.py - IL MOTORE PYTHON COMPLETO (Backend)
from flask import Flask, request, jsonify, send_from_directory
import subprocess
import os 
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy 
import mysql.connector # Driver di connessione a MySQL

# =====================================================
# 1. CONFIGURAZIONE DATABASE
# =====================================================

app = Flask(__name__)
CORS(app) 

# ATTENZIONE: DEVI SOSTITUIRE QUESTE VALORI CON I TUOI DATI REALI DI ALTERVISTA
DATABASE_USER = 
DATABASE_PASSWORD =  # <-- IL TUO PASSWORD
DATABASE_NAME = "simoneferita"
DATABASE_HOST = "https://simoneferita.altervista.org/mp3/" # Manteniamo localhost per il test locale

# Costruisci l'URI di connessione
DATABASE_URI = f'mysql+mysqlconnector://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# --- MODELLO DEL DATABASE (La struttura della tabella 'song') ---
class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    artist = db.Column(db.String(128), nullable=False)
    filename = db.Column(db.String(128), unique=True, nullable=False)
    youtube_url = db.Column(db.String(512))

# Esegui questa parte una sola volta per creare la tabella
with app.app_context():
    db.create_all()
    print("\n=====================================================")
    print("✅ Database e Tabelle MySQL creati con successo!")
    print("=====================================================")


# =====================================================
# 2. FUNZIONE DI ESTRAZIONE E CONVERSIONE (IL TRUCCO)
# =====================================================

def extract_audio_from_youtube(youtube_url):
    """
    Esegue yt-dlp per scaricare, estrarre l'audio e rinominare il file.
    """
    output_template = "%(title)s.%(ext)s" 
    
    try:
        # Il comando fa tutto: download, conversione in mp3, e nomina il file!
        command = [
            'yt-dlp', 
            '--extract-audio', 
            '-x',                
            '--audio-format', 'mp3', 
            '-o', output_template, 
            youtube_url
        ]
        
        # Esegue il comando (ATTENZIONE: richiede yt-dlp e ffmpeg installati sul sistema)
        subprocess.run(command, check=True, capture_output=True, text=True)
        
        # Troviamo il file appena creato nella directory corrente
        filename_found = [f for f in os.listdir('.') if f.endswith('.mp3')]
        
        if filename_found:
            final_filename = filename_found[0] 
            return {"success": True, "message": "Audio elaborato con successo!", "filename": final_filename}
        else:
            return {"success": False, "error": "Conversione avvenuta, ma il file .mp3 non è stato trovato."}

    except subprocess.CalledProcessError as e:
        return {"success": False, "error": f"ERRORE DI ESECUZIONE: Assicurati che yt-dlp e ffmpeg siano installati. Dettagli: {e.stderr}"}
    except Exception as e:
        return {"success": False, "error": f"Errore sconosciuto: {e}"}


# ------------------------------------------------
# API ENDPOINT 1: INIZIA IL LAVORO
# ------------------------------------------------
@app.route('/api/download-audio', methods=['POST'])
def handle_download_request():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"success": False, "error": "URL non fornito"}), 400

    youtube_url = data['url']
    
    # 1. Esegue la conversione e ottiene il nome del file
    extraction_result = extract_audio_from_youtube(youtube_url)

    if extraction_result['success']:
        filename = extraction_result['filename']
        
        # 2. SALVA IL RECORD NEL DATABASE (Cataloga)
        try:
            # Tentativo di estrarre Titolo e Artista dal nome del file per pulizia nel DB
            parts = filename.split(' - ')
            if len(parts) >= 2:
                title = parts[1].replace('.mp3', '').strip()
                artist = parts[0].replace('.mp3', '').strip()
            else:
                title = filename
                artist = "Sconosciuto"
            
            song_record = Song(
                title=title,
                artist=artist,
                filename=filename,
                youtube_url=youtube_url
            )
            db.session.add(song_record)
            db.session.commit()
            
            return jsonify({"success": True, "message": "Audio salvato e catalogato nel database!", "filename": filename})
        except Exception as e:
             return jsonify({"success": False, "error": f"Errore al salvataggio nel database: {e}"})
    else:
        return jsonify(extraction_result), 500 


# ------------------------------------------------
# API ENDPOINT 2: SERVISIONE DEL FILE (IL DOWNLOAD)
# ------------------------------------------------
@app.route('/download/<filename>')
def serve_file(filename):
    # Questo dice al server: "Dai questo file all'utente che lo ha chiesto."
    return send_from_directory('.', filename)


if __name__ == '__main__':
    print("\n=====================================================")
    print("✅ SERVER PRONTO! Avviare la conversione e il download.")
    print("=====================================================")
    # Per il test locale:
    app.run(debug=True, port=5000)