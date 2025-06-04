# Google Photos Metadata Linker

## Description
Ce projet permet de lier les métadonnées JSON des photos Google Photos aux fichiers image correspondants. Si vous avez utilisé Google Takeout pour faire une sauvegarde de vos photos par exemple Les métadonnées, telles que la date de prise de vue, les coordonnées GPS et les descriptions, sont injectées directement dans les fichiers image.

## Fonctionnalités
- **Interface graphique (Tkinter)** : Sélectionnez un dossier contenant des fichiers image et JSON.
- **Injection de métadonnées** : Ajout des informations JSON dans les fichiers image.
- **Gestion des erreurs** : Affichage des erreurs et des succès dans une zone de log.
- **Progression** : Indication du pourcentage de progression pendant le traitement.

## Prérequis
- Python 3.7 ou supérieur
- Bibliothèques Python :
  - `Pillow`
  - `piexif`

## Installation
1. Clonez ce dépôt ou téléchargez le fichier ZIP
2. Installez les dépendances avec `pip` :
   ```bash
   pip install -r requirements.txt
   ```

## Utilisation
1. Lancez l'application avec la commande suivante :
   ```bash
   python main.py
   ```
2. Utilisez l'interface graphique pour :
   - Sélectionner un dossier contenant des fichiers image et JSON.
   - Lancer la synchronisation des métadonnées.
3. Les fichiers traités seront sauvegardés dans un sous-dossier nommé `Linked Photos`.

## Structure du projet
```
Google Photos Metadata Linker/
├── main.py                # Point d'entrée principal
├── gui.py                 # Interface graphique Tkinter
├── metadata_processor.py  # Logique de traitement des métadonnées
├── requirements.txt       # Dépendances Python
├── README.md              # Documentation du projet
```

## Exemple de fichiers
### Fichier JSON
```json
{
  "title": "example.jpg",
  "description": "Photo prise lors de mes vacances.",
  "photoTakenTime": {
    "timestamp": "1678886400",
    "formatted": "15 mars 2023 à 00:00:00 UTC"
  },
  "geoData": {
    "latitude": 45.696667,
    "longitude": 3.090556
  }
}
```

### Fichier Image
- `example.jpg`

## Notes
- Les fichiers JSON doivent avoir un nom correspondant à celui des fichiers image (sans extension).
- Nous respectons votre vie privée, vos photos et métadonnées sont uniquements sauvegardées sur votre ordinateur et non sur un serveur externe.



## Licence
Ce projet est sous licence MIT.