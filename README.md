# free-shop — Cabine Faso

Application d'essayage 3D pour une boutique de vêtements homme à Ouagadougou.

Le client compose une tenue à partir du stock réel du commerçant et la voit
portée sur un mannequin à **sa** morphologie. Deux problèmes de terrain sont
traités au passage : personne ne connaît sa taille, et on négocie le prix.

## État

| | |
|---|---|
| `prototype/mannequin-3d/` | Maquette jouable. Ouvrir `index.html` via un serveur HTTP (elle charge des fichiers). |
| `prototype/mannequin-3d/assets/` | Maillage du mannequin + profil anthropométrique. Voir `SOURCE.md` pour la licence. |
| `tools/` | Chaîne de préparation du maillage (Python + numpy). |

L'application (PWA + APK) n'est pas encore écrite ; la maquette sert à valider
le moteur avant d'investir dedans.

## Ce que fait la maquette

**Le corps.** Un vrai maillage anatomique (13 380 sommets, base MakeHuman, CC0)
déformé sommet par sommet pour atteindre les mesures du client. Les membres
bougent autour de leur propre axe anatomique, jamais autour de l'axe du corps.
Le ventre pousse vers l'avant plus que sur les côtés, à tour de taille égal.

**Les mesures.** Taille et poids suffisent à estimer les 8 mesures utiles. Chaque
mesure réelle saisie remplace une estimation et fait monter la confiance
affichée. Les régressions sont génériques et devront être recalées sur des
clients réellement mesurés en boutique — c'est le seul vrai fossé concurrentiel
du projet.

**Les vêtements.** Bâtis sur le profil du corps déformé, dilatés par l'aisance
réelle de la taille choisie. La recommandation de taille vient de la comparaison
`mesures du vêtement à plat × mesures du corps`, zone par zone, avec un verdict
serré / bien / ample par zone.

**Le marchandage.** Le commerçant règle un prix plancher que le client ne voit
jamais, et une humeur. L'app négocie à sa place. Trois tours, puis dernier prix.
Un bouton bascule sur WhatsApp pour ceux qui veulent parler à un humain.

## Régénérer les assets

```bash
pip install numpy
curl -o base.obj https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/3dobjs/base.obj
python3 tools/conv.py      # base.obj    -> mannequin.glb + squelette.json
python3 tools/profil.py    # mannequin.glb -> profil.json (mensurations par tranche)
python3 tools/masc.py      # morph masculin, puis relancer profil.py
```

## Limites connues

- La base MakeHuman est androgyne et penche encore féminin malgré le morph
  d'aplatissement du buste. Il faut une vraie cible de morphologie masculine.
- L'empiècement d'épaule des hauts laisse une arête visible sur le deltoïde.
- Le haut de cuisse traverse encore le pantalon par endroits.
- Stock, textures et prix sont simulés.
