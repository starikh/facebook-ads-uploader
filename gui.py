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
        self.geometry("900x700")

        self.config_manager = ConfigManager()
        self.uploader = None # Uploader is now created per-upload
        self.upload_thread = None
        self.selected_folder = ""
        self.video_files = []

        # Tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.tab_upload = self.tabview.add("Upload")
        self.tab_settings = self.tabview.add("Settings")

        # --- Upload Tab ---
        self.setup_upload_tab()

        # --- Settings Tab ---
        self.setup_settings_tab()

    # --- Settings Tab Logic ---
    def setup_settings_tab(self):
        # 1. Organization Management (Top)
        self.lbl_orgs = ctk.CTkLabel(self.tab_settings, text="Organizations:", font=("Arial", 14, "bold"))
        self.lbl_orgs.pack(pady=(20, 5), anchor="w", padx=20)

        self.frame_org_controls = ctk.CTkFrame(self.tab_settings)
        self.frame_org_controls.pack(pady=5, padx=20, fill="x", anchor="w")

        self.option_settings_org = ctk.CTkOptionMenu(self.frame_org_controls, command=self.on_settings_org_change)
        self.option_settings_org.pack(side="left", padx=(0, 10))

        self.btn_add_org = ctk.CTkButton(self.frame_org_controls, text="Add Org", width=100, command=self.add_org_dialog)
        self.btn_add_org.pack(side="left", padx=5)

        self.btn_del_org = ctk.CTkButton(self.frame_org_controls, text="Delete Org", width=100, fg_color="red", command=self.delete_current_org)
        self.btn_del_org.pack(side="left", padx=5)

        # 2. Token (Dependent on Selected Org)
        self.lbl_token = ctk.CTkLabel(self.tab_settings, text="Access Token (for Selected Org):", font=("Arial", 14, "bold"))
        self.lbl_token.pack(pady=(20, 5), anchor="w", padx=20)

        self.frame_token = ctk.CTkFrame(self.tab_settings)
        self.frame_token.pack(pady=5, padx=20, fill="x", anchor="w")

        self.entry_token = ctk.CTkEntry(self.frame_token, width=400, show="*")
        self.entry_token.pack(side="left", padx=(0, 10))
        
        self.btn_save_token = ctk.CTkButton(self.frame_token, text="Save Token", command=self.save_token)
        self.btn_save_token.pack(side="left")

        # 3. Ad Accounts for Selected Org
        self.lbl_accs = ctk.CTkLabel(self.tab_settings, text="Ad Accounts (for Selected Org):", font=("Arial", 14, "bold"))
        self.lbl_accs.pack(pady=(20, 5), anchor="w", padx=20)

        # Add Account Frame
        self.frame_add_acc = ctk.CTkFrame(self.tab_settings)
        self.frame_add_acc.pack(pady=5, padx=20, fill="x", anchor="w")

        self.entry_acc_id = ctk.CTkEntry(self.frame_add_acc, placeholder_text="Account ID (act_...)", width=200)
        self.entry_acc_id.pack(side="left", padx=(0, 5))
        
        self.entry_acc_comment = ctk.CTkEntry(self.frame_add_acc, placeholder_text="Comment (e.g. Client A)", width=200)
        self.entry_acc_comment.pack(side="left", padx=5)

        self.btn_add_acc = ctk.CTkButton(self.frame_add_acc, text="Add/Update", command=self.add_account)
        self.btn_add_acc.pack(side="left", padx=5)

        # Account List
        self.scroll_accs = ctk.CTkScrollableFrame(self.tab_settings, height=200)
        self.scroll_accs.pack(pady=10, padx=20, fill="x", expand=True)

        self.refresh_org_list_settings()

    def refresh_org_list_settings(self):
        orgs = self.config_manager.get_organization_names()
        if not orgs:
            orgs = ["Default"]
            self.config_manager.add_organization("Default")
        
        self.option_settings_org.configure(values=orgs)
        
        # Keep selection or default to first
        current = self.option_settings_org.get()
        if current not in orgs:
            self.option_settings_org.set(orgs[0])
            current = orgs[0]
        
        self.on_settings_org_change(current)
            
        # Refresh upload tab too if needed
        self.refresh_upload_orgs()

    def on_settings_org_change(self, choice):
        self.refresh_account_list_settings(choice)
        self.refresh_token_field(choice)

    def refresh_token_field(self, org_name):
        self.entry_token.delete(0, 'end')
        token = self.config_manager.get_token(org_name)
        if token:
            self.entry_token.insert(0, "********")

    def save_token(self):
        org_name = self.option_settings_org.get()
        token = self.entry_token.get()
        
        if not org_name: return

        if token != "********":
            self.config_manager.set_token(org_name, token)
            self.entry_token.delete(0, 'end')
            self.entry_token.insert(0, "********")
            tk.messagebox.showinfo("Success", f"Token saved securely for '{org_name}'.")

    def add_org_dialog(self):
        dialog = ctk.CTkInputDialog(text="Enter Organization Name:", title="Add Organization")
        name = dialog.get_input()
        if name:
            self.config_manager.add_organization(name)
            self.refresh_org_list_settings()
            self.option_settings_org.set(name)
            self.on_settings_org_change(name)

    def delete_current_org(self):
        name = self.option_settings_org.get()
        if not name: return
        if tk.messagebox.askyesno("Confirm Delete", f"Delete organization '{name}', its accounts, and its token?"):
            self.config_manager.remove_organization(name)
            self.refresh_org_list_settings()

    def add_account(self):
        org_name = self.option_settings_org.get()
        if not org_name: return

        acc_id = self.entry_acc_id.get().strip()
        comment = self.entry_acc_comment.get().strip()
        if acc_id:
            self.config_manager.add_ad_account(org_name, acc_id, comment)
            self.refresh_account_list_settings(org_name)
            # Refresh upload tab if same org selected
            if self.option_upload_org.get() == org_name:
                self.on_upload_org_change(org_name)
            
            self.entry_acc_id.delete(0, 'end')
            self.entry_acc_comment.delete(0, 'end')

    def remove_account(self, acc_id):
        org_name = self.option_settings_org.get()
        self.config_manager.remove_ad_account(org_name, acc_id)
        self.refresh_account_list_settings(org_name)
        if self.option_upload_org.get() == org_name:
            self.on_upload_org_change(org_name)

    def refresh_account_list_settings(self, org_name):
        # Clear existing
        for widget in self.scroll_accs.winfo_children():
            widget.destroy()

        accounts = self.config_manager.get_ad_accounts(org_name)
        for acc in accounts:
            row = ctk.CTkFrame(self.scroll_accs)
            row.pack(fill="x", pady=2)
            lbl = ctk.CTkLabel(row, text=f"{acc['id']} - {acc.get('comment', '')}", anchor="w")
            lbl.pack(side="left", padx=5)
            btn = ctk.CTkButton(row, text="Remove", width=60, fg_color="red", command=lambda a=acc['id']: self.remove_account(a))
            btn.pack(side="right", padx=5)

    # --- Upload Tab Logic ---
    def setup_upload_tab(self):
        # Organization Selection
        self.lbl_u_org = ctk.CTkLabel(self.tab_upload, text="Select Organization:")
        self.lbl_u_org.pack(pady=(10, 5), padx=20, anchor="w")

        self.option_upload_org = ctk.CTkOptionMenu(self.tab_upload, command=self.on_upload_org_change)
        self.option_upload_org.pack(pady=5, padx=20, anchor="w")

        # Account Selection
        self.lbl_u_acc = ctk.CTkLabel(self.tab_upload, text="Select Ad Account:")
        self.lbl_u_acc.pack(pady=(10, 5), padx=20, anchor="w")

        self.option_account = ctk.CTkOptionMenu(self.tab_upload, values=[])
        self.option_account.pack(pady=5, padx=20, anchor="w")
        
        self.refresh_upload_orgs()

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

    def refresh_upload_orgs(self):
        orgs = self.config_manager.get_organization_names()
        if not orgs:
            orgs = ["No Orgs"]
        self.option_upload_org.configure(values=orgs)
        self.option_upload_org.set(orgs[0])
        self.on_upload_org_change(orgs[0])

    def on_upload_org_change(self, choice):
        if choice == "No Orgs":
            self.option_account.configure(values=["No Accounts"])
            self.option_account.set("No Accounts")
            return
            
        accounts = self.config_manager.get_ad_accounts(choice)
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
        # We need an instance of VideoUploader just to check files info? 
        # Actually existing VideoUploader logic for get_video_files is static-ish, 
        # but let's just make it a static method or create a dummy instance.
        # But wait, logic is in Uploader class. Uploader needs token.
        # For file listing, token is NOT needed.
        # Let's just create a temporary uploader or move get_video_files out.
        # For minimal refactor, I'll pass None as token.
        temp_uploader = VideoUploader(None)
        
        # clear
        for w in self.scroll_files.winfo_children():
            w.destroy()
        
        self.video_files = temp_uploader.get_video_files(self.selected_folder)
        
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
        
        org_name = self.option_upload_org.get()
        if org_name == "No Orgs" or not org_name:
             tk.messagebox.showerror("Error", "Please select an organization.")
             return

        selection = self.option_account.get()
        if "No Accounts" in selection:
            tk.messagebox.showerror("Error", "Please configure an Ad Account first.")
            return
        
        # Get Token
        token = self.config_manager.get_token(org_name)
        if not token:
             tk.messagebox.showerror("Error", f"No access token found for Organization '{org_name}'. Please go to Settings and save a token.")
             return

        # Parse account ID from "act_123 (Comment)" -> "act_123"
        acc_id = selection.split(" ")[0]
        
        self.btn_upload.configure(state="disabled")
        self.btn_cancel.configure(state="normal")
        self.progress_bar.set(0)
        
        # Create uploader with specific token
        self.uploader = VideoUploader(token)
        
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
