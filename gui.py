import tkinter as tk
from tkinter import filedialog, messagebox
import os
from metadata_processor import process_folder


class PhotoMetadataApp:
    def __init__(self, master):
        self.master = master
        master.title("Google Photos Metadata Linker")
        master.geometry("800x600")  
        master.resizable(False, False) 
        if os.path.exists('icon.png'):
            try:
                master.iconphoto(False, tk.PhotoImage(file='icon.png'))
            except tk.TclError:
                pass

        self.folder_path = tk.StringVar()


        tk.Label(master, text="Chemin du dossier des photos et des fichiers JSON ").pack(pady=10)

        self.folder_entry = tk.Entry(master, textvariable=self.folder_path, width=50, state="readonly", font=("Arial", 10, "italic")) 
        self.folder_entry.insert(0, "aucun dossier choisi")  
        self.folder_entry.pack(pady=5)

        self.browse_button = tk.Button(master, text="Parcourir", command=self.browse_folder)
        self.browse_button.pack(pady=5)

        self.start_button = tk.Button(master, text="Lancer le lien des métadonnées et des photos", command=self.start_sync)
        self.start_button.pack(pady=20)

        self.log_text = tk.Text(master, height=20, width=80)
        self.log_text.pack(pady=10)

    def browse_folder(self):
        selected_folder = filedialog.askdirectory()
        if selected_folder:
            self.folder_path.set(selected_folder)
            self.folder_entry.configure(state="normal") 
            self.folder_entry.delete(0, tk.END) 
            self.folder_entry.insert(0, selected_folder)  
            self.folder_entry.configure(state="readonly")  
            self.log_message(f"Dossier sélectionné : {selected_folder}")
        else:
            self.folder_entry.configure(state="normal")
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, "aucun dossier choisi, cliquez sur parcourir pour en choisir un")  
            self.folder_entry.configure(state="readonly")
            self.log_message("Aucun dossier sélectionné.")

    def start_sync(self):
        folder = self.folder_path.get()
        if folder == "aucun dossier choisis,cliquez sur parcourir pour en choisir un " or not os.path.isdir(folder):
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier valide !")
            return

        if not os.listdir(folder):  # Vérification si le dossier est vide
            messagebox.showerror("Erreur", "Le dossier sélectionné est vide !")
            return

        valid_files = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        json_files = [f for f in os.listdir(folder) if f.lower().endswith('.json')]

        self.log_message(f"Fichiers image détectés : {valid_files}")
        self.log_message(f"Fichiers JSON détectés : {json_files}")

        if not valid_files:
            messagebox.showerror("Erreur", "Aucun fichier image valide trouvé dans le dossier sélectionné ( .jpg, .jpeg, .png )  ")
            return

        if not json_files:
            messagebox.showerror("Erreur", "Aucun fichier JSON trouvé dans le dossier sélectionné !")
            return

        self.log_message("Début de la synchronisation...")
        try:
            results = process_folder(folder, self.log_message)
            self.log_message("\n--- Synchronisation terminée ---")
            self.log_message(f"Fichiers traités : {results.get('processed_files', 0)}")
            self.log_message(f"Erreurs : {results.get('errors', 0)}")
        except Exception as e:
            self.log_message(f"Une erreur inattendue est survenue : {e}")
            messagebox.showerror("Erreur", f"Une erreur inattendue est survenue : {e}")

    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)