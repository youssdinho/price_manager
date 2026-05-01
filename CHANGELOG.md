# Changelog

  ## 0.0.3 - 2026-05-01
  ### Feature
  - Ajout d'un job planifié quotidien à 3h du matin (`scheduled.update_all_prices`)
    qui met à jour tous les prix de vente (Item Price) à partir du PMP TTC courant.
  - Chargement bulk des données en 3 requêtes SQL, traitement en mémoire Python,
    commit par batch de 500 articles pour éviter les transactions trop longues.
  - Les articles sans PMP (valuation_rate = 0 ou absent du Bin) sont ignorés.
  - `valid_from = 2000-01-01` appliqué sur toutes les créations d'Item Price.
  - Si `marge = 0` sur un Item Price existant, utilise la `marge_defaut` de la Price List.

  ## 0.0.2 - 2026-05-01
  ### Fix
  - Ajout de `valid_from = 2000-01-01` lors de la création des Item Price
    pour éviter les doublons lors de la modification de factures backdatées.

  ## 0.0.1
  - Version initiale
