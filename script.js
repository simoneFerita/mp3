// script.js - LA VERSIONE PIÙ ROBUSTA PER IL DOWNLOAD
document.addEventListener('DOMContentLoaded', function() {
    // Ottenimento dei riferimenti DOM
    const youtubeForm = document.getElementById('youtubeForm');
    const youtubeInput = document.getElementById('youtubeInput');
    const videoContainer = document.getElementById('videoContainer'); 
    const downloadButton = document.getElementById('downloadButton');
    const messageArea = document.getElementById('messageArea');

    // La URL del tuo server (DEVE essere l'indirizzo live)
    const API_URL = "https://mp3-f35o.onrender.com/mp3/api/download-audio"; 
    const DOWNLOAD_URL_BASE = "https://mp3-f35o.onrender.com/mp3/download/"; 

    // ------------------------------------------------
    // FUNZIONE 1: Estrazione dell'ID (Perfetta)
    // ------------------------------------------------
    function getYouTubeId(url) {
        const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
        const match = url.match(regex);
        return match ? match[1] : null;
    }

    // ------------------------------------------------
    // FUNZIONE 2: Visualizza il Video (Perfetta)
    // ------------------------------------------------
    function displayYouTubeVideo(youtubeUrl) {
        const videoId = getYouTubeId(youtubeUrl);
        
        downloadButton.disabled = true;
        downloadButton.style.display = 'none';
        videoContainer.innerHTML = '';
        messageArea.textContent = '';

        if (videoId) {
            const embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`;
            const iframe = document.createElement('iframe');
            iframe.src = embedUrl;
            iframe.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
            iframe.allowFullScreen = true;
            iframe.title = "Player YouTube";
            videoContainer.appendChild(iframe);
            messageArea.textContent = "Video caricato. Ora puoi tentare di scaricare l'audio!";
            downloadButton.disabled = false;
            downloadButton.style.display = 'inline-block';
        } else {
            alert("❌ Link YouTube non valido.");
        }
    }

    // ------------------------------------------------
    // FUNZIONE 3: IL SERVIZIO DI DOWNLOAD (La logica che invia la richiesta)
    // ------------------------------------------------
    async function handleAudioDownload() {
        const youtubeUrl = youtubeInput.value;
        messageArea.textContent = "⏳ Richiesta di conversione inviata al SERVER... Attendi la risposta dal motore.";
        downloadButton.disabled = true;

        try {
            // 1. Richiesta al server
            const response = await fetch(API_URL, { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: youtubeUrl })
            });

            if (!response.ok) {
                // Questo avverrà se Flask/Render crasha o dà un errore 500
                const error_data = await response.json()
                throw new Error(`ERRORE DAL SERVER (${response.status}): ${error_data.get('error', 'Errore sconosciuto.')}`);
            }
            
            // 2. Recupera il filename dal JSON di successo
            const data = await response.json();
            const filename = data.get('filename');
            
            if filename) {
                messageArea.textContent = f"🎉 Download avviato! File: {filename}";
                
                // 3. Costruisce l'URL di download usando il nome del file
                const downloadUrl = DOWNLOAD_URL_BASE + filename; 
                
                // 4. FORZA IL DOWNLOAD
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = filename;
                document.body.appendChild(a);
                a.click(); 
                document.body.removeChild(a);

            } else {
                 messageArea.textContent = "❌ ERRORE: Il server non ha restituito il nome del file.";
                 downloadButton.disabled = false;
            }
        } catch (error) {
            // Questo cattura tutti i fallimenti di rete/server
            messageArea.textContent = `🛑 ERRORE CRITICO: La connessione è fallita. Controlla che il server sia attivo. Dettagli: ${error.message}`;
            console.error("Errore nel fetch:", error);
            downloadButton.disabled = false;
        }
    }

    // ------------------------------------------------
    // GESTIONE DEGLI EVENTI (L'aggancio finale)
    // ------------------------------------------------
    // 1. Gestisce il click sul bottone "Mostra Video"
    youtubeForm.addEventListener('submit', function(e) {
        e.preventDefault(); 
        const link = youtubeInput.value;
        displayYouTubeVideo(link);
    });

    // 2. Gestisce il click sul bottone "Scarica MP3"
    downloadButton.addEventListener('click', handleAudioDownload);
});
