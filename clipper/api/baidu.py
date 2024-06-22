import hashlib
import random
import time

from clipper.api.base import TranslationAPIWithAppID, TranslationError


class BaiduTranslationAPI(TranslationAPIWithAppID):
    """
    Baidu translation API.
    """

    endpoint = "https://fanyi-api.baidu.com/api/trans/vip/translate"

    def translate(self, text: str, orig: str, to: str):
        # Split text into chunks of 6000 characters or until the end of a sentence
        chunks = []
        chunk = ""
        for sentence in text.split("."):
            if len(chunk) + len(sentence) >= 6000:
                chunks.append(chunk)
                chunk = ""
            if chunk:
                chunk += "."
            chunk += sentence
        if chunk:
            chunks.append(chunk)

        # Translate each chunk and append to the final result
        result = ""
        for i, chunk in enumerate(chunks):
            salt = str(random.randint(32768, 65536))
            sign_str = f"{self.appid}{chunk}{salt}{self.appkey}"
            sign = hashlib.md5(sign_str.encode()).hexdigest()

            params = {
                "q": chunk,
                "from": orig,
                "to": to,
                "appid": self.appid,
                "salt": salt,
                "sign": sign,
            }
            response = self.session.get(self.endpoint, params=params)
            try:
                if response.status_code == 200:
                    chunk_result = response.json()
                    if "trans_result" in chunk_result:
                        chunk_translation = ""
                        for res in chunk_result["trans_result"]:
                            chunk_translation += f"{res['dst']}\n"
                        result += chunk_translation
                        if i < len(chunks) - 1 and i % 10 == 9:
                            time.sleep(0.2)
                    else:
                        raise TranslationError(
                            f"Unknown error when translating: {chunk_result}"
                        )
                else:
                    raise TranslationError(
                        f"HTTP error with status code: {response.status_code}"
                    )
            except Exception as e:
                raise TranslationError(f"Error translating: {e}")
        return result
