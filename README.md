# Facebook Ads Uploader (GUI)

A modern desktop application to batch upload video creatives to Facebook Ads Manager.

## Features

- **Modern GUI**: User-friendly interface built with CustomTkinter.
- **Multi-Organization Support**: Manage ad accounts for multiple different businesses or clients.
- **Secure Token Storage**: Access Tokens are stored securely in your OS Credential Manager (Keyring), not in plain text files.
- **Per-Organization Tokens**: Each organization carries its own specific access token.
- **Batch Upload**: Upload multiple video files at once with progress tracking.
- **Standalone Executable**: No Python installation required if using the `.exe`.

## Installation

### Using the Executable
1. Go to the `dist` folder.
2. Run `FBAdsUploader_v3.exe`.

### Running from Source
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python gui.py
   ```

## Usage Guide

### 1. Initial Setup (Settings Tab)
The first time you run the app, you need to configure your organizations.

1.  **Add Organization**:
    -   Click "Add Org" to create a profile (e.g., "Client A", "My Business").
2.  **Add Access Token**:
    -   Select your new Organization from the dropdown.
    -   Enter your **Facebook Graph API Access Token** (must have `ads_management` permission).
    -   Click "Save Token". *It is stored securely.*
3.  **Add Ad Accounts**:
    -   With the Organization selected, enter an Ad Account ID (beginning with `act_`) and a comment.
    -   Click "Add/Update".

### 2. Uploading Videos (Upload Tab)
1.  **Select Organization**: Choose the context for your upload.
2.  **Select Ad Account**: Pick the target ad account from the dropdown.
3.  **Select Folder**: Choose the folder containing your video files (`.mp4`, `.mov`, `.avi`, `.mkv`).
4.  **Upload**: Click "UPLOAD ALL" to start the process.

## Configuration Data

-   Non-sensitive data (Organization names, Ad Account IDs) is stored in `config.json`.
-   **Sensitive Data** (Access Tokens) is stored in the system Keyring.