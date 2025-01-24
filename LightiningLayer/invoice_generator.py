import time

import requests


class InvoiceGenerator:
    def __init__(self, ln_address: str):
        """
        Erstellt einen InvoiceGenerator für eine Lightning-Adresse.
        """
        self.ln_address = ln_address
        self.lnurlp_url = self._lnaddress_to_lnurlp(ln_address)
        self.meta = self._fetch_lnurlp_metadata(self.lnurlp_url)

        self.callback_url = self.meta["callback"]
        self.min_sendable_msat = self.meta["minSendable"]
        self.max_sendable_msat = self.meta["maxSendable"]

    def _lnaddress_to_lnurlp(self, ln_address: str) -> str:
        """
        Aus 'alice@domain.com' -> 'https://domain.com/.well-known/lnurlp/alice'
        (Standard-Pfad für Lightning-Adressen / LNURL-Pay).
        """
        user, domain = ln_address.split("@")
        return f"https://{domain}/.well-known/lnurlp/{user}"

    def _fetch_lnurlp_metadata(self, lnurlp_url: str) -> dict:
        """
        LNURL-Pay-Request: Ruft die LNURL-Pay-URL auf und holt
        JSON mit callback, minSendable, maxSendable etc.
        """
        r = requests.get(lnurlp_url)
        r.raise_for_status()
        return r.json()

    def _get_bolt11_invoice(self, sats_amount: int) -> str:
        """
        LNURL-Pay-Schritt:
        - callback_url + '?amount=XYZ' (XYZ in msat)
        - Liefert das JSON mit 'pr' = BOLT11-Invoice zurück.
        """
        msat = sats_amount * 1000
        if msat < self.min_sendable_msat or msat > self.max_sendable_msat:
            raise ValueError(
                f"Gewünschte Sats liegen nicht in min/max-Bereich: "
                f"{self.min_sendable_msat / 1000} - {self.max_sendable_msat / 1000} Sats"
            )

        url = f"{self.callback_url}?amount={msat}"
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        return data["pr"]  # 'pr' ist die BOLT11-Invoice

    def generate_invoices(self, sats_amount: int, count: int) -> list:
        """
        Erzeugt eine Liste von `count` BOLT11-Invoices für den
        angegebenen Betrag in Sats.
        """
        invoices = []
        for i in range(count):
            invoice = self._get_bolt11_invoice(sats_amount)
            invoices.append(invoice)
            #API umgehen von Fehler "too many requests"
            time.sleep(10)
        return invoices

    def debug_test_invoice(self, sats_amount: int):
        """
        Debug-Funktion: Ruft EINMAL eine Invoice für den angegebenen
        Betrag ab und druckt sie in der Konsole aus.
        """
        print(f"--- Debug Test Invoice for {sats_amount} sats ---")
        invoice = self._get_bolt11_invoice(sats_amount)
        print("BOLT11 Invoice:", invoice)
        print("------------------------------------------------")
