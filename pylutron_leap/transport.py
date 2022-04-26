import ssl


def create_leap_ssl_context():
    _ctx = ssl.create_default_context()
    _ctx.check_hostname = False
    _ctx.verify_mode = ssl.CERT_NONE

    return _ctx
