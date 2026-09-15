"""Petit utilitaire GLB partagé : lecture par nom d'attribut, écriture en place."""
import json, struct, numpy as np

def lire(chemin):
    raw = open(chemin,"rb").read()
    jlen = struct.unpack("<I", raw[12:16])[0]
    gl = json.loads(raw[20:20+jlen].decode())
    binoff = 20 + jlen + 8
    prim = gl["meshes"][0]["primitives"][0]
    def acc(i, dt, comp):
        a = gl["accessors"][i]; bv = gl["bufferViews"][a["bufferView"]]
        arr = np.frombuffer(raw, dtype=dt, count=a["count"]*comp, offset=binoff+bv.get("byteOffset",0))
        return arr.reshape(-1, comp) if comp > 1 else arr
    d = {"raw":raw, "gltf":gl, "binoff":binoff, "prim":prim,
         "P": acc(prim["attributes"]["POSITION"], np.float32, 3).astype(np.float64),
         "I": acc(prim["indices"], np.uint16, 1).astype(np.int64).reshape(-1,3)}
    if "TEXCOORD_0" in prim["attributes"]:
        d["UV"] = acc(prim["attributes"]["TEXCOORD_0"], np.float32, 2)
    return d

def ecrire_positions(chemin, d, P2):
    """Réécrit les positions sur place : même nombre de sommets, donc même
    longueur de tampon. Rien d'autre du fichier n'est touché."""
    gl, raw = d["gltf"], bytearray(d["raw"])
    ia = d["prim"]["attributes"]["POSITION"]
    a = gl["accessors"][ia]; bv = gl["bufferViews"][a["bufferView"]]
    off = d["binoff"] + bv.get("byteOffset", 0)
    b = P2.astype(np.float32).tobytes()
    raw[off:off+len(b)] = b
    a["min"] = [float(P2[:,i].min()) for i in range(3)]
    a["max"] = [float(P2[:,i].max()) for i in range(3)]
    # l'en-tête JSON peut changer de longueur : on reconstruit proprement
    binlen = struct.unpack("<I", bytes(raw[d["binoff"]-8:d["binoff"]-4]))[0]
    buf = bytes(raw[d["binoff"]:d["binoff"]+binlen])
    js = json.dumps(gl, separators=(",",":")).encode(); js += b" "*((-len(js))%4)
    out  = struct.pack("<III", 0x46546C67, 2, 12+8+len(js)+8+len(buf))
    out += struct.pack("<II", len(js), 0x4E4F534A) + js
    out += struct.pack("<II", len(buf), 0x004E4942) + buf
    open(chemin,"wb").write(out)
    return len(out)
