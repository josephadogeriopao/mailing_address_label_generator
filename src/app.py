"""
Application Controller Layer & Orchestrator
------------------
Description: Intercepts business metrics, assigns threading streams, coordinates
             state transformations between data managers and display layers.

Author: Joseph Adogeri
Version: 1.2.0
File: app.py
"""

import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Import specialized architectural modules
from src.config_manager import ConfigManager
from src.ui import AddressLabelGeneratorUI
from src.labels_engine import generate_word_labels_engine


class AddressLabelGeneratorController:
    def __init__(self):
        # Instantiate dependencies
        self.config_manager = ConfigManager()

        # Hydrate execution defaults out of settings layers
        config = self.config_manager.load_config()
        self.saved_theme = config.get("appearance_mode", "System")
        self.csv_path = config.get("last_csv_path", "")
        self.output_dir = config.get("last_output_dir", "")
        self.saved_filename = config.get("last_filename", "mailing_labels.docx")

        # Set default presentation layer parameters
        ctk.set_appearance_mode(self.saved_theme)

        # Build UI layout passively
        self.ui = AddressLabelGeneratorUI(self)
        self.hydrate_ui_states()

    def hydrate_ui_states(self):
        """Bridges data entries directly into presentation controls safely."""
        self.ui.theme_switch.set(self.saved_theme)

        if self.csv_path and os.path.exists(self.csv_path):
            self.ui.set_csv_text(self.csv_path)
        else:
            self.csv_path = ""

        if self.output_dir and os.path.exists(self.output_dir):
            self.ui.set_dest_text(self.output_dir)
        else:
            self.output_dir = ""

        if self.saved_filename:
            self.ui.set_filename_text(self.saved_filename)

    def change_theme(self, choice: str):
        ctk.set_appearance_mode(choice)
        self.config_manager.save_setting("appearance_mode", choice)

    def browse_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.csv_path = file_path
            self.ui.set_csv_text(file_path)
            self.config_manager.save_setting("last_csv_path", file_path)

    def browse_dest(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir = dir_path
            self.ui.set_dest_text(dir_path)
            self.config_manager.save_setting("last_output_dir", dir_path)

    def update_progress(self, val):
        self.ui.after(0, lambda: self.ui.progress_bar.set(val))

    def start_generation_thread(self):
        if not self.csv_path:
            messagebox.showerror("Error", "Please select a source CSV address file.")
            return
        if not self.output_dir:
            messagebox.showerror("Error", "Please select a target save folder directory.")
            return

        filename = self.ui.name_entry.get().strip()
        if not filename:
            messagebox.showerror("Error", "Output document file name cannot be blank.")
            return
        if not filename.endswith(".docx"):
            filename += ".docx"

        self.config_manager.save_setting("last_filename", filename)
        final_out_path = os.path.join(self.output_dir, filename)

        # Update and secure layout controls
        self.ui.generate_btn.configure(state="disabled")
        self.ui.status_label.configure(text="Processing file rows...", text_color="#3B8ED0")
        self.ui.progress_bar.set(0)

        # Dispatch async generation loop worker context
        t = threading.Thread(target=self._run_generation, args=(final_out_path,))
        t.daemon = True
        t.start()

    def _run_generation(self, final_out_path):
        """Asynchronous execution container for building physical label arrays."""
        try:
            generate_word_labels_engine(self.csv_path, final_out_path, self.update_progress)
            self.ui.after(0, lambda: self.on_generation_success(final_out_path))
        except Exception as e:
            # Thread-safe Exception String Assignment captures scope safely
            error_message = str(e)
            self.ui.after(0, lambda msg=error_message: self.on_generation_failure(msg))

    def on_generation_success(self, out_path):
        self.ui.status_label.configure(text="Document compiled successfully!", text_color="green")
        self.ui.generate_btn.configure(state="normal")

        msg = f"File created successfully!\n\nSaved to: {out_path}"
        self.ui.show_custom_success_box("Success", msg)

    def on_generation_failure(self, error_msg):
        self.ui.status_label.configure(text="Error occurred during build", text_color="red")
        self.ui.generate_btn.configure(state="normal")
        messagebox.showerror("Execution Error", f"Failed to generate layout file safely:\n{error_msg}")

    def start_main_loop(self):
        """Activates presentation engine event handlers."""
        self.ui.mainloop()


if __name__ == "__main__":
    app = AddressLabelGeneratorController()
    app.start_main_loop()
