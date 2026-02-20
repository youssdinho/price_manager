# Changelog

## [1.0.0] — 2026-02-20

### Ajouté
- Hook on_submit Purchase Invoice → recalcul automatique prix de vente (PMP TTC + marge)
- Hook after_insert Item → création automatique Item Price dans toutes les listes de vente (prix = 0)
- Hook after_insert Price List → propagation automatique sur tous les articles à la création
- Hook on_trash Price List → suppression automatique de tous les Item Price à la suppression
- Custom field marge_defaut (%) sur Price List
- Custom field marge (%) sur Item Price
- Marge par défaut 10% si non renseignée
- TVA hardcodée à 20%
- Formule : Prix vente = PMP HT × 1.20 × (1 + marge/100)
