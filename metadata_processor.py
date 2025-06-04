import os
import json
from PIL import Image, UnidentifiedImageError
import piexif
from datetime import datetime

def process_folder(folder_path, log_callback=None):
    """
    Parcourt le dossier, trouve les paires image-json et traite les métadonnées
    """
    images = {}
    jsons = {}
    total_files = 0
    processed_count = 0
    error_count = 0

    output_folder = os.path.join(folder_path, "Linked Photos")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        if log_callback:
            log_callback(f"Dossier de sortie créé : {output_folder}")
    else:
        if log_callback:
            log_callback(f"Dossier de sortie existant : {output_folder}")


    if log_callback:
        log_callback(f"Début du traitement du dossier : {folder_path}")


    for root, _, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            name_without_ext, ext = os.path.splitext(file)

            if log_callback:
                log_callback(f"Fichier trouvé : {file}, Nom sans extension : {name_without_ext}, Extension : {ext}")

            try:
            
                with Image.open(full_path):
                    images[name_without_ext] = full_path
                    if log_callback:
                        log_callback(f"  -> Détecté comme image : '{name_without_ext}'")
            except UnidentifiedImageError:
               
                if ext.lower() == '.json':
                    current_json_key = name_without_ext
                    if current_json_key.lower().endswith('.supplementa'):
                        current_json_key = os.path.splitext(current_json_key)[0]
                    
                    final_key_for_json = os.path.splitext(current_json_key)[0]

                    jsons[final_key_for_json] = full_path
                    if log_callback:
                        log_callback(f"  -> Détecté comme JSON, clé générée : '{final_key_for_json}'")
                else:
                    if log_callback:
                        log_callback(f"  -> Fichier ignoré (ni image ni JSON) : {file}")

    total_files = len(images)

    # Traite les paires
    for img_name_key, img_path in images.items():
        json_path = jsons.get(img_name_key)

        if json_path and os.path.exists(json_path) and os.path.exists(img_path):
            try:
            
                inject_metadata_from_json(img_path, json_path, output_folder, log_callback)
                processed_count += 1
            except Exception as e:
                error_count += 1
                if log_callback:
                    log_callback(f"Erreur lors du traitement de {os.path.basename(img_path)} : {e}")
        else:
            error_count += 1
            if log_callback:
                log_callback(f"Erreur : Fichier JSON ou image introuvable pour {img_name_key}")

        # MAJ % progression
        if log_callback:
            progress = (processed_count + error_count) / total_files * 100
            log_callback(f"Processus en cours : {progress:.2f}%")

    if log_callback:
        log_callback("\n--- Synchronisation terminée ---")
        log_callback(f"Fichiers traités avec succès : {processed_count}")
        log_callback(f"Erreurs : {error_count}")
    return {"processed_files": processed_count, "errors": error_count}


def convert_to_dms(value):
    """
    Convertit une coordonnée en degrés, minutes, secondes (DMS).
    """
    degrees = int(value)
    minutes = int((value - degrees) * 60)
    seconds = round((value - degrees - minutes / 60) * 3600, 6)
   
    return [(degrees, 1), (minutes, 1), (int(seconds * 10000), 10000)]


def inject_metadata_from_json(image_path, json_path, output_folder, log_callback=None):
    print(f"Début injection métadonnées pour {os.path.basename(image_path)}")

    with open(json_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    img = Image.open(image_path)
    
    try:
        exif_dict = piexif.load(img.info.get("exif", b""))
        if log_callback:
            log_callback("  > EXIF existant chargé.")
    except Exception as e:
        if log_callback:
            log_callback(f"  > Erreur lors du chargement de l'EXIF existant, création d'un nouveau : {e}")
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}, "thumbnail": None}

    # Date prise de vue
    if "photoTakenTime" in metadata and "timestamp" in metadata["photoTakenTime"]:
        timestamp = int(metadata["photoTakenTime"]["timestamp"])
        dt_object = datetime.fromtimestamp(timestamp)
        date_str = dt_object.strftime("%Y:%m:%d %H:%M:%S")
        
        exif_dict["0th"][piexif.ImageIFD.DateTime] = date_str.encode("utf-8")
        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_str.encode("utf-8")
        exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = date_str.encode("utf-8")
        if log_callback:
            log_callback(f"  > Date de prise de vue ajoutée/mise à jour : {date_str}")

    # Coordonnées GPS
    if "geoData" in metadata:
        lat = metadata["geoData"].get("latitude")
        lon = metadata["geoData"].get("longitude")
        if lat is not None and lon is not None:
            try:
                exif_dict["GPS"] = {
                    piexif.GPSIFD.GPSLatitudeRef: ("N" if lat >= 0 else "S").encode("utf-8"),
                    piexif.GPSIFD.GPSLatitude: convert_to_dms(abs(lat)),
                    piexif.GPSIFD.GPSLongitudeRef: ("E" if lon >= 0 else "W").encode("utf-8"),
                    piexif.GPSIFD.GPSLongitude: convert_to_dms(abs(lon)),
                }
                if log_callback:
                    log_callback(f"  > Coordonnées GPS ajoutées/mises à jour : Lat {lat}, Lon {lon}")
            except Exception as e:
                if log_callback:
                    log_callback(f"  > Erreur lors de la conversion des coordonnées GPS : {e}")
                print(f"Erreur lors de la conversion des coordonnées GPS : {e}")

    # Description / Commentaire
    if "description" in metadata:
        comment = metadata["description"]
        if isinstance(comment, str):
            encoded_comment = b'\x00\x00' + comment.encode("utf-8")
            exif_dict["Exif"][piexif.ExifIFD.UserComment] = encoded_comment
            if log_callback:
                log_callback(f"  > Description ajoutée/mise à jour.")
        else:
            if log_callback:
                log_callback(f"  > Avertissement: La description n'est pas une chaîne valide : {comment}")

    # Sauvegarde de l'image finale
    output_image_path = os.path.join(output_folder, os.path.basename(image_path))
    try:
        exif_bytes = piexif.dump(exif_dict)
        img.save(output_image_path, exif=exif_bytes)
    except Exception as e:
        if log_callback:
            log_callback(f"Erreur lors de la sauvegarde de l'image avec EXIF : {e}")
        raise