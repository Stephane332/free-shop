import json, struct, numpy as np

raw = open("mannequin.glb","rb").read()
jlen = struct.unpack("<I", raw[12:16])[0]
gl = json.loads(raw[20:20+jlen].decode())
binoff = 20 + jlen + 8
acc, bv = gl["accessors"], gl["bufferViews"]
n = acc[0]["count"]
P = np.frombuffer(raw, dtype=np.float32, count=n*3, offset=binoff+bv[0]["byteOffset"]).reshape(-1,3).astype(np.float64)
idxbytes = raw[binoff+bv[1]["byteOffset"] : binoff+bv[1]["byteOffset"]+bv[1]["byteLength"]]

pr = json.load(open("profil.json"))
R, H0 = pr["reperes"], pr["hauteurBase"]

def zAxe(y):
    t = pr["profil"]; h = np.clip(y/H0, 0, 1)/0.005
    i = np.clip(h.astype(int), 0, len(t)-2); f = h-i
    z = np.array([r[4] for r in t])
    return z[i]*(1-f) + z[i+1]*f

X, Y, Z = P[:,0], P[:,1], P[:,2]
za = zAxe(Y)
lisse = lambda t: np.clip(t,0,1)**2*(3-2*np.clip(t,0,1))

# --- 1. Aplatissement du buste -------------------------------------------
# Deux noyaux ellipsoïdaux centrés sur les seins de la base. On ramène la
# surface avant vers l'axe du thorax : c'est la morphologie, pas une retouche.
# Attention : ce morph est ensuite MULTIPLIÉ par le facteur de poitrine à
# l'exécution (×1,18 pour un 178/74). Un aplatissement trop timide est donc
# intégralement ré-gonflé. On tape franc.
yb, xb, avant = R["poitrine"] - 0.5, 5.4, Z > za
d = np.sqrt(((np.abs(X)-xb)/7.4)**2 + ((Y-yb)/8.2)**2)
w = lisse(1.0 - d) * avant
Z2 = Z - w * (Z - za) * 0.66
X3, Z3 = X, Z2

P2 = np.stack([X3, Y, Z3], axis=1)
bouge = np.linalg.norm(P2-P, axis=1)
print("sommets déplacés : %d / %d | déplacement max %.2f cm | moyen %.3f cm"
      % ((bouge>0.01).sum(), n, bouge.max(), bouge[bouge>0.01].mean()))

pos = P2.astype(np.float32)
gl["accessors"][0]["min"] = [float(pos[:,i].min()) for i in range(3)]
gl["accessors"][0]["max"] = [float(pos[:,i].max()) for i in range(3)]
gl["asset"]["generator"] = "free-shop / base MakeHuman CC0 + morph masculin"
bposd = pos.tobytes(); bposd += b"\x00"*((-len(bposd))%4)
buf = bposd + idxbytes
gl["buffers"][0]["byteLength"] = len(buf)
gl["bufferViews"][1]["byteOffset"] = len(bposd)
js = json.dumps(gl, separators=(",",":")).encode(); js += b" "*((-len(js))%4)
glb  = struct.pack("<III", 0x46546C67, 2, 12+8+len(js)+8+len(buf))
glb += struct.pack("<II", len(js), 0x4E4F534A) + js
glb += struct.pack("<II", len(buf), 0x004E4942) + buf
open("mannequin.glb","wb").write(glb)
print("mannequin.glb réécrit : %.0f ko" % (len(glb)/1024))
