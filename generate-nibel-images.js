import 'dotenv/config';
import fs from 'node:fs/promises';
import path from 'node:path';

const API_BASE = 'https://api.kie.ai/api/v1';
const UPLOAD_BASE = 'https://kieai.redpandaai.co/api';
const API_KEY = process.env.KIE_AI_API_KEY;

// Modelo de imagen-a-imagen usado para componer el producto en la escena.
// qwen/image-to-image preserva el texto de la etiqueta pixel-exacto (confirmado
// en pruebas); nano-banana-2 se ve mas "organico" pero reinventa la etiqueta,
// asi que se descarto. Verifica el slug en https://docs.kie.ai/ si Kie AI
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

// Estilo "full organico" tipo resena de cliente real: nada de fondos cargados
// ni props de mas, luz natural imperfecta, foco total en el producto (o en la
// familia en las selfies).
// NOTA: qwen/image-to-image devuelve "Internal Error" con prompts mayores a
// ~800 caracteres, por eso STYLE_BASE + extras + shot se mantienen cortos.
const STYLE_BASE = 'Genuine organic customer review photo, real phone camera, natural ' +
  'light only, no studio. Simple plain background, minimal props. Keep the pouch design, ' +
  'logo, colors and all printed text pixel-identical to the reference image, exactly as ' +
  'written -- do not redesign or invent label text.';

const FAMILIA_EXTRA = 'Selfie angle, focus on mom and her kids real expressions, ' +
  'background simple and out of focus, product held naturally.';

const PRODUCTO_EXTRA = 'Product-only shot, full focus on the pouch, plain bare ' +
  'surface, no clutter.';

const shots = [
  // 3 selfies familiares (mama con hijos pequenos), foco en la familia
  {
    name: 'familia-selfie-01-cocina',
    prompt: `${STYLE_BASE} ${FAMILIA_EXTRA} Mama sonriente con sus dos hijos pequenos en ` +
      'casa, ella sostiene la bolsa del producto mostrandola a camara, ninos curiosos y ' +
      'felices, luz natural de dia.',
  },
  {
    name: 'familia-selfie-02-sala',
    prompt: `${STYLE_BASE} ${FAMILIA_EXTRA} Mama abraza a su hijo pequeno, el nino sostiene ` +
      'la bolsa del producto sonriendo a camara, ambiente relajado y casero, luz natural.',
  },
  {
    name: 'familia-selfie-03-desayunador',
    prompt: `${STYLE_BASE} ${FAMILIA_EXTRA} Mama con su hija pequena sonriendo a camara, ` +
      'sostiene la bolsa del producto cerca de su hija, momento genuino de manana, luz ' +
      'natural suave.',
  },

  // 10 fotos de producto solamente, foco total en el producto
  {
    name: 'producto-01-frente-fondo-blanco',
    prompt: `${STYLE_BASE} ${PRODUCTO_EXTRA} La bolsa de pie centrada de frente sobre ` +
      'superficie blanca lisa, luz natural suave.',
  },
  {
    name: 'producto-02-angulo-3-4',
    prompt: `${STYLE_BASE} ${PRODUCTO_EXTRA} La bolsa en angulo de tres cuartos sobre mesa ` +
      'de madera clara, luz natural lateral.',
  },
  {
    name: 'producto-03-con-gomitas',
    prompt: `${STYLE_BASE} ${PRODUCTO_EXTRA} La bolsa de pie con solo un par de gomitas de ` +
      'colores junto a la base, luz natural de dia.',
  },
  {
    name: 'producto-04-mano-sosteniendo',
    prompt: `${STYLE_BASE} ${PRODUCTO_EXTRA} Una mano de adulto sosteniendo la bolsa en el ` +
      'aire, fondo neutro desenfocado, luz natural de ventana.',
  },
  {
    name: 'producto-05-mostrador-cocina',
    prompt: `${STYLE_BASE} ${PRODUCTO_EXTRA} La bolsa de pie sobre un mostrador de cocina ` +
      'liso, luz natural matutina.',
  },
  {
    name: 'producto-06-mesa-madera',
    prompt: `${STYLE_BASE} ${PRODUCTO_EXTRA} La bolsa de pie sobre una mesa de madera ` +
      'simple, luz natural calida de tarde.',
  },
  {
    name: 'producto-07-fondo-neutro',
    prompt: `${STYLE_BASE} ${PRODUCTO_EXTRA} La bolsa de pie contra una pared lisa de tono ` +
      'neutro, luz natural suave y difusa.',
  },
  {
    name: 'producto-08-cenital-flat-lay',
    prompt: `${STYLE_BASE} ${PRODUCTO_EXTRA} Fotografia cenital (top-down) de la bolsa ` +
      'acostada sobre una superficie simple, luz natural uniforme.',
  },
  {
    name: 'producto-09-vaso-agua',
    prompt: `${STYLE_BASE} ${PRODUCTO_EXTRA} La bolsa de pie junto a un solo vaso de agua ` +
      'simple, sin nada mas alrededor, luz natural de dia.',
  },
  {
    name: 'producto-10-detalle-etiqueta',
    prompt: `${STYLE_BASE} ${PRODUCTO_EXTRA} Primer plano de la etiqueta frontal, detalle ` +
      'nitido del empaque, fondo neutro desenfocado, luz natural suave.',
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
