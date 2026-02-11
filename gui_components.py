import tkinter as tk
from tkinter import ttk
import mysql.connector


class ManifestPopup:
    def __init__(self, parent, plane_id):
        self.win = tk.Toplevel(parent)
        self.win.title(f"Manifest: AC#{plane_id}")
        self.win.geometry("600x450")

        tk.Label(self.win, text=f"LOAD MANIFEST - AIRCRAFT {plane_id}", font=("Arial", 14, "bold")).pack(pady=10)

        self.tree = ttk.Treeview(self.win, columns=("Pos", "ULD", "Type", "Weight"), show='headings')
        for col in ("Pos", "ULD", "Type", "Weight"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.fetch_data(plane_id)

    def fetch_data(self, plane_id):
        db = mysql.connector.connect(host="localhost", user="root", password="", database="ups_sim")
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT position_on_plane, uld_id, uld_type, current_weight 
            FROM uld_inventory WHERE parent_plane = %s
        """, (plane_id,))

        for r in cursor.fetchall():
            self.tree.insert("", tk.END, values=(r['position_on_plane'], r['uld_id'],
                                                 r['uld_type'], f"{r['current_weight']} lbs"))
        db.close()