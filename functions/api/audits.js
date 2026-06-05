// functions/api/audits.js
export async function onRequestPost({ request, env }) {
  try {
    const data = await request.json();
    
    // === GESTION DES LOGINS ===
    if (data.email && data.userType) {
      await env.DB.prepare(`
        INSERT INTO logins (email, userType, consentRGPD, dateConnexion)
        VALUES (?, ?, ?, ?)
      `).bind(
        data.email,
        data.userType,
        data.consentRGPD || true,
        data.dateConnexion || new Date().toISOString()
      ).run();

      return Response.json({ success: true, message: "Login enregistré" });
    }

    // === GESTION DES AUDITS ===
    const { type = "audit_simple", ...auditData } = data;

    await env.DB.prepare(`
      INSERT INTO audits (
        type, lieu, dateHeureVisite, operation, planPrevention, chargeAffaire,
        entrepriseRang1, entrepriseRang2, arretChantier, courrierAR, contreVisite,
        nomRenault, signatureRenault, nomExterne, signatureExterne,
        q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15,
        q16, q17, q18, q19, q20, q21, q22, q23, q24, q25, q26
      ) VALUES (
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
      )
    `).bind(
      type,
      auditData.lieu,
      auditData.dateHeureVisite || null,
      auditData.operation || null,
      auditData.planPrevention || null,
      auditData.chargeAffaire || null,
      auditData.entrepriseRang1 || null,
      auditData.entrepriseRang2 || null,
      auditData.arretChantier || null,
      auditData.courrierAR || null,
      auditData.contreVisite || null,
      auditData.nomRenault || null,
      auditData.signatureRenault || null,
      auditData.nomExterne || null,
      auditData.signatureExterne || null,
      auditData.q1 || null, auditData.q2 || null, auditData.q3 || null, auditData.q4 || null,
      auditData.q5 || null, auditData.q6 || null, auditData.q7 || null, auditData.q8 || null,
      auditData.q9 || null, auditData.q10 || null, auditData.q11 || null, auditData.q12 || null,
      auditData.q13 || null, auditData.q14 || null, auditData.q15 || null, auditData.q16 || null,
      auditData.q17 || null, auditData.q18 || null, auditData.q19 || null, auditData.q20 || null,
      auditData.q21 || null, auditData.q22 || null, auditData.q23 || null, auditData.q24 || null,
      auditData.q25 || null, auditData.q26 || null
    ).run();

    return Response.json({ success: true });

  } catch (error) {
    console.error(error);
    return Response.json({ success: false, error: error.message }, { status: 500 });
  }
}

export async function onRequestGet({ env }) {
  try {
    const { results } = await env.DB.prepare("SELECT * FROM audits ORDER BY dateCreation DESC").all();
    return Response.json(results);
  } catch (error) {
    return Response.json([]);
  }
}
