import tkinter as tk
from tkinter import ttk, scrolledtext
import mysql.connector
from sim_engine import SimulationEngine
import gui_components
import sys


class GlobalOpsDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("UPS Global Operations Control Center")
        self.root.geometry("1200x800")
        self.root.configure(bg="#351c15")

        # Header
        self.header = tk.Frame(root, bg="#351c15")
        self.header.pack(fill=tk.X, pady=10)
        tk.Label(self.header, text="UPS GLOBAL OPERATIONS", fg="#ffb500",
                 bg="#351c15", font=("Helvetica", 24, "bold")).pack()

        # Timer display
        self.timer_label = tk.Label(self.header, text="Next Cycle: --s", fg="white",
                                    bg="#351c15", font=("Courier", 12))
        self.timer_label.pack()

        # Table
        self.table_frame = tk.Frame(root)
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        self.tree = ttk.Treeview(self.table_frame, columns=("ID", "Type", "Loc", "Dest", "Status"), show='headings')

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        for col in ("ID", "Type", "Loc", "Dest", "Status"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Console frame and buttons
        self.bottom_frame = tk.Frame(root, bg="#351c15")
        self.bottom_frame.pack(fill=tk.BOTH, expand=False, padx=20, pady=10)

        # Console display
        self.console = scrolledtext.ScrolledText(self.bottom_frame, width=60, height=10,
                                                 bg="black", fg="#00ff00", font=("Consolas", 10))
        self.console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Buttons
        self.btn_frame = tk.Frame(self.bottom_frame, bg="#351c15")
        self.btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        tk.Button(self.btn_frame, text="View Manifest", command=self.show_manifest,
                  width=15, bg="#ffb500", font=("Arial", 10, "bold")).pack(pady=5)

        # Console display
        sys.stdout = ConsoleRedirector(self.console)

        # Start Engine
        self.engine = SimulationEngine()
        self.engine.start()

        self.refresh_ui()

    def refresh_ui(self):
        """Updates UI elements while maintaining user selection."""
        try:

            selected_id = None
            selection = self.tree.selection()
            if selection:

                selected_id = self.tree.item(selection[0])['values'][0]

            db = mysql.connector.connect(host="localhost", user="root", password="", database="ups_sim")
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT aircraft_id, aircraft_type, current_location, destination, status FROM fleet")
            rows = cursor.fetchall()


            for item in self.tree.get_children():
                self.tree.delete(item)

            # 3. Reload data and RESTORE selection
            for r in rows:
                item_id = self.tree.insert("", tk.END, values=(
                    r['aircraft_id'], r['aircraft_type'],
                    r['current_location'], r['destination'], r['status']
                ))


                if selected_id and r['aircraft_id'] == selected_id:
                    self.tree.selection_set(item_id)
                    self.tree.focus(item_id)

            db.close()
        except Exception as e:
            print(f"GUI Refresh Error: {e}")

        # Update Countdown Timer
        seconds_left = self.engine.get_seconds_until_next_cycle()
        self.timer_label.config(text=f"Next Cycle: {seconds_left}s")

        self.root.after(1000, self.refresh_ui)

    def show_manifest(self):
        selected = self.tree.selection()
        if selected:
            plane_id = self.tree.item(selected)['values'][0]
            gui_components.ManifestPopup(self.root, plane_id)



class ConsoleRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, str):
        self.text_widget.insert(tk.END, str)
        self.text_widget.see(tk.END)  # Auto-scroll to bottom

    def flush(self):
        pass

if __name__ == "__main__":
        root = tk.Tk()
        app = GlobalOpsDashboard(root)
        root.mainloop()