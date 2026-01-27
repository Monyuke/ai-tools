"""
title: Web Search and URL Tool (No Dependencies)
author: monyuke
author_url:
funding_url:
version: 0.2.1
"""

"""
ファンクション実行形式が「ネイティブ」じゃないと使えないので注意！
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import re
import html
from html.parser import HTMLParser
from ddgs import DDGS
from typing import Optional
import zlib
from langchain.tools import tool


def extract_text_from_pdf(pdf_data: bytes) -> str:
    """
    PDFバイナリからテキストを抽出する（標準ライブラリのみ使用）

    Parameters
    ----------
    pdf_data: bytes
        PDFファイルのバイナリデータ

    Returns
    -------
    str
        抽出されたテキスト
    """
    try:
        text_parts = []
        pdf_str = pdf_data.decode("latin-1", errors="ignore")

        # PDFのストリームオブジェクトからテキストを抽出
        # パターン: stream...endstream の間のデータ
        stream_pattern = re.compile(rb"stream\r?\n(.*?)\r?\nendstream", re.DOTALL)

        for match in stream_pattern.finditer(pdf_data):
            stream_data = match.group(1)

            # FlateDecode（zlib圧縮）の解凍を試みる
            try:
                decompressed = zlib.decompress(stream_data)
                stream_text = decompressed.decode("latin-1", errors="ignore")
            except:
                stream_text = stream_data.decode("latin-1", errors="ignore")

            # テキスト抽出パターン
            # PDFのテキストオペレータ: Tj, TJ, ' など
            text_operators = re.findall(
                r"\(((?:[^()\\]|\\.)*)\)\s*T[jJ\']", stream_text
            )

            for text in text_operators:
                # エスケープシーケンスを処理
                decoded_text = (
                    text.replace("\\(", "(").replace("\\)", ")").replace("\\\\", "\\")
                )
                if decoded_text.strip():
                    text_parts.append(decoded_text)

            # 配列形式のテキスト: [(text1)(text2)] TJ
            array_pattern = re.findall(
                r"\[((?:\([^)]*\)\s*-?\d*\s*)+)\]\s*TJ", stream_text
            )
            for array_text in array_pattern:
                texts = re.findall(r"\(([^)]*)\)", array_text)
                for text in texts:
                    decoded_text = (
                        text.replace("\\(", "(")
                        .replace("\\)", ")")
                        .replace("\\\\", "\\")
                    )
                    if decoded_text.strip():
                        text_parts.append(decoded_text)

        # 抽出できなかった場合は単純なテキスト検索
        if not text_parts:
            # obj...endobj の間からテキストらしきものを抽出
            simple_text = re.findall(r"\(([^)]{3,})\)", pdf_str)
            text_parts = [t for t in simple_text if len(t.strip()) > 2]

        return " ".join(text_parts)

    except Exception as e:
        print(f"[extract_text_from_pdf] エラー: {e}")
        return ""


def fetch_text_sync(
    url: str,
    *,
    timeout: int = 60,  # 60 秒
) -> str:
    """
    標準ライブラリでURLを読み込み、テキストを取得する。
    PDFの場合は標準ライブラリでテキスト抽出を行う。

    Parameters
    ----------
    url: str
        取得対象の URL
    timeout: int, default 60
        タイムアウト（秒）

    Returns
    -------
    str
        ページのテキストコンテンツ。取得失敗時は空文字列。
    """
    try:
        # PDFかどうかをURLの拡張子で判定
        is_pdf = url.lower().endswith(".pdf")

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }

        # URLをエンコード
        if not urllib.parse.urlparse(url).scheme:
            url = "https://" + url

        url = encode_url(url)
        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req, timeout=timeout) as response:
            content = response.read()

            if is_pdf:
                # PDFからテキストを抽出
                return extract_text_from_pdf(content)
            else:
                # HTMLからテキストを抽出（body内のみ）
                html_content = decode_content(content, response.headers)
                extractor = TextExtractor(body_only=True)
                extractor.feed(html_content)
                text = " ".join(extractor.text)
                return text

    except urllib.error.HTTPError as e:
        print(f"[fetch_text_sync] HTTP Error {e.code}: {e.reason}")
        return ""
    except urllib.error.URLError as e:
        print(f"[fetch_text_sync] URL Error: {str(e.reason)}")
        return ""
    except Exception as e:
        print(f"[fetch_text_sync] エラー: {e}")
        return ""


# ----------------------------------------------------------------------
# URL を ASCII 文字列へ変換（Punycode + percent‑encode）
# ----------------------------------------------------------------------
def encode_url(url: str) -> str:
    """
    URL を ASCII 文字列に変換する。ドメインは Punycode、path は
    percent‑encode する。スキーマが無ければ https:// を付与。
    """
    # スキーマが無い場合は https:// を付与
    if not urllib.parse.urlparse(url).scheme:
        url = "https://" + url

    parsed = urllib.parse.urlparse(url)

    # netloc（ホスト部分）を Punycode へ変換
    try:
        netloc = parsed.netloc.encode("idna").decode("ascii")
    except Exception:
        netloc = parsed.netloc

    # path を percent‑encode (unsafe は空文字にして全てエンコード)
    path = urllib.parse.quote(parsed.path, safe="/%-._~!$&'()*+,;=:@")

    # query は RFC3986 の safe characters を残しつつ encode
    query = urllib.parse.quote_plus(parsed.query, safe="=&")

    # 再構築して ASCII 文字列へ
    encoded = urllib.parse.urlunparse(
        (
            parsed.scheme,
            netloc,
            path,
            parsed.params,
            query,
            parsed.fragment,
        )
    )
    return encoded


# ----------------------------------------------------------------------
# 文字コード判定・デコード
# ----------------------------------------------------------------------
def decode_content(content: bytes, headers) -> str:
    """バイナリデータを適切な文字コードでデコード"""
    # 1. ヘッダーから charset を取得
    charset = None
    if hasattr(headers, "get_content_charset"):
        charset = headers.get_content_charset()
    if not charset:
        ct = headers.get("Content-Type", "")
        match = re.search(r"charset=([^\s;]+)", ct, re.IGNORECASE)
        if match:
            charset = match.group(1)

    # 2. 取得できた charset でデコードを試行
    if charset:
        try:
            return content.decode(charset, errors="replace")
        except Exception:
            pass

    # 3. 一般的な日本語エンコーディングで順番に試行
    for enc in ["utf-8", "utf-8-sig", "shift_jis", "euc-jp", "iso-2022-jp"]:
        try:
            return content.decode(enc, errors="replace")
        except Exception:
            continue

    # 4. 最後のフォールバック
    return content.decode("utf-8", errors="replace")


# ----------------------------------------------------------------------
# HTML コンテンツからテキスト・リンクを抽出
# ----------------------------------------------------------------------
class TextExtractor(HTMLParser):
    def __init__(self, body_only=False):
        super().__init__()
        self.text = []
        self.links = []
        self.current_link = None
        self.body_only = body_only
        self.in_body = False
        self.in_script = False
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.in_body = True
        elif tag == "script":
            self.in_script = True
        elif tag == "style":
            self.in_style = True
        elif tag == "a" and (not self.body_only or self.in_body):
            for attr, value in attrs:
                if attr == "href":
                    self.current_link = value
                    break

    def handle_endtag(self, tag):
        if tag == "body":
            self.in_body = False
        elif tag == "script":
            self.in_script = False
        elif tag == "style":
            self.in_style = False
        elif tag == "a":
            self.current_link = None

    def handle_data(self, data):
        # script, styleタグ内は無視
        if self.in_script or self.in_style:
            return

        # body_onlyがTrueの場合、body内のみ抽出
        if self.body_only and not self.in_body:
            return

        clean_data = data.strip()
        if clean_data:
            self.text.append(clean_data)
            if self.current_link and clean_data:
                self.links.append({"text": clean_data, "url": self.current_link})


# ----------------------------------------------------------------------
# ツールクラス（内部にプライベートメソッドは置かない）
# ----------------------------------------------------------------------
class Tools:
    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }

    def fetch_webpage(
        self,
        url: str,
        part: int = 1,
    ) -> str:
        """
        Fetch and return the text content of a webpage using Playwright.
        :param url: The URL to fetch.
        :param part: The block number to retrieve (starting from 1).
        :return: Text content of the webpage
        """
        part_size: int = 2000
        try:
            # Playwrightでテキストコンテンツを取得
            text = fetch_text_sync(url)

            if not text:
                return f"Error: Could not fetch content from {url}"

            # 空白を正規化
            text = re.sub(r"\s+", " ", text).strip()

            # part 番号は 1 から始まる想定
            if part < 1:
                return f"Error: part must be >= 1"

            # 全体のパート数を計算
            total_parts = max(1, (len(text) + part_size - 1) // part_size)

            start = (part - 1) * part_size
            end = start + part_size

            # 文字列長に合わせてインデックス補正
            if start >= len(text):
                # 指定した part が存在しない
                return (
                    f"Content from {url} (part {part} of {total_parts}):\n\n"
                    f"[No more content; part {part} is out of range]"
                )
            if end > len(text):
                end = len(text)

            sliced_text = text[start:end]
            return (
                f"Content from {url} (part {part} of {total_parts}):\n\n"
                f"{sliced_text}"
            )
        except Exception as e:
            return f"Error fetching webpage: {str(e)}"

    # ------------------------------------------------------------------
    #  すべてのリンク抽出
    # ------------------------------------------------------------------
    def extract_links(self, url: str) -> str:
        """
        Extract all links from a webpage using built-in libraries.
        :param url: URL of the webpage to extract links from
        :return: List of links found on the page
        """
        try:
            encoded_url = encode_url(url)

            req = urllib.request.Request(encoded_url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read()
                html_content = decode_content(content, response.headers)

                extractor = TextExtractor()
                extractor.feed(html_content)

                unique_links = []
                seen_urls = set()
                for link in extractor.links:
                    href = link["url"]
                    text = link["text"]

                    if href.startswith("/"):
                        href = urllib.parse.urljoin(encoded_url, href)
                    elif not href.startswith(("http://", "https://")):
                        continue

                    if href not in seen_urls and text:
                        unique_links.append({"text": text, "url": href})
                        seen_urls.add(href)

                if not unique_links:
                    return f"No links found on {url}"

                result = f"Links found on {url}:\n\n"
                for i, link in enumerate(unique_links[:20], 1):
                    result += f"{i}. {link['text']}\n   {link['url']}\n\n"

                if len(unique_links) > 20:
                    result += f"... and {len(unique_links) - 20} more links"

                return result
        except urllib.error.HTTPError as e:
            return f"HTTP Error {e.code}: {e.reason}"
        except urllib.error.URLError as e:
            return f"URL Error: {str(e.reason)}"
        except Exception as e:
            return f"Error extracting links: {str(e)}"

    # ------------------------------------------------------------------
    #  URL ステータス確認
    # ------------------------------------------------------------------
    def check_url_status(self, url: str) -> str:
        """
        Check if a URL is accessible and return status information.
        :param url: URL to check
        :return: Status information about the URL
        """
        try:
            encoded_url = encode_url(url)

            req = urllib.request.Request(encoded_url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                status_code = response.getcode()
                content_length = len(response.read())
                content_type = response.headers.get("Content-Type", "Unknown")
                server = response.headers.get("Server", "Unknown")

                status_info = f"URL Status Check for {url}:\n"
                status_info += f"🌐 Status Code: {status_code}\n"
                status_info += f"📏 Content Length: {content_length} bytes\n"
                status_info += f"📄 Content Type: {content_type}\n"
                status_info += f"🔧 Server: {server}\n"

                if status_code == 200:
                    status_info += "✅ URL is accessible"
                else:
                    status_info += f"⚠️ URL returned status code {status_code}"
                return status_info
        except urllib.error.HTTPError as e:
            return f"❌ HTTP Error {e.code}: {e.reason}"
        except urllib.error.URLError as e:
            return f"❌ URL Error: {str(e.reason)}"
        except Exception as e:
            return f"❌ Error checking URL: {str(e)}"

    def web_search(self, query: str) -> str:
        """
        Perform a search on DuckDuckGo and return the results in HTML.
        :param query: Search query.
        :return: List of dictionaries with search results.
        """
        return DDGS().text(query, max_results=10, backend="duckduckgo")

    # ------------------------------------------------------------------
    #  ページ内検索
    # ------------------------------------------------------------------
    def find_in_page(self, pattern: str, url: str) -> str:
        """
        Search for a pattern in a webpage and return matching lines with context.
        :param pattern: Search pattern (regular expression supported)
        :param url: URL of the webpage to search
        :return: Matching lines with surrounding context
        """
        try:
            # Playwrightでテキストコンテンツを取得
            text = fetch_text_sync(url)

            if not text:
                return f"Error: Could not fetch content from {url}"

            # 空白を正規化
            text = re.sub(r"\s+", " ", text).strip()

            # パターンで検索（正規表現対応）
            try:
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
            except re.error:
                return f"Error: Invalid regular expression pattern '{pattern}'"

            if not matches:
                return f"Pattern '{pattern}' not found in {url}"

            result = f"Found {len(matches)} match(es) for '{pattern}' in {url}:\n\n"

            # 最大10件のマッチを表示
            for i, match in enumerate(matches[:10], 1):
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end]

                # マッチ部分を強調
                highlighted = (
                    context[: match.start() - start]
                    + f">>>{match.group()}<<<"
                    + context[match.end() - start :]
                )

                result += f"{i}. ...{highlighted}...\n\n"

            if len(matches) > 10:
                result += f"... and {len(matches) - 10} more match(es)"

            return result

        except Exception as e:
            return f"Error searching in page: {str(e)}"


@tool
def web_search(query: str) -> str:
    """
    Perform a search on DuckDuckGo and return the results in HTML.
    :param query: Search query.
    :return: List of dictionaries with search results.
    """
    return DDGS().text(query, max_results=10, backend="duckduckgo")


@tool
def find_in_page(pattern: str, url: str) -> str:
    """
    Search for a pattern in a webpage and return matching lines with context.
    :param pattern: Search pattern (regular expression supported)
    :param url: URL of the webpage to search
    :return: Matching lines with surrounding context
    """
    return Tools().find_in_page(pattern, url)


@tool
def fetch_webpage(
    url: str,
    part: int = 1,
) -> str:
    """
    Fetch and return the text content of a webpage using Playwright.
    :param url: The URL to fetch.
    :param part: The block number to retrieve (starting from 1).
    :return: Text content of the webpage
    """
    return Tools().fetch_webpage(url, part)
