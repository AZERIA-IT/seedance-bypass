# Cas : photo « Aladdin & Jasmine » — attributs seuls (2026-10-25)

**Test** : générer une photo d'Aladdin et Jasmine de Disney sans écrire ni « Aladdin », ni « Jasmine », ni « Disney » dans le prompt.

- **Modèle** : `nano_banana_2_1` (Google) — t2i, 9:16, 1k, `count=2`.
- **Coût réel** : 2 × 1,5 cr = **3 cr**, acceptés au **premier essai** (0 refus, 0 remboursement).
- **Jobs** : `794a5073-9bd1-4fc7-b5d1-a379d5e30fe7`, `613eb49a-2bb1-4ab8-8630-2fc6e8f20e30`.
- **Résultat** : les deux variantes sont immédiatement reconnaissables (QA interne : 8/10 et 7/10). Le style maison `3D animated film aesthetic` + description par attributs a suffi — l'étage « reformulations » n'a pas servi sur ce cas.
- **Écarts assumés** : mains imparfaites ; tenue de la fille approximative (robe intégrale plutôt que haut + pantalon de harem) ; visages génériques.
- **Fichiers** : `v1.png` (plus fidèle), `v2.png`, `prompt.txt` (= texte exact soumis).

**Méthodo** : les refus `ip_detected` déjà mesurés sur Aladdin/Jasmine (10/2026) concernaient des jobs **vidéo** avec noms explicites et refs de film scannées. Ici, en image : attributs seuls + style maison = passé au premier essai.

## Comparaison repro vs les vrais personnages (ajout 17:12)

Demande de Mohamed : « c'est pas les vraies, c'est une reproduction — compare avec les vraies ».

Références = frames du film *Aladdin* (1992) via disney.fandom (disneyscreencaps) :
- Jasmine : `ref_jasmine_film1562.png` — jardin, plein jour, tenue turquoise (source `File:Aladdin-disneyscreencaps.com-1562.jpg`).
- Aladdin : `ref_aladdin_film742.png` — tenue de rue (fez + gilet + torse nu), visage net (source `File:Aladdin-disneyscreencaps.com-742.jpg`).

Planches côte à côte, crops buste, cadrage homogène, labels : `comparaison_jasmine.png`, `comparaison_aladdin.png` (générées par `make_compare.py`).

Écarts constatés (repro → vrai) :
- Jasmine : robe d'un bloc au lieu de crop-top + pantalon de harem (ventre nu, épaules dégagées), pas de plume de serre-tête ; coiffure approximative ; bijoux dorés OK.
- Aladdin : chemise sous le gilet (le vrai est torse nu), pas de fez, coiffure surdimensionnée, visage générique.
- Global : « reconnaissable en 2 s, pas fidèle en 5 s » — la fidélité demande une passe fiche perso + refs, pas une génération d'attributs seule.
