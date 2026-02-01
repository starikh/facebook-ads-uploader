import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import threading
import os
from config_manager import ConfigManager
from uploader import VideoUploader

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Facebook Ads Uploader")
        self.geometry("1000x750")

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

        # --- Upload Tab First to init variables ---
        self.setup_upload_tab()

        # --- Settings Tab ---
        self.setup_settings_tab()

    # --- Settings Tab Logic ---
    def setup_settings_tab(self):
        self.tab_settings.grid_columnconfigure(0, weight=1)

        # 1. Organization Management
        self.frame_org = ctk.CTkFrame(self.tab_settings)
        self.frame_org.grid(row=0, column=0, pady=10, padx=20, sticky="ew")
        
        self.lbl_orgs = ctk.CTkLabel(self.frame_org, text="Organization Management", font=("Arial", 16, "bold"))
        self.lbl_orgs.pack(pady=(10, 5), padx=10, anchor="w")

        self.frame_org_controls = ctk.CTkFrame(self.frame_org, fg_color="transparent")
        self.frame_org_controls.pack(pady=5, padx=10, fill="x")

        self.option_settings_org = ctk.CTkOptionMenu(self.frame_org_controls, command=self.on_settings_org_change, width=250)
        self.option_settings_org.pack(side="left", padx=(0, 10))

        self.btn_add_org = ctk.CTkButton(self.frame_org_controls, text="Add Org", width=100, command=self.add_org_dialog)
        self.btn_add_org.pack(side="left", padx=5)

        self.btn_del_org = ctk.CTkButton(self.frame_org_controls, text="Delete Org", width=100, fg_color="#C0392B", hover_color="#943126", command=self.delete_current_org)
        self.btn_del_org.pack(side="left", padx=5)

        # 2. Token
        self.frame_token = ctk.CTkFrame(self.tab_settings)
        self.frame_token.grid(row=1, column=0, pady=10, padx=20, sticky="ew")

        self.lbl_token = ctk.CTkLabel(self.frame_token, text="Access Token (Associated with Selected Org)", font=("Arial", 16, "bold"))
        self.lbl_token.pack(pady=(10, 5), padx=10, anchor="w")

        self.inner_token_frame = ctk.CTkFrame(self.frame_token, fg_color="transparent")
        self.inner_token_frame.pack(pady=5, padx=10, fill="x")

        self.entry_token = ctk.CTkEntry(self.inner_token_frame, placeholder_text="Enter Facebook Graph API Token", show="*")
        self.entry_token.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_save_token = ctk.CTkButton(self.inner_token_frame, text="Save Token", command=self.save_token)
        self.btn_save_token.pack(side="left")

        # 3. Ad Accounts
        self.frame_accs = ctk.CTkFrame(self.tab_settings)
        self.frame_accs.grid(row=2, column=0, pady=10, padx=20, sticky="nsew")
        self.tab_settings.grid_rowconfigure(2, weight=1)

        self.lbl_accs = ctk.CTkLabel(self.frame_accs, text="Ad Accounts", font=("Arial", 16, "bold"))
        self.lbl_accs.pack(pady=(10, 5), padx=10, anchor="w")

        self.frame_add_acc = ctk.CTkFrame(self.frame_accs, fg_color="transparent")
        self.frame_add_acc.pack(pady=5, padx=10, fill="x")

        self.entry_acc_id = ctk.CTkEntry(self.frame_add_acc, placeholder_text="Account ID (e.g. act_12345)", width=200)
        self.entry_acc_id.pack(side="left", padx=(0, 5))
        
        self.entry_acc_comment = ctk.CTkEntry(self.frame_add_acc, placeholder_text="Comment (e.g. Client Name)", width=200)
        self.entry_acc_comment.pack(side="left", padx=5)

        self.btn_add_acc = ctk.CTkButton(self.frame_add_acc, text="Add/Update", command=self.add_account)
        self.btn_add_acc.pack(side="left", padx=5)

        self.scroll_accs = ctk.CTkScrollableFrame(self.frame_accs)
        self.scroll_accs.pack(pady=10, padx=10, fill="both", expand=True)

        self.refresh_org_list_settings()

    def refresh_org_list_settings(self):
        orgs = self.config_manager.get_organization_names()
        if not orgs:
            orgs = ["Default"]
            self.config_manager.add_organization("Default")
        
        self.option_settings_org.configure(values=orgs)
        current = self.option_settings_org.get()
        if current not in orgs:
            self.option_settings_org.set(orgs[0])
            current = orgs[0]
        self.on_settings_org_change(current)
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
            tk.messagebox.showinfo("Saved", f"Token saved for '{org_name}'.")

    def add_org_dialog(self):
        dialog = ctk.CTkInputDialog(text="Organization Name:", title="Add Organization")
        name = dialog.get_input()
        if name:
            self.config_manager.add_organization(name)
            self.refresh_org_list_settings()
            self.option_settings_org.set(name)
            self.on_settings_org_change(name)

    def delete_current_org(self):
        name = self.option_settings_org.get()
        if not name: return
        if tk.messagebox.askyesno("Confirm", f"Delete '{name}'?"):
            self.config_manager.remove_organization(name)
            self.refresh_org_list_settings()

    def add_account(self):
        org = self.option_settings_org.get()
        if not org: return
        acc = self.entry_acc_id.get().strip()
        comm = self.entry_acc_comment.get().strip()
        if acc:
            self.config_manager.add_ad_account(org, acc, comm)
            self.refresh_account_list_settings(org)
            if self.option_upload_org.get() == org:
                self.on_upload_org_change(org)
            self.entry_acc_id.delete(0, 'end')
            self.entry_acc_comment.delete(0, 'end')

    def remove_account(self, acc_id):
        org = self.option_settings_org.get()
        self.config_manager.remove_ad_account(org, acc_id)
        self.refresh_account_list_settings(org)
        if self.option_upload_org.get() == org:
            self.on_upload_org_change(org)

    def refresh_account_list_settings(self, org_name):
        for w in self.scroll_accs.winfo_children(): w.destroy()
        for acc in self.config_manager.get_ad_accounts(org_name):
            r = ctk.CTkFrame(self.scroll_accs)
            r.pack(fill="x", pady=2)
            ctk.CTkLabel(r, text=f"{acc['id']} - {acc.get('comment', '')}").pack(side="left", padx=10)
            ctk.CTkButton(r, text="Remove", width=60, fg_color="#C0392B", hover_color="#943126", command=lambda a=acc['id']: self.remove_account(a)).pack(side="right", padx=5)

    # --- Upload Tab Logic ---
    def setup_upload_tab(self):
        # Configure Grid
        self.tab_upload.grid_columnconfigure(0, weight=1)
        self.tab_upload.grid_columnconfigure(1, weight=1)
        self.tab_upload.grid_rowconfigure(2, weight=1) # Main content area expands

        # 1. Header Logic (Org & Account)
        self.frame_header = ctk.CTkFrame(self.tab_upload)
        self.frame_header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
        
        self.option_upload_org = ctk.CTkOptionMenu(self.frame_header, command=self.on_upload_org_change, width=200)
        self.option_upload_org.pack(side="left", padx=10, pady=10)
        
        self.option_account = ctk.CTkOptionMenu(self.frame_header, values=[], width=300)
        self.option_account.pack(side="left", padx=10, pady=10)

        self.refresh_upload_orgs()

        # 2. File Selection
        self.frame_file = ctk.CTkFrame(self.tab_upload)
        self.frame_file.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        self.btn_folder = ctk.CTkButton(self.frame_file, text="Select Video Folder", command=self.select_folder, width=150)
        self.btn_folder.pack(side="left", padx=10, pady=10)
        
        self.lbl_folder_path = ctk.CTkLabel(self.frame_file, text="No folder selected", text_color="gray")
        self.lbl_folder_path.pack(side="left", padx=10)

        # 3. Main Split View (Videos | Log)
        self.frame_videos = ctk.CTkFrame(self.tab_upload)
        self.frame_videos.grid(row=2, column=0, sticky="nsew", padx=(10, 5), pady=5)
        
        self.lbl_files = ctk.CTkLabel(self.frame_videos, text="Videos Found", font=("Arial", 14, "bold"))
        self.lbl_files.pack(pady=5)
        
        self.scroll_files = ctk.CTkScrollableFrame(self.frame_videos)
        self.scroll_files.pack(fill="both", expand=True, padx=5, pady=5)

        self.frame_log = ctk.CTkFrame(self.tab_upload)
        self.frame_log.grid(row=2, column=1, sticky="nsew", padx=(5, 10), pady=5)
        
        self.lbl_log = ctk.CTkLabel(self.frame_log, text="Activity Log", font=("Arial", 14, "bold"))
        self.lbl_log.pack(pady=5)
        
        self.txt_log = ctk.CTkTextbox(self.frame_log)
        self.txt_log.pack(fill="both", expand=True, padx=5, pady=5)

        # 4. Actions & Progress
        self.frame_footer = ctk.CTkFrame(self.tab_upload)
        self.frame_footer.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 10))

        self.btn_upload = ctk.CTkButton(self.frame_footer, text="Start Upload", command=self.start_upload, fg_color="#27AE60", hover_color="#1E8449", height=40, font=("Arial", 14, "bold"), state="disabled")
        self.btn_upload.pack(side="left", pady=10, fill="x", padx=(50, 5), expand=True)

        self.btn_cancel = ctk.CTkButton(self.frame_footer, text="Cancel", command=self.cancel_upload, fg_color="#C0392B", hover_color="#943126", height=40, font=("Arial", 14, "bold"), state="disabled")
        self.btn_cancel.pack(side="left", pady=10, fill="x", padx=(5, 50), expand=True)

        self.progress_bar = ctk.CTkProgressBar(self.frame_footer)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 5), side="bottom")

        self.lbl_status = ctk.CTkLabel(self.frame_footer, text="Ready")
        self.lbl_status.pack(pady=(0, 5), side="bottom")

    def refresh_upload_orgs(self):
        orgs = self.config_manager.get_organization_names()
        if not orgs: orgs = ["No Orgs"]
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
        if not values: values = ["No Accounts"]
        self.option_account.configure(values=values)
        self.option_account.set(values[0])

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder = folder
            self.lbl_folder_path.configure(text=folder, text_color="white")
            self.refresh_file_list()

    def refresh_file_list(self):
        for w in self.scroll_files.winfo_children(): w.destroy()
        temp_uploader = VideoUploader(None)
        self.video_files = temp_uploader.get_video_files(self.selected_folder)
        for f in self.video_files:
            # Display only basename
            display_name = os.path.basename(f)
            ctk.CTkLabel(self.scroll_files, text=display_name, anchor="w").pack(fill="x", padx=5)
        
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
        if not self.video_files: return
        org = self.option_upload_org.get()
        if org == "No Orgs": 
            tk.messagebox.showerror("Error", "Select Organization")
            return
        
        selection = self.option_account.get()
        if "No Accounts" in selection:
            tk.messagebox.showerror("Error", "Configure Ad Account")
            return
            
        token = self.config_manager.get_token(org)
        if not token:
            tk.messagebox.showerror("Error", f"No token for '{org}'")
            return

        acc_id = selection.split(" ")[0]
        self.btn_upload.configure(state="disabled", text="Uploading...")
        self.btn_cancel.configure(state="normal")
        self.progress_bar.set(0)
        self.uploader = VideoUploader(token)
        self.upload_thread = threading.Thread(target=self.run_upload, args=(acc_id, self.video_files))
        self.upload_thread.start()

    def run_upload(self, acc_id, files):
        self.uploader.upload_videos(acc_id, files, self.update_progress, self.log_from_thread)
        self.after(0, self.upload_finished)

    def update_progress(self, current, total):
        self.after(0, lambda: self.progress_bar.set(current/total))
        self.after(0, lambda: self.lbl_status.configure(text=f"Uploaded {current}/{total}"))

    def log_from_thread(self, msg):
        self.after(0, lambda: self.log(msg))

    def cancel_upload(self):
        if self.uploader:
            self.uploader.cancel_upload()
            self.log("Cancelling...")

    def upload_finished(self):
        self.btn_upload.configure(state="normal", text="Start Upload")
        self.btn_cancel.configure(state="disabled")
        self.log("Finished.")

if __name__ == "__main__":
    app = App()
    app.mainloop()
