import yaml
import os
from pathlib import Path

class ConfigLoader:
    _instance = None
    _config = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        base_dir = Path(__file__).resolve().parent.parent.parent
        config_path = base_dir / "config.yaml"
        
        if not config_path.exists():
            # Fallback to defaults if file missing
            self._config = {
                "economy": {"monthly_inflation": 0.05, "target_margin": 0.25},
                "thresholds": {"martyr_threshold": 0.29, "max_price_up": 0.40, "days_inventory": 15},
                "tenants": {"demo_saas_id": "3947b9dc-7e89-4a05-a659-46e8ccdde558"}
            }
            return

        with open(config_path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f)

    def get(self, key_path, default=None):
        """Get value from nested dictionary using dot notation (e.g., 'economy.monthly_inflation')"""
        keys = key_path.split(".")
        value = self._config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

# Singleton instance
config = ConfigLoader()
