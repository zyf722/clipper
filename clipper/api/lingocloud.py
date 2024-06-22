import json

from clipper.api.base import TranslationAPIWithToken, TranslationError


class LingoCloudTranslationAPI(TranslationAPIWithToken):
    """
    LingoCloud translation API.
    """

    endpoint = "http://api.interpreter.caiyunai.com/v1/translator"

    def translate(self, text: str, orig: str, to: str):
        response = self.session.post(
            self.endpoint,
            data=json.dumps(
                {
                    "source": text,
                    "trans_type": f"{orig}2{to}",
                    "request_id": "demo",
                    "detect": orig == "auto",
                }
            ),
            headers={
                "content-type": "application/json",
                "x-authorization": "token " + self.token,
            },
        )
        try:
            if response.status_code == 200:
                return json.loads(response.text)["target"]
            else:
                raise TranslationError(
                    f"HTTP error with status code: {response.status_code}"
                )
        except Exception as e:
            raise TranslationError(f"Error translating: {e}")
