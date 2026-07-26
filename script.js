// Ottenimento dei riferimenti DOM
const youtubeForm = document.getElementById('youtubeForm');
const youtubeInput = document.getElementById('youtubeInput');
const videoContainer = document.getElementById('videoContainer'); 
const downloadButton = document.getElementById('downloadButton');
const messageArea = document.getElementById('messageArea');

// ------------------------------------------------
// FUNZIONE 1: Estrazione dell'ID (perfetta)
// ------------------------------------------------
function getYouTubeId(url) {
    const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
    const match = url.match(regex);
    return match ? match[1] : null;
}

// ------------------------------------------------
// FUNZIONE 2: Visualizza il Video (come prima)
// ------------------------------------------------
function displayYouTubeVideo(youtubeUrl) {
    const videoId = getYouTubeId(youtubeUrl);
    
    // Reset dello stato prima di caricare
    downloadButton.disabled = true;
    downloadButton.style.display = 'none';
    videoContainer.innerHTML = '';
    messageArea.textContent = '';


    if (videoId) {
        // Costruisce il lettore
        const embedUrl = `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`;
        const iframe = document.createElement('iframe');
        iframe.src = embedUrl;
        iframe.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
        iframe.allowFullScreen = true;
        iframe.title = "Player YouTube";
        
        videoContainer.appendChild(iframe);
        messageArea.textContent = "Video caricato. Ora puoi tentare di scaricare l'audio!";

        // Abilita il bottone download
        downloadButton.disabled = false;
        downloadButton.style.display = 'inline-block';

    } else {
        alert("❌ Link YouTube non valido.");
    }
}

// ------------------------------------------------
// FUNZIONE 3: IL SERVIZIO DI DOWNLOAD (IL PLACEHOLDER DEL BACKEND)
// ------------------------------------------------
// MODIFICA LA FUNZIONE HANDLE AUDIO DOWNLOAD
function handleAudioDownload() {
    const youtubeUrl = youtubeInput.value;
    messageArea.textContent = "⏳ Inviato al server (Backend) per la conversione... Aspetta 10 secondi.";
    downloadButton.disabled = true;

    // --- CHIAMATA AL TUO NUOVO SERVER (app.py) ---
    fetch('http://127.0.0.1:5000/api/download-audio', { // <-- DEVE PUNTARE AL TUO SERVER
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: youtubeUrl })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            messageArea.textContent = "✅ Successo del server! Il file è pronto. (ATTENZIONE: Qui andrebbe il download vero)";
            // Nel mondo reale, qui crei il link di download con il file_path ricevuto
            alert(`Download simulato! Percorso dal server: ${data.file_path}`); 
        } else {
            messageArea.textContent = `❌ ERRORE DAL SERVER: ${data.error}`;
        }
        downloadButton.disabled = false;
    })
    .catch(error => {
        messageArea.textContent = "🛑 ERRORE DI CONNESSIONE: Controlla che il server Python sia avviato e in esecuzione (app.py).";
        console.error("Errore nel fetch:", error);
        downloadButton.disabled = false;
    });
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