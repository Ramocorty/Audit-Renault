// functions/api/logins.js
export async function onRequestGet({ env }) {
  try {
    const { results } = await env.DB.prepare("SELECT * FROM logins ORDER BY dateConnexion DESC").all();
    return Response.json(results || []);
  } catch (error) {
    console.error(error);
    return Response.json([]);
  }
}
