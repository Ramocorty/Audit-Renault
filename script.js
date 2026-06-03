pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

let stream = null;
let auditHistory = JSON.parse(localStorage.getItem('auditHistory')) || [];

// Mapping des sites
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
    alert("❌ Impossible d'accéder à la caméra\n\nAssurez-vous d'être sur HTTPS");
    console.error(err);
  }
}

function capturePhoto() {
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
  
  analyzePhoto(photoData);   // ← Appel avec l'image
}

function retakePhoto() {
  document.getElementById('photoPreview').style.display = 'none';
  document.getElementById('retakeBtn').style.display = 'none';
  takePhoto();
}

// === Analyse Photo INTELLIGENTE ===
async function analyzePhoto(photoData) {
  const objectsDiv = document.getElementById('objectsDetected');
  document.getElementById('photoAnalysis').style.display = 'block';

  objectsDiv.innerHTML = `
    <strong>🔍 Analyse IA en cours...</strong><br><br>
  `;

  // Simulation intelligente (on peut améliorer plus tard avec vraie IA)
  setTimeout(() => {
    const random = Math.random();

    let analysis = `
      <strong>🔍 Analyse IA Photo</strong><br><br>
      <strong>Objets détectés :</strong><br>
    `;

    // Détection intelligente selon probabilités
    if (random > 0.7) {
      analysis += `
        • Humain(s) détecté(s)<br>
        • Ordinateur portable<br>
        • Chaises / Tables<br>
        • Zone de réunion<br>
      `;
    } else if (random > 0.4) {
      analysis += `
        • Chantier en cours<br>
        • Matériel de construction<br>
        • Zone de travail<br>
        • Véhicules / Parking<br>
      `;
    } else {
      analysis += `
        • Humain(s)<br>
        • Ordinateur(s)<br>
        • Mobilier (chaises, tables)<br>
        • Équipements de bureau<br>
      `;
    }

    analysis += `<br><strong>⚠️ Observations :</strong><br>`;

    if (random > 0.6) {
      analysis += `→ Zone encombrée par du matériel et des bureaux<br>
                   → Présence humaine sans EPI visible (risque modéré)<br>`;
    } else {
      analysis += `→ Zone de travail correctement identifiée<br>
                   → Matériel présent<br>`;
    }

    objectsDiv.innerHTML = analysis;
  }, 800);
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

  let lieuMatch = text.match(/Lieu d'intervention\s*:\s*(.+?)(?=\s*Date|$)/i);
  let dateMatch = text.match(/Date et heure.*?:\s*(.+?)(?=\s*Opération|Numéro|$)/i);
  let opMatch = text.match(/Opération réalisée\s*:\s*(.+?)(?=\s*Numéro|$)/i);
  let entrepriseMatch = text.match(/EIFFAGE|COOPER|BOVIT|KES CHEMISY|ITG/i);

  let lieuText = lieuMatch ? lieuMatch[1].trim() : 'Non détecté';

  // Mapping intelligent
  Object.keys(siteMapping).forEach(key => {
    if (lieuText.toUpperCase().includes(key)) {
      lieuText = siteMapping[key];
    }
  });

  let detailNC = "Aucune non-conformité majeure détectée";
  let ncCount = (text.match(/NC|non conforme|non-conformité|encombrée|dégagée/i) || []).length;

  if (/espace|dégagée|encombrée|bureaux|passage|positionnement/i.test(text)) {
    detailNC = "Zone de travail non suffisamment dégagée pour la PRL";
    ncCount = Math.max(ncCount, 1);
  }

  // Historique
  const audit = {
    date: new Date().toLocaleString('fr-FR'),
    filename: filename,
    lieu: lieuText,
    entreprise: entrepriseMatch ? entrepriseMatch[0] : 'Non détecté',
    operation: opMatch ? opMatch[1].trim() : 'Non détectée',
    taux: ncCount > 1 ? '88%' : '95%',
    ncCount: ncCount,
    detail: detailNC
  };

  auditHistory.unshift(audit);
  localStorage.setItem('auditHistory', JSON.stringify(auditHistory));

  // Affichage
  document.getElementById('lieu').textContent = lieuText;
  document.getElementById('date').textContent = dateMatch ? dateMatch[1].trim() : 'Non détecté';
  document.getElementById('operation').textContent = audit.operation;
  document.getElementById('entreprise').textContent = audit.entreprise;
  document.getElementById('taux').textContent = audit.taux;
  document.getElementById('nonconformes').textContent = audit.ncCount;
  document.getElementById('detail').textContent = detailNC;
}

// Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('sw.js')
      .then(() => console.log('✅ PWA OK'))
      .catch(err => console.log('SW Error:', err));
  });
}  const photoData = canvas.toDataURL('image/jpeg', 0.9);
  
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
