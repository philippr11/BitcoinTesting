import json
import requests

API_ENDPOINT = "https://ba-test-node.m.voltageapp.io"
MACAROON_PATH = "admin.macaroon"
OUTPUT_JSON_FILE = "../Data/LNDataRaw/all_payments.json"

def load_macaroon(macaroon_path):
    with open(macaroon_path, "rb") as f:
        return f.read().hex()

def get_all_payments(api_endpoint, macaroon_hex):
    """
    Ruft alle Payments aus LND ab
    """
    headers = {"Grpc-Metadata-macaroon": macaroon_hex}
    url = f"{api_endpoint}/v1/payments?include_incomplete=true"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def main():
    macaroon_hex = load_macaroon(MACAROON_PATH)

    # Hol dir die Liste aller Payments
    payments_data = get_all_payments(API_ENDPOINT, macaroon_hex)
    payments_list = payments_data.get("payments", [])

    # In JSON-Datei schreiben
    with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(payments_list, f, indent=2)

    print(f"Gespeicherte Zahlungen: {len(payments_list)}")
    print(f"Datei erstellt: {OUTPUT_JSON_FILE}")

if __name__ == "__main__":
    main()
