import 'dotenv/config';
import fs from 'node:fs/promises';
import path from 'node:path';

const API_BASE = 'https://api.kie.ai/api/v1';
const UPLOAD_BASE = 'https://kieai.redpandaai.co/api';
const API_KEY = process.env.KIE_AI_API_KEY;

// Modelo de imagen-a-imagen usado para componer el producto en la escena.
// Verifica el slug exacto en https://docs.kie.ai/ (seccion "Models") si Kie AI
// cambia sus nombres; puedes sobreescribirlo con KIE_AI_MODEL en .env.
const MODEL = process.env.KIE_AI_MODEL || 'qwen/image-to-image';

const REFERENCE_IMAGE = process.env.REFERENCE_IMAGE_PATH ||
  '/tmp/claude-0/-home-user-CLAUDE/7cefee55-f5f2-5e8d-8d52-936457d5501a/images/1.webp';

const OUTPUT_DIR = path.resolve('output-nibel');

if (!API_KEY) {
  console.error('Falta KIE_AI_API_KEY. Copia .env.example a .env y agrega tu API key.');
  process.exit(1);
}

const headers = {
  Authorization: `Bearer ${API_KEY}`,
  'Content-Type': 'application/json',
};

// NOTA: el modelo qwen/image-to-image devuelve "Internal Error" con prompts
// mayores a ~800 caracteres. Mantener STYLE_BASE + texto de cada shot corto.
const STYLE_BASE = 'Captured with iPhone 17 Pro quality: natural smartphone photo, ' +
  'hyperrealistic, natural skin texture, no retouching, sharp background in focus, natural ' +
  'lighting, UGC style, no phone visible in frame. Integrate the teal NIBEL Zeolita Detox ' +
  'pouch as a real 3D object with correct perspective, scale, lighting and shadows -- never ' +
  'a flat sticker or cutout.';

const shots = [
  // 3 selfies familiares (mama con hijos pequenos)
  {
    name: 'familia-selfie-01-cocina',
    prompt: `${STYLE_BASE} Selfie casera en la cocina: mama sonriente con sus dos hijos ` +
      'pequenos, ella sostiene la bolsa del producto mostrandola a camara, ninos curiosos, ' +
      'luz natural de ventana, ambiente hogareno.',
  },
  {
    name: 'familia-selfie-02-sala',
    prompt: `${STYLE_BASE} Selfie casera en la sala: mama abraza a su hijo pequeno en el ` +
      'sofa, el nino sostiene la bolsa del producto sonriendo a camara, luz de tarde, ' +
      'ambiente relajado de fin de semana.',
  },
  {
    name: 'familia-selfie-03-desayunador',
    prompt: `${STYLE_BASE} Selfie casera en el desayunador por la manana: mama con su hija ` +
      'pequena sonriendo a camara, sostiene la bolsa del producto junto a un vaso de agua, ' +
      'luz natural matutina.',
  },

  // 10 fotos de producto solamente
  {
    name: 'producto-01-frente-fondo-blanco',
    prompt: `${STYLE_BASE} Fotografia de producto sobre superficie blanca lisa, la bolsa ` +
      'de pie centrada de frente, luz suave uniforme, sombra de contacto realista, estilo ' +
      'catalogo e-commerce.',
  },
  {
    name: 'producto-02-angulo-3-4',
    prompt: `${STYLE_BASE} Fotografia de producto en angulo de tres cuartos sobre mesa de ` +
      'madera clara, luz natural lateral suave, fondo desenfocado de cocina.',
  },
  {
    name: 'producto-03-con-gomitas-esparcidas',
    prompt: `${STYLE_BASE} Fotografia de producto de pie sobre mesa de madera con gomitas ` +
      'de colores esparcidas alrededor de la base, luz natural de dia, estilo flat lay ' +
      'angulado.',
  },
  {
    name: 'producto-04-mano-sosteniendo',
    prompt: `${STYLE_BASE} Fotografia de una mano de adulto sosteniendo la bolsa del ` +
      'producto frente a un fondo de cocina desenfocado, luz natural de ventana.',
  },
  {
    name: 'producto-05-fondo-cocina-desayuno',
    prompt: `${STYLE_BASE} Fotografia de producto de pie sobre la barra de cocina junto a ` +
      'un vaso de jugo de naranja y fruta picada, luz natural matutina.',
  },
  {
    name: 'producto-06-mochila-escolar',
    prompt: `${STYLE_BASE} Fotografia de producto apoyado junto a una mochila escolar ` +
      'infantil de colores sobre una mesa, luz natural de dia, contexto escolar matutino.',
  },
  {
    name: 'producto-07-fondo-verde-plantas',
    prompt: `${STYLE_BASE} Fotografia de producto de pie sobre madera con plantas verdes ` +
      'desenfocadas de fondo, luz natural suave, concepto de detox y bienestar.',
  },
  {
    name: 'producto-08-cenital-flat-lay',
    prompt: `${STYLE_BASE} Fotografia cenital (top-down) de la bolsa acostada sobre madera ` +
      'clara junto a gomitas de colores, luz natural uniforme, estilo redes sociales.',
  },
  {
    name: 'producto-09-vaso-agua',
    prompt: `${STYLE_BASE} Fotografia de producto de pie junto a un vaso de agua con ` +
      'hielo sobre mesa de cocina, luz natural de dia, composicion fresca.',
  },
  {
    name: 'producto-10-detalle-etiqueta',
    prompt: `${STYLE_BASE} Fotografia de producto en primer plano, enfocando la etiqueta ` +
      'frontal con detalle nitido del empaque, angulo lateral, luz suave, fondo desenfocado.',
  },
];

