# Clara - Interface Admin

## Status

📅 **Prévue pour Phase 3**

Interface d'administration et de monitoring pour Clara.

## Fonctionnalités prévues

### Phase 3
- Visualisation des agents (nom, rôle, état)
- Liste des drivers/tools installés
- Consultation des sessions récentes
- Accès aux logs (session + debug)
- Visualisation des erreurs récurrentes

### Phases ultérieures
- Édition des paramètres (température, modèles, timeouts)
- Gestion des workflows
- Statistiques d'utilisation
- Monitoring en temps réel
- Gestion de la mémoire

## Technologies envisagées

- React ou Vue.js pour le frontend
- Dashboard UI (Material-UI, Ant Design, ou Tailwind)
- FastAPI pour le backend API
- WebSockets pour les mises à jour en temps réel

## Architecture

```
admin_frontend/
  ├── src/
  │   ├── components/
  │   │   ├── AgentList/
  │   │   ├── SessionViewer/
  │   │   ├── LogViewer/
  │   │   └── Settings/
  │   ├── pages/
  │   ├── api/
  │   └── utils/
  ├── public/
  └── package.json
```

