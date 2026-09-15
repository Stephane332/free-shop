# free-shop — Cabine Faso

Application d'essayage 3D pour une boutique de vêtements homme à Ouagadougou.

Le client compose une tenue à partir du stock réel du commerçant et la voit
portée sur un mannequin photoréaliste. Il ne donne **ni son poids, ni sa
taille** : juste ce qu'il porte d'habitude. Deux problèmes de terrain sont
traités au passage — un L n'est pas le même L d'une boutique à l'autre, et on
négocie le prix.

## État

| | |
|---|---|
| `prototype/mannequin-3d/` | Maquette jouable. Ouvrir `index.html` via un serveur HTTP (elle charge des fichiers). |
| `prototype/mannequin-3d/assets/` | Mannequin et peau. Licences et provenance dans `SOURCE.md`. |
| `tools/` | Chaîne de préparation du mannequin (Python + numpy + Pillow). |

L'application (PWA + APK) n'est pas encore écrite ; la maquette sert à valider
le moteur avant d'investir dedans.

## Les partis pris

**Un seul mannequin, fixe.** Photoréaliste, 1,81 m, tour de poitrine 100 cm —
il porte du L. Maillage anatomique de 14 517 sommets et peau photographique,
tous deux issus de MakeHuman sous licence CC0. La morphologie vient de la
cible officielle `african-male-young` : un vrai morph d'auteur, pas une
déformation devinée. Détail des licences et des mensurations dans
`prototype/mannequin-3d/assets/SOURCE.md`.

**Le client dit juste sa taille habituelle.** Pas de formulaire, pas de
mètre-ruban. L'app compare les mesures réelles de l'article à ce qu'une taille
veut dire en général, et corrige : « ce L taille petit de 4 cm, prends le XL ».
Un article en M sera visiblement juste sur le mannequin, un XL visiblement
ample — c'est la même information, montrée au lieu d'être expliquée.

**Le commerçant relève 4 mesures par article.** Le vêtement posé à plat,
largeur fois deux. 90 secondes. Sans ces chiffres, aucun conseil de taille
n'est possible et on retombe sur « ça ne me va pas » après livraison, ce qui
coûte cher ici.

**Les photos sont les siennes.** Chaque article porte la vraie photo prise au
téléphone. Elle sert de vignette dans le rayon *et* de tissu sur le mannequin.
Le bouton « Photo du patron » dans la maquette fait la chaîne en miniature :
détourage par couleur de coin, recadrage sur le vêtement, application.

**Le marchandage reste un marchandage.** Le commerçant règle un prix plancher
que le client ne voit jamais, plus une humeur. L'app négocie à sa place,
24 h/24. Trois tours, puis dernier prix. Un bouton bascule sur WhatsApp pour
ceux qui veulent parler à un humain.

## Régénérer les assets

```bash
pip install numpy pillow
curl -o base.obj https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/3dobjs/base.obj
curl -o skins02.zip https://files2.makehumancommunity.org/asset_packs/skins02/skins02_cc0.zip
python3 tools/conv.py     # base.obj + morph -> mannequin.glb + squelette.json
python3 tools/profil.py   # mannequin.glb -> profil.json (mensurations par tranche)
python3 tools/tex.py      # peaux PNG -> WebP recalés
```

## Limites connues

- L'empiècement d'épaule des hauts laisse une légère arête au deltoïde.
- Les vêtements sont des surfaces décalées du corps, pas du tissu simulé :
  la tombée est plausible mais il n'y a ni plis ni poids de tissu.
- Un seul gabarit de corps. Un client costaud ne se projette pas complètement.
- Stock et prix simulés ; les photos du patron se chargent à la main.
