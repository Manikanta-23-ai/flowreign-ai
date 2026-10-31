import ipaddress
import re
import socket
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urlparse

import requests


MAX_BYTES = 1_000_000
MAX_TEXT = 20_000


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            text = data.strip()
            if text:
                self.parts.append(text)


def validate_public_url(url: str):
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only HTTP and HTTPS URLs are supported.")

    if not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Invalid source URL.")

    if parsed.port not in (None, 80, 443):
        raise ValueError("Custom ports are not allowed.")

    try:
        addresses = socket.getaddrinfo(
            parsed.hostname,
            parsed.port or (443 if parsed.scheme == "https" else 80),
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as error:
        raise ValueError("Could not resolve source hostname.") from error

    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])
        if not ip.is_global:
            raise ValueError("Private or non-public addresses are not allowed.")


def extract_text(html: str) -> str:
    parser = TextExtractor()
    parser.feed(html)
    return re.sub(r"\s+", " ", " ".join(parser.parts))[:MAX_TEXT]


def find_evidence(text: str, objective: str) -> list[str]:
    keywords = {
        word.lower()
        for word in re.findall(r"[a-zA-Z]{4,}", objective)
    }

    sentences = re.split(r"(?<=[.!?])\s+", text)
    matches = []

    for sentence in sentences:
        sentence = sentence.strip()

        if len(sentence) < 50:
            continue

        score = sum(
            1 for word in keywords
            if re.search(r"\b" + re.escape(word) + r"\b",
                         sentence, re.IGNORECASE)
        )

        if score:
            matches.append((score, sentence[:500]))

    matches.sort(key=lambda item: item[0], reverse=True)

    if matches:
        return [sentence for _, sentence in matches[:5]]

    return [text[:400]] if text else []


def research_sources(objective: str, source_urls: list[str]) -> dict:
    results = []

    for url in source_urls:
        try:
            validate_public_url(url)

            response = requests.get(
                url,
                timeout=12,
                allow_redirects=False,
                headers={
                    "User-Agent": "FlowReignAI/1.0 (open-source research tool)"
                },
                stream=True,
            )

            if response.status_code in (301, 302, 303, 307, 308):
                raise ValueError("Redirects are not followed for security.")

            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "").lower()

            if not any(
                kind in content_type
                for kind in ("text/html", "text/plain")
            ):
                raise ValueError("Source is not an HTML or plain-text page.")

            chunks = []
            size = 0

            for chunk in response.iter_content(16_384):
                size += len(chunk)

                if size > MAX_BYTES:
                    raise ValueError("Source exceeds the 1 MB limit.")

                chunks.append(chunk)

            raw = b"".join(chunks).decode(
                response.encoding or "utf-8",
                errors="replace",
            )

            text = extract_text(raw)
            evidence = find_evidence(text, objective)

            results.append({
                "source_url": url,
                "status": "retrieved",
                "http_status": response.status_code,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "content_length": len(text),
                "evidence": evidence,
            })

        except Exception as error:
            results.append({
                "source_url": url,
                "status": "failed",
                "error": str(error),
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "evidence": [],
            })

    successful = sum(item["status"] == "retrieved" for item in results)

    return {
        "platform": "FlowReign AI",
        "agent": "Evidence Research Agent",
        "objective": objective,
        "research_status": "completed" if successful else "failed",
        "sources_requested": len(source_urls),
        "sources_retrieved": successful,
        "sources": results,
        "limitations": [
            "Only user-supplied URLs were examined.",
            "Evidence snippets are extracted from page text.",
            "Source credibility and factual accuracy are not independently verified.",
            "This agent does not perform web search.",
            "No AI-generated conclusions were used.",
        ],
    }