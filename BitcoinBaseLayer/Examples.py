import requests
import json

API_BASE = "https://mempool.space/api"
block_height = 870000  # Beispiel-Blockhöhe

# Block-Hash abrufen
block_hash_url = f"{API_BASE}/block-height/{block_height}"
block_hash = requests.get(block_hash_url).text.strip()

# Blockdaten abrufen
block_data_url = f"{API_BASE}/block/{block_hash}"
block_data = requests.get(block_data_url).json()

# Erste Seite der Transaktionen abrufen
txs_url = f"{API_BASE}/block/{block_hash}/txs"
txs_data = requests.get(txs_url).json()

print(block_hash_url + ": ")
print(json.dumps(block_data, indent=4))
print(txs_url + ": ")
print(json.dumps(txs_data, indent=4))
