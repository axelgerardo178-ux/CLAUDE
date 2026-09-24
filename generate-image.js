import 'dotenv/config';

const API_BASE = 'https://api.kie.ai/api/v1';
const API_KEY = process.env.KIE_AI_API_KEY;

if (!API_KEY) {
  console.error('Falta KIE_AI_API_KEY. Copia .env.example a .env y agrega tu API key.');
  process.exit(1);
}

const prompt = process.argv.slice(2).join(' ') || 'A cute orange cat sitting on a rainbow, cartoon style, bright colors';
const model = process.env.KIE_AI_MODEL || 'qwen/text-to-image';

const headers = {
  Authorization: `Bearer ${API_KEY}`,
  'Content-Type': 'application/json',
};

async function createTask() {
  const res = await fetch(`${API_BASE}/jobs/createTask`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      model,
      input: { prompt },
    }),
  });

  const json = await res.json();
  if (!res.ok || json.code !== 200) {
    throw new Error(`Error creando la tarea: ${JSON.stringify(json)}`);
  }
  return json.data.taskId;
}

async function getTaskResult(taskId) {
  const res = await fetch(`${API_BASE}/jobs/recordInfo?taskId=${taskId}`, {
    method: 'GET',
    headers,
  });

  const json = await res.json();
  if (!res.ok || json.code !== 200) {
    throw new Error(`Error consultando la tarea: ${JSON.stringify(json)}`);
  }
  return json.data;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
  console.log(`Generando imagen con modelo "${model}"...`);
  console.log(`Prompt: ${prompt}`);

  const taskId = await createTask();
  console.log(`Tarea creada: ${taskId}`);

  const maxAttempts = 30;
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    await sleep(4000);
    const data = await getTaskResult(taskId);

    if (data.state === 'success') {
      const resultJson = JSON.parse(data.resultJson);
      console.log('Imagen generada con exito:');
      resultJson.resultUrls.forEach((url) => console.log(url));
      return;
    }

    if (data.state === 'fail') {
      throw new Error(`La generacion fallo: ${data.failMsg || 'sin detalle'}`);
    }

    console.log(`Estado: ${data.state} (intento ${attempt}/${maxAttempts})`);
  }

  throw new Error('Se agoto el tiempo de espera esperando el resultado.');
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
