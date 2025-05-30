import os
import jwt
from configparser import ConfigParser
import requests
import json
def set_up():
    """Sets up configuration for the app"""

    env = os.getenv("ENV", None)

    if env == ".config":
        config = ConfigParser()
        config.read(".config")
        config = config["AUTH0"]
    else:
        config = {
            "AUDIENCE": os.getenv("AUDIENCE", "account"),
            "ISSUER": os.getenv("ISSUER", ""),
            "ALGORITHMS": os.getenv("ALGORITHMS", "RS256"),
            "JWKS_URL": os.getenv("JWKS_URL", ""),
            "CLAIM_SERVICE": os.getenv("CLAIM_SERVICE", ""),
            "REQUIRED_CLAIMS": os.getenv("REQUIRED_CLAIMS", "")
        }
    return config


class VerifyToken():
    """Does all the token verification using PyJWT"""

    def __init__(self, token, permissions=None, scopes=None):
        self.token = token
        self.permissions = permissions
        self.scopes = scopes
        self.config = set_up()

        # This gets the JWKS from a given URL and does processing so you can
        # use any of the keys available
        self.jwks_client = jwt.PyJWKClient(self.config["JWKS_URL"])

    def verify(self):
        # This gets the 'kid' from the passed token
        try:
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(
                self.token
            ).key
        except jwt.exceptions.PyJWKClientError as error:
            return {"status": "error", "msg": error.__str__()}
        except jwt.exceptions.DecodeError as error:
            return {"status": "error", "msg": error.__str__()}

        try: 
            payload = jwt.decode(
                self.token,
                self.signing_key,
                algorithms=self.config["ALGORITHMS"],
                audience=self.config["AUDIENCE"],
                issuer=self.config["ISSUER"],
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}

        if self.scopes:
            result = self._check_claims(payload, 'scope', str, self.scopes.split(' '))
            if result.get("error"):
                return result

        if self.permissions:
            result = self._check_claims(payload, 'permissions', list, self.permissions)
            if result.get("error"):
                return result

        return payload

    def _check_claims(self, payload, claim_name, claim_type, expected_value):

        instance_check = isinstance(payload[claim_name], claim_type)
        result = {"status": "success", "status_code": 200}

        payload_claim = payload[claim_name]

        if claim_name not in payload or not instance_check:
            result["status"] = "error"
            result["status_code"] = 400

            result["code"] = f"missing_{claim_name}"
            result["msg"] = f"No claim '{claim_name}' found in token."
            return result

        if claim_name == 'scope':
            payload_claim = payload[claim_name].split(' ')

        for value in expected_value:
            if value not in payload_claim:
                result["status"] = "error"
                result["status_code"] = 403

                result["code"] = f"insufficient_{claim_name}"
                result["msg"] = (f"Insufficient {claim_name} ({value}). You "
                                  "don't have access to this resource")
                return result

        ### Claim Check must be here


        return result