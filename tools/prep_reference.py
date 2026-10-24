#!/usr/bin/env python3
"""Prépare une référence pour passer le filtre visage de Seedance 2.5 / 2.0.

Principe : le filtre est un classifieur "photo de personne réelle". On ne triche pas
sur le visage, on change la CLASSE SÉMANTIQUE de l'image (photo -> planche de référence)
et on casse l'indice principal du détecteur (les yeux).

Modes image :
  sheet  = bandeau "CHARACTER SHEET REFERENCE" + croix rouge épaisse sur un oeil  (recommandé)
  eyes   = pixellise la bande des yeux
  grid   = grille fine sur la zone visage
  all    = sheet + grid

Mode vidéo :
  --video in.mp4 --out out.mp4 --seconds 3   floute la bande des yeux sur les N premières
  secondes ; le prompt fourni par le script demande au modèle de retirer le flou.

Détection : OpenCV (Haar) si dispo, sinon bande heuristique. Surcharge manuelle :
  --eye-y 0.38 --eye-x 0.42

Usage:
  python3 prep_reference.py photo.png out.png --mode sheet
  python3 prep_reference.py --video in.mp4 --out out.mp4 --seconds 3
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Géométrie par défaut pour un portrait tête-épaules cadré large.
EYE_BAND_Y = 0.34   # haut de la bande des yeux (fraction de la hauteur)
EYE_BAND_H = 0.10   # hauteur de la bande
VIDEO_EYE_Y = 0.29  # bande vidéo si aucune détection (cadrage tête-épaules)
VIDEO_EYE_H = 0.085
CROSS_ARM = 0.10    # demi-bras de la croix
CROSS_STROKE = 26   # épaisseur, en px sur une base 1024
BANNER_H = 0.085
BANNER_TEXT = "CHARACTER SHEET REFERENCE"
PIXEL_DIV = 12      # facteur de pixellisation du mode eyes

REMOVE_BLUR_PROMPT = (
    "The eyes of @Image1 are blurred/pixelated in the reference only: reconstruct sharp, "
    "coherent eyes with the correct iris detail and gaze direction. Keep the rest of the "
    "identity, skin, hair and outfit exactly as referenced. Do not reproduce any overlay, "
    "cross, banner or grid line in the output."
)

try:
    import cv2  # type: ignore
    import numpy as np  # type: ignore
    HAS_CV = True
except Exception:  # pragma: no cover
    HAS_CV = False


def _font(size: int) -> ImageFont.FreeTypeFont:
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


_MODEL = Path(__file__).resolve().parent / "models" / "face_detection_yunet_2023mar.onnx"
_FORCED: list = [None]


def detect_eyes(img: Image.Image):
    """Retourne [(cx, cy, w, h), ...] des yeux détectés (coordonnées pixels).

    YuNet (OpenCV) si le modèle est présent — il rend directement les 5 points du visage,
    dont les deux yeux. Sinon cascades Haar, sinon liste vide (heuristique en aval).
    """
    if not HAS_CV:
        return []
    rgb = img.convert("RGB")
    if _MODEL.exists():
        bgr = cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2BGR)
        h, w = bgr.shape[:2]
        det = cv2.FaceDetectorYN.create(str(_MODEL), "", (w, h), 0.6, 0.3, 5000)
        det.setInputSize((w, h))
        _, faces = det.detect(bgr)
        out = []
        if faces is not None:
            for f in faces:
                for i in (4, 6):  # 4/5 = oeil droit, 6/7 = oeil gauche
                    x, y = float(f[i]), float(f[i + 1])
                    if x > 0 and y > 0:
                        out.append((int(x), int(y), int(f[2] * 0.18), int(f[3] * 0.18)))
        if out:
            return out

    gray = cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2GRAY)
    gray = cv2.equalizeHist(gray)
    casc = getattr(cv2, "CascadeClassifier", None)
    if casc is None:
        return []
    faces = casc(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    eyes_c = casc(cv2.data.haarcascades + "haarcascade_eye.xml")
    out = []
    for (fx, fy, fw, fh) in faces.detectMultiScale(gray, 1.1, 5, minSize=(60, 60)):
        roi = gray[fy:fy + int(fh * 0.6), fx:fx + fw]
        for (ex, ey, ew, eh) in eyes_c.detectMultiScale(roi, 1.1, 6, minSize=(18, 18)):
            out.append((fx + ex + ew // 2, fy + ey + eh // 2, ew, eh))
    return out


def eye_band(img: Image.Image, eyes, eye_y: float) -> tuple[int, int, int, int]:
    """Bande oculaire (x, y, w, h) : bande forcée, sinon yeux détectés, sinon heuristique."""
    if _FORCED[0]:
        return tuple(int(v) for v in _FORCED[0])  # type: ignore[return-value]
    W, H = img.size
    if eyes:
        x0 = max(0, int(min(e[0] - e[2] for e in eyes) - W * 0.04))
        x1 = min(W, int(max(e[0] + e[2] for e in eyes) + W * 0.04))
        y0 = max(0, int(min(e[1] - e[3] for e in eyes) - H * 0.03))
        y1 = min(H, int(max(e[1] + e[3] for e in eyes) + H * 0.03))
        return x0, y0, x1 - x0, y1 - y0
    return int(W * 0.10), int(H * eye_y), int(W * 0.80), int(H * EYE_BAND_H)


def mode_sheet(img: Image.Image, text: str = BANNER_TEXT, eye_y: float = EYE_BAND_Y,
               eye_x: float = 0.42, both: bool = False) -> Image.Image:
    W, H = img.size
    out = img.convert("RGB").copy()
    d = ImageDraw.Draw(out)

    # Croix rouge sur les yeux (épaisse mais franchement un overlay).
    eyes = detect_eyes(out)
    if eyes:
        eye = max(eyes, key=lambda e: e[2] * e[3])
        targets = [(e[0], e[1]) for e in eyes] if both else [(eye[0], eye[1])]
        arm = max(W * 0.05, min(W * 0.10, eye[2] * 2.2))
    else:
        cx = W * eye_x
        cy = H * (eye_y + EYE_BAND_H / 2)
        targets = [(cx - W * 0.09, cy), (cx + W * 0.09, cy)] if both else [(cx, cy)]
        arm = W * CROSS_ARM
    stroke = max(6, int(W * CROSS_STROKE / 1024))
    for (cx, cy) in targets:
        d.line([(cx - arm, cy), (cx + arm, cy)], fill=(220, 38, 38), width=stroke)
        d.line([(cx, cy - arm), (cx, cy + arm)], fill=(220, 38, 38), width=stroke)

    # Bandeau blanc opaque en haut : signal "asset de production", jamais présent sur une photo.
    bh = int(H * BANNER_H)
    d.rectangle([0, 0, W, bh], fill=(255, 255, 255))
    size = max(12, int(bh * 0.55))
    f = _font(size)
    while size > 10 and d.textlength(text, font=f) > W * 0.94:
        size -= 2
        f = _font(size)
    tb = d.textbbox((0, 0), text, font=f)
    d.text(((W - (tb[2] - tb[0])) / 2, (bh - (tb[3] - tb[1])) / 2 - tb[1]), text, font=f, fill=(0, 0, 0))
    return out


def mode_eyes(img: Image.Image, eye_y: float = EYE_BAND_Y) -> Image.Image:
    W, H = img.size
    out = img.convert("RGB").copy()
    x, y, w, h = eye_band(out, detect_eyes(out), eye_y)
    box = (x, y, x + w, y + h)
    patch = out.crop(box)
    small = patch.resize((max(8, patch.width // PIXEL_DIV), max(4, patch.height // PIXEL_DIV)), Image.BILINEAR)
    out.paste(small.resize(patch.size, Image.NEAREST), box)
    return out


def mode_grid(img: Image.Image, step: int = 48, width: int = 3) -> Image.Image:
    W, H = img.size
    out = img.convert("RGB").copy()
    d = ImageDraw.Draw(out)
    for x in range(0, W, step):
        d.line([(x, 0), (x, H)], fill=(255, 255, 255, 190), width=width)
        d.line([(x + 1, 0), (x + 1, H)], fill=(0, 0, 0, 120), width=1)
    for y in range(0, H, step):
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 190), width=width)
        d.line([(0, y + 1), (W, y + 1)], fill=(0, 0, 0, 120), width=1)
    return out


def video_blur_eyes(src: Path, dst: Path, seconds: float, strength: int = 14, forced=None) -> str:
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", str(src)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    try:
        w, h = (int(v) for v in probe.split("x"))
    except ValueError:
        sys.exit(f"dimensions illisibles: {probe!r}")

    # bande : forcée > détectée sur plusieurs instants > heuristique
    band = None
    if forced:
        if all(isinstance(v, float) for v in forced):
            band = (int(forced[0] * w), int(forced[1] * h), int(forced[2] * w), int(forced[3] * h))
        else:
            band = tuple(int(v) for v in forced)
    if HAS_CV and not band:
        tmp = Path("/tmp/_sd_frame.png")
        for t in (0.5, 1.5, 3.0, 5.0, 8.0):
            subprocess.run(
                ["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", str(src), "-frames:v", "1", str(tmp)],
                check=True,
            )
            frame = Image.open(tmp)
            found = detect_eyes(frame)
            if found:
                band = eye_band(frame, found, EYE_BAND_Y)
                break
    if not band:
        band = (int(w * 0.10), int(h * VIDEO_EYE_Y), int(w * 0.80), int(h * VIDEO_EYE_H))
    bx, by, bw, bh = band
    vf = (
        f"[0:v]split=2[base][tmp];"
        f"[tmp]crop={bw}:{bh}:{bx}:{by},boxblur={strength}:2[patch];"
        f"[base][patch]overlay={bx}:{by}:enable='lt(t,{seconds})'[outv]"
    )
    subprocess.run(
        ["ffmpeg", "-y", "-v", "warning", "-i", str(src),
         "-filter_complex", vf, "-map", "[outv]", "-map", "0:a?",
         "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "copy", str(dst)],
        check=True,
    )
    return f"yeux floutés sur les {seconds} premières secondes (bande {bx},{by} {bw}x{bh}) -> {dst}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", nargs="?", help="image d'entrée (ou vidéo si --video)")
    ap.add_argument("out", nargs="?", help="fichier de sortie")
    ap.add_argument("--mode", choices=["sheet", "eyes", "grid", "all"], default="sheet")
    ap.add_argument("--banner", default=BANNER_TEXT)
    ap.add_argument("--video", action="store_true", help="traiter une vidéo (flou des yeux)")
    ap.add_argument("--seconds", type=float, default=3.0)
    ap.add_argument("--strength", type=int, default=14)
    ap.add_argument("--eye-y", type=float, default=EYE_BAND_Y, help="bande oculaire si pas de détection")
    ap.add_argument("--eye-x", type=float, default=0.42, help="position croix si pas de détection")
    ap.add_argument("--band", help="bande forcée en pixels 'x,y,w,h' (prioritaire sur la détection)")
    ap.add_argument("--band-rel", help="bande forcée en fractions 'x,y,w,h' (ex: 0.1,0.30,0.8,0.09)")
    ap.add_argument("--cross", choices=["one", "both"], default="one", help="croix sur un oeil ou les deux")
    a = ap.parse_args()

    if not a.input or not a.out:
        ap.error("input et out sont requis")
    if a.video and shutil.which("ffmpeg") is None:
        sys.exit("ffmpeg requis pour le mode vidéo")

    forced = None
    if a.band:
        forced = tuple(int(v) for v in a.band.split(","))
    if a.band_rel:
        forced = tuple(float(v) for v in a.band_rel.split(","))  # résolu après lecture des dimensions

    if a.video:
        print(video_blur_eyes(Path(a.input), Path(a.out), a.seconds, a.strength, forced))
        print("\nPrompt à joindre :\n" + REMOVE_BLUR_PROMPT)
        return

    img = Image.open(a.input)
    if forced and all(isinstance(v, float) for v in (forced or ())):
        W, H = img.size
        forced = (int(forced[0] * W), int(forced[1] * H), int(forced[2] * W), int(forced[3] * H))
    if forced:
        _FORCED[0] = forced
    if a.mode == "sheet":
        out = mode_sheet(img, a.banner, a.eye_y, a.eye_x, a.cross == "both")
    elif a.mode == "eyes":
        out = mode_eyes(img, a.eye_y)
    elif a.mode == "grid":
        out = mode_grid(img)
    else:
        out = mode_grid(mode_sheet(img, a.banner, a.eye_y, a.eye_x, a.cross == "both"))
    out.save(a.out)
    print(f"{a.mode} -> {a.out} ({out.width}x{out.height}) | détection OpenCV: {HAS_CV} | yeux: {len(detect_eyes(img.convert('RGB')))}")
    if a.mode in ("sheet", "all"):
        print("\nPrompt à joindre (annule visuellement l'overlay) :\n" + REMOVE_BLUR_PROMPT)


if __name__ == "__main__":
    main()
