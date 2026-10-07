# Nibel · Campaña 2 · INSTRUCCIONES DE IMÁGENES para Claude Code

> **Para Claude Code.** Tu trabajo en esta campaña es **solo generar las imágenes**. Los copies ya están hechos y no los tocas. Este archivo trae todo: reglas, las 9 piezas con su prompt de generación y el texto exacto que va encima, y el orden de trabajo.

## 0. Correcciones a CLAUDE.md (aplican desde hoy)
- **La fórmula sí lleva silimarina al 80%, colina y NAC.** La regla "no menciones NAC ni dosis" queda **anulada**. El frente del frasco muestra silimarina, colina, diente de león y alcachofa, y ese frente es el que usamos de referencia visual. En los textos de las imágenes sí se puede escribir "silimarina al 80%, colina y NAC". **No escribas mg.**
- **Público: hombres de 45 años o más** (85% de los compradores).
- Actualiza `CLAUDE.md` con estas dos líneas.

## 1. Cómo generar
- Generador: kie.ai con la variable de entorno `KIE_AI_API_KEY`. **Si no existe, detente y avísame. No la pidas en el chat.**
- **Formato: 1:1, 1080×1080.** Pide al generador el ratio 1:1 en el parámetro de proporción. Que el prompt lo diga no basta.
- **Referencia del producto:** `marca/frasco-frente.png`. Úsala como imagen de referencia en **todas** las generaciones donde aparece el frasco. El frasco es **cilíndrico, del tamaño de una botella de agua (~20 cm)**; respeta forma, colores y etiqueta.
- **Si la etiqueta sale deformada:** genera el frasco liso (sin etiqueta) y pega encima la etiqueta real de `marca/frasco-frente.png` con perspectiva.
- **Genera 2 variantes por pieza** y quédate con la mejor. Enséñame las dos.
- **Texto dentro de escenas** (glucómetro, hojas de laboratorio, ultrasonido): genéralas en blanco y compón el texto con código, con la misma perspectiva, luz y un poco de desenfoque, para que se vea real.
- **Texto de diseño** (retargeting): siempre compuesto con código (HTML/CSS → PNG o Pillow). Nunca con el generador.

## 2. Estilo
| | Prospección (P1–P5) | Retargeting (R1–R4) |
|---|---|---|
| Look | Foto nativa de celular, minimalista, con grano ligero, no de stock | Diseño de anuncio con producto protagonista |
| Texto encima | **Ninguno.** Solo el que vive dentro de la escena | Titular, ✅, píldora/sello 2x1, botón y pie |
| Frasco | **No aparece** | Siempre, con la etiqueta legible |
| Tipografía | — | Outfit ExtraBold en mayúsculas (titular) y Outfit Regular/Medium (cuerpo) |
| Paleta | Natural | #004A48 principal · ✅ #22780C · fondos #F8F8F8→#C8D8E0 · acento cálido para el 2x1 |

## 3. Prohibido en todas
Caras de médicos, batas o estetoscopios. Alcohol. Marcas reales. Texto en inglés. Números de mejora (solo los del problema). Estrellas o reseñas. Urgencia falsa ("solo hoy", contadores). Frases entre comillas puestas en boca de una persona.

---

## PROSPECCIÓN

### P1 · Azúcar · glucómetro al amanecer
**Prompt:**
```
Square 1:1 image. Candid smartphone photo, realistic, slight grain, not a stock photo. Early morning in an ordinary Mexican kitchen, soft bluish dawn light from a window. Close-up of a Mexican man's hand (light-brown skin, around 50, some arm hair, simple wristwatch) holding a generic home glucose meter with a test strip; the screen is blank. On the counter, slightly blurred: a steaming mug of coffee and a glass of water. Minimal composition, clean counter, no face visible. No brands, no text.
```
**Componer:** en la pantalla del glucómetro, **118** en dígitos LCD grises.
**Salida:** `salidas/campana2/prospeccion/nibel_C2_TOF_azucar_P1_1x1_v1.png`

