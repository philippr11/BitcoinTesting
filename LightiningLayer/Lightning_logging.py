import requests
import time
import csv

# Konfigurationsdaten
API_ENDPOINT = "https://test-node.t.voltageapp.io/v1"
MACAROON_PATH = "admin.macaroon"

# Macaroon in Hex umwandeln
def load_macaroon(macaroon_path):
    with open(macaroon_path, "rb") as f:
        return f.read().hex()

# Rechnung erstellen
def create_invoice(api_endpoint, macaroon_hex, amount_msat):
    headers = {"Grpc-Metadata-macaroon": macaroon_hex}
    data = {"value_msat": amount_msat}
    try:
        response = requests.post(f"{api_endpoint}/invoices", headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Erstellen der Rechnung: {e}")
        return None

# Rechnung bezahlen und Hops loggen
def pay_invoice(api_endpoint, macaroon_hex, payment_request):
    headers = {"Grpc-Metadata-macaroon": macaroon_hex}
    data = {"payment_request": payment_request}
    try:
        start_time = time.time()
        response = requests.post(f"{api_endpoint}/channels/transactions", headers=headers, json=data)
        end_time = time.time()
        response.raise_for_status()

        result = response.json()
        duration_ms = (end_time - start_time) * 1000  # Millisekunden
        fees = result["payment_route"]["total_fees_msat"]
        hops = result["payment_route"]["hops"]
        return {"duration_ms": duration_ms, "fees_msat": fees, "hops": hops}
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der Zahlung: {e}")
        return None

# Ergebnisse in CSV-Datei schreiben
def log_results_to_csv(log_file, amount_msat, duration_ms, fees, hops_count):
    with open(log_file, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([amount_msat, duration_ms, fees, hops_count])

# Testtransaktionen durchführen
def test_transactions(api_endpoint, macaroon_hex, test_cases, log_file):
    # CSV-Header schreiben
    with open(log_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Amount (msat)", "Duration (ms)", "Fees (msat)", "Hops Count"])

    for amount_msat, repeat in test_cases:
        print(f"Starte Tests für {amount_msat} msat, {repeat} mal.")
        for i in range(repeat):
            # Rechnung erstellen
            invoice = create_invoice(api_endpoint, macaroon_hex, amount_msat)
            if not invoice:
                print(f"Rechnung {i+1} für {amount_msat} msat konnte nicht erstellt werden.")
                continue

            # Rechnung bezahlen
            payment_result = pay_invoice(api_endpoint, macaroon_hex, invoice["payment_request"])
            if payment_result:
                duration_ms = payment_result["duration_ms"]
                fees = payment_result["fees_msat"]
                hops_count = len(payment_result["hops"])
                print(f"Transaktion {i+1}/{repeat}: Gebühren: {fees} msat, Dauer: {duration_ms:.2f} ms, Hops: {hops_count}")

                # Ergebnisse loggen
                log_results_to_csv(log_file, amount_msat, duration_ms, fees, hops_count)

if __name__ == "__main__":
    # Macaroon laden
    macaroon_hex = load_macaroon(MACAROON_PATH)

    # Testfälle: (Betrag in msat, Wiederholungen)
    TEST_CASES = [
        (1000000, 1),  # 1x 1000 Sats
        (100000, 10),  # 10x 100 Sats
        (10000, 100),  # 100x 10 Sats
    ]

    # Log-Datei
    LOG_FILE = "transaction_logs_ms.csv"

    # Tests ausführen
    test_transactions(API_ENDPOINT, macaroon_hex, TEST_CASES, LOG_FILE)
    print(f"Tests abgeschlossen. Ergebnisse in {LOG_FILE} gespeichert.")
