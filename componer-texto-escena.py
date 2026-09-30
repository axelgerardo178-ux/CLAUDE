"""Compone texto dentro de una escena (hoja, etiqueta, pantalla) con homografía.

Uso:
  python3 componer-texto-escena.py ref01 marca/tof-ref01-escena.png salida.png [--corners x1,y1,x2,y2,x3,y3,x4,y4]
                                   [--blur 0.8] [--debug debug.png]

Las esquinas van en orden: arriba-izq, arriba-der, abajo-der, abajo-izq DE LA HOJA
(según cómo se lee el texto, no según la imagen). Sin --corners intenta detectar el
cuadrilátero claro más grande.

El texto se renderiza plano, se proyecta con cv2.warpPerspective y se mezcla
multiplicando por la luz de la propia hoja (sombras, gradientes). Solo se pinta
donde el píxel parece papel, así los dedos que tapan la hoja quedan encima.
"""
import argparse
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = '/usr/share/fonts/truetype/liberation/'
F_REG = FONT_DIR + 'LiberationSans-Regular.ttf'
F_BOLD = FONT_DIR + 'LiberationSans-Bold.ttf'


def font(size, bold=False):
    return ImageFont.truetype(F_BOLD if bold else F_REG, size)


# ---------- layouts planos (RGBA, fondo transparente) ----------

def layout_ref01():
    """Hoja de resultados tamaño carta: 'Resultado: pre diabetes'."""
    W, H = 1275, 1650  # carta a 150 dpi
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ink = (38, 38, 42, 255)
    gray = (120, 120, 126, 255)
    light = (175, 175, 180, 255)
    red = (150, 22, 28, 255)
    m = 110

    # encabezado de laboratorio genérico
    d.text((m, 80), 'LABORATORIO CLÍNICO', font=font(30, True), fill=gray)
    d.text((m, 120), 'Reporte de resultados', font=font(24), fill=light)
    d.text((W - m, 80), 'Folio 0048217', font=font(24), fill=light, anchor='ra')
    d.text((W - m, 115), 'Fecha 12/09/2026', font=font(24), fill=light, anchor='ra')
    d.line((m, 170, W - m, 170), fill=light, width=3)

    # titular en rojo oscuro
    d.text((m, 225), 'Resultado: pre diabetes', font=font(84, True), fill=red)

    # indicaciones subrayadas
    y = 370
    t = 'Indicaciones: cuidar alimentación'
    f = font(46, True)
    d.text((m, y), t, font=f, fill=ink)
    w = d.textlength(t, font=f)
    d.line((m, y + 58, m + w, y + 58), fill=ink, width=4)

    # renglones ilegibles bajo indicaciones
    rng = np.random.default_rng(7)
    y = 470
    for _ in range(3):
        x = m + 30
        d.ellipse((m, y + 6, m + 12, y + 18), fill=gray)
        for _ in range(rng.integers(6, 10)):
            ww = int(rng.integers(40, 130))
            if x + ww > W - m:
                break
            d.rounded_rectangle((x, y + 6, x + ww, y + 18), 6, fill=light)
            x += ww + 16
        y += 48

    # tabla "Tus resultados"
    y = 660
    d.text((m, y), 'Tus resultados', font=font(40, True), fill=ink)
    y += 70
    cols = [m, m + 520, m + 800]
    hf = font(28, True)
    for c, h in zip(cols, ['Estudio', 'Resultado', 'Referencia']):
        d.text((c, y), h, font=hf, fill=gray)
    y += 48
    d.line((m, y, W - m, y), fill=light, width=2)
    rf = font(32)
    rfb = font(32, True)
    rows = [('Glucosa en ayunas', '108 mg/dL', '70 – 99'),
            ('Hemoglobina glucosilada', '6.0 %', '< 5.7')]
    for est, res, ref in rows:
        y += 22
        d.text((cols[0], y), est, font=rf, fill=ink)
        d.text((cols[1], y), res, font=rfb, fill=red)
        d.text((cols[2], y), ref, font=rf, fill=ink)
        y += 52
        d.line((m, y, W - m, y), fill=light, width=2)

    # bloques de texto ilegible más abajo (como en la referencia)
    y += 90
    for block in range(3):
        d.rounded_rectangle((m, y, m + 240, y + 20), 8, fill=gray)
        y += 50
        for _ in range(int(rng.integers(2, 4))):
            x = m
            lim = W - m - int(rng.integers(0, 260))
            while True:
                ww = int(rng.integers(40, 150))
                if x + ww > lim:
                    break
                d.rounded_rectangle((x, y, x + ww, y + 14), 6, fill=light)
                x += ww + 14
            y += 38
        y += 40
    return img


LAYOUTS = {'ref01': layout_ref01}