async function uploadReferenceImage() {
  const buffer = await fs.readFile(REFERENCE_IMAGE);
  const base64Data = `data:image/webp;base64,${buffer.toString('base64')}`;

  const res = await fetch(`${UPLOAD_BASE}/file-base64-upload`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      base64Data,
      uploadPath: 'nibel-reference',
      fileName: 'nibel-zeolita-detox.webp',
    }),
  });

  const json = await res.json();
  if (!res.ok || !json.success) {
    throw new Error(`Error subiendo la imagen de referencia: ${JSON.stringify(json)}`);
  }
  return json.data.downloadUrl;
}

async function createTask(prompt, referenceUrl) {
  const res = await fetch(`${API_BASE}/jobs/createTask`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      model: MODEL,
      input: {
        prompt,
        image_url: referenceUrl,
      },
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

async function waitForResult(taskId, label) {
  const maxAttempts = 30;
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    await sleep(4000);
    const data = await getTaskResult(taskId);

    if (data.state === 'success') {
      const resultJson = JSON.parse(data.resultJson);
      return resultJson.resultUrls;
    }
    if (data.state === 'fail') {
      throw new Error(`[${label}] La generacion fallo: ${data.failMsg || 'sin detalle'}`);
    }
    console.log(`  [${label}] estado: ${data.state} (intento ${attempt}/${maxAttempts})`);
  }
  throw new Error(`[${label}] Se agoto el tiempo de espera.`);
}

async function downloadImage(url, destPath) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`No se pudo descargar ${url}`);
  const buffer = Buffer.from(await res.arrayBuffer());
  await fs.writeFile(destPath, buffer);
}

async function main() {
  await fs.mkdir(OUTPUT_DIR, { recursive: true });

  console.log('Subiendo imagen de referencia del producto...');
  const referenceUrl = await uploadReferenceImage();
  console.log(`Referencia disponible en: ${referenceUrl}\n`);

  const results = [];

  for (const shot of shots) {
    console.log(`Generando: ${shot.name}`);
    try {
      const taskId = await createTask(shot.prompt, referenceUrl);
      const urls = await waitForResult(taskId, shot.name);

      for (let i = 0; i < urls.length; i++) {
        const ext = path.extname(new URL(urls[i]).pathname) || '.png';
        const destPath = path.join(OUTPUT_DIR, `${shot.name}${urls.length > 1 ? `-${i + 1}` : ''}${ext}`);
        await downloadImage(urls[i], destPath);
        console.log(`  Guardada: ${destPath}`);
      }

      results.push({ name: shot.name, prompt: shot.prompt, urls });
    } catch (err) {
      console.error(`  Error en ${shot.name}: ${err.message}`);
      results.push({ name: shot.name, prompt: shot.prompt, error: err.message });
    }
  }

  await fs.writeFile(
    path.join(OUTPUT_DIR, 'resultados.json'),
    JSON.stringify(results, null, 2),
  );

  console.log(`\nListo. Revisa la carpeta ${OUTPUT_DIR}`);
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
