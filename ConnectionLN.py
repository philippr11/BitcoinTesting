import grpc
from lightning_pb2 import GetInfoRequest  # Import aus den generierten Dateien
from lightning_pb2_grpc import LightningStub

# Verbindungseinstellungen
lnd_host = "192.168.2.143"  # IP-Adresse der Node
lnd_port = 10009  # gRPC-Port der Node
tls_cert_path = "tls.cert"  # Pfad zum TLS-Zertifikat
macaroon_path = "admin.macaroon"  # Pfad zum Macaroon

# TLS-Zertifikat laden
with open(tls_cert_path, 'rb') as f:
    tls_cert = f.read()

# Macaroon laden und in Hex umwandeln
with open(macaroon_path, 'rb') as f:
    macaroon = f.read().hex()

# gRPC-Kanal erstellen
credentials = grpc.ssl_channel_credentials(tls_cert)
channel = grpc.secure_channel(f"{lnd_host}:{lnd_port}", credentials)
stub = LightningStub(channel)

# Header für die Authentifizierung
metadata = [("macaroon", macaroon)]

# Funktion zum Abrufen von Node-Informationen
def get_info():
    try:
        request = GetInfoRequest()  # Erstelle die Anfrage
        response = stub.GetInfo(request, metadata=metadata)
        print("Node Info:")
        print(response)
    except grpc.RpcError as e:
        print(f"Fehler bei der Verbindung: {e.details()}")

if __name__ == "__main__":
    get_info()
