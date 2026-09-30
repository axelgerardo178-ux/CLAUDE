"""Compone texto dentro de una escena (hoja, etiqueta, pantalla) con homografía.

Uso:
  python3 componer-texto-escena.py ref01 marca/tof-ref01-escena.png salida.png [--corners x1,y1,x2,y2,x3,y3,x4,y4]
                                   [--blur 0.8] [--blur-ramp x0,y0,x1,y1,s1] [--debug debug.png]

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

def illegible_lines(d, rng, x0, y, x1, n, fill, h=14, gap=38, bullet=None):
    """Renglones de texto ilegible (bloques redondeados), como letra chica desenfocada."""
    for _ in range(n):
        x = x0
        if bullet:
            d.ellipse((x0, y, x0 + 12, y + 12), fill=bullet)
            x = x0 + 30
        lim = x1 - int(rng.integers(0, 220))
        while True:
            ww = int(rng.integers(25, 120))
            if x + ww > lim:
                break
            d.rounded_rectangle((x, y, x + ww, y + h), h // 2, fill=fill)
            x += ww + 12
        y += gap
    return y


def layout_ref01():
    """Hoja de resultados tamaño carta: 'Resultado: pre diabetes'.

    Acomodada a la foto de ref-01: la esquina superior derecha sale de cuadro, el
    pulgar tapa el margen izquierdo entre y≈720 y y≈1000 y la mitad de abajo se
    curva hacia la cámara. Por eso todo lo legible va arriba (y < 700) y abajo
    solo quedan renglones ilegibles.
    """
    W, H = 1275, 1650  # carta a 150 dpi
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ink = (38, 38, 42, 255)
    gray = (125, 125, 130, 255)
    light = (206, 206, 210, 255)
    red = (150, 22, 28, 255)
    m = 130
    rng = np.random.default_rng(7)

    # encabezado de laboratorio genérico
    d.text((m, 78), 'LABORATORIO CLÍNICO', font=font(28, True), fill=gray)
    d.text((m, 114), 'Reporte de resultados', font=font(22), fill=light)
    d.line((m, 158, W - m, 158), fill=light, width=3)

    # titular en rojo oscuro
    d.text((m, 222), 'Resultado: pre diabetes', font=font(68, True), fill=red)

    # indicaciones subrayadas
    y = 330
    t = 'Indicaciones: cuidar alimentación'
    f = font(42, True)
    d.text((m, y), t, font=f, fill=ink)
    w = d.textlength(t, font=f)
    d.line((m, y + 54, m + w, y + 54), fill=ink, width=4)

    # tabla "Tus resultados"
    y = 425
    d.text((m, y), 'Tus resultados', font=font(40, True), fill=ink)
    y += 58
    cols = [m, m + 520, m + 800]
    hf = font(27, True)
    for c, h in zip(cols, ['Estudio', 'Resultado', 'Referencia']):
        d.text((c, y), h, font=hf, fill=gray)
    y += 38
    d.line((m, y, W - m, y), fill=light, width=2)
    rf = font(38)
    rfb = font(42, True)
    rows = [('Glucosa en ayunas', '108 mg/dL', '70 – 99'),
            ('Hemoglobina glucosilada', '6.0 %', '< 5.7')]
    for est, res, ref in rows:
        y += 12
        d.text((cols[0], y), est, font=rf, fill=ink)
        d.text((cols[1], y), res, font=rfb, fill=red)
        d.text((cols[2], y), ref, font=rf, fill=ink)
        y += 56
        d.line((m, y, W - m, y), fill=light, width=2)

    # texto ilegible más abajo (como en la referencia)
    y = 750
    d.rounded_rectangle((m, y, m + 200, y + 12), 6, fill=gray)
    y = illegible_lines(d, rng, m, y + 36, W - m, 5, light, h=7, gap=27)
    y += 34
    d.rounded_rectangle((m, y, m + 240, y + 12), 6, fill=gray)
    y = illegible_lines(d, rng, m, y + 36, W - m, 6, light, h=7, gap=27)
    y += 34
    d.rounded_rectangle((m, y, m + 180, y + 12), 6, fill=gray)
    illegible_lines(d, rng, m, y + 36, W - m, 4, light, h=7, gap=27)
    illegible_lines(d, rng, m, H - 150, W - m - 300, 2, light, h=7, gap=22)
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

def blur_map(H, W, s0, ramp):
    """Sigma por píxel: s0 en (x0,y0) y s1 en (x1,y1), lineal entre ambos (profundidad de campo)."""
    if not ramp:
        return np.full((H, W), s0, np.float32)
    x0, y0, x1, y1, s1 = ramp
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx, dy = x1 - x0, y1 - y0
    t = np.clip(((xx - x0) * dx + (yy - y0) * dy) / (dx * dx + dy * dy), 0, 1)
    return s0 + (s1 - s0) * t


def varying_blur(img, sig):
    """Desenfoque gaussiano con sigma variable: interpola entre varios niveles."""
    levels = np.linspace(sig.min(), sig.max(), 6) if sig.max() > sig.min() else [sig.min()]
    stack = [cv2.GaussianBlur(img, (0, 0), float(l)) if l > 0 else img for l in levels]
    if len(stack) == 1:
        return stack[0]
    pos = (sig - levels[0]) / (levels[1] - levels[0])
    i0 = np.clip(np.floor(pos).astype(int), 0, len(levels) - 2)
    f = pos - i0
    st = np.stack(stack)
    rows, cols = np.indices(sig.shape)
    lo, hi = st[i0, rows, cols], st[i0 + 1, rows, cols]
    if img.ndim == 3:
        f = f[..., None]
    return lo * (1 - f) + hi * f


def compose(scene_path, out_path, layout, corners, blur, debug_path=None, ramp=None):
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
    sig = blur_map(H, W, blur, ramp)
    a = varying_blur(a, sig)
    inked = varying_blur(inked, sig)
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
    ap.add_argument('--blur-ramp', help='x0,y0,x1,y1,s1: el desenfoque sube de --blur en (x0,y0) a s1 en (x1,y1)')
    ap.add_argument('--debug')
    ap.add_argument('--flat', help='solo guarda el layout plano en esta ruta')
    args = ap.parse_args()
    if args.flat:
        LAYOUTS[args.layout]().save(args.flat)
        return
    corners = None
    if args.corners:
        corners = np.float32([float(v) for v in args.corners.split(',')]).reshape(4, 2)
    ramp = [float(v) for v in args.blur_ramp.split(',')] if args.blur_ramp else None
    compose(args.scene, args.out, args.layout, corners, args.blur, args.debug, ramp)


if __name__ == '__main__':
    main()
