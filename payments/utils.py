# payments/utils.py
import hmac
import hashlib
import base64


def generate_signature(data: dict, secret: str) -> str:
    """
    Builds the HMAC-SHA256 signature eSewa requires on outgoing payment
    requests. eSewa tells us which fields to sign via `signed_field_names`,
    and the order matters — the message string must be built in that exact
    order, joined as key=value pairs.
    """
    signed_fields = data['signed_field_names'].split(',')
    message = ",".join(f"{field}={data[field]}" for field in signed_fields)

    digest = hmac.new(
        secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()

    return base64.b64encode(digest).decode('utf-8')


def verify_signature(payload: dict, secret: str) -> bool:
    """
    Recomputes the signature on data eSewa sends BACK to us, and compares
    it against the signature eSewa included. If they match, we know the
    payload wasn't tampered with in transit — this is the entire security
    guarantee of the whole integration.
    """
    expected = generate_signature(payload, secret)
    received = payload.get('signature', '')

    return hmac.compare_digest(expected, received)