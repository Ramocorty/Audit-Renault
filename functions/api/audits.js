export async function onRequestPost({ request, env }) {
  try {
    const data = await request.json();

    if (data.email) {
      await env.DB.prepare("INSERT INTO logins (email, userType, consentRGPD, dateConnexion) VALUES (?, ?, ?, ?)")
        .bind(data.email, data.userType || 'externe', true, new Date().toISOString()).run();
      return Response.json({ success: true });
    }

    // Insertion exacte pour 43 colonnes
    await env.DB.prepare(`
      INSERT INTO audits (type, lieu, dateHeureVisite, operation, planPrevention, chargeAffaire,
        entrepriseRang1, entrepriseRang2, arretChantier, courrierAR, contreVisite,
        nomRenault, signatureRenault, nomExterne, signatureExterne,
        q1,q2,q3,q4,q5,q6,q7,q8,q9,q10,q11,q12,q13,q14,q15,q16,q17,q18,q19,q20,q21,q22,q23,q24,q25,q26)
      VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    `).bind(
      data.type || "grille_detaillee",
      data.lieu,
      data.dateHeureVisite || null,
      data.operation || null,
      data.planPrevention || null,
      data.chargeAffaire || null,
      data.entrepriseRang1 || null,
      data.entrepriseRang2 || null,
      data.arretChantier || null,
      data.courrierAR || null,
      data.contreVisite || null,
      data.nomRenault || null,
      data.signatureRenault || null,
      data.nomExterne || null,
      data.signatureExterne || null,
      data.q1 || null, data.q2 || null, data.q3 || null, data.q4 || null, data.q5 || null,
      data.q6 || null, data.q7 || null, data.q8 || null, data.q9 || null, data.q10 || null,
      data.q11 || null, data.q12 || null, data.q13 || null, data.q14 || null, data.q15 || null,
      data.q16 || null, data.q17 || null, data.q18 || null, data.q19 || null, data.q20 || null,
      data.q21 || null, data.q22 || null, data.q23 || null, data.q24 || null, data.q25 || null, data.q26 || null
    ).run();

    return Response.json({ success: true });

  } catch (error) {
    console.error(error);
    return Response.json({ success: false, error: error.message });
  }
}

export async function onRequestGet({ env }) {
  const { results } = await env.DB.prepare("SELECT * FROM audits ORDER BY dateCreation DESC").all();
  return Response.json(results || []);
}
