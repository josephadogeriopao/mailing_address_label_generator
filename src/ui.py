"""
UI Components Presentation Layer
------------------
Description: Houses all custom widgets, geometry alignments, padding layout arrays,
             and window declarations using the CustomTkinter framework.

Author: Joseph Adogeri
File: ui.py
"""

import os
import customtkinter as ctk

class AddressLabelGeneratorUI(ctk.CTk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        # Window Config
        self.title("Address Label Generator")
        self.geometry("540x520")
        self.resizable(False, False)

        icon_filename = "app_icon.ico"
        if os.path.exists(icon_filename):
            self.iconbitmap(icon_filename)

        ctk.set_default_color_theme("blue")
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
            command=self.controller.change_theme,
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

        self.csv_btn = ctk.CTkButton(self.csv_entry_frame, text="Browse...", width=100, command=self.controller.browse_csv)
        self.csv_btn.pack(side="right")

        # Row B: Destination Directory Selection
        self.dest_label = ctk.CTkLabel(self.form_frame, text="Save Location Folder Path:", font=ctk.CTkFont(weight="bold"))
        self.dest_label.pack(anchor="w", padx=20, pady=(15, 5))

        self.dest_entry_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.dest_entry_frame.pack(fill="x", padx=20)

        self.dest_entry = ctk.CTkEntry(self.dest_entry_frame, placeholder_text="No folder selected...", state="readonly")
        self.dest_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.dest_btn = ctk.CTkButton(self.dest_entry_frame, text="Browse...", width=100, command=self.controller.browse_dest)
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
            command=self.controller.start_generation_thread
        )
        self.generate_btn.pack(fill="x", padx=30, pady=(5, 20))

    def set_csv_text(self, text):
        """Interface method to safely update text entries horizontally."""
        self.csv_entry.configure(state="normal")
        self.csv_entry.delete(0, "end")
        self.csv_entry.insert(0, text)
        self.csv_entry.configure(state="readonly")

    def set_dest_text(self, text):
        """Interface method to safely update destination values horizontally."""
        self.dest_entry.configure(state="normal")
        self.dest_entry.delete(0, "end")
        self.dest_entry.insert(0, text)
        self.dest_entry.configure(state="readonly")

    def set_filename_text(self, text):
        """Interface method to populate output descriptor fields."""
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, text)

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
