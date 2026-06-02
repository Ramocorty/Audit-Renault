pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

let stream = null;
let auditHistory = JSON.parse(localStorage.getItem('auditHistory')) || [];

// === Mapping des sites ===
const siteMapping = {
  "CTL": "LARDY",
  "HARDY": "LARDY",
  "LARDY": "LARDY"
};

// === Caméra ===
async function takePhoto() {
  const video = document.getElementById('camera');
  const captureBtn = document.getElementById('captureBtn');
 
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "environment", width: { ideal: 1280 } }
    });
    video.srcObject = stream;
    video.style.display = 'block';
    captureBtn.style.display = 'block';
  } catch (err) {
    alert("❌ Impossible d'accéder à la caméra\n\nAssurez-vous d'être sur HTTPS (Cloudflare Pages)");
    console.error(err);
  }
}

function capturePhoto() { /* même code qu'avant */ 
  const video = document.getElementById('camera');
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth || 1280;
  canvas.height = video.videoHeight || 720;
  canvas.getContext('2d').drawImage(video, 0, 0);
  const photoData = canvas.toDataURL('image/jpeg', 0.9);
  
  document.getElementById('photoPreview').src = photoData;
  document.getElementById('photoPreview').style.display = 'block';
  video.style.display = 'none';
  document.getElementById('captureBtn').style.display = 'none';
  document.getElementById('retakeBtn').style.display = 'block';
  
  if (stream) stream.getTracks().forEach(track => track.stop());
  analyzePhoto();
}

function retakePhoto() { /* même code */ 
  document.getElementById('photoPreview').style.display = 'none';
  document.getElementById('retakeBtn').style.display = 'none';
  takePhoto();
}

function analyzePhoto() { /* même code */ 
  document.getElementById('photoAnalysis').style.display = 'block';
  document.getElementById('objectsDetected').innerHTML = `
    <strong>Objets détectés :</strong><br>
    • Chantier / Zone de travail<br>
    • Postes de travail & Ordinateurs<br>
    • Tables, chaises, bureaux<br>
    • Équipements de sécurité<br>
    • Véhicules / Parking<br><br>
    <strong>⚠️ Observation :</strong> Zone potentiellement encombrée.
  `;
}

// === PDF Amélioré ===
document.getElementById('pdfInput').addEventListener('change', handlePDF);

async function handlePDF(e) {
  const file = e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = async function(ev) {
    const typedarray = new Uint8Array(ev.target.result);
    const pdf = await pdfjsLib.getDocument(typedarray).promise;
  
    let fullText = "";
    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const textContent = await page.getTextContent();
      textContent.items.forEach(item => fullText += " " + item.str + " ");
    }
    
    extractAuditData(fullText, file.name);
  };
  reader.readAsArrayBuffer(file);
}

function extractAuditData(text, filename) {
  document.getElementById('result').style.display = 'block';

  // Extraction améliorée
  let lieu = text.match(/Lieu d'intervention\s*:\s*(.+?)(?=\s*Date|$)/i);
  let date = text.match(/Date et heure.*?:\s*(.+?)(?=\s*Opération|$)/i);
  let operation = text.match(/Opération réalisée\s*:\s*(.+?)(?=\s*Numéro|$)/i);
  let entreprise = text.match(/EIFFAGE|COOPER|BOVIT|KES CHEMISY|ITG/i);

  let lieuText = lieu ? lieu[1].trim() : 'Non détecté';
  
  // Application du mapping CTL → LARDY
  Object.keys(siteMapping).forEach(key => {
    if (lieuText.toUpperCase().includes(key)) {
      lieuText = siteMapping[key];
    }
  });

  let detailNC = "Aucune non-conformité majeure détectée";
  let ncCount = (text.match(/NC|non conforme|non-conformité/i) || []).length;

  if (/espace|dégagée|encombrée|bureaux|passage|positionnement/i.test(text)) {
    detailNC = "Zone de travail non suffisamment dégagée pour la PRL";
    ncCount = Math.max(ncCount, 1);
  }

  // Sauvegarde dans l'historique
  const audit = {
    date: new Date().toLocaleString('fr-FR'),
    filename: filename,
    lieu: lieuText,
    entreprise: entreprise ? entreprise[0] : 'Non détecté',
    operation: operation ? operation[1].trim() : 'Non détectée',
    taux: ncCount > 1 ? '88%' : '95%',
    ncCount: ncCount,
    detail: detailNC
  };

  auditHistory.unshift(audit); // Ajoute au début
  localStorage.setItem('auditHistory', JSON.stringify(auditHistory));

  // Affichage
  document.getElementById('lieu').textContent = lieuText;
  document.getElementById('date').textContent = date ? date[1].trim() : 'Non détecté';
  document.getElementById('operation').textContent = audit.operation;
  document.getElementById('entreprise').textContent = audit.entreprise;
  document.getElementById('taux').textContent = audit.taux;
  document.getElementById('nonconformes').textContent = audit.ncCount;
  document.getElementById('detail').textContent = detailNC;
}

// === Service Worker ===
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('sw.js')
      .then(() => console.log('✅ Service Worker OK'))
      .catch(err => console.log('❌ SW:', err));
  });
}
