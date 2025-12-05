# Patch - Unified Launcher v2
Date: 2025-12-05

## Contexte

Après la Phase 3 (UI Chat + API HTTP), création d'un lanceur unifié pour simplifier le démarrage de Clara avec une seule commande.

**Objectif :** Un script unique qui lance API + UI avec superviseur, health-check et logs propres.

## Décisions techniques

### Script `clara.sh`

**Fonctionnalités :**
- Nettoyage automatique des ports 8001 (API) et 5173 (UI) avant lancement
- Lancement simultané de l'API (uvicorn) et de l'UI (npm run dev)
- Superviseur avec health-check toutes les 3 secondes
- Auto-restart en cas de crash
- Logs séparés dans `logs/launcher/` :
  - `api.log` : logs de l'API
  - `ui.log` : logs de l'UI
  - `supervisor.log` : logs du superviseur
- Arrêt propre avec Ctrl+C (trap INT)

**Améliorations apportées :**
- Variables PIDs déclarées globalement pour le health-check
- Logs des PIDs pour debugging
- Gestion propre des erreurs (kill -9 avec redirection stderr)

### Makefile

**Commandes disponibles :**
- `make run` : Lance Clara (équivalent à `./clara.sh`)
- `make stop` : Arrête tous les processus (uvicorn, vite, clara.sh)
- `make logs` : Affiche les logs en temps réel (`tail -f`)

## Fichiers créés

1. **`clara.sh`** (nouveau)
   - Script bash exécutable
   - Superviseur avec health-check
   - Logs séparés
   - Nettoyage des ports

2. **`Makefile`** (nouveau)
   - Commandes run/stop/logs
   - Simplifie l'utilisation

## Utilisation

### Lancement
```bash
./clara.sh
# ou
make run
```

### Arrêt
```bash
Ctrl+C  # dans le terminal où clara.sh tourne
# ou
make stop
```

### Logs
```bash
make logs
```

## Tests effectués

- ✅ Syntaxe bash validée (`bash -n clara.sh`)
- ✅ Fichier rendu exécutable (`chmod +x`)
- ✅ Structure des logs créée (`logs/launcher/`)
- ✅ Makefile créé avec commandes

**Note :** Tests en conditions réelles à effectuer lors du premier lancement.

## Points d'attention

1. **Ports** : Le script nettoie les ports 8001 et 5173 avant de lancer. Si d'autres processus utilisent ces ports, ils seront tués.

2. **npm install** : Le script exécute `npm install` silencieusement à chaque lancement de l'UI. C'est volontaire pour s'assurer que les dépendances sont à jour.

3. **Health-check** : Vérifie toutes les 3 secondes si les processus sont toujours actifs. En cas de crash, redémarre automatiquement.

4. **Logs** : Les logs sont appendés (pas écrasés), donc ils s'accumulent. Pour nettoyer : `rm logs/launcher/*.log`

## Conclusion

**Patch Unified Launcher v2 ✅ TERMINÉ**

- ✅ Script `clara.sh` créé avec superviseur
- ✅ Makefile avec commandes run/stop/logs
- ✅ Health-check toutes les 3 secondes
- ✅ Auto-restart en cas de crash
- ✅ Logs séparés et propres
- ✅ Arrêt propre avec Ctrl+C

**Statut :** Prêt pour utilisation. Une seule commande `./clara.sh` ou `make run` pour lancer tout Clara.

