"""렌더 결과에 시네마틱 그레이딩을 입힌다 (앰버·베이지 하이라이트, 짙은 청록 그림자, 필름 그레인, 비네팅, 빛 번짐).

사용법: python3 tools/grade_still.py IN.png OUT.png
"""
import sys

import numpy as np
from PIL import Image, ImageFilter

SHADOW_GAIN = np.array([0.58, 0.86, 0.90], dtype=np.float32)     # 짙은 청록
HIGHLIGHT_GAIN = np.array([1.06, 0.96, 0.82], dtype=np.float32)  # 앰버/베이지
GRAIN_STRENGTH = 0.016
VIGNETTE = 0.38
SEED = 7


def load(path: str) -> np.ndarray:
    img = Image.open(path).convert("RGB")
    return np.asarray(img).astype(np.float32) / 255.0


def luminance(a: np.ndarray) -> np.ndarray:
    return a @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)


def split_tone(a: np.ndarray) -> np.ndarray:
    lum = luminance(a)[..., None]
    t = np.clip((lum - 0.08) / 0.55, 0, 1)
    t = t * t * (3 - 2 * t)                       # smoothstep
    gain = SHADOW_GAIN * (1 - t) + HIGHLIGHT_GAIN * t
    out = a * gain
    out = np.power(np.clip(out, 0, 1), 1.12)      # 저녁 느낌으로 미드톤을 살짝 가라앉힘
    out = 0.018 + out * 0.975                     # 들뜬 블랙 (필름)
    return np.clip(out, 0, 1)


def halation(a: np.ndarray) -> np.ndarray:
    lum = luminance(a)
    bright = np.clip((lum - 0.72) / 0.28, 0, 1)[..., None] * a
    img = Image.fromarray((bright * 255).astype(np.uint8))
    glow = np.asarray(img.filter(ImageFilter.GaussianBlur(radius=18))).astype(np.float32) / 255.0
    glow *= np.array([1.0, 0.62, 0.35], dtype=np.float32)
    return np.clip(a + glow * 0.55, 0, 1)


def vignette(a: np.ndarray) -> np.ndarray:
    h, w = a.shape[:2]
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2) / np.sqrt(2)
    return a * (1 - VIGNETTE * np.clip(r, 0, 1) ** 2.2)[..., None]


def grain(a: np.ndarray) -> np.ndarray:
    rng = np.random.default_rng(SEED)
    h, w = a.shape[:2]
    noise = rng.normal(0, 1, (h, w)).astype(np.float32)
    n_img = Image.fromarray(((noise * 0.25 + 0.5).clip(0, 1) * 255).astype(np.uint8))
    noise = (np.asarray(n_img.filter(ImageFilter.GaussianBlur(0.7))).astype(np.float32) / 255.0 - 0.5) * 4
    lum = luminance(a)[..., None]
    weight = GRAIN_STRENGTH * (0.6 + 0.8 * lum * (1 - lum) * 4) / 1.4
    return np.clip(a + noise[..., None] * weight, 0, 1)


def main(src: str, dst: str) -> None:
    a = load(src)
    a = halation(a)
    a = split_tone(a)
    a = vignette(a)
    a = grain(a)
    Image.fromarray((a * 255 + 0.5).astype(np.uint8)).save(dst)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
