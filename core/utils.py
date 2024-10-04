import string
import secrets
import base64
import uuid

def generate_unique_code(length=None):
    """
    base64 encoded 22 char long string from a uuid4, this will generate unique url safe code
        Like: wGDai-wcRsi9hJ1i0bIPeg, 5YygikYTTqO5mJGBanOmrw, luJAXMQoRD2umlFT46_5aQ
    To decode and get back the uuid:
        uuid.UUID(bytes=base64.urlsafe_b64decode(unique_code+'=='))
    if length is defined then generate code by secrets module using 62 char
    """
    if length:
        _alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(_alphabet) for _ in range(length))

    # unique 22 char long string thats include - and _ special char
    return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode("utf-8").strip("=")
