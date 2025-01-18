import requests

# API Endpoint und Macaroon-Pfad
API_ENDPOINT = "https://test-node.t.voltageapp.io/v1"
MACAROON_PATH = "admin.macaroon"

# Macaroon in Hex umwandeln
def load_macaroon(macaroon_path):
    with open(macaroon_path, "rb") as f:
        return f.read().hex()

# Neue Wallet erstellen
def create_wallet(api_endpoint, macaroon_hex, password):
    headers = {"Grpc-Metadata-macaroon": macaroon_hex}
    data = {"wallet_password": password.encode("utf-8").hex()}
    try:
        response = requests.post(f"{api_endpoint}/wallet/unlock", headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Erstellen der Wallet: {e}")
        return None

# Neue Adresse generieren
def get_new_address(api_endpoint, macaroon_hex, address_type="p2wkh"):
    headers = {"Grpc-Metadata-macaroon": macaroon_hex}
    data = {"type": address_type}
    try:
        response = requests.post(f"{api_endpoint}/newaddress", headers=headers, json=data)
        response.raise_for_status()
        return response.json().get("address")
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Generieren der Adresse: {e}")
        return None

# Wallet-Saldo abfragen
def get_wallet_balance(api_endpoint, macaroon_hex):
    headers = {"Grpc-Metadata-macaroon": macaroon_hex}
    try:
        response = requests.get(f"{api_endpoint}/balance/blockchain", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen des Wallet-Saldos: {e}")
        return None

# Hauptfunktion
def main():
    macaroon_hex = load_macaroon(MACAROON_PATH)

    # Optionen auskommentieren, je nach Bedarf
    # 1. Neue Wallet erstellen
    print("Neue Wallet erstellen:")
    password = "asdfasdf"
    wallet_response = create_wallet(API_ENDPOINT, macaroon_hex, password)
    if wallet_response:
        print("Wallet erfolgreich erstellt!")
        print(wallet_response)

    # 2. Neue Adresse generieren
    #print("\nNeue Adresse generieren:")
    #new_address = get_new_address(API_ENDPOINT, macaroon_hex, address_type="p2wkh")
    #if new_address:
    #    print(f"Neue Adresse: {new_address}")

    # 3. Wallet-Saldo anzeigen
    #print("\nWallet-Saldo:")
    #wallet_balance = get_wallet_balance(API_ENDPOINT, macaroon_hex)
    #if wallet_balance:
    #    print("Saldo:")
    #    print(wallet_balance)

if __name__ == "__main__":
    main()
