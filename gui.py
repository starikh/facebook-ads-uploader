import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import threading
from config_manager import ConfigManager
from uploader import VideoUploader

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Facebook Ads Uploader")
        self.geometry("800x600")

        self.config_manager = ConfigManager()
        self.uploader = None
        self.upload_thread = None
        self.selected_folder = ""
        self.video_files = []

        # Tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.tab_upload = self.tabview.add("Upload")
        self.tab_settings = self.tabview.add("Settings")

        # --- Settings Tab ---
        self.setup_settings_tab()

        # --- Upload Tab ---
        self.setup_upload_tab()

        # Initialize Uploader with token if available
        self.refresh_uploader()

    def refresh_uploader(self):
        token = self.config_manager.get_token()
        self.uploader = VideoUploader(token)

    # --- Settings Tab Logic ---
    def setup_settings_tab(self):
        # Token
        self.lbl_token = ctk.CTkLabel(self.tab_settings, text="Access Token (Secure):", font=("Arial", 14, "bold"))
        self.lbl_token.pack(pady=(10, 5), anchor="w", padx=20)

        self.entry_token = ctk.CTkEntry(self.tab_settings, width=400, show="*")
        self.entry_token.pack(pady=5, padx=20, anchor="w")
        
        # Pre-fill placeholder if token exists (don't show actual token)
        if self.config_manager.get_token():
            self.entry_token.insert(0, "********")

        self.btn_save_token = ctk.CTkButton(self.tab_settings, text="Save Token", command=self.save_token)
        self.btn_save_token.pack(pady=5, padx=20, anchor="w")

        # Business Name
        self.lbl_biz = ctk.CTkLabel(self.tab_settings, text="Business Name:", font=("Arial", 14, "bold"))
        self.lbl_biz.pack(pady=(20, 5), anchor="w", padx=20)

        self.entry_biz = ctk.CTkEntry(self.tab_settings, width=400)
        self.entry_biz.insert(0, self.config_manager.get_business_name())
        self.entry_biz.pack(pady=5, padx=20, anchor="w")

        self.btn_save_biz = ctk.CTkButton(self.tab_settings, text="Save Business Name", command=self.save_biz)
        self.btn_save_biz.pack(pady=5, padx=20, anchor="w")

        # Ad Accounts Header
        self.lbl_accs = ctk.CTkLabel(self.tab_settings, text="Ad Accounts:", font=("Arial", 14, "bold"))
        self.lbl_accs.pack(pady=(20, 5), anchor="w", padx=20)

        # Add Account Frame
        self.frame_add_acc = ctk.CTkFrame(self.tab_settings)
        self.frame_add_acc.pack(pady=5, padx=20, fill="x", anchor="w")

        self.entry_acc_id = ctk.CTkEntry(self.frame_add_acc, placeholder_text="Account ID (act_...)", width=200)
        self.entry_acc_id.pack(side="left", padx=5)
        
        self.entry_acc_comment = ctk.CTkEntry(self.frame_add_acc, placeholder_text="Comment (e.g. Client A)", width=200)
        self.entry_acc_comment.pack(side="left", padx=5)

        self.btn_add_acc = ctk.CTkButton(self.frame_add_acc, text="Add/Update", command=self.add_account)
        self.btn_add_acc.pack(side="left", padx=5)

        # Account List
        self.scroll_accs = ctk.CTkScrollableFrame(self.tab_settings, height=200)
        self.scroll_accs.pack(pady=10, padx=20, fill="x")
        
        self.refresh_account_list()

    def save_token(self):
        token = self.entry_token.get()
        if token != "********":
            self.config_manager.set_token(token)
            self.entry_token.delete(0, 'end')
            self.entry_token.insert(0, "********")
            self.refresh_uploader()
            tk.messagebox.showinfo("Success", "Token saved securely.")

    def save_biz(self):
        self.config_manager.set_business_name(self.entry_biz.get())
        tk.messagebox.showinfo("Success", "Business name saved.")

    def add_account(self):
        acc_id = self.entry_acc_id.get().strip()
        comment = self.entry_acc_comment.get().strip()
        if acc_id:
            self.config_manager.add_ad_account(acc_id, comment)
            self.refresh_account_list()
            self.refresh_upload_tab_accounts()
            self.entry_acc_id.delete(0, 'end')
            self.entry_acc_comment.delete(0, 'end')

    def remove_account(self, acc_id):
        self.config_manager.remove_ad_account(acc_id)
        self.refresh_account_list()
        self.refresh_upload_tab_accounts()

    def refresh_account_list(self):
        # Clear existing
        for widget in self.scroll_accs.winfo_children():
            widget.destroy()

        accounts = self.config_manager.get_ad_accounts()
        for acc in accounts:
            row = ctk.CTkFrame(self.scroll_accs)
            row.pack(fill="x", pady=2)
            lbl = ctk.CTkLabel(row, text=f"{acc['id']} - {acc.get('comment', '')}", anchor="w")
            lbl.pack(side="left", padx=5)
            btn = ctk.CTkButton(row, text="Remove", width=60, fg_color="red", command=lambda a=acc['id']: self.remove_account(a))
            btn.pack(side="right", padx=5)

    # --- Upload Tab Logic ---
    def setup_upload_tab(self):
        # Account Selection
        self.lbl_u_acc = ctk.CTkLabel(self.tab_upload, text="Select Ad Account:")
        self.lbl_u_acc.pack(pady=(10, 5), padx=20, anchor="w")

        self.option_account = ctk.CTkOptionMenu(self.tab_upload, values=[])
        self.option_account.pack(pady=5, padx=20, anchor="w")
        self.refresh_upload_tab_accounts()

        # Folder Selection
        self.frame_folder = ctk.CTkFrame(self.tab_upload)
        self.frame_folder.pack(pady=10, padx=20, fill="x")

        self.btn_folder = ctk.CTkButton(self.frame_folder, text="Select Video Folder", command=self.select_folder)
        self.btn_folder.pack(side="left", padx=5)

        self.lbl_folder_path = ctk.CTkLabel(self.frame_folder, text="No folder selected", text_color="gray")
        self.lbl_folder_path.pack(side="left", padx=5)

        # File Preview
        self.lbl_preview = ctk.CTkLabel(self.tab_upload, text="Videos found:")
        self.lbl_preview.pack(pady=(10, 0), padx=20, anchor="w")

        self.scroll_files = ctk.CTkScrollableFrame(self.tab_upload, height=150)
        self.scroll_files.pack(pady=5, padx=20, fill="x")

        # Action Buttons
        self.frame_actions = ctk.CTkFrame(self.tab_upload, fg_color="transparent")
        self.frame_actions.pack(pady=20, padx=20, fill="x")

        self.btn_upload = ctk.CTkButton(self.frame_actions, text="UPLOAD ALL", command=self.start_upload, fg_color="green", state="disabled")
        self.btn_upload.pack(side="left", padx=5)

        self.btn_cancel = ctk.CTkButton(self.frame_actions, text="Cancel", command=self.cancel_upload, fg_color="red", state="disabled")
        self.btn_cancel.pack(side="left", padx=5)

        # Progress
        self.progress_bar = ctk.CTkProgressBar(self.tab_upload)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10, padx=20, fill="x")

        self.lbl_status = ctk.CTkLabel(self.tab_upload, text="Ready")
        self.lbl_status.pack(pady=5)

        # Log
        self.txt_log = ctk.CTkTextbox(self.tab_upload, height=100)
        self.txt_log.pack(pady=10, padx=20, fill="both", expand=True)

    def refresh_upload_tab_accounts(self):
        accounts = self.config_manager.get_ad_accounts()
        values = [f"{acc['id']} ({acc.get('comment','')})" for acc in accounts]
        if not values:
            values = ["No Accounts Configured"]
        self.option_account.configure(values=values)
        self.option_account.set(values[0])

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder = folder
            self.lbl_folder_path.configure(text=folder, text_color="white")
            self.refresh_file_list()

    def refresh_file_list(self):
        # clear
        for w in self.scroll_files.winfo_children():
            w.destroy()
        
        self.video_files = self.uploader.get_video_files(self.selected_folder)
        
        for f in self.video_files:
            lbl = ctk.CTkLabel(self.scroll_files, text=f)
            lbl.pack(anchor="w")

        if self.video_files:
            self.btn_upload.configure(state="normal")
            self.log(f"Found {len(self.video_files)} video files.")
        else:
            self.btn_upload.configure(state="disabled")
            self.log("No video files found.")

    def log(self, message):
        self.txt_log.insert("end", message + "\n")
        self.txt_log.see("end")

    def start_upload(self):
        if not self.video_files:
            return
        
        selection = self.option_account.get()
        if "No Accounts" in selection:
            tk.messagebox.showerror("Error", "Please configure an Ad Account first.")
            return
        
        # Parse account ID from "act_123 (Comment)" -> "act_123"
        acc_id = selection.split(" ")[0]
        
        self.btn_upload.configure(state="disabled")
        self.btn_cancel.configure(state="normal")
        self.progress_bar.set(0)
        
        self.upload_thread = threading.Thread(target=self.run_upload, args=(acc_id, self.video_files))
        self.upload_thread.start()

    def run_upload(self, acc_id, files):
        self.uploader.upload_videos(
            acc_id, 
            files, 
            progress_callback=self.update_progress, 
            log_callback=self.log_from_thread
        )
        self.after(0, self.upload_finished)

    def update_progress(self, current, total):
        val = current / total
        self.after(0, lambda: self.progress_bar.set(val))
        self.after(0, lambda: self.lbl_status.configure(text=f"Uploaded {current}/{total}"))

    def log_from_thread(self, msg):
        self.after(0, lambda: self.log(msg))

    def cancel_upload(self):
        if self.uploader:
            self.uploader.cancel_upload()
            self.log("Cancelling...")

    def upload_finished(self):
        self.btn_upload.configure(state="normal")
        self.btn_cancel.configure(state="disabled")
        self.log("Upload sequence ended.")

if __name__ == "__main__":
    app = App()
    app.mainloop()
