from typing import List
from marker.schema import Page


def add_link_to_spans(blocks: List[Page]):
    for page in blocks:
        for block in page.blocks:
            for line in block.lines:
                for span in line.spans:
                    if span.link is not None:
                        span.text = f"[{span.text}]({span.link})"
