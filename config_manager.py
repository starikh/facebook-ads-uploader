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

        self._migrate_legacy_config()

    def _migrate_legacy_config(self):
        # Check if legacy structure exists (root level ad_accounts or business_name)
        # and if 'organizations' key is missing
        if 'organizations' not in self.config_data:
            self.config_data['organizations'] = []
            
            # Check for legacy data
            legacy_biz = self.config_data.get('business_name')
            legacy_accounts = self.config_data.get('ad_accounts', [])

            if legacy_biz or legacy_accounts:
                org_name = legacy_biz if legacy_biz else "Default Organization"
                new_org = {
                    "name": org_name,
                    "ad_accounts": legacy_accounts
                }
                self.config_data['organizations'].append(new_org)
                
                # Check for legacy global token and migrate to new org if possible
                global_token = keyring.get_password(SERVICE_ID, 'access_token')
                if global_token:
                    self.set_token(org_name, global_token)
                    # Optional: delete old global token, but safe to keep for now or manual cleanup
                
                # Clean up legacy keys
                self.config_data.pop('business_name', None)
                self.config_data.pop('ad_accounts', None)
                
                self.save_config()

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config_data, f, indent=4)

    # --- Token Management (Per Org) ---
    def get_token(self, org_name):
        if not org_name: return None
        # Key: "access_token::{org_name}"
        key = f"access_token::{org_name}"
        return keyring.get_password(SERVICE_ID, key)

    def set_token(self, org_name, token):
        if not org_name: return
        key = f"access_token::{org_name}"
        
        if token:
            keyring.set_password(SERVICE_ID, key, token)
        else:
            try:
                keyring.delete_password(SERVICE_ID, key)
            except keyring.errors.PasswordDeleteError:
                pass

    # --- Organization Management ---
    def get_organization_names(self):
        return [org['name'] for org in self.config_data.get('organizations', [])]

    def add_organization(self, name):
        if not name:
            return
        
        # Check if exists
        for org in self.config_data['organizations']:
            if org['name'] == name:
                return # Already exists
        
        self.config_data['organizations'].append({
            "name": name,
            "ad_accounts": []
        })
        self.save_config()

    def remove_organization(self, name):
        self.config_data['organizations'] = [
            org for org in self.config_data.get('organizations', []) 
            if org['name'] != name
        ]
        # Also remove associated token
        self.set_token(name, None)
        self.save_config()

    def rename_organization(self, old_name, new_name):
        for org in self.config_data.get('organizations', []):
            if org['name'] == old_name:
                org['name'] = new_name
                # Migrate token
                token = self.get_token(old_name)
                if token:
                    self.set_token(new_name, token)
                    self.set_token(old_name, None)
                
                self.save_config()
                return

    # --- Ad Account Management ---
    def get_ad_accounts(self, org_name):
        for org in self.config_data.get('organizations', []):
            if org['name'] == org_name:
                return org.get('ad_accounts', [])
        return []

    def add_ad_account(self, org_name, account_id, comment):
        for org in self.config_data.get('organizations', []):
            if org['name'] == org_name:
                # Check for duplicate
                for acc in org['ad_accounts']:
                    if acc['id'] == account_id:
                        acc['comment'] = comment
                        self.save_config()
                        return
                
                org['ad_accounts'].append({'id': account_id, 'comment': comment})
                self.save_config()
                return

    def remove_ad_account(self, org_name, account_id):
        for org in self.config_data.get('organizations', []):
            if org['name'] == org_name:
                org['ad_accounts'] = [
                    acc for acc in org['ad_accounts'] 
                    if acc['id'] != account_id
                ]
                self.save_config()
                return
