import hashlib
import json
import os
import time
from typing import Any, Dict
from loguru import logger

class DigitalAsset:
    def __init__(self, asset_id: str, content: Any, asset_type: str, source_model: str):
        self.asset_id = asset_id
        self.content = content
        self.asset_type = asset_type
        self.source_model = source_model
        self.timestamp = time.time()
        self.hash = self._generate_hash()
        self.metadata = {
            "version": "2.0",
            "provenance": f"NeuralNode:{source_model}",
            "encryption": "AES-256-NODE-LINK"
        }

    def _generate_hash(self) -> str:
        content_str = str(self.content).encode('utf-8')
        return hashlib.sha256(content_str).hexdigest()

    def to_manifest(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "hash": self.hash,
            "type": self.asset_type,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

class AssetManager:
    """
    Manages the 'Digital Neural Vault'.
    Tracks ownership and cryptographic integrity of all system outputs.
    """
    def __init__(self, storage_dir: str = "./vault"):
        self.storage_dir = storage_dir
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir, exist_ok=True)
        self.registry_path = os.path.join(self.storage_dir, "asset_registry.json")
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict[str, Any]:
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_registry(self):
        try:
            with open(self.registry_path, "w", encoding="utf-8") as f:
                json.dump(self.registry, f, indent=4)
        except Exception as e:
            logger.error(f"[ASSET]: Registry write failure: {e}")

    def register_asset(self, content: Any, asset_type: str, source_model: str) -> DigitalAsset:
        # Fixed slice logic to avoid index errors on different types
        timestamp_str = str(time.time()).encode()
        raw_id = hashlib.md5(timestamp_str).hexdigest()
        asset_id = f"DA-{raw_id[:8].upper()}"
        
        asset = DigitalAsset(asset_id, content, asset_type, source_model)
        
        # Save to registry
        self.registry[asset_id] = asset.to_manifest()
        self._save_registry()
        
        logger.success(f"[ASSET]: New Digital Asset Registered: {asset_id}")
        return asset

    def verify_integrity(self, asset_id: str, current_content: Any) -> bool:
        if asset_id not in self.registry:
            return False
            
        stored_hash = self.registry[asset_id].get("hash")
        if not stored_hash:
            return False
            
        current_hash = hashlib.sha256(str(current_content).encode('utf-8')).hexdigest()
        
        is_valid = (stored_hash == current_hash)
        if not is_valid:
            logger.critical(f"[SECURITY]: Integrity breach detected for asset {asset_id}!")
        return is_valid

if __name__ == "__main__":
    am = AssetManager()
    am.register_asset("System Boot Logic v2", "code", "gemini")
