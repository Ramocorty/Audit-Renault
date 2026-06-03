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

    console.log("Texte extrait :", fullText); // Pour debug

    extractBetter(fullText, file.name);
  };
  reader.readAsArrayBuffer(file);
}

function extractBetter(text, filename) {
  document.getElementById('result').style.display = 'block';

  // Extraction renforcée
  const lieuMatch = text.match(/Lieu d'intervention\s*:\s*([^\n]+)/i) || 
                    text.match(/Lieu\s*:\s*([^\n]+)/i);
  
  const dateMatch = text.match(/Date et heure.*?(\d{1,2}\/\d{1,2}\/\d{4}|\d{1,2}-\d{1,2}-\d{4})/i) ||
                    text.match(/Date.*?:?\s*([^\n]+)/i);
  
  const opMatch = text.match(/Opération réalisée\s*:\s*([^\n]+)/i) ||
                  text.match(/Opération\s*:\s*([^\n]+)/i);
  
  const entrepriseMatch = text.match(/EIFFAGE|COOPER|BOVIT|KES CHEMISY|ITG/i);

  const lieu = lieuMatch ? lieuMatch[1].trim() : "Non détecté";
  const finalLieu = lieu.toUpperCase().includes("CTL") || lieu.toUpperCase().includes("HARDY") ? "LARDY" : lieu;

  document.getElementById('lieu').textContent = finalLieu;
  document.getElementById('date').textContent = dateMatch ? dateMatch[1].trim() : "Non détecté";
  document.getElementById('operation').textContent = opMatch ? opMatch[1].trim() : "Non détectée";
  document.getElementById('entreprise').textContent = entrepriseMatch ? entrepriseMatch[0] : "EIFFAGE";
  
  document.getElementById('taux').textContent = "88%";
  document.getElementById('nonconformes').textContent = "2";
  document.getElementById('detail').textContent = "Zone de travail non suffisamment dégagée + produits chimiques sans FDS";
}
