import logging
import json
from authlib.jose import JWSObject, jwt
from authlib.jose.errors import BadSignatureError, DecodeError

SAHAMATI_UAT_PUBLIC_KEY=json.loads('''{
            "kid": "mrIv4jl1Zk36xpEHNdIPPldz4XUKipQOuapGNCSQwZM",
            "kty": "RSA",
            "alg": "RS256",
            "use": "sig",
            "n": "yMzHt4zMlplvP6XvbxfE7TivX0T2w1yN7uWPX_428jlr51PqJIuv2Mv1q3QAnty9hBlz-VLw5prXvl1xUlr9BYqjBQR7ijMBRCJcXZK26u4auzyFA5YAZQ9sGGUxJrtYwHsFIXN58g6tZbQPYmQWXtaoGWTC-UUEXPb5BngiKyAcUpgmyfUM1fseQjz7V6v_LlhdWOPtEPBzx7s-CpvjoiuqEVTk6RcBd8-PTGsbuHL7r3fDb1haWdc7RJ0LbnP0rmA301wEWDdQTV_QVUN2eY8eNIRBbGmYXOzqjI5DCxAm-gL3ztDtKNQW9sLiI14YEIb4aonV36rhj8xtSDCU5Q",
            "e": "AQAB",
            "x5c": [
                "MIICnzCCAYcCBgF19FMx/TANBgkqhkiG9w0BAQsFADATMREwDwYDVQQDDAhzYWhhbWF0aTAeFw0yMDExMjMwODU2MzRaFw0zMDExMjMwODU4MTRaMBMxETAPBgNVBAMMCHNhaGFtYXRpMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyMzHt4zMlplvP6XvbxfE7TivX0T2w1yN7uWPX/428jlr51PqJIuv2Mv1q3QAnty9hBlz+VLw5prXvl1xUlr9BYqjBQR7ijMBRCJcXZK26u4auzyFA5YAZQ9sGGUxJrtYwHsFIXN58g6tZbQPYmQWXtaoGWTC+UUEXPb5BngiKyAcUpgmyfUM1fseQjz7V6v/LlhdWOPtEPBzx7s+CpvjoiuqEVTk6RcBd8+PTGsbuHL7r3fDb1haWdc7RJ0LbnP0rmA301wEWDdQTV/QVUN2eY8eNIRBbGmYXOzqjI5DCxAm+gL3ztDtKNQW9sLiI14YEIb4aonV36rhj8xtSDCU5QIDAQABMA0GCSqGSIb3DQEBCwUAA4IBAQCkXAAe+o6DWuO9KB8s6P5A0W6w9IpcelyuhCID2lW6TD/M4sBfM2oppGLzc4ifc2COamQHwAhKHa3FcYdk1zzIL/opbVH2ppHYftgoFuNt+Q07iu8IzWjGi9LR1PaCyMJswzFN86PU0R27qG18ZL2ayxLoPcq4ouZRTC7zgRe6VUHdFvjPJV5MqF4vlkv2eWj1RltTDissCc/mSaIjsWShWSPou7Xs6pPhS2GRi78qaPOsR6phgqSdls5eb/315wDuwbpGt30LCd+x8pqxmpw8NFqcaLCLVNaxrpHay7IVjd1LeDwZCSrosDBTO0RglrUcVHn7ydKnQL1QZ5y6/BhC"
            ],
            "x5t": "YyGyTXjLrfXp0R2lwCInPGAduUw",
            "x5t#S256": "nzzJSI2oZQ0XdV5tV54gyeCp_5ebEpCnSwADkc6yB7Q"
        }''')

def verify_and_decode_credentials(api_key: str, role: str) -> JWSObject:
        """Verify FIU's client_api_key/AA's api_key credentials using Sahamati public key"""

        try:
            claims = jwt.decode(api_key, SAHAMATI_UAT_PUBLIC_KEY)
            # TODO: Enable this and validate role
            # claims.validate()
            logging.info(claims)
            return claims
        except (DecodeError, BadSignatureError):
            logging.error('JWT auth error!')
            raise
        