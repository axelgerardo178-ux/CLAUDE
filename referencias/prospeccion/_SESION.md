# Sesión: PROSPECCIÓN (ref-01, ref-02, ref-03)

> Instrucciones para Claude Code. Léelo completo antes de empezar.

## Qué hay en esta carpeta
| Ref | Imagen | Ángulo Nibel | Escena | ¿Frasco Nibel? |
|---|---|---|---|---|
| ref-01 | `ref-01.png` | Azúcar (#1) | Mujer en consultorio sosteniendo su hoja de resultados ("pre diabetes") | No |
| ref-02 | `ref-02.png` | Colesterol (#2) | Consulta: brazo señalando el hígado en una pantalla, paciente mujer de espaldas | No |
| ref-03 | `ref-03.png` | Azúcar (#1), vía "ya probé cardo mariano" | Buró de noche con un frasco genérico de cardo mariano y un glucómetro | No |

Las 3 vienen de **Happy Liver (Ritual Labs, EE. UU.)**. Sus copies usan una hepatóloga que recomienda la marca y un testimonio inventado con cifras de laboratorio: **todo eso se descarta**. Se toma solo la estructura visual.

## Qué es distinto en prospección
- **Son fotos nativas**: tienen que parecer tomadas con celular por una persona, no un anuncio. **No llevan titular, ✅, píldora ni pie encima.** No uses la tipografía ni los recuadros de retargeting y mid.
- **El frasco Nibel no aparece.** El trabajo de la imagen es detener el scroll; el copy largo presenta el producto.
- El único texto es el que está **dentro de la escena**: la hoja de resultados (ref-01), la hoja del escritorio (ref-02) y la etiqueta del frasco genérico (ref-03). Si el generador lo deforma, genera esa superficie en blanco y compón el texto con código, con la misma perspectiva, iluminación y un poco de desenfoque para que se vea real.
- La leyenda legal va en el texto del anuncio (sección 6 de cada ficha), no en la imagen.

## Qué leer
1. `CLAUDE.md` (raíz).
2. Del brief, solo las secciones **1, 4, 5 y 9**.
3. Las 3 fichas de esta carpeta, con sus imágenes.

## Orden de trabajo
1. **Paso A (sin generar):** tabla corta por ficha con lo que entendiste de la escena, qué texto va dentro de ella y qué te falta. Espera mi OK.
2. **Fondos:** los prompts están en la sección 5 de cada ficha. Si no tienes `KIE_AI_API_KEY`, pídeme las imágenes. Yo las genero en **1:1** y las pongo en `marca/` como:
   - `marca/tof-ref01-escena.png`
   - `marca/tof-ref02-escena.png`
   - `marca/tof-ref03-escena.png`
3. **Paso B:** termina **solo ref-01** (texto de la hoja con perspectiva), guárdala y enséñamela.
4. Con mi visto bueno, haz ref-02 y ref-03.

## Nombres de archivo
- `salidas/prospeccion/nibel_TOF_azucar_ref01_1x1_v1.png`
- `salidas/prospeccion/nibel_TOF_colesterol_ref02_1x1_v1.png`
- `salidas/prospeccion/nibel_TOF_azucar_ref03_1x1_v1.png`

## Errores que NO debes cometer
- Mostrar la cara de un médico, un gafete o un estetoscopio. En ref-02 solo se ve un brazo.
- Poner "You have fatty liver", "Nature's Bounty" o cualquier texto en inglés o marca real.
- Mostrar números de mejora. Solo el número del problema (ref-01 y el glucómetro de ref-03).
- Mano en la panza o cualquier cosa que señale el cuerpo o el peso.
- Agregarle titular o diseño de anuncio encima. Tiene que verse como foto.
