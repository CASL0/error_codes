"""エラーコードJSON出力
"""
from dataclasses import dataclass
import logging
import sys
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, ConnectionError, HTTPError, Timeout
from dataclasses_json import dataclass_json


@dataclass
class ErrorDetail:
    """エラーの詳細"""

    code: int
    alias: str
    description: str


@dataclass_json
@dataclass
class ErrorDetails:
    """エラーリスト"""

    errors: list[ErrorDetail]


def main():
    """エントリーポイント"""
    try:
        collect_windows_system_error_codes()
    except ConnectionError as error:
        logging.error(error)
        sys.exit(1)
    except HTTPError as error:
        logging.error(error)
        sys.exit(1)
    except Timeout as error:
        logging.error(error)
        sys.exit(1)
    except RequestException as error:
        logging.error(error)
        sys.exit(1)


def collect_windows_system_error_codes():
    """WindowsのシステムエラーコードをJSON出力"""
    urls: list[str] = [
        "https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--0-499-",
        "https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--500-999-",
        "https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--1000-1299-",
        "https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--1300-1699-",
        "https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--1700-3999-",
        "https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--4000-5999-",
        "https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--6000-8199-",
        "https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--8200-8999-",
        "https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--9000-11999-",
        "https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--12000-15999-",
    ]
    error_codes = ErrorDetails(errors=[])
    for url in urls:
        parsed_codes = parse_doc(url)
        error_codes.errors.extend(parsed_codes)
    with open(
        "windows_system_errors.json", "w", encoding="utf-8", newline="\n"
    ) as file:
        file.write(error_codes.to_json(indent=2, ensure_ascii=False))


def parse_doc(url: str) -> list[ErrorDetail]:
    """エラーコードのWebページのスクレイピング

    Args:
        url (str): エラーコードのページURL

    Returns:
        list[ErrorDetail]: ページ解析結果のエラーリスト
    """
    res = requests.get(url=url, timeout=(30, 30))
    soup = BeautifulSoup(res.text, "html.parser")
    wrapper_elem = soup.find("dl")
    error_codes: list[ErrorDetail] = []
    for elem in wrapper_elem.find_all("dt", recursive=False):
        alias = elem.p.strong.text
        description_elements = elem.find_next_sibling("dd").dl.find_all("dt")
        error_codes.append(
            ErrorDetail(
                code=convert_error_codes(description_elements[0].p.text),
                alias=alias,
                description=description_elements[1].p.text,
            )
        )
    return error_codes


def convert_error_codes(error_codes: str) -> int:
    """エラーコードを数値だけ抽出する

    Args:
        error_codes (str): エラーコードが含まれた文字列

    Returns:
        int: 抽出したエラーコードの数値（例：1 (0x1)の場合は1）
    """
    return int(error_codes.split()[0])


if __name__ == "__main__":
    main()
