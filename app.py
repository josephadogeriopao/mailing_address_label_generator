import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Import the functional generation logic from your engine module
from labels_engine import generate_word_labels_engine


class AddressLabelGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Config
        self.title("Address Label Generator")
        self.geometry("540x520")
        self.resizable(False, False)

        # Apply custom application icon if it exists locally
        icon_filename = "app_icon.ico"
        if os.path.exists(icon_filename):
            self.iconbitmap(icon_filename)

        # Basic Theme Mapping
        ctk.set_appearance_mode("System")  # Uses OS setting by default
        ctk.set_default_color_theme("blue")

        # Variables to store paths
        self.csv_path = ""
        self.output_dir = ""

        self.create_widgets()

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
        self.theme_switch.set("System")

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
        self.csv_label = ctk.CTkLabel(self.form_frame, text="Source CSV File:", font=ctk.CTkFont(weight="bold"))
        self.csv_label.pack(anchor="w", padx=20, pady=(15, 5))

        self.csv_entry_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.csv_entry_frame.pack(fill="x", padx=20)

        self.csv_entry = ctk.CTkEntry(self.csv_entry_frame, placeholder_text="No file selected...", state="readonly")
        self.csv_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.csv_btn = ctk.CTkButton(self.csv_entry_frame, text="Browse...", width=100, command=self.browse_csv)
        self.csv_btn.pack(side="right")

        # Row B: Destination Directory Selection
        self.dest_label = ctk.CTkLabel(self.form_frame, text="Save Location Folder:", font=ctk.CTkFont(weight="bold"))
        self.dest_label.pack(anchor="w", padx=20, pady=(15, 5))

        self.dest_entry_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.dest_entry_frame.pack(fill="x", padx=20)

        self.dest_entry = ctk.CTkEntry(self.dest_entry_frame, placeholder_text="No folder selected...",
                                       state="readonly")
        self.dest_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.dest_btn = ctk.CTkButton(self.dest_entry_frame, text="Browse...", width=100, command=self.browse_dest)
        self.dest_btn.pack(side="right")

        # Row C: Target Name File Box
        self.name_label = ctk.CTkLabel(self.form_frame, text="Output Document Name:", font=ctk.CTkFont(weight="bold"))
        self.name_label.pack(anchor="w", padx=20, pady=(15, 5))

        self.name_entry = ctk.CTkEntry(self.form_frame, placeholder_text="mailing_labels.docx")
        self.name_entry.pack(fill="x", padx=20, pady=(0, 5))
        self.name_entry.insert(0, "mailing_labels.docx")

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

    def change_theme(self, choice):
        ctk.set_appearance_mode(choice)

    def browse_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.csv_path = file_path
            self.csv_entry.configure(state="normal")
            self.csv_entry.delete(0, "end")
            self.csv_entry.insert(0, os.path.basename(file_path))
            self.csv_entry.configure(state="readonly")

    def browse_dest(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir = dir_path
            self.dest_entry.configure(state="normal")
            self.dest_entry.delete(0, "end")
            self.dest_entry.insert(0, dir_path)
            self.dest_entry.configure(state="readonly")

    def update_progress(self, val):
        self.progress_bar.set(val)

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

        final_out_path = os.path.join(self.output_dir, filename)

        # Lock UI Elements during operations
        self.generate_btn.configure(state="disabled")
        self.status_label.configure(text="Processing file rows...", text_color="#3B8ED0")
        self.progress_bar.set(0)

        # Run background thread so UI stays active
        t = threading.Thread(target=self.run_generation, args=(final_out_path,))
        t.start()

    def run_generation(self, out_path):
        try:
            generate_word_labels_engine(
                self.csv_path,
                out_path,
                progress_callback=self.update_progress
            )
            self.status_label.configure(text="Document compiled successfully!", text_color="green")
            messagebox.showinfo("Success", f"File created successfully!\n\nSaved to: {out_path}")
        except Exception as e:
            self.status_label.configure(text="Error occurred during build", text_color="red")
            messagebox.showerror("Execution Error", f"Failed to generate layout file safely:\n{str(e)}")
        finally:
            self.generate_btn.configure(state="normal")


if __name__ == "__main__":
    app = AddressLabelGeneratorApp()
    app.mainloop()
