// ======================
// API Audits - Cloudflare Pages Functions
// ======================

export async function onRequestPost({ request, env }) {
  try {
    const audit = await request.json();

    const result = await env.DB.prepare(`
      INSERT INTO audits (
        dateCreation, lieu, dateHeureVisite, operation, planPrevention,
        chargeAffaire, entrepriseRang1, entrepriseRang2,
        arretChantier, courrierAR, contreVisite,
        nomRenault, signatureRenault, nomExterne, signatureExterne
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(
      new Date().toISOString(),
      audit.lieu || '',
      audit.dateHeureVisite || '',
      audit.operation || '',
      audit.planPrevention || '',
      audit.chargeAffaire || '',
      audit.entrepriseRang1 || '',
      audit.entrepriseRang2 || '',
      audit.arretChantier || '',
      audit.courrierAR || '',
      audit.contreVisite || '',
      audit.nomRenault || '',
      audit.signatureRenault || '',
      audit.nomExterne || '',
      audit.signatureExterne || ''
    ).run();

    return Response.json({ 
      success: true, 
      message: "Audit enregistré avec succès",
      id: result.meta.last_row_id 
    });

  } catch (err) {
    console.error(err);
    return Response.json({ success: false, error: err.message }, { status: 500 });
  }
}

// Récupérer tous les audits (pour le dashboard)
export async function onRequestGet({ env }) {
  try {
    const { results } = await env.DB.prepare(`
      SELECT * FROM audits 
      ORDER BY dateCreation DESC
    `).all();

    return Response.json(results);
  } catch (err) {
    console.error(err);
    return Response.json({ success: false, error: err.message }, { status: 500 });
  }
}
