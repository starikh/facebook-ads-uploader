from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.advideo import AdVideo
import os
import sys
import json
import glob
import tkinter as tk
from tkinter import filedialog

CONFIG_FILE = 'config.json'
VIDEO_EXTENSIONS = ('.mp4', '.mov', '.avi', '.mkv')

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: {CONFIG_FILE} not found.")
        sys.exit(1)
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def get_video_files(folder_path):
    files = []
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        return []
    
    for file in os.listdir(folder_path):
        if file.lower().endswith(VIDEO_EXTENSIONS):
            files.append(os.path.join(folder_path, file))
    return files

def select_folder_gui():
    print("Opening folder selection dialog...")
    root = tk.Tk()
    root.withdraw() 
    root.attributes('-topmost', True)
    folder_selected = filedialog.askdirectory(title="Select Video Folder")
    root.destroy()
    return folder_selected

def upload_single_video(ad_account_id, video_path):
    print(f"Uploading: {os.path.basename(video_path)}...")
    try:
        video = AdVideo(parent_id=ad_account_id)
        video[AdVideo.Field.filepath] = video_path
        video.remote_create()
        print(f"  -> SUCCESS! Video ID: {video['id']}")
        return True
    except Exception as e:
        print(f"  -> FAILED: {e}")
        return False

def main():
    config = load_config()
    business_name = config.get('business_name', 'UNKOWN BUSINESS')
    print(f"\n\033[1mAD ACCOUNT OF {business_name}\033[0m")
    
    access_token = config.get('access_token')
    ad_accounts = config.get('ad_accounts', [])

    if not access_token:
        print("Error: 'access_token' missing in config.json")
        return
    
    if not ad_accounts:
        print("Error: No 'ad_accounts' found in config.json")
        return

    # init api
    try:
        FacebookAdsApi.init(access_token=access_token)
    except Exception as e:
        print(f"Error initializing API: {e}")
        return

    # select ad account
    print("\n--- Select Ad Account ---")
    for idx, account in enumerate(ad_accounts):
        print(f"{idx + 1}) {account['id']} - {account.get('comment', '')}")
    
    selected_account = None
    while True:
        try:
            choice = input("\nEnter account number: ")
            account_idx = int(choice) - 1
            if 0 <= account_idx < len(ad_accounts):
                selected_account = ad_accounts[account_idx]['id']
                break
            print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # select video folder gui
    print("\n--- Select Video Folder ---")
    while True:
        folder_path = select_folder_gui()
        
        if not folder_path:
            print("Folder selection cancelled.")
            retry = input("Do you want to try again? (y/n): ").lower()
            if retry != 'y':
                return
            continue

        print(f"Selected: {folder_path}")
        
        if os.path.isdir(folder_path):
            video_files = get_video_files(folder_path)
            if video_files:
                break
            else:
                print(f"No video files found in '{folder_path}' with extensions {VIDEO_EXTENSIONS}")
                retry = input("Try another folder? (y/n): ").lower()
                if retry != 'y':
                    return
        else:
            print("Invalid directory path.")

    # configrm upload
    print("\n--- Confirmation ---")
    print(f"Target Account: {selected_account}")
    print(f"Videos to Upload ({len(video_files)}):")
    for v in video_files:
        print(f" - {os.path.basename(v)}")
    
    confirm = input("\nAre you sure you want to proceed? (y/n): ").lower()
    if confirm != 'y':
        print("Operation cancelled.")
        return
        
    print("\n--- Starting Uploads ---")
    success_count = 0
    for video_path in video_files:
        if upload_single_video(selected_account, video_path):
            success_count += 1
    
    print(f"\nCompleted. Successful uploads: {success_count}/{len(video_files)}")

if __name__ == '__main__':
    main()
