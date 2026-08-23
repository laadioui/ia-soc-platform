# 🚀 Déploiement permanent gratuit — Vercel (frontend) + Render (backend)

Ce guide déploie l'application **sans coût** avec des URLs permanentes, à partir
du repo GitHub `laadioui/ia-soc-platform`. Tout le nécessaire est déjà dans le
repo : `render.yaml` (blueprint backend), Dockerfile, frontend Next.js
compatible Vercel, et seed automatique de données de démo
(`SEED_DEMO_DATA=true`).

> **Durée totale : ~15 minutes.** Aucune carte bancaire requise pour les deux
> plateformes (comptes gratuits).

---

## Étape 1 — Backend sur Render (5 min)

1. Créez un compte sur **https://render.com** (connexion GitHub recommandée).
2. Dashboard → **New +** → **Blueprint**.
3. Sélectionnez le repository **laadioui/ia-soc-platform**.
4. Render lit `render.yaml` à la racine et propose le service
   `ai-soc-platform-api` (Docker, plan **Free**).
5. À l'invite **CORS_ORIGINS**, entrez pour l'instant :
   `["https://placeholder.vercel.app"]` (on mettra la vraie URL Vercel à
   l'étape 3). Laissez `JWT_SECRET_KEY` sur *Generated*.
6. Cliquez **Apply**. Le build Docker prend 3–5 minutes.
7. À la fin, notez l'URL du service, par exemple :
   **`https://ai-soc-platform-api.onrender.com`**
8. Vérifiez :
   - `https://<votre-api>.onrender.com/health` → `{"status": "healthy", ...}`
   - `https://<votre-api>.onrender.com/api/v1/events?page_size=5` → données de
     démo (le seed s'est exécuté au démarrage)
   - `https://<votre-api>.onrender.com/docs` → documentation Swagger

## Étape 2 — Frontend sur Vercel (5 min)

1. Créez un compte sur **https://vercel.com** (connexion GitHub recommandée).
2. **Add New… → Project** → importez **laadioui/ia-soc-platform**.
3. Configurez le projet :
   - **Framework Preset** : Next.js (auto-détecté)
   - **Root Directory** : `apps/frontend`
   - **Build Command** : `npm run build` (défaut)
4. **Environment Variables** → ajoutez :

   | Name | Value |
   |------|-------|
   | `NEXT_PUBLIC_API_URL` | `https://<votre-api>.onrender.com/api/v1` |

5. Cliquez **Deploy** (2–3 minutes).
6. Notez l'URL de production, par exemple :
   **`https://ia-soc-platform.vercel.app`**

## Étape 3 — Relier les deux (2 min)

Le navigateur appelle l'API directement : l'origine Vercel doit être autorisée
par le CORS du backend.

1. Render → service `ai-soc-platform-api` → **Environment**.
2. Éditez `CORS_ORIGINS` → remplacez la valeur par :
   `["https://<votre-app>.vercel.app"]`
3. **Save & Deploy** (redéploiement ~2 min). Attention à conserver les
   guillemets et les crochets (valeur JSON).
4. Ouvrez `https://<votre-app>.vercel.app` → le badge en haut doit afficher
   **LIVE API** (et non DEMO DATA).

## Étape 4 — Mettre à jour l'URL dans LinkedIn / README

Utilisez les URLs permanentes :

- Frontend : `https://<votre-app>.vercel.app`
- API : `https://<votre-api>.onrender.com` (docs sur `/docs`)
- Comptes de démo : `socadmin / AdminPass123!` — `analyst / Analyst@2026!`

---

## ⚠️ Spécificités des plans gratuits (à connaître)

| Comportement | Explication | Impact |
|---|---|---|
| **Mise en veille de l'API** | Render free endort le service après 15 min sans trafic | 1ʳᵉ requête lente (~30–60 s), puis normale. Rechargez la page si le badge affiche DEMO DATA au réveil |
| **Disque éphémère** | SQLite vit dans le conteneur : perdu à chaque redéploiement/restart | Les données de démo sont **réinjectées automatiquement** au démarrage (`SEED_DEMO_DATA=true`). Les modifications faites dans la démo ne persistent pas |
| **750 h/mois** | Render free offre 750 h de runtime par mois | Largement suffisant pour un seul service 24/7 |

Persistance réelle (optionnel) : créez un **Render PostgreSQL** (plan free) et
remplacez `DATABASE_URL` par `postgresql+asyncpg://...` — le schéma est créé
au démarrage et le seed s'exécute si la base est vide.

## 🔄 Redéployer après un `git push`

- **Render** : `autoDeploy: true` → redéploiement automatique à chaque push
  sur `main`.
- **Vercel** : redéploiement automatique à chaque push.
- Si vous modifiez `NEXT_PUBLIC_API_URL` ou `CORS_ORIGINS`, pensez à
  synchroniser l'autre plateforme (étape 3).

## 🧪 Déploiement local équivalent

```bash
# Backend avec seed auto sur base vierge
cd services/collector-service
SEED_DEMO_DATA=true uvicorn app.main:app --port 8000

# Frontend
cd apps/frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 npm run dev
```
