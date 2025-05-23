from __future__ import annotations

import os
from typing import Any



def run_extract_text_from_html_bytes(html_bytes: bytes) -> str | None:
    from cs336_data.extract_text import extract
    return extract(html_bytes)


def run_identify_language(text: str) -> tuple[Any, float]:
    from cs336_data.extract_text import identify_language
    return identify_language(text)


def run_mask_emails(text: str) -> tuple[str, int]:
    from cs336_data.extract_text import mask_emails
    return mask_emails(text)


def run_mask_phone_numbers(text: str) -> tuple[str, int]:
    from cs336_data.extract_text import mask_phone_numbers
    return mask_phone_numbers(text)


def run_mask_ips(text: str) -> tuple[str, int]:
    from cs336_data.extract_text import mask_ip
    return mask_ip(text)


def run_classify_nsfw(text: str) -> tuple[Any, float]:
    from cs336_data.extract_text import NSFW
    return NSFW(text)


def run_classify_toxic_speech(text: str) -> tuple[Any, float]:
    from cs336_data.extract_text import hate_speech
    return hate_speech(text)


def run_classify_quality(text: str) -> tuple[Any, float]:
    from cs336_data.extract_text import classify_quality
    return classify_quality(text)


def run_gopher_quality_filter(text: str) -> bool:
    from cs336_data.extract_text import gopher
    return gopher(text)


def run_exact_line_deduplication(
    input_files: list[os.PathLike], output_directory: os.PathLike
):
    from cs336_data.deduplication import exact_deduplicate
    exact_deduplicate(input_files, output_directory)


def run_minhash_deduplication(
    input_files: list[os.PathLike],
    num_hashes: int,
    num_bands: int,
    ngrams: int,
    jaccard_threshold: float,
    output_directory: os.PathLike,
):
    from cs336_data.deduplication import LSH_hash
    LSH_hash(input_files, num_hashes, num_bands, ngrams, jaccard_threshold, output_directory)
    
