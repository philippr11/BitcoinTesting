import requests
import csv
import time


### Skript für das rausfinden der Transaktionsgebühren pro Block

API_BASE = "https://mempool.space/api"
BLOCK_INTERVAL = 5000  # Jeden 1000. Block betrachten
START_BLOCK = 870000  # Startblockhöhe
END_BLOCK = 100  # Endblockhöhe (ältester Block)

def get_block_hash_by_height(height: int) -> str:
    """Lädt den Block-Hash basierend auf der Höhe."""
    url = f"{API_BASE}/block-height/{height}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text.strip()

def calculate_total_fees(block_hash: str) -> int:
    """Berechnet die Gesamtgebühren eines Blocks durch Abrufen aller Transaktionen."""
    total_fees = 0
    offset = 0

    while True:
        # Abrufen der Transaktionen, seitenweise
        if offset == 0:
            url = f"{API_BASE}/block/{block_hash}/txs"
        else:
            url = f"{API_BASE}/block/{block_hash}/txs/{offset}"

        response = requests.get(url)
        if response.status_code != 200:
            break  # Keine weiteren Daten

        transactions = response.json()
        if not transactions:
            break  # Ende erreicht

        # Summiere die Gebühren der aktuellen Seite
        total_fees += sum(tx.get("fee", 0) for tx in transactions)

        # Überprüfen, ob weniger als 25 Transaktionen geladen wurden (Ende)
        if len(transactions) < 25:
            break

        offset += 25  # Nächste Seite

    return total_fees

def main():
    with open("../Data/block_fees_summary.csv", mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["block_height", "total_fees", "num_txs"])

        for height in range(START_BLOCK, END_BLOCK, -BLOCK_INTERVAL):
            try:
                block_hash = get_block_hash_by_height(height)

                # Berechne die Gesamtgebühren
                total_fees = calculate_total_fees(block_hash)

                # Abrufen von Blockdaten
                url = f"{API_BASE}/block/{block_hash}"
                block_data = requests.get(url).json()
                num_txs = block_data.get("tx_count", 0)  # Anzahl der Transaktionen

                writer.writerow([height, total_fees, num_txs])

                print(f"Block {height} verarbeitet: total_fees={total_fees}, num_txs={num_txs}")
                time.sleep(0.5)  # Vermeidung von Rate-Limits

            except Exception as e:
                print(f"Fehler bei Block {height}: {e}")

    print("Fertig! Daten in block_fees_summary.csv geschrieben.")

if __name__ == "__main__":
    main()
