import requests
import csv
import time

API_BASE = "https://mempool.space/api"
#Blöcke dich ich betrachten möchte:
BLOCK_HEIGHTS = [100000, 300000, 500000, 700000, 870000]


def get_block_hash_by_height(height: int) -> str:
    url = f"{API_BASE}/block-height/{height}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text.strip()


def get_block_data(block_hash: str) -> dict:
    url = f"{API_BASE}/block/{block_hash}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()


def get_all_block_txs(block_hash: str) -> list:

    all_txs = []
    offset = 0  # Anzahl bereits geladener TXs (Seitenzahl)

    while True:

        if offset == 0:
            url = f"{API_BASE}/block/{block_hash}/txs"
        else:
            url = f"{API_BASE}/block/{block_hash}/txs/{offset}"

        resp = requests.get(url)
        if resp.status_code != 200:
            break

        txs_batch = resp.json()
        if not txs_batch:
            break

        all_txs.extend(txs_batch)

        if len(txs_batch) < 25:
            break

        offset += 25

    return all_txs



def get_tx_details(txid: str) -> dict:
    url = f"{API_BASE}/tx/{txid}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()


def main():
    with open("../Data/transactions5.csv", mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)


        writer.writerow([
            "block_height",
            "txid",
            "fee_sats",
            "fee_per_vbyte",
            "block_timestamp",
            "time_to_confirm_seconds",
            "vsize",
            "value_btc"
        ])

        for height in BLOCK_HEIGHTS:
            try:
                block_hash = get_block_hash_by_height(height)
                block_data = get_block_data(block_hash)
                block_timestamp = block_data.get("timestamp")

                txs = get_all_block_txs(block_hash)

                time.sleep(0.5)

                for tx in txs:
                    txid = tx.get("txid")
                    fee_sats = tx.get("fee", 0)
                    vsize = tx.get("vsize", 0)

                    if vsize != 0:
                        fee_per_vbyte = fee_sats / vsize
                    else:
                        fee_per_vbyte = None

                    # Summieren aller Outputs, um "gesendeten" Betrag in Satoshi zu erhalten
                    # (Aus Perspektive der Tx sind das alle "ausgegebenen" Werte, inkl. möglicher Change-Ausgaben)
                    vout = tx.get("vout", [])
                    total_out_sats = 0
                    for out in vout:
                        total_out_sats += out.get("value", 0)

                    # In BTC umrechnen
                    value_btc = total_out_sats / 1e8

                    # Zeit bis Bestätigung
                    time_to_confirm_seconds = None
                    try:
                        tx_details = get_tx_details(txid)
                        status_info = tx_details.get("status", {})
                        first_seen = tx_details.get("firstSeen", None)
                        block_time = status_info.get("block_time", block_timestamp)
                        if block_time and first_seen:
                            time_to_confirm_seconds = block_time - first_seen
                        time.sleep(0.1)
                    except Exception as e:
                        # Falls Rate-Limit oder 'firstSeen' nicht vorhanden, ignorieren
                        pass

                    writer.writerow([
                        height,
                        txid,
                        fee_sats,
                        fee_per_vbyte,
                        block_timestamp,
                        time_to_confirm_seconds,
                        vsize,
                        value_btc
                    ])

                print(f"Block {height} verarbeitet, {len(txs)} TXs geschrieben.")

            except Exception as e:
                print(f"Fehler bei Block {height}: {e}")

    print("Fertig! Daten in transactions5.csv geschrieben.")


if __name__ == "__main__":
    main()
