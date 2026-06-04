export async function onRequestPost({ request, env }) {
  try {
    const data = await request.json();

    const isGrille = data.type === "grille_detaillee";

    const result = await env.DB.prepare(`
      INSERT INTO audits (
        dateCreation, lieu, dateHeureVisite, operation, planPrevention,
        chargeAffaire, entrepriseRang1, entrepriseRang2,
        arretChantier, courrierAR, contreVisite,
        nomRenault, signatureRenault, nomExterne, signatureExterne,
        type_audit, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10,
        q11, q12, q13, q14, q15, q16, q17, q18, q19, q20,
        q21, q22, q23, q24, q25, q26
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(
      new Date().toISOString(),
      data.lieu || '',
      data.dateHeureVisite || '',
      data.operation || '',
      data.planPrevention || '',
      data.chargeAffaire || '',
      data.entrepriseRang1 || '',
      data.entrepriseRang2 || '',
      data.arretChantier || 'Non',
      data.courrierAR || 'Non',
      data.contreVisite || 'Non',
      data.nomRenault || '',
      data.signatureRenault || '',
      data.nomExterne || '',
      data.signatureExterne || '',
      isGrille ? 'grille_detaillee' : 'audit_standard',
      data.q1 || 'NC', data.q2 || 'NC', data.q3 || 'NC', data.q4 || 'NC', data.q5 || 'NC',
      data.q6 || 'NC', data.q7 || 'NC', data.q8 || 'NC', data.q9 || 'NC', data.q10 || 'NC',
      data.q11 || 'NC', data.q12 || 'NC', data.q13 || 'NC', data.q14 || 'NC', data.q15 || 'NC',
      data.q16 || 'NC', data.q17 || 'NC', data.q18 || 'NC', data.q19 || 'NC', data.q20 || 'NC',
      data.q21 || 'NC', data.q22 || 'NC', data.q23 || 'NC', data.q24 || 'NC', data.q25 || 'NC',
      data.q26 || 'NC'
    ).run();

    return Response.json({ 
      success: true, 
      message: isGrille ? "Grille détaillée enregistrée" : "Audit enregistré",
      id: result.meta.last_row_id 
    });

  } catch (err) {
    console.error(err);
    return Response.json({ success: false, error: err.message }, { status: 500 });
  }
}

export async function onRequestGet({ env }) {
  try {
    const { results } = await env.DB.prepare("SELECT * FROM audits ORDER BY dateCreation DESC").all();
    return Response.json(results || []);
  } catch (err) {
    console.error(err);
    return Response.json({ success: false, error: err.message }, { status: 500 });
  }
}
