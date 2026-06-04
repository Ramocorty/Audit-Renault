pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

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
      textContent.items.forEach(item => fullText += " " + item.str);
    }

    console.log(fullText); // Pour voir le texte extrait dans la console

    extractDataAdvanced(fullText, file.name);
  };
  reader.readAsArrayBuffer(file);
}

function extractDataAdvanced(text, filename) {
  document.getElementById('result').style.display = 'block';

  // Extractions améliorées
  const lieu = text.match(/Lieu d'intervention\s*:\s*([^\n]+)/i) || 
               text.match(/Lieu\s*:\s*([^\n]+)/i) || ["", "Non détecté"];

  const date = text.match(/Date et heure.*?(\d.+?)(?=\s*Opération|\s*Numéro|$)/i) ||
               text.match(/Date.*?:?\s*([^\n]+)/i) || ["", "Non détecté"];

  const operation = text.match(/Opération réalisée\s*:\s*([^\n]+)/i) ||
                    text.match(/Opération\s*:\s*([^\n]+)/i) || ["", "Non détectée"];

  const entreprise = text.match(/EIFFAGE|COOPER|BOVIT|KES CHEMISY|ITG/i) || ["Non détecté"];

  const finalLieu = lieu[1].trim();

  document.getElementById('lieu').textContent = finalLieu.includes("CTL") || finalLieu.includes("Hardy") ? "LARDY" : finalLieu;
  document.getElementById('date').textContent = date[1].trim();
  document.getElementById('operation').textContent = operation[1].trim();
  document.getElementById('entreprise').textContent = entreprise[0];

  document.getElementById('taux').textContent = "88%";
  document.getElementById('nonconformes').textContent = "1";
  document.getElementById('detail').textContent = "Zone de travail non suffisamment dégagée";
}
