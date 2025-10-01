import dataclasses
import os

import temporalio.converter
from dotenv import load_dotenv
from temporalio.client import Client
from temporalio.service import TLSConfig

from encryption_codec import EncryptionCodec

# Load environment variables from .env file
load_dotenv()


async def get_client() -> Client:
    client = None
    encrypt_payloads = os.getenv("ENCRYPT_PAYLOADS", "false").lower() == "true"

    tls_cert = os.getenv("TEMPORAL_MTLS_TLS_CERT")
    tls_key = os.getenv("TEMPORAL_MTLS_TLS_KEY")
    host_url = os.getenv("TEMPORAL_HOST_URL")
    namespace = os.getenv("TEMPORAL_NAMESPACE")

    if tls_cert and tls_key:
        server_root_ca_cert: bytes | None = None
        with open(tls_cert, "rb") as f:
            client_cert = f.read()

        with open(tls_key, "rb") as f:
            client_key = f.read()

        if encrypt_payloads:
            print("Worker payloads will be encrypted")
            if not host_url or not namespace:
                raise ValueError("TEMPORAL_HOST_URL and TEMPORAL_NAMESPACE must be set for TLS connection")
            client = await Client.connect(
                host_url,
                namespace=namespace,
                tls=TLSConfig(
                    server_root_ca_cert=server_root_ca_cert,
                    client_cert=client_cert,
                    client_private_key=client_key,
                ),
                data_converter=dataclasses.replace(temporalio.converter.default(), payload_codec=EncryptionCodec()),
            )
        else:
            if not host_url or not namespace:
                raise ValueError("TEMPORAL_HOST_URL and TEMPORAL_NAMESPACE must be set for TLS connection")
            client = await Client.connect(
                host_url,
                namespace=namespace,
                tls=TLSConfig(
                    server_root_ca_cert=server_root_ca_cert,
                    client_cert=client_cert,
                    client_private_key=client_key,
                ),
            )
    else:
        client = await Client.connect(
            "localhost:7233",
        )

    return client
