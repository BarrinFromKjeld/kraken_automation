"""Module to interact with kraken API"""
import base64
import hashlib
import hmac
import os
import pathlib
import urllib
import urllib.parse

from typing import Any, Dict, List

import requests
from modules.log import create_logger

HOME = pathlib.Path(os.path.expanduser("~"))

logger = create_logger(__name__)


def _read_file(file_name: pathlib.Path) -> List[str]:
    with open(file_name, "r", encoding="ascii") as the_file:
        lines: List[str] = the_file.readlines()
        new_lines: List[str] = []
        for line in lines:
            new_line = line.strip("\n")
            new_lines.append(new_line)
        return new_lines


def _read_key() -> Dict[str, str]:
    lines = _read_file(HOME.joinpath(".kraken_key"))
    return {"key": lines[0], "secret": lines[1]}


def _read_otp() -> str:
    return _read_file(HOME.joinpath(".kraken_otp"))[0]


def _read_nonce() -> int:
    nonce_file = HOME.joinpath(".kraken_nonce")
    if not nonce_file.exists():
        with open(nonce_file, "w", encoding="ascii") as the_file:
            the_file.write("0")
    content = _read_file(nonce_file)
    nonce = int(content[0]) + 1
    with open(nonce_file, "w", encoding="ascii") as the_file:
        the_file.write(str(nonce))
    return nonce


def _get_payload(data: Dict[str, str] = None) -> Dict[str, str]:
    payload = {"nonce": str(_read_nonce()), "otp": _read_otp()}
    if data:
        payload = {**payload, **data}
    return payload


def _get_kraken_signature(urlpath: str, data: Dict[str, str], secret: str) -> str:
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data["nonce"]) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()
    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()


def kraken_request(uri: str, data: Dict[str, str] = None) -> Dict[str, Any]:
    """Execute a request against the kraken api."""
    url_base = "https://api.kraken.com"
    url_path = url_base + uri
    payload = _get_payload(data)
    key = _read_key()
    headers: Dict[str, str] = {"API-Key": key["key"], "API-Sign": _get_kraken_signature(uri, payload, key["secret"])}
    response = requests.post(url_path, data=payload, headers=headers)
    response.raise_for_status()
    result: Dict[str, Any] = response.json()
    logger.info(result)
    return result["result"]