# ---------- geometría ----------

def order_corners(pts):
    pts = np.array(pts, dtype=np.float32).reshape(4, 2)
    s = pts.sum(1)
    diff = np.diff(pts, axis=1).ravel()
    return np.array([pts[np.argmin(s)], pts[np.argmin(diff)],
                     pts[np.argmax(s)], pts[np.argmax(diff)]], dtype=np.float32)


def detect_sheet(bgr):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    v, s = hsv[..., 2], hsv[..., 1]
    mask = ((v > np.percentile(v, 80)) & (s < 45)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        sys.exit('No encontré la hoja; pásame --corners.')
    c = max(cnts, key=cv2.contourArea)
    hull = cv2.convexHull(c)
    peri = cv2.arcLength(hull, True)
    for eps in np.linspace(0.01, 0.08, 30):
        approx = cv2.approxPolyDP(hull, eps * peri, True)
        if len(approx) == 4:
            return order_corners(approx)
    rect = cv2.boxPoints(cv2.minAreaRect(c))
    return order_corners(rect)


# ---------- composición ----------

def compose(scene_path, out_path, layout, corners, blur, debug_path=None):
    bgr = cv2.imread(scene_path)
    if bgr is None:
        sys.exit(f'No pude leer {scene_path}')
    if bgr.shape[:2] != (1080, 1080):
        bgr = cv2.resize(bgr, (1080, 1080), interpolation=cv2.INTER_AREA)
    H, W = bgr.shape[:2]
    scene = bgr.astype(np.float32) / 255.0

    flat = np.array(LAYOUTS[layout]())  # RGBA
    fh, fw = flat.shape[:2]
    src = np.float32([[0, 0], [fw, 0], [fw, fh], [0, fh]])
    dst = corners if corners is not None else detect_sheet(bgr)
    M = cv2.getPerspectiveTransform(src, dst)

    rgb = cv2.warpPerspective(flat[..., :3], M, (W, H), flags=cv2.INTER_AREA)
    alpha = cv2.warpPerspective(flat[..., 3], M, (W, H), flags=cv2.INTER_AREA)
    ink = rgb[..., ::-1].astype(np.float32) / 255.0
    a = alpha.astype(np.float32) / 255.0

    # máscara de papel dentro del cuadrilátero (los dedos quedan fuera)
    quad = np.zeros((H, W), np.uint8)
    cv2.fillConvexPoly(quad, dst.astype(np.int32), 255)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    inside = quad > 0
    vq = hsv[..., 2][inside]
    paper = (hsv[..., 2] > np.percentile(vq, 12) * 0.9) & (hsv[..., 1] < 60) & inside
    paper = cv2.morphologyEx(paper.astype(np.uint8) * 255, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    paper = cv2.GaussianBlur(paper, (0, 0), 1.2).astype(np.float32) / 255.0

    # tinta = color del papel en la escena * color de tinta (multiplicar): hereda luz y sombras
    paper_col = cv2.GaussianBlur(scene, (0, 0), 4)
    inked = paper_col * ink
    a = a * paper
    if blur > 0:
        a = cv2.GaussianBlur(a, (0, 0), blur)
        inked = cv2.GaussianBlur(inked, (0, 0), blur)
    a = (a * 0.93)[..., None]  # tinta de impresora, nunca 100 % opaca
    out = scene * (1 - a) + inked * a

    # grano uniforme en toda la foto para que la zona compuesta no destaque
    rng = np.random.default_rng(3)
    noise = rng.normal(0, 0.012, (H, W, 1)).astype(np.float32)
    out = np.clip(out + noise, 0, 1)

    cv2.imwrite(out_path, (out * 255).round().astype(np.uint8))
    if debug_path:
        dbg = bgr.copy()
        cv2.polylines(dbg, [dst.astype(np.int32)], True, (0, 0, 255), 2)
        for i, p in enumerate(dst):
            cv2.putText(dbg, str(i), tuple(int(v) for v in p), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imwrite(debug_path, dbg)
    print('Esquinas:', ','.join(f'{v:.0f}' for v in dst.ravel()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('layout', choices=LAYOUTS)
    ap.add_argument('scene')
    ap.add_argument('out')
    ap.add_argument('--corners')
    ap.add_argument('--blur', type=float, default=0.8)
    ap.add_argument('--debug')
    ap.add_argument('--flat', help='solo guarda el layout plano en esta ruta')
    args = ap.parse_args()
    if args.flat:
        LAYOUTS[args.layout]().save(args.flat)
        return
    corners = None
    if args.corners:
        corners = np.float32([float(v) for v in args.corners.split(',')]).reshape(4, 2)
    compose(args.scene, args.out, args.layout, corners, args.blur, args.debug)


if __name__ == '__main__':
    main()
