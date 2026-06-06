// functions/api/audits.js
export async function onRequestPost({ request, env }) {
  try {
    const data = await request.json();

    // === LOGIN ===
    if (data.email) {
      await env.DB.prepare(`
        INSERT INTO logins (email, userType, consentRGPD, dateConnexion)
        VALUES (?, ?, ?, ?)
      `).bind(data.email, data.userType || 'externe', true, new Date().toISOString()).run();
      return Response.json({ success: true });
    }

    // === AUDIT + GRILLE (version exacte pour ta table) ===
    await env.DB.prepare(`
      INSERT INTO audits VALUES (
        NULL, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
      )
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
      data.q1 || "NC", data.q2 || "NC", data.q3 || "NC", data.q4 || "NC", data.q5 || "NC",
      data.q6 || "NC", data.q7 || "NC", data.q8 || "NC", data.q9 || "NC", data.q10 || "NC",
      data.q11 || "NC", data.q12 || "NC", data.q13 || "NC", data.q14 || "NC", data.q15 || "NC",
      data.q16 || "NC", data.q17 || "NC", data.q18 || "NC", data.q19 || "NC", data.q20 || "NC",
      data.q21 || "NC", data.q22 || "NC", data.q23 || "NC", data.q24 || "NC", data.q25 || "NC", data.q26 || "NC"
    ).run();

    return Response.json({ success: true });

  } catch (error) {
    console.error("Erreur sauvegarde :", error.message);
    return Response.json({ success: false, error: error.message });
  }
}

export async function onRequestGet({ env }) {
  const { results } = await env.DB.prepare("SELECT * FROM audits ORDER BY dateCreation DESC").all();
  return Response.json(results || []);
}
