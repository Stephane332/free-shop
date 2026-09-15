"""Prépare les textures de peau pour le web.

Deux choses à faire :

1. Le poids. Les PNG d'origine pèsent 10,6 Mo à eux trois : impensable sur un
   forfait data burkinabè. On passe en WebP, et la rugosité est dérivée du
   spéculaire.

2. La teinte. L'auteur de cette peau a peint un visage africain foncé sur un
   corps nettement plus clair — le torse ressort 45 % plus lumineux que le
   visage, ce qui donne un mannequin bicolore. On recale le corps sur le
   visage (gain mesuré : 0,69 sur les trois canaux, donc pur écart de
   luminosité, aucune dérive de teinte).
"""
from PIL import Image
import numpy as np, os

SRC, OUT = "peau/", "peau_web/"
os.makedirs(OUT, exist_ok=True)

# --- albédo, recalé puis compressé ---------------------------------------
im = np.asarray(Image.open(SRC+"skin_male_african_middleage.png").convert("RGB")).astype(np.float64)
H, W, _ = im.shape
peau = im.sum(axis=2) > 40                      # le fond noir de l'atlas est hors sujet
tete = np.zeros((H,W), bool); tete[int(.16*H):int(.86*H), int(.60*W):] = True
mt, mc = peau & tete, peau & ~tete
gain = im[mt].mean(axis=0) / im[mc].mean(axis=0)
im[mc] = np.clip(im[mc]*gain, 0, 255)
print("recalage du corps sur le visage : gain %s" % gain.round(3))
Image.fromarray(im.astype(np.uint8)).save(OUT+"peau_albedo.webp", "WEBP", quality=86, method=6)

# --- normales : grain de peau, rides, pores. 1K suffit à distance d'écran -
Image.open(SRC+"skin_male_african_middleage_NRM.png").convert("RGB") \
     .resize((1024,1024), Image.LANCZOS) \
     .save(OUT+"peau_normal.webp", "WEBP", quality=88, method=6)

# --- rugosité dérivée du spéculaire --------------------------------------
# Spéculaire fort = peau lisse et brillante, donc peu rugueuse. On reste dans
# une plage plausible (0,55-0,86) : plus bas, la peau vire au plastique sous
# la carte d'environnement.
spec = Image.open(SRC+"skin_male_african_middleage_SPEC.png").convert("L").resize((1024,1024), Image.LANCZOS)
spec.point(lambda v: int(0.86*255 - (v/255.0)*(0.86-0.55)*255)) \
    .save(OUT+"peau_rugosite.webp", "WEBP", quality=80, method=6)

tot = 0
for f in sorted(os.listdir(OUT)):
    p = os.path.getsize(OUT+f)/1024; tot += p
    print("  %-22s %7.0f ko" % (f, p))
print("  %-22s %7.0f ko   (contre 10 600 ko de PNG bruts)" % ("TOTAL", tot))
