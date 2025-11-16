"""
Backup & Restore per Windows con GUI
by Ettore Lucchesi
"""

import os
import shutil
import zipfile
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox

# Cartelle utente da proteggere
USERPROFILE = os.environ.get("USERPROFILE")
FOLDERS = {
    "Desktop":   os.path.join(USERPROFILE, "Desktop"),
    "Documenti": os.path.join(USERPROFILE, "Documents"),
    "Musica":    os.path.join(USERPROFILE, "Music"),
    "Video":     os.path.join(USERPROFILE, "Videos"),
    "Immagini":  os.path.join(USERPROFILE, "Pictures"),
}

def ensure_path(path: str):
    if not os.path.exists(path):
        os.makedirs(path)

def backup(destination: str):
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    backup_root = os.path.join(destination, stamp)
    ensure_path(backup_root)

    for name, src in FOLDERS.items():
        if os.path.exists(src):
            dst = os.path.join(backup_root, name)
            shutil.copytree(src, dst, dirs_exist_ok=True)

            # Compressione ZIP
            zip_path = dst + ".zip"
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(dst):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, dst)
                        zf.write(full_path, rel_path)
            shutil.rmtree(dst)  # elimina cartella non compressa
        else:
            print(f"! Sorgente non trovata: {src}")

    messagebox.showinfo("Backup", f"Backup completato in:\n{backup_root}")

def restore(destination: str):
    # Seleziona cartella backup
    dirs = [d for d in os.listdir(destination) if os.path.isdir(os.path.join(destination, d))]
    if not dirs:
        messagebox.showerror("Restore", "Nessun backup trovato.")
        return
    chosen_backup = os.path.join(destination, sorted(dirs)[-1])

    for name, dst in FOLDERS.items():
        zip_path = os.path.join(chosen_backup, name + ".zip")
        if os.path.exists(zip_path):
            ensure_path(dst)
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(dst)
        else:
            print(f"! Backup non trovato per {name}")

    messagebox.showinfo("Restore", f"Restore completato da:\n{chosen_backup}")

# GUI
def choose_folder():
    folder = filedialog.askdirectory(title="Seleziona cartella destinazione backup")
    if folder:
        dest_var.set(folder)

def run_backup():
    dest = dest_var.get()
    if not dest:
        messagebox.showwarning("Backup", "Seleziona una cartella di destinazione.")
        return
    backup(dest)

def run_restore():
    dest = dest_var.get()
    if not dest:
        messagebox.showwarning("Restore", "Seleziona la cartella di destinazione.")
        return
    restore(dest)

root = tk.Tk()
root.title("Backup & Restore by Ettore Lucchesi")

tk.Label(root, text="Backup & Restore by Ettore Lucchesi", font=("Arial", 14, "bold")).pack(pady=10)

dest_var = tk.StringVar()

tk.Button(root, text="Scegli cartella destinazione", command=choose_folder).pack(pady=5)
tk.Entry(root, textvariable=dest_var, width=50).pack(pady=5)

tk.Button(root, text="Backup", command=run_backup, bg="lightblue").pack(pady=10)
tk.Button(root, text="Restore", command=run_restore, bg="lightgreen").pack(pady=10)

root.mainloop()
