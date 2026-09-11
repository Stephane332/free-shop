import json, numpy as np, struct

# --- relecture du GLB qu'on vient d'écrire --------------------------------
raw = open("mannequin.glb","rb").read()
jlen = struct.unpack("<I", raw[12:16])[0]
gl = json.loads(raw[20:20+jlen].decode())
binoff = 20 + jlen + 8
acc, bv = gl["accessors"], gl["bufferViews"]
P = np.frombuffer(raw, dtype=np.float32, count=acc[0]["count"]*3,
                  offset=binoff+bv[0]["byteOffset"]).reshape(-1,3).astype(np.float64)
I = np.frombuffer(raw, dtype=np.uint16, count=acc[1]["count"],
                  offset=binoff+bv[1]["byteOffset"]).astype(np.int64).reshape(-1,3)
sk = json.load(open("squelette.json"))
J  = {k:np.array(v) for k,v in sk["articulations"].items()}
H0 = sk["hauteur"]
print("maillage %d sommets, %d triangles, %.1f cm" % (len(P), len(I), H0))

# --- enveloppe convexe 2D (chaîne monotone d'Andrew) ----------------------
def hull(pts):
    pts = sorted(map(tuple, pts))
    if len(pts) < 3: return np.array(pts)
    def demi(ps):
        h=[]
        for p in ps:
            while len(h)>=2 and (h[-1][0]-h[-2][0])*(p[1]-h[-2][1])-(h[-1][1]-h[-2][1])*(p[0]-h[-2][0]) <= 0: h.pop()
            h.append(p)
        return h
    return np.array(demi(pts)[:-1] + demi(pts[::-1])[:-1])
def perim(h):
    return float(np.sum(np.linalg.norm(np.roll(h,-1,axis=0)-h, axis=1))) if len(h)>2 else 0.0

# --- coupe du maillage à une hauteur y ------------------------------------
E = np.vstack([I[:,[0,1]], I[:,[1,2]], I[:,[2,0]]])
Y = P[:,1]
def coupe(y, xmax=None, xsign=None):
    a, b = E[:,0], E[:,1]
    ya, yb = Y[a], Y[b]
    m = ((ya-y)*(yb-y) < 0)
    if not m.any(): return np.empty((0,2))
    t = ((y-ya[m])/(yb[m]-ya[m]))[:,None]
    pts = P[a[m]] + t*(P[b[m]]-P[a[m]])
    if xmax is not None: pts = pts[np.abs(pts[:,0]) < xmax]
    if xsign is not None: pts = pts[pts[:,0]*xsign > 0]
    return pts[:,[0,2]]

def tronc(pts, gap=2.2):
    """Isole la composante contenant l'axe du corps. Sans ça, l'enveloppe
    convexe d'une coupe à hauteur de poitrine avale les deux bras et le
    tour de poitrine sort 25 cm trop grand."""
    if len(pts) == 0: return pts
    o = pts[np.argsort(pts[:,0])]; xs = o[:,0]
    brk = np.where(np.diff(xs) > gap)[0]
    deb = np.concatenate(([0], brk+1)); fin = np.concatenate((brk+1, [len(xs)]))
    for s, e in zip(deb, fin):
        if xs[s] <= 0.0 <= xs[e-1]: return o[s:e]
    k = int(np.argmax(fin-deb)); return o[deb[k]:fin[k]]

# --- mensurations de la base ---------------------------------------------
yPelvis, yNeck = J["pelvis"][1], J["neck"][1]
ySh = J["l-shoulder"][1]
# Entrejambe = hauteur la plus haute où la coupe présente encore un vide
# autour de l'axe, donc où les deux cuisses sont séparées. (La version
# précédente prenait « juste sous l'articulation du bassin » : circulaire.)
def fourche():
    for y in np.arange(yPelvis, yPelvis-40, -0.25):
        pts = coupe(y, xmax=30)
        if len(pts) < 8: continue
        xs = np.sort(pts[:,0])
        trous = np.diff(xs)
        k = np.argmax(trous)
        if trous[k] > 1.5 and xs[k] < 0 < xs[k+1]:
            return float(y)
    return float(yPelvis - 12)
yCrotch = fourche()
def circ(y, xmax=26, gap=2.2): return perim(hull(tronc(coupe(y, xmax=xmax), gap)))

