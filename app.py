import os
import json
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Import the functional generation logic from your engine module
from labels_engine import generate_word_labels_engine


class AddressLabelGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuration file path for persistent settings
        self.config_file = "app_config.json"

        # Window Config
        self.title("Address Label Generator")
        self.geometry("540x520")
        self.resizable(False, False)

        # Apply custom application icon if it exists locally
        icon_filename = "app_icon.ico"
        if os.path.exists(icon_filename):
            self.iconbitmap(icon_filename)

        # Load Saved Configuration Settings
        config = self.load_saved_config()
        saved_theme = config.get("appearance_mode", "System")

        # Initialize paths and file names from persistence layer
        self.csv_path = config.get("last_csv_path", "")
        self.output_dir = config.get("last_output_dir", "")
        saved_filename = config.get("last_filename", "mailing_labels.docx")

        ctk.set_appearance_mode(saved_theme)
        ctk.set_default_color_theme("blue")

        self.create_widgets()

        # Restore saved entries into UI states
        self.theme_switch.set(saved_theme)

        # Show full CSV path if it still exists on the system
        if self.csv_path and os.path.exists(self.csv_path):
            self.csv_entry.configure(state="normal")
            self.csv_entry.insert(0, self.csv_path)
            self.csv_entry.configure(state="readonly")

        # Show full directory folder path if it still exists
        if self.output_dir and os.path.exists(self.output_dir):
            self.dest_entry.configure(state="normal")
            self.dest_entry.insert(0, self.output_dir)
            self.dest_entry.configure(state="readonly")

        if saved_filename:
            self.name_entry.delete(0, "end")
            self.name_entry.insert(0, saved_filename)

    def create_widgets(self):
        # 1. Header Frame
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=30, pady=(25, 15))

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Address Label Generator",
            font=ctk.CTkFont(family="Arial", size=24, weight="bold")
        )
        self.title_label.pack(side="left")

        # Quick Appearance Mode Toggle
        self.theme_switch = ctk.CTkOptionMenu(
            self.header_frame,
            values=["System", "Dark", "Light"],
            command=self.change_theme,
            width=90
        )
        self.theme_switch.pack(side="right")

        # Subtitle Template Flag
        self.subtitle = ctk.CTkLabel(
            self,
            text="Generate print-ready Word files formatted for Avery 5160 template layout sheets.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.subtitle.pack(anchor="w", padx=30, pady=(0, 20))

        # Main Input Layout Form
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(fill="x", padx=30, pady=0, ipady=15)

        # Row A: Input CSV selection
        self.csv_label = ctk.CTkLabel(self.form_frame, text="Source CSV File Path:", font=ctk.CTkFont(weight="bold"))
        self.csv_label.pack(anchor="w", padx=20, pady=(15, 5))

        self.csv_entry_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.csv_entry_frame.pack(fill="x", padx=20)

        self.csv_entry = ctk.CTkEntry(self.csv_entry_frame, placeholder_text="No file selected...", state="readonly")
        self.csv_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.csv_btn = ctk.CTkButton(self.csv_entry_frame, text="Browse...", width=100, command=self.browse_csv)
        self.csv_btn.pack(side="right")

        # Row B: Destination Directory Selection
        self.dest_label = ctk.CTkLabel(self.form_frame, text="Save Location Folder Path:", font=ctk.CTkFont(weight="bold"))
        self.dest_label.pack(anchor="w", padx=20, pady=(15, 5))

        self.dest_entry_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.dest_entry_frame.pack(fill="x", padx=20)

        self.dest_entry = ctk.CTkEntry(self.dest_entry_frame, placeholder_text="No folder selected...", state="readonly")
        self.dest_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.dest_btn = ctk.CTkButton(self.dest_entry_frame, text="Browse...", width=100, command=self.browse_dest)
        self.dest_btn.pack(side="right")

        # Row C: Target Name File Box
        self.name_label = ctk.CTkLabel(self.form_frame, text="Output Document Name:", font=ctk.CTkFont(weight="bold"))
        self.name_label.pack(anchor="w", padx=20, pady=(15, 5))

        self.name_entry = ctk.CTkEntry(self.form_frame, placeholder_text="mailing_labels.docx")
        self.name_entry.pack(fill="x", padx=20, pady=(0, 5))

        # Action Execution Box
        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(25, 5))

        self.status_label = ctk.CTkLabel(self, text="Ready", font=ctk.CTkFont(size=11), text_color="gray")
        self.status_label.pack(pady=(0, 10))

        self.generate_btn = ctk.CTkButton(
            self,
            text="Generate Labels Word Doc",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45,
            command=self.start_generation_thread
        )
        self.generate_btn.pack(fill="x", padx=30, pady=(5, 20))

    def load_saved_config(self) -> dict:
        """Reads complete configuration properties from the JSON file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_config(self, key: str, value: str):
        """Updates a specific configuration property safely in the storage layer."""
        config = self.load_saved_config()
        config[key] = value
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def change_theme(self, choice: str):
        """Sets application mode and writes current value to persistent storage."""
        ctk.set_appearance_mode(choice)
        self.save_config("appearance_mode", choice)

    def browse_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.csv_path = file_path
            self.csv_entry.configure(state="normal")
            self.csv_entry.delete(0, "end")
            self.csv_entry.insert(0, file_path)
            self.csv_entry.configure(state="readonly")
            self.save_config("last_csv_path", file_path)

    def browse_dest(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir = dir_path
            self.dest_entry.configure(state="normal")
            self.dest_entry.delete(0, "end")
            self.dest_entry.insert(0, dir_path)
            self.dest_entry.configure(state="readonly")
            self.save_config("last_output_dir", dir_path)

    def update_progress(self, val):
        self.after(0, lambda: self.progress_bar.set(val))

    def start_generation_thread(self):
        if not self.csv_path:
            messagebox.showerror("Error", "Please select a source CSV address file.")
            return
        if not self.output_dir:
            messagebox.showerror("Error", "Please select a target save folder directory.")
            return

        filename = self.name_entry.get().strip()
        if not filename:
            messagebox.showerror("Error", "Output document file name cannot be blank.")
            return
        if not filename.endswith(".docx"):
            filename += ".docx"

        # Persist the clean file name parameter
        self.save_config("last_filename", filename)

        final_out_path = os.path.join(self.output_dir, filename)

        # Lock UI Elements during operations
        self.generate_btn.configure(state="disabled")
        self.status_label.configure(text="Processing file rows...", text_color="#3B8ED0")
        self.progress_bar.set(0)

        # Run background thread so UI stays active
        t = threading.Thread(target=self.run_generation, args=(final_out_path,))
        t.daemon = True
        t.start()

    def on_generation_success(self, out_path):
        """Unified success routine executing structural and alert updates on the main thread."""
        self.status_label.configure(text="Document compiled successfully!", text_color="green")
        self.generate_btn.configure(state="normal")

        msg = f"File created successfully!\n\nSaved to: {out_path}"
        self.show_custom_success_box("Success", msg)

    def on_generation_failure(self, error_msg):
        """Unified failure routine handling layout exceptions and error warnings safely."""
        self.status_label.configure(text="Error occurred during build", text_color="red")
        self.generate_btn.configure(state="normal")
        messagebox.showerror("Execution Error", f"Failed to generate layout file safely:\n{error_msg}")

    def show_custom_success_box(self, title, message):
        """Creates a custom high-visibility pop-up window with a Championship Cup emoji icon."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("420x180")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        content_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        icon_label = ctk.CTkLabel(content_frame, text="🏆", font=ctk.CTkFont(size=44))
        icon_label.pack(side="left", padx=(10, 20), anchor="n")

        text_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True)

        msg_title = ctk.CTkLabel(text_frame, text="Generation Complete!", font=ctk.CTkFont(weight="bold", size=14))
        msg_title.pack(anchor="w", pady=(0, 5))

        msg_body = ctk.CTkLabel(text_frame, text=message, font=ctk.CTkFont(size=12), justify="left", wraplength=280)
        msg_body.pack(anchor="w")

        ok_btn = ctk.CTkButton(dialog, text="OK", width=90, command=dialog.destroy)
        ok_btn.pack(side="bottom", pady=(0, 15))

        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

    def run_generation(self, final_out_path):
        """Asynchronous execution task for labels file generation."""
        try:
            generate_word_labels_engine(self.csv_path, final_out_path, self.update_progress)
            self.after(0, lambda: self.on_generation_success(final_out_path))
        except Exception as e:
            # Pass formatting error messages directly into the UI state wrapper method
            # NEW FIXED CODE FOR APP.PY
            error_message = str(e)  # Tethers the text safely to a local variable
            self.after(0, lambda msg=error_message: self.on_generation_failure(msg))


if __name__ == "__main__":
    app = AddressLabelGeneratorApp()
    app.mainloop()
