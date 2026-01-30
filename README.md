# Facebook Ads Video Uploader

A Python script to batch upload video creatives to Facebook Ad Accounts using the Facebook Marketing API.

## Features

- **Batch Upload**: Upload multiple videos at once from a selected folder.
- **Multiple Accounts**: Configure and choose from multiple Ad Accounts.
- **Interactive CLI**: Simple command-line interface for selecting accounts.
- **GUI Folder Selection**: Uses a graphical dialog to easily pick the source folder.
- **Supported Formats**: `.mp4`, `.mov`, `.avi`, `.mkv`.

## Prerequisites

- Python 3.6+
- A [Facebook App](https://developers.facebook.com/) with the `ads_management` permission.
- An Access Token for the Facebook App.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/starikh/facebook-ads-uploader.git
   cd facebook-ads-uploader
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The script uses a `config.json` file to store your credentials and account information.

1. Ensure `config.json` is present in the root directory.
2. Edit `config.json` with your details:

```json
{
    "access_token": "YOUR_ACCESS_TOKEN", 
    "business_name": "My Business",
    "ad_accounts": [
        {
            "id": "act_1234567890",
            "comment": "Client A"
        },
        {
            "id": "act_0987654321",
            "comment": "Client B"
        }
    ]
}
```

- **access_token**: Your Facebook Graph API access token (must have `ads_management` permission).
- **business_name**: A label for your business (displayed when the script starts).
- **ad_accounts**: A list of ad accounts you want to upload to.
  - **id**: The Ad Account ID (must start with `act_`). (When you choosing AD Account you see this ID, but without act_ prefix)
  - **comment**: A friendly name or note to help you identify the account.

> **Note**: You can add as many ad account entries as you need in the `ad_accounts` list by adding more
```json
        {
            "id": "act_1234567890",
            "comment": "Client A"
        }
```


## Usage

1. Run the script:
   ```bash
   python upload_video.py
   ```

2. **Select Ad Account**: The script will list the accounts from your config. Enter the number corresponding to the desired account.

3. **Select Video Folder**: A window will pop up asking you to select the folder containing your video files.
   - The script scans for `.mp4`, `.mov`, `.avi`, and `.mkv` files.

4. **Confirm Upload**: The script will show the selected account and list of videos to be uploaded. Type `y` to proceed.

5. **Wait for Completion**: The script will upload each video and print the result (Success/Failure).

## Troubleshooting

- **Token Expired**: If you see authentication errors, generate a new access token and update `config.json`.
- **Permission Error**: Ensure your System User or User access token has the `ads_management` permission and access to the target Ad Accounts.