"""Prepara la escena base de prospección a partir de la referencia, solo con OpenCV.

Uso:
  python3 preparar-escena.py ref01 referencias/prospeccion/ref-01.png marca/tof-ref01-escena.png

ref01: borra el texto de la hoja (rellena con la luz del propio papel), recorta para
sacar la mano en la panza y el monitor del ultrasonido, y escala a 1080×1080 con
Lanczos + enfoque suave + grano de celular.
"""
import sys

import cv2
import numpy as np


def blank_sheet(im, seed_xy):
    """Borra lo impreso en la hoja que contiene seed_xy y deja papel limpio con su luz."""
    f = im.astype(np.float32)
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    paper = ((hsv[..., 2] > 150) & (hsv[..., 1] < 40)).astype(np.uint8)
    _, lab = cv2.connectedComponents(paper, connectivity=8)
    comp = (lab == lab[seed_xy[1], seed_xy[0]]).astype(np.uint8) * 255
    # la hoja con sus letras = componente de papel con los huecos rellenos
    ff = comp.copy()
    h, w = ff.shape
    cv2.floodFill(ff, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 255)
    filled = comp | cv2.bitwise_not(ff)
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)

    def normconv(wt, sig):
        wt = wt.astype(np.float32)
        num = cv2.GaussianBlur(f * wt[..., None], (0, 0), sig)
        den = cv2.GaussianBlur(wt, (0, 0), sig)
        return num / np.maximum(den, 1e-4)[..., None], den

    # papel limpio = píxeles de la hoja que no son más oscuros que la luz local
    clean = cv2.erode(comp, np.ones((3, 3), np.uint8)) > 0
    for _ in range(3):
        bg, _ = normconv(clean, 5)
        bgg = cv2.cvtColor(np.clip(bg, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
        clean = (filled > 0) & (gray > bgg - 6)
        clean = cv2.erode(clean.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    bg, den = normconv(clean, 5)
    bg_wide, _ = normconv(clean, 14)
    wgt = np.clip(den / 0.25, 0, 1)[..., None]
    bg = bg * wgt + bg_wide * (1 - wgt)

    rng = np.random.default_rng(1)
    noise = cv2.GaussianBlur(rng.normal(0, 3.2, (h, w)).astype(np.float32), (0, 0), 0.6)[..., None]
    a = cv2.GaussianBlur(cv2.erode(filled, np.ones((3, 3), np.uint8)), (0, 0), 0.8)
    a = (a.astype(np.float32) / 255)[..., None]
    return np.clip(f * (1 - a) + (bg + noise) * a, 0, 255).astype(np.uint8)


def upscale(crop, size=1080):
    up = cv2.resize(crop, (size, size), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    up = up + 0.6 * (up - cv2.GaussianBlur(up, (0, 0), 2.0))
    rng = np.random.default_rng(5)
    grain = cv2.GaussianBlur(rng.normal(0, 4.0, (size, size)).astype(np.float32), (0, 0), 0.7)[..., None]
    return np.clip(up + grain, 0, 255).astype(np.uint8)


def ref01(im):
    # coordenadas de la referencia a 600×600
    im = blank_sheet(im, (450, 420))
    return upscale(im[125:555, 170:600])


RECIPES = {'ref01': ref01}

if __name__ == '__main__':
    recipe, src, dst = sys.argv[1:4]
    im = cv2.imread(src)
    if im.shape[:2] != (600, 600):
        im = cv2.resize(im, (600, 600), interpolation=cv2.INTER_AREA)
    cv2.imwrite(dst, RECIPES[recipe](im))
