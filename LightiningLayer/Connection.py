import requests

# Konfigurationsdaten
API_ENDPOINT = "https://ba-test-node.m.voltageapp.io"
MACAROON_PATH = "admin.macaroon"


# Macaroon laden und in Hex konvertieren
def load_macaroon(macaroon_path):
    with open(macaroon_path, "rb") as f:
        return f.read().hex()


# Verbindung zur Node testen
def get_node_info(api_endpoint, macaroon_hex):
    headers = {"Grpc-Metadata-macaroon": macaroon_hex}
    try:
        response = requests.get(f"{api_endpoint}/v1/getinfo", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der Verbindung zur Node: {e}")
        return None


# Alle ausgehenden Lightning-Zahlungen abrufen
def get_payments(api_endpoint, macaroon_hex):
    headers = {"Grpc-Metadata-macaroon": macaroon_hex}
    try:
        response = requests.get(f"{api_endpoint}/v1/payments", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen der Zahlungen: {e}")
        return None


if __name__ == "__main__":
    # Macaroon in Hex laden
    macaroon_hex = load_macaroon(MACAROON_PATH)

    # Node-Info abrufen
    node_info = get_node_info(API_ENDPOINT, macaroon_hex)
    if node_info:
        print("Erfolgreich verbunden! Node Info:")
        print(node_info)

        # Zahlungen abrufen
        payments_data = get_payments(API_ENDPOINT, macaroon_hex)
        if payments_data:
            print("\nAusgehende Zahlungen (payments):")
            print(payments_data)
        else:
            print("Konnte keine Zahlungen abrufen oder es sind keine vorhanden.")
    else:
        print("Verbindung fehlgeschlagen.")
