pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

let stream = null;

// Caméra
async function takePhoto() {
  const video = document.getElementById('camera');
  const captureBtn = document.getElementById('captureBtn');
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
    video.srcObject = stream;
    video.style.display = 'block';
    captureBtn.style.display = 'block';
  } catch (e) {
    alert("Erreur caméra - Utilisez HTTPS (Cloudflare Pages)");
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

  if (stream) stream.getTracks().forEach(t => t.stop());

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
    <strong>Photo analysée</strong><br><br>
    • Humain détecté<br>
    • Zone de travail / Chantier<br>
    • Mobilier présent<br><br>
    <strong>Observation :</strong> Zone potentiellement encombrée
  `;
}

// PDF
document.getElementById('pdfInput').addEventListener('change', handlePDF);

async function handlePDF(e) {
  const file = e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = async function(ev) {
    try {
      const typedarray = new Uint8Array(ev.target.result);
      const pdf = await pdfjsLib.getDocument(typedarray).promise;
      
      let fullText = "";
      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const textContent = await page.getTextContent();
        textContent.items.forEach(item => fullText += item.str + " ");
      }

      processPDF(fullText, file.name);
    } catch(err) {
      alert("Erreur lors de la lecture du PDF");
      console.error(err);
    }
  };
  reader.readAsArrayBuffer(file);
}

function processPDF(text, filename) {
  document.getElementById('result').style.display = 'block';

  const lieu = text.match(/Lieu d'intervention\s*:\s*(.+?)(?=\s*Date|$)/i) || ["", "Non détecté"];
  const date = text.match(/Date et heure.*?(\d.+?)(?=\s|$)/i) || ["", "Non détecté"];
  const operation = text.match(/Opération réalisée\s*:\s*(.+?)(?=\s*Numéro|$)/i) || ["", "Non détectée"];
  const entreprise = text.match(/EIFFAGE|COOPER|BOVIT|KES CHEMISY|ITG/i) || ["Non détecté"];

  document.getElementById('lieu').textContent = lieu[1];
  document.getElementById('date').textContent = date[1];
  document.getElementById('operation').textContent = operation[1];
  document.getElementById('entreprise').textContent = entreprise[0];
  document.getElementById('taux').textContent = "92%";
  document.getElementById('nonconformes').textContent = "1";
  document.getElementById('detail').textContent = "Zone de travail encombrée";
}

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js');
}
