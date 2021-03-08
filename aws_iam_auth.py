import hashlib
import hmac
from urllib.parse import urlparse
import datetime


class AWSIamAuth:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        endpoint: str,
        region: str,
        service: str,
    ):
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint = endpoint
        self.region = region
        self.service = service

    def generate_auth_headers(self, method: str, content_type: str, body):
        host = urlparse(self.endpoint).netloc.split(":")[0]
        t = datetime.datetime.utcnow()
        amz_date = t.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = t.strftime("%Y%m%d")

        content_sha256 = hashlib.sha256(body).hexdigest()

        return {
            "x-amz-date": amz_date,
            "x-amz-content-sha256": content_sha256,
            "Authorization": self.__generate_authorization(
                method=method,
                content_type=content_type,
                host=host,
                amz_content_sha256=content_sha256,
                amz_date=amz_date,
                date_stamp=date_stamp,
            ),
        }

    def __generate_authorization(
        self,
        method: str,
        content_type: str,
        host: str,
        amz_content_sha256: str,
        amz_date: str,
        date_stamp: str,
    ):
        canonical_headers = (
            "content-type:"
            + content_type
            + "\n"
            + "host:"
            + host
            + "\n"
            + "x-amz-content-sha256:"
            + amz_content_sha256
            + "\n"
            + "x-amz-date:"
            + amz_date
            + "\n"
        )

        canonical_uri = urlparse(self.endpoint).path
        # note: appsyncをPOSTで実行する際にはquerystringが不要だったので、特に処理を実装しない
        canonical_querystring = ""

        signed_headers = "content-type;host;x-amz-content-sha256;x-amz-date"

        canonical_request = (
            method
            + "\n"
            + canonical_uri
            + "\n"
            + canonical_querystring
            + "\n"
            + canonical_headers
            + "\n"
            + signed_headers
            + "\n"
            + amz_content_sha256
        )

        credential_scope = (
            date_stamp + "/" + self.region + "/" + self.service + "/" + "aws4_request"
        )
        algorithm = "AWS4-HMAC-SHA256"
        string_to_sign = (
            algorithm
            + "\n"
            + amz_date
            + "\n"
            + credential_scope
            + "\n"
            + hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
        )

        signing_key = self.__get_signature_key(
            self.secret_key, date_stamp, self.region, self.service
        )

        signature = hmac.new(
            signing_key, string_to_sign.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        return (
            algorithm
            + " "
            + "Credential="
            + self.access_key
            + "/"
            + credential_scope
            + ", "
            + "SignedHeaders="
            + signed_headers
            + ", "
            + "Signature="
            + signature
        )

    def __sign(self, key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def __get_signature_key(self, key, date_stamp, region, service):
        k_date = self.__sign(key=("AWS4" + key).encode("utf-8"), msg=date_stamp)
        k_region = self.__sign(key=k_date, msg=region)
        k_service = self.__sign(key=k_region, msg=service)
        k_signing = self.__sign(key=k_service, msg="aws4_request")
        return k_signing
