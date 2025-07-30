export async function onRequest(context) {
  const payload = await context.request.json();
  const resp = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
    },
    body: JSON.stringify(payload)
  });

  return new Response(resp.body, {
    status: resp.status,
    headers: {
      'Access-Control-Allow-Origin': '*'
    }
  });
}