### P2 · Colesterol · hoja de lípidos con pastillas
**Prompt:**
```
Square 1:1 image. Candid smartphone photo taken from above, realistic, natural window light, slight grain. A wooden kitchen table with only three things: a blank printed lab results sheet with faint gray lines, a generic blister strip of white pills resting on the sheet, and a pair of men's reading glasses folded beside it. Minimal, lots of empty table space. No brands, no readable text, no people.
```
**Componer en la hoja:** encabezado "Perfil de lípidos"; renglones "Colesterol total", "Triglicéridos", "HDL", "LDL" **sin números**; el renglón "Colesterol total" resaltado con marcatexto amarillo.
**Salida:** `.../nibel_C2_TOF_colesterol_P2_1x1_v1.png`

### P3 · Hígado graso · ultrasonido en el coche
**Prompt:**
```
Square 1:1 image. Candid smartphone photo, realistic, midday daylight, slight grain. Inside a parked car, shot from the driver's seat looking at the passenger seat. On the passenger seat: an open white medical lab envelope and a blank printed report sheet with faint gray lines, and a set of car keys resting on it. Minimal, nothing else on the seat. No people, no brands, no readable text.
```
**Componer en la hoja:** encabezado "Ultrasonido de hígado y vías biliares"; renglón "Esteatosis hepática grado II" **subrayado con pluma azul**; el resto, renglones ilegibles.
**Salida:** `.../nibel_C2_TOF_higado_P3_1x1_v1.png`

### P4 · Medicamentos · pastillero semanal
**Prompt:**
```
Square 1:1 image. Candid smartphone photo, realistic, warm morning light, slight grain. A plain kitchen table with a 7-day weekly pill organizer full of pills of different colors and sizes. A Mexican man's hand (light-brown skin, around 55, simple wedding ring) is opening the first compartment. A glass of water beside the organizer. Minimal composition, empty table space around. No face, no brands, no readable text.
```
**Componer:** las letras de los días en las tapas, en español: **L M M J V S D**.
**Salida:** `.../nibel_C2_TOF_medicamentos_P4_1x1_v1.png`

### P5 · Pesadez · mesa después de la carne asada
**Prompt:**
```
Square 1:1 image. Candid smartphone photo, realistic, warm late-afternoon light, slight grain. A Mexican backyard table after a family carne asada: one empty plate with leftover bits of grilled meat and onion, a cloth tortilla warmer, a stone molcajete with red salsa, and a glass of agua de jamaica. Minimal, only these items, slightly messy like a real Sunday. No people, no beer, no alcohol, no brands, no readable text.
```
**Componer:** nada.
**Salida:** `.../nibel_C2_TOF_pesadez_P5_1x1_v1.png`

---

## RETARGETING

