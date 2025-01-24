import time
import csv
import requests
from invoice_generator import InvoiceGenerator

#Konfigurationsdaten
LN_ADDRESS = "groomedshallot09@walletofsatoshi.com"
SATS_PER_PAYMENT = 10000
PAYMENT_COUNT = 10
DELAY_SECONDS = 10

LND_REST_URL = "https://ba-test-node.m.voltageapp.io"
MACAROON_PATH = "admin.macaroon"
CSV_FILENAME = "../Data/LNDataRaw/10x10000sats.csv"
VERIFY_TLS = True


def load_macaroon(macaroon_path):
    with open(macaroon_path, "rb") as f:
        return f.read().hex()

def pay_invoice_lnd(bolt11_invoice, lnd_rest_url, macaroon_hex, verify_tls=True):
    """
    Returned JSON der bolt11 formatierten invoices
    """
    headers = {"Grpc-Metadata-macaroon": macaroon_hex}
    payload = {"payment_request": bolt11_invoice}
    url = f"{lnd_rest_url}/v1/channels/transactions"

    resp = requests.post(url, json=payload, headers=headers, verify=verify_tls)
    resp.raise_for_status()
    return resp.json()

def main():
    macaroon_hex = load_macaroon(MACAROON_PATH)
    gen = InvoiceGenerator(LN_ADDRESS)

    # Generieren der zu zahlenden Invoices
    invoices = gen.generate_invoices(sats_amount=SATS_PER_PAYMENT, count=PAYMENT_COUNT)

    # CSV Generierung und befüllung:
    with open(CSV_FILENAME, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        # Kopfzeile
        writer.writerow([
            "Payment Hash",
            "Amount (sats)",
            "Num Hops",
            "Fee (sats)",
            "Local Start (unix)",
            "Local End (unix)",
            "Local Duration (s)",
            "Attempt Time (ns)",
            "Resolve Time (ns)",
            "LN Duration (s)"
        ])

        # alle Invoices bezahlen
        for i, invoice in enumerate(invoices, start=1):
            print(f"\n[{i}/{PAYMENT_COUNT}] Zahle Invoice: {invoice[:60]}...")

            # lokale Zeit loggen
            local_start = time.time()
            payment_result = pay_invoice_lnd(invoice, LND_REST_URL, macaroon_hex, verify_tls=VERIFY_TLS)
            local_end = time.time()
            local_duration = local_end - local_start

            # prüfen ob Zahlung erfolgreich
            payment_error = payment_result.get("payment_error")
            if payment_error:
                print(f"Fehler bei der Zahlung: {payment_error}")
                continue

            payment_hash = payment_result.get("payment_hash", "unbekannt")
            payment_route = payment_result.get("payment_route", {})
            total_fees_str = payment_route.get("total_fees", "0")
            total_fees = int(total_fees_str) if total_fees_str.isdigit() else 0

            hops = payment_route.get("hops", [])
            num_hops = len(hops)

            # LND-interne Zeitstempel: attempt_time_ns / resolve_time_ns auslesen
            htlcs = payment_result.get("htlcs", [])
            if len(htlcs) > 0:
                last_htlc = htlcs[-1]
                attempt_ns_str = last_htlc.get("attempt_time_ns", "0")
                resolve_ns_str = last_htlc.get("resolve_time_ns", "0")

                # In float konvertieren für Berechnung
                attempt_ns = float(attempt_ns_str)
                resolve_ns = float(resolve_ns_str)

                # LN-Dauer in Sekunden
                ln_duration_s = (resolve_ns - attempt_ns) / 1_000_000_000.0
            else:
                attempt_ns = 0.0
                resolve_ns = 0.0
                ln_duration_s = 0.0

            # gesammelte Daten in die CSV schreiben
            writer.writerow([
                payment_hash,
                SATS_PER_PAYMENT,
                num_hops,
                total_fees,
                int(local_start),
                int(local_end),
                round(local_duration, 3),
                int(attempt_ns),
                int(resolve_ns),
                round(ln_duration_s, 3)
            ])

            # Feedback in der Konsole zur Übersicht + Logging
            print(f"Payment Hash: {payment_hash}")
            print(f"Local Duration = {local_duration:.3f}s")
            print(f"LN Duration    = {ln_duration_s:.3f}s (LND intern)")
            print(f"Fee            = {total_fees} sat")
            print(f"Hops           = {num_hops}")

            # pausenintervall zwischen Payments
            if i < PAYMENT_COUNT:
                print(f"Warte {DELAY_SECONDS} Sekunden bis zum nächsten Payment...")
                time.sleep(DELAY_SECONDS)


if __name__ == "__main__":
    main()
