"""Database connection utility for Supabase PostgreSQL using pure-Python pg8000.

Constructs connection URLs using SQLAlchemy's URL.create() for robust escaping.
Prioritizes discrete environment variables (DB_HOST, DB_USER, etc.).
Uses certifi and Supabase's official Root CA for strict, verified SSL/TLS encryption.
Ensures passwords and connection strings are masked across all logs and outputs.
"""

import os
import ssl
from pathlib import Path
from typing import Optional
import certifi
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, Engine, make_url

# Ensure .env is loaded from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

# Official Supabase Root 2021 CA certificate (used to verify Supabase database certificates)
SUPABASE_ROOT_CA_PEM = """-----BEGIN CERTIFICATE-----
MIIDxDCCAqygAwIBAgIUbLxMod62P2ktCiAkxnKJwtE9VPYwDQYJKoZIhvcNAQEL
BQAwazELMAkGA1UEBhMCVVMxEDAOBgNVBAgMB0RlbHdhcmUxEzARBgNVBAcMCk5l
dyBDYXN0bGUxFTATBgNVBAoMDFN1cGFiYXNlIEluYzEeMBwGA1UEAwwVU3VwYWJh
c2UgUm9vdCAyMDIxIENBMB4XDTIxMDQyODEwNTY1M1oXDTMxMDQyNjEwNTY1M1ow
azELMAkGA1UEBhMCVVMxEDAOBgNVBAgMB0RlbHdhcmUxEzARBgNVBAcMCk5ldyBD
YXN0bGUxFTATBgNVBAoMDFN1cGFiYXNlIEluYzEeMBwGA1UEAwwVU3VwYWJhc2Ug
Um9vdCAyMDIxIENBMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqQXW
QyHOB+qR2GJobCq/CBmQ40G0oDmCC3mzVnn8sv4XNeWtE5XcEL0uVih7Jo4Dkx1Q
DmGHBH1zDfgs2qXiLb6xpw/CKQPypZW1JssOTMIfQppNQ87K75Ya0p25Y3ePS2t2
GtvHxNjUV6kjOZjEn2yWEcBdpOVCUYBVFBNMB4YBHkNRDa/+S4uywAoaTWnCJLUi
cvTlHmMw6xSQQn1UfRQHk50DMCEJ7Cy1RxrZJrkXXRP3LqQL2ijJ6F4yMfh+Gyb4
O4XajoVj/+R4GwywKYrrS8PrSNtwxr5StlQO8zIQUSMiq26wM8mgELFlS/32Uclt
NaQ1xBRizkzpZct9DwIDAQABo2AwXjALBgNVHQ8EBAMCAQYwHQYDVR0OBBYEFKjX
uXY32CztkhImng4yJNUtaUYsMB8GA1UdIwQYMBaAFKjXuXY32CztkhImng4yJNUt
aUYsMA8GA1UdEwEB/wQFMAMBAf8wDQYJKoZIhvcNAQELBQADggEBAB8spzNn+4VU
tVxbdMaX+39Z50sc7uATmus16jmmHjhIHz+l/9GlJ5KqAMOx26mPZgfzG7oneL2b
VW+WgYUkTT3XEPFWnTp2RJwQao8/tYPXWEJDc0WVQHrpmnWOFKU/d3MqBgBm5y+6
jB81TU/RG2rVerPDWP+1MMcNNy0491CTL5XQZ7JfDJJ9CCmXSdtTl4uUQnSuv/Qx
Cea13BX2ZgJc7Au30vihLhub52De4P/4gonKsNHYdbWjg7OWKwNv/zitGDVDB9Y2
CMTyZKG3XEu5Ghl1LEnI3QmEKsqaCLv12BnVjbkSeZsMnevJPs1Ye6TjjJwdik5P
o/bKiIz+Fq8=
-----END CERTIFICATE-----"""


def build_ssl_context() -> ssl.SSLContext:
    """Construct an SSLContext using certifi trusted CA bundle and Supabase Root CA.
    
    Ensures strict SSL verification without bypassing certificate checks.
    """
    # 1. Start with certifi's Mozilla trusted CA bundle
    ctx = ssl.create_default_context(cafile=certifi.where())

    # 2. Add Supabase Root CA to trust store for verified TLS handshake
    cert_file = PROJECT_ROOT / "certs" / "prod-ca-2021.crt"
    if cert_file.exists():
        ctx.load_verify_locations(cafile=str(cert_file))
    else:
        ctx.load_verify_locations(cadata=SUPABASE_ROOT_CA_PEM)

    return ctx


def get_connection_url_object() -> URL:
    """Build a SQLAlchemy URL object for PostgreSQL with pg8000 driver.
    
    Prefers discrete environment variables; falls back to DATABASE_URL if configured.
    """
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    port_str = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME", "postgres")

    # 1. Prefer discrete environment variables
    if host and user:
        try:
            port = int(port_str)
        except ValueError:
            port = 5432

        return URL.create(
            drivername="postgresql+pg8000",
            username=user,
            password=password,
            host=host,
            port=port,
            database=dbname,
        )

    # 2. Fallback to DATABASE_URL
    raw_url = os.getenv("DATABASE_URL")
    if raw_url and raw_url.strip():
        parsed = make_url(raw_url.strip())
        return parsed.set(drivername="postgresql+pg8000")

    raise ValueError(
        "Database connection parameters not configured. "
        "Please configure DB_HOST, DB_USER, and DB_PASSWORD (or DATABASE_URL) in .env."
    )


def get_masked_connection_url() -> str:
    """Return the connection URL with credentials safely masked."""
    try:
        url_obj = get_connection_url_object()
        return url_obj.render_as_string(hide_password=True)
    except Exception:
        return "<MASKED_CONNECTION_URL>"


def get_engine(pool_size: int = 5, max_overflow: int = 10) -> Engine:
    """Return a SQLAlchemy Engine configured with pg8000 and verified SSL for Supabase."""
    url_obj = get_connection_url_object()
    sslmode = os.getenv("DB_SSLMODE", "require").lower()

    connect_args = {}
    if sslmode not in ("disable", "false", "off", "no"):
        connect_args["ssl_context"] = build_ssl_context()

    return create_engine(
        url_obj,
        connect_args=connect_args,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True,
    )


def get_raw_connection():
    """Return a DB-API connection via SQLAlchemy engine."""
    return get_engine().raw_connection()
