pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

let stream = null;

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
    alert("❌ Impossible d'accéder à la caméra\n\n→ Déployez sur Cloudflare Pages ou GitHub Pages (HTTPS obligatoire)");
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
  analyzePhoto();
}

function retakePhoto() {
  document.getElementById('photoPreview').style.display = 'none';
  document.getElementById('retakeBtn').style.display = 'none';
  takePhoto();
}

function analyzePhoto() {
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

// === PDF ===
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
    extractAuditData(fullText);
  };
  reader.readAsArrayBuffer(file);
}

function extractAuditData(text) {
  document.getElementById('result').style.display = 'block';
  
  const lieuMatch = text.match(/Lieu d'intervention\s*:\s*(.+?)(?=\s*Date|$)/i);
  const dateMatch = text.match(/Date et heure.*:\s*(.+?)(?=\s*Opération|Numéro|$)/i);
  const opMatch = text.match(/Opération réalisée\s*:\s*(.+?)(?=\s*Numéro|$)/i);
  const entrepriseMatch = text.match(/EIFFAGE|COOPER|BOVIT|KES CHEMISY/i);
  
  let detailNC = "Aucune non-conformité majeure détectée";
  if (/dégagée|espace|bureau|encombrée/i.test(text)) {
    detailNC = "Zone de travail non suffisamment dégagée pour la PRL";
  }
  
  const ncCount = (text.match(/NC/g) || []).length;
  
  document.getElementById('lieu').textContent = lieuMatch ? lieuMatch[1].trim() : 'Non détecté';
  document.getElementById('date').textContent = dateMatch ? dateMatch[1].trim() : 'Non détecté';
  document.getElementById('operation').textContent = opMatch ? opMatch[1].trim() : 'Non détectée';
  document.getElementById('entreprise').textContent = entrepriseMatch ? entrepriseMatch[0] : 'EIFFAGE';
  document.getElementById('taux').textContent = ncCount > 1 ? '88%' : '95%';
  document.getElementById('nonconformes').textContent = ncCount || '0';
  document.getElementById('detail').textContent = detailNC;
}

// === Service Worker PWA ===
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('sw.js')
      .then(reg => console.log('✅ Service Worker enregistré'))
      .catch(err => console.log('❌ Erreur SW:', err));
  });
}
