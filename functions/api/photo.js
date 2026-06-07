// functions/api/photo.js
export async function onRequestPost({ request, env }) {
  try {
    const data = await request.json();

    if (!data.photo_base64) {
      return Response.json({ success: false, error: "Aucune photo" });
    }

    await env.DB.prepare(`
      INSERT INTO photos (email, photo_base64, description)
      VALUES (?, ?, ?)
    `).bind(
      data.email || "inconnu",
      data.photo_base64,
      data.description || "Photo audit"
    ).run();

    return Response.json({ success: true });

  } catch (error) {
    console.error(error);
    return Response.json({ success: false, error: error.message });
  }
}