### R1 · Oferta directa 2x1
**Prompt del fondo (con `marca/frasco-frente.png` como referencia):**
```
Square 1:1 image. Realistic studio product photography. Two identical cylindrical supplement bottles from the reference image, each about the size of a water bottle, standing side by side on a light stone surface in the lower right half of the frame, labels facing the camera, exactly as in the reference (do not redraw the labels, keep real proportions). Dark teal background (#004A48) with a soft spotlight behind the bottles and gentle reflections. The left half and the top are empty clean background for text. Premium commercial style. No text, no other objects.
```
**Componer:**
- Sello circular grande, arriba a la derecha, color acento, girado unos 8°: **2x1**
- Titular (blanco): **2 FRASCOS POR EL PRECIO DE 1**
- Subtítulo: Tus primeros 60 días por unos $10 al día
- ✅ Silimarina al 80%, colina y NAC
- ✅ Más diente de león y alcachofa
- ✅ Junto con tu tratamiento
- ✅ Garantía de 60 días aunque el frasco esté vacío
- Botón ancho abajo (blanco, texto #004A48): **PÍDELO HOY →**
- Pie chico: Este producto no es un medicamento. Si tomas medicamentos, consulta a tu médico.

**Salida:** `salidas/campana2/retargeting/nibel_C2_BOF_R1_1x1_v1.png`

### R2 · Garantía "Pruébalo 60 días"
**Prompt del fondo:**
```
Square 1:1 image. Realistic studio product photography. One cylindrical supplement bottle from the reference image, about the size of a water bottle, standing on a white round pedestal on the right side of the frame, label facing the camera, exactly as in the reference (do not redraw the label, keep real proportions). Light background with a soft gradient from off-white (#F8F8F8) to pale blue-gray (#C8D8E0), soft daylight from above, gentle shadow. The left half is empty clean background for text. No text, no other objects.
```
**Componer:**
- Titular (#004A48): **PRUÉBALO 60 DÍAS**
- Subtítulo: Si no te convence, te devolvemos tu dinero. **Aunque el frasco esté vacío.**
- 3 pasos con círculo numerado #004A48:
  1. Hazte tus análisis hoy
  2. Toma Nibel 8 semanas, junto con tu tratamiento
  3. Repítelos y compara
- Sello circular junto al frasco: **GARANTÍA · 60 DÍAS**
- Píldora de oferta con 🔥: **2x1** · 2 frascos = tus 60 días
- Pie chico: Este producto no es un medicamento. Si tomas medicamentos, consulta a tu médico.

**Salida:** `.../nibel_C2_BOF_R2_1x1_v1.png`

### R3 · "¿Lo puedo tomar con mi pastilla?"
**Prompt del fondo:**
```
Square 1:1 image. Realistic product photography, warm natural morning light. On a light wooden kitchen table, on the right side of the frame: one cylindrical supplement bottle from the reference image, about the size of a water bottle, label facing the camera, exactly as in the reference (do not redraw the label, keep real proportions), standing next to a 7-day weekly pill organizer with colorful pills and a glass of water. Soft warm off-white background, slightly blurred. The left half and the top are empty clean background for text. No text, no other brands.
```
**Componer:**
- Titular (#004A48): **¿LO PUEDO TOMAR CON MI PASTILLA?**
- Respuesta grande: Sí. Nibel no sustituye tu tratamiento: va junto con él.
- ✅ Lleva la etiqueta a tu próxima consulta
- ✅ Si tomas medicamento para la diabetes, platícalo antes con tu médico
- ✅ Silimarina al 80%, colina y NAC, todo a la vista
- Píldora de oferta con 🔥: **2x1** + garantía de 60 días
- Pie chico: Este producto no es un medicamento.

**Salida:** `.../nibel_C2_BOF_R3_1x1_v1.png`

### R4 · Selfie UGC de hombre 45+ + 2x1
**Prompt (con `marca/frasco-frente.png` como referencia):**
```
Square 1:1 image. Authentic UGC selfie taken with an iPhone 14 front camera, handheld at arm's length, natural and unpolished. A Mexican man around 52 with light-brown skin, short graying hair and a trimmed gray beard, wearing a plain navy t-shirt. He holds the product from the reference image next to his face: a cylindrical bottle about the size of a water bottle (around 20 cm tall), gripped with his whole hand, label facing the camera, sharp and readable, exactly as in the reference (do not redraw the label, keep real proportions). Genuine relaxed smile. Soft window light, simple indoor background softly blurred. Natural skin texture, no retouching. No text, no other brands.
```
**Componer (poco, para que siga viéndose orgánico):**
- Sticker arriba a la izquierda (blanco, esquinas redondeadas, girado unos -6°, texto #004A48): **HOY 2x1**
- Banda inferior (#004A48 al 90%, texto blanco): 2 frascos = 60 días · Garantía aunque el frasco esté vacío
- Pie chico: Este producto no es un medicamento.
- **Sin comillas ni frases como si él hablara.**

**Salida:** `.../nibel_C2_BOF_R4_1x1_v1.png`

---

## 4. Orden de trabajo
1. **Paso A (sin generar):** confirma que existe `KIE_AI_API_KEY` y `marca/frasco-frente.png`, actualiza `CLAUDE.md` con la sección 0 y dame una tabla corta de las 9 piezas. Espera mi OK.
2. **Prospección:** genera P1 a P5 (2 variantes cada una), compón el texto de escena y enséñamelas juntas.
3. **Retargeting:** genera y compón **solo R1** y enséñamela. Con mi visto bueno, haz R2, R3 y R4 con el mismo estilo.
4. Al final, revisa cada pieza contra la sección 3 y dame la lista de archivos.
