import requests

# Konfigurationsdaten
API_ENDPOINT = "https://test-node.t.voltageapp.io/v1"
MACAROON_PATH = "admin.macaroon"


# Macaroon laden und in Hex konvertieren
def load_macaroon(macaroon_path):
    with open(macaroon_path, "rb") as f:
        return f.read().hex()


# Verbindung zur Node testen
def get_node_info(api_endpoint, macaroon_hex):
    headers = {"Grpc-Metadata-macaroon": macaroon_hex}
    try:
        response = requests.get(f"{api_endpoint}/getinfo", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der Verbindung zur Node: {e}")
        return None


if __name__ == "__main__":
    macaroon_hex = load_macaroon(MACAROON_PATH)

    # Node-Info abrufen
    node_info = get_node_info(API_ENDPOINT, macaroon_hex)
    if node_info:
        print("Erfolgreich verbunden! Node Info:")
        print(node_info)
    else:
        print("Verbindung fehlgeschlagen.")
