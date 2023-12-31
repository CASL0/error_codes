"""エラーコードJSON出力
"""
from dataclasses import dataclass
import logging
import sys
import re
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
        collect_linux_system_error_codes()
        collect_curl_error_codes()
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


def collect_error_codes(urls: list[str], parser: callable, file_name: str):
    """指定のURLのページをパースし、エラーコードの一覧を取得します

    Args:
        urls (list[str]): URLのリスト
        parser (callable): Webページのパーサー
    """
    error_codes = ErrorDetails(errors=[])
    for url in urls:
        parsed_codes = parser(url)
        error_codes.errors.extend(parsed_codes)
    with open(file_name, "w", encoding="utf-8", newline="\n") as file:
        file.write(error_codes.to_json(indent=2, ensure_ascii=False))


def collect_curl_error_codes():
    """cURLのエラーコードをJSON出力"""
    urls: list[str] = ["https://curl.se/libcurl/c/libcurl-errors.html"]
    collect_error_codes(urls=urls, parser=parse_curl_doc, file_name="curl_errors.json")


def parse_curl_doc(url: str) -> list[ErrorDetail]:
    """cURLエラーコードのWebページのスクレイピング

    Args:
        url (str): エラーコードのページURL

    Returns:
        list[ErrorDetail]: ページ解析結果のエラーリスト
    """
    res = requests.get(url=url, timeout=(30, 30))
    soup = BeautifulSoup(res.text, "html.parser")
    error_elements = soup.find_all("span", string=re.compile(r"^CURLE.+\(\d+\)$"))
    error_codes: list[ErrorDetail] = []
    for elem in error_elements:
        # ()内の数字を取り出す
        tmp = re.search(r"\(\d+\)", elem.text).group()
        code = re.search(r"\d+", tmp).group()
        alias = re.search(r"^CURLE[_A-Z]+", elem.text).group()
        description = elem.parent.find_next_sibling("p").text
        error_codes.append(
            ErrorDetail(code=int(code), alias=alias, description=description)
        )
    return error_codes


def collect_linux_system_error_codes():
    """LinuxのシステムエラーコードをJSON出力"""
    urls: list[str] = ["https://www.thegeekstuff.com/2010/10/linux-error-codes/"]
    collect_error_codes(urls=urls, parser=parse_linux_doc, file_name="errno.json")


def parse_linux_doc(url: str) -> list[ErrorDetail]:
    """LinuxエラーコードのWebページのスクレイピング

    Args:
        url (str): エラーコードのページURL

    Returns:
        list[ErrorDetail]: ページ解析結果のエラーリスト
    """
    res = requests.get(url=url, timeout=(30, 30))
    soup = BeautifulSoup(res.text, "html.parser")
    table_elem = soup.find("table", id="optiontable")
    error_codes: list[ErrorDetail] = []
    for i, elem in enumerate(table_elem.tbody.find_all("tr", recursive=False)):
        if i == 0 or i == 1:
            continue
        tds = elem.find_all("td")
        error_codes.append(
            ErrorDetail(
                code=int(tds[0].text), alias=tds[1].text, description=tds[2].text
            )
        )
    return error_codes


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
    collect_error_codes(
        urls=urls, parser=parse_windows_doc, file_name="windows_system_errors.json"
    )


def parse_windows_doc(url: str) -> list[ErrorDetail]:
    """WindowsエラーコードのWebページのスクレイピング

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
                code=convert_windows_error_codes(description_elements[0].p.text),
                alias=alias,
                description=description_elements[1].p.text,
            )
        )
    return error_codes


def convert_windows_error_codes(error_codes: str) -> int:
    """エラーコードを数値だけ抽出する

    Args:
        error_codes (str): エラーコードが含まれた文字列

    Returns:
        int: 抽出したエラーコードの数値（例：1 (0x1)の場合は1）
    """
    return int(error_codes.split()[0])


if __name__ == "__main__":
    main()
