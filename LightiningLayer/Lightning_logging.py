# test_lightning.py
from invoice_generator import InvoiceGenerator

def main():
    # Lightning-Adresse von privater Wallet
    ln_address = "groomedshallot09@walletofsatoshi.com"
    gen = InvoiceGenerator(ln_address)

    # debugging mit 100 sats
    gen.debug_test_invoice(100)

    # invoices generieren mit gewünschten Parametern
    batch_invoices = gen.generate_invoices(sats_amount=50, count=3)
    for inv in batch_invoices:
        print("Invoice:", inv)

if __name__ == "__main__":
    main()
