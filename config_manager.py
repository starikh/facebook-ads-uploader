import json
import os
import keyring
import sys

CONFIG_FILE = 'config.json'
SERVICE_ID = 'FacebookAdsUploader'

class ConfigManager:
    def __init__(self):
        self.config_data = {}
        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self.config_data = json.load(f)
            except json.JSONDecodeError:
                self.config_data = {}
        else:
            self.config_data = {}

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config_data, f, indent=4)

    def get_token(self):
        return keyring.get_password(SERVICE_ID, 'access_token')

    def set_token(self, token):
        if token:
            keyring.set_password(SERVICE_ID, 'access_token', token)
        else:
            try:
                keyring.delete_password(SERVICE_ID, 'access_token')
            except keyring.errors.PasswordDeleteError:
                pass

    def get_business_name(self):
        return self.config_data.get('business_name', '')

    def set_business_name(self, name):
        self.config_data['business_name'] = name
        self.save_config()

    def get_ad_accounts(self):
        return self.config_data.get('ad_accounts', [])

    def add_ad_account(self, account_id, comment):
        if 'ad_accounts' not in self.config_data:
            self.config_data['ad_accounts'] = []
        
        # Check if exists
        for acc in self.config_data['ad_accounts']:
            if acc['id'] == account_id:
                acc['comment'] = comment # Update comment
                self.save_config()
                return

        self.config_data['ad_accounts'].append({'id': account_id, 'comment': comment})
        self.save_config()

    def remove_ad_account(self, account_id):
        if 'ad_accounts' in self.config_data:
            self.config_data['ad_accounts'] = [acc for acc in self.config_data['ad_accounts'] if acc['id'] != account_id]
            self.save_config()
