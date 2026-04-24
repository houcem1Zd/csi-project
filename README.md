# 🏭 Formation de Cellules Industrielles

Outil d'optimisation de la disposition des ateliers industriels basé sur :
- **Méthode de King** — Formation d'îlots de fabrication par réordonnancement de la matrice d'incidence
- **Méthode Chaînon** — Optimisation de la disposition des flux par recuit simulé sur grille en nid d'abeille

---

## 🚀 Déploiement sur Render

### Étape 1 — Créer un dépôt GitHub

1. Créez un nouveau dépôt GitHub (public ou privé)
2. Ajoutez les fichiers suivants dans le dépôt :
   - `app.py`
   - `requirements.txt`
   - `render.yaml`
   - `.streamlit/config.toml`

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/VOTRE_NOM/VOTRE_REPO.git
git push -u origin main
```

### Étape 2 — Déployer sur Render

1. Connectez-vous sur [render.com](https://render.com)
2. Cliquez sur **"New +"** → **"Web Service"**
3. Connectez votre compte GitHub et sélectionnez votre dépôt
4. Render détecte automatiquement `render.yaml` et configure le service
5. Cliquez sur **"Create Web Service"**
6. Attendez ~3 minutes que le build se termine
7. Votre app est disponible à l'URL fournie par Render 🎉

### Configuration manuelle (si render.yaml non détecté)

| Paramètre | Valeur |
|-----------|--------|
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true --server.enableCORS false` |
| **Plan** | Free |

---

## 💻 Lancement local

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run app.py
```

L'application sera accessible à : http://localhost:8501

---

## 📋 Utilisation

### Étape 0 — Données de gamme
- Importez un fichier Excel (`.xlsx`) ou saisissez manuellement
- Colonnes : **Produit** | **Gamme** | **Nombre de manutentions**
- Séparateurs acceptés pour la gamme : `-`, `;`, `,`, espace

### Étape 1 — Méthode de King
- Cliquez sur **"Appliquer la méthode de King"**
- La matrice d'incidence est réordonnée et les îlots sont détectés automatiquement

### Étape 2 — Méthode Chaînon
- Sélectionnez un îlot à analyser
- Ajustez les paramètres d'optimisation (nombre de pas, redémarrages)
- Cliquez sur **"Calculer la disposition Chaînon"**

---

## 📦 Dépendances

- `streamlit` — Interface web
- `pandas` + `numpy` — Traitement des données
- `matplotlib` + `seaborn` — Visualisations
- `openpyxl` + `xlrd` — Lecture des fichiers Excel