# Hauteur d'aisselle : première tranche, en descendant depuis l'épaule, où la
# coupe se scinde en trois composantes (tronc + deux bras). Au-dessus, les
# deltoïdes sont anatomiquement soudés au tronc et fausseraient la poitrine.
def nbComposantes(y, gap=2.2):
    pts = coupe(y, xmax=30)
    if len(pts) == 0: return 0
    xs = np.sort(pts[:,0])
    return 1 + int((np.diff(xs) > gap).sum())
yAisselle = ySh
for yy in np.arange(ySh, yPelvis, -0.5):
    if nbComposantes(yy) >= 3: yAisselle = yy; break
print("  aisselle          %.1f cm" % yAisselle)

# balayage : la poitrine est le max sous l'aisselle, la taille le min au-dessus du bassin
ys = np.arange(yCrotch, yNeck, 0.5)
cs = np.array([circ(y) for y in ys])
zone_p = (ys > yPelvis+14) & (ys < yAisselle-1)
zone_t = (ys > yPelvis+2)  & (ys < yPelvis+18)
zone_b = (ys > yCrotch+9)  & (ys < yPelvis+8)   # +9 : au-dessus de la fusion des cuisses
yP = ys[zone_p][np.argmax(cs[zone_p])]; cP = cs[zone_p].max()
yT = ys[zone_t][np.argmin(cs[zone_t])]; cT = cs[zone_t].min()
yB = ys[zone_b][np.argmax(cs[zone_b])]; cB = cs[zone_b].max()
largeurEp = 2*abs(J["l-shoulder"][0])
print("\n--- mensurations réelles du maillage de base ---")
print("  entrejambe (y)    %.1f cm" % yCrotch)
print("  poitrine   %6.1f cm  (à y=%.1f)" % (cP, yP))
print("  taille     %6.1f cm  (à y=%.1f)" % (cT, yT))
print("  bassin     %6.1f cm  (à y=%.1f)" % (cB, yB))
print("  épaules    %6.1f cm  (écart acromions)" % largeurEp)
yc = np.arange(J["neck"][1]+1, J["head"][1]-2, 0.5)
cc = np.array([circ(y, xmax=14, gap=1.2) for y in yc])
cCou = float(cc.min()); yCou = float(yc[np.argmin(cc)])
print("  cou        %6.1f cm  (à y=%.1f)" % (cCou, yCou))

# --- table de profil : par tranche de 0,5 % de la hauteur, on note le
#     périmètre, la demi-largeur, la demi-profondeur et l'axe z du tronc
#     (le maillage n'est pas centré en z : le torse est à z ~ -9).
table=[]
for h in np.arange(0.0, 1.0001, 0.005):
    y = h*H0
    pts = tronc(coupe(y, xmax=26))
    if len(pts) < 6:
        table.append([round(h,4), 0.0, 0.0, 0.0, 0.0]); continue
    hl = hull(pts)
    rx = float((hl[:,0].max()-hl[:,0].min())/2)
    rz = float((hl[:,1].max()-hl[:,1].min())/2)
    zc = float((hl[:,1].max()+hl[:,1].min())/2)
    table.append([round(h,4), round(perim(hl),2), round(rx,2), round(rz,2), round(zc,2)])

# largeur d'épaules mesurée sur la peau, pas entre les centres d'articulation
iSh = min(int(round((ySh/H0)/0.005)), len(table)-1)
largEp = 2*table[iSh][2]
print("  épaules (peau) %6.1f cm" % largEp)

A = {k:[round(float(x),2) for x in J[k]] for k in
     ["l-shoulder","l-elbow","l-hand","l-upper-leg","l-knee","l-ankle","neck","head","pelvis"]}
json.dump({
 "hauteurBase": round(H0,3), "yEntrejambe": round(float(yCrotch),2), "articulations": A,
 "base":{"poitrine":round(float(cP),2), "ceinture":round(float(cT),2), "bassin":round(float(cB),2),
         "epaules":round(float(largEp),2), "acromions":round(float(largeurEp),2), "cou":round(float(cCou),2)},
 "reperes":{"bassin":round(float(yB),2), "ceinture":round(float(yT),2), "poitrine":round(float(yP),2),
            "aisselle":round(float(yAisselle),2), "epaule":round(float(ySh),2), "cou":round(float(yCou),2),
            "tete":round(float(J["head"][1]),2)},
 "profil": table
}, open("profil.json","w"), separators=(",",":"))
print("\nprofil.json : %d tranches" % len(table))
