// Navigation
function goToHome() {
  document.getElementById('homeScreen').style.display = 'block';
  document.getElementById('scanScreen').style.display = 'none';
  document.getElementById('resultScreen').style.display = 'none';
}

function goToScan() {
  document.getElementById('homeScreen').style.display = 'none';
  document.getElementById('scanScreen').style.display = 'block';
  document.getElementById('resultScreen').style.display = 'none';
}

function goToResult() {
  document.getElementById('homeScreen').style.display = 'none';
  document.getElementById('scanScreen').style.display = 'none';
  document.getElementById('resultScreen').style.display = 'block';
}

// Gestion du fichier
function handleFile(input) {
  if (input.files.length > 0) {
    console.log("Fichier sélectionné :", input.files[0].name);
  }
}

// Simulation d'analyse
function analyzeDocument() {
  goToResult();
  
  const content = document.getElementById('resultContent');
  content.innerHTML = `
    <h2 style="color:#ffcc00; margin-bottom:15px">✅ Audit Terminé</h2>
    <p><strong>Site :</strong> CTL - Lardy</p>
    <p><strong>Bâtiment :</strong> 125</p>
    <p><strong>Entreprise :</strong> EIFFAGE</p>
    <p><strong>Date :</strong> 10/04/2026</p>
    
    <hr style="margin:20px 0; border-color:#ffcc00">
    
    <h3 style="color:#00ff88; font-size:32px; margin:15px 0">94.4% conforme</h3>
    
    <p><strong>1 point non conforme :</strong></p>
    <p style="color:#ffaa00; background:rgba(255,170,0,0.1); padding:12px; border-radius:8px">
      Les intervenants n’ont pas suffisamment d’espace pour travailler efficacement dans les lieux prépond à l’aide de la PRL.
    </p>
    
    <button onclick="goToHome()" style="margin-top:30px; width:100%; padding:16px; background:#ffcc00; color:#001a4d; border:none; border-radius:12px; font-weight:bold; font-size:16px">
      Retour à l'accueil
    </button>
  `;
}

// Initialisation au chargement
window.onload = function() {
  goToHome();
};