# Cas : photo « Aladdin & Jasmine » — attributs seuls (2026-10-25)

**Test** : générer une photo d'Aladdin et Jasmine de Disney sans écrire ni « Aladdin », ni « Jasmine », ni « Disney » dans le prompt.

- **Modèle** : `nano_banana_2_1` (Google) — t2i, 9:16, 1k, `count=2`.
- **Coût réel** : 2 × 1,5 cr = **3 cr**, acceptés au **premier essai** (0 refus, 0 remboursement).
- **Jobs** : `794a5073-9bd1-4fc7-b5d1-a379d5e30fe7`, `613eb49a-2bb1-4ab8-8630-2fc6e8f20e30`.
- **Résultat** : les deux variantes sont immédiatement reconnaissables (QA interne : 8/10 et 7/10). Le style maison `3D animated film aesthetic` + description par attributs a suffi — l'étage « reformulations » n'a pas servi sur ce cas.
- **Écarts assumés** : mains imparfaites ; tenue de la fille approximative (robe intégrale plutôt que haut + pantalon de harem) ; visages génériques.
- **Fichiers** : `v1.png` (plus fidèle), `v2.png`, `prompt.txt` (= texte exact soumis).

**Méthodo** : les refus `ip_detected` déjà mesurés sur Aladdin/Jasmine (10/2026) concernaient des jobs **vidéo** avec noms explicites et refs de film scannées. Ici, en image : attributs seuls + style maison = passé au premier essai.
