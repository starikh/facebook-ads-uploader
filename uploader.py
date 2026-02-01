import os
import threading
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.advideo import AdVideo

VIDEO_EXTENSIONS = ('.mp4', '.mov', '.avi', '.mkv')

class VideoUploader:
    def __init__(self, access_token):
        self.access_token = access_token
        self.is_cancelled = False
        
        if self.access_token:
            try:
                FacebookAdsApi.init(access_token=self.access_token)
            except Exception as e:
                print(f"API Init Error: {e}")

    def get_video_files(self, folder_path):
        files = []
        if not os.path.exists(folder_path):
            return []
        
        for file in os.listdir(folder_path):
            if file.lower().endswith(VIDEO_EXTENSIONS):
                files.append(os.path.join(folder_path, file))
        return files

    def cancel_upload(self):
        self.is_cancelled = True

    def upload_videos(self, ad_account_id, video_paths, progress_callback=None, log_callback=None):
        """
        ad_account_id: str 'act_...'
        video_paths: list of str
        progress_callback: function(current, total)
        log_callback: function(message)
        """
        self.is_cancelled = False
        total = len(video_paths)
        success_count = 0

        for i, video_path in enumerate(video_paths):
            if self.is_cancelled:
                if log_callback:
                    log_callback("Upload cancelled by user.")
                break

            filename = os.path.basename(video_path)
            if log_callback:
                log_callback(f"Uploading {i+1}/{total}: {filename}...")

            try:
                # API Call
                video = AdVideo(parent_id=ad_account_id)
                video[AdVideo.Field.filepath] = video_path
                video.remote_create()
                
                success_count += 1
                if log_callback:
                    log_callback(f" -> Success! ID: {video['id']}")
            except Exception as e:
                if log_callback:
                    log_callback(f" -> Failed: {e}")

            if progress_callback:
                progress_callback(i + 1, total)

        if log_callback:
            log_callback(f"Finished. Successful: {success_count}/{total}")
