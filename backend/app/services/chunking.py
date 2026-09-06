import re
from typing import List, Dict


MAX_CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150


def is_heading(line: str) -> bool:
    line = line.strip()

    if not line:
        return False

    if len(line) > 100:
        return False

    # Example: VACATION POLICY
    if line.isupper() and len(line.split()) <= 10:
        return True

    # Example:
    # 1. Introduction
    # 2.3 Employee Benefits
    numbered_heading = re.match(
        r"^\d+(\.\d+)*[\.\)]?\s+.+$",
        line
    )

    if numbered_heading:
        return True

    # Example: Vacation Policy
    words = line.split()

    if 1 <= len(words) <= 8:
        capitalized_words = sum(
            1 for word in words
            if word[:1].isupper()
        )

        if capitalized_words >= max(1, len(words) - 1):
            return True

    return False


def extract_sections(text: str) -> List[Dict]:
    lines = text.splitlines()

    sections = []

    current_title = "Untitled Section"
    current_content = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if is_heading(line):

            if current_content:
                sections.append({
                    "title": current_title,
                    "text": " ".join(current_content)
                })

            current_title = line
            current_content = []

        else:
            current_content.append(line)

    if current_content:
        sections.append({
            "title": current_title,
            "text": " ".join(current_content)
        })

    return sections


def split_large_text(
    text: str,
    max_size: int = MAX_CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP
) -> List[str]:

    if len(text) <= max_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + max_size, len(text))

        chunk = text[start:end]

        # Try to finish the chunk at a sentence boundary
        if end < len(text):
            last_period = chunk.rfind(". ")

            if last_period > max_size * 0.5:
                end = start + last_period + 1
                chunk = text[start:end]

        chunks.append(chunk.strip())

        # Finished the document
        if end >= len(text):
            break

        # Approximate overlap position
        overlap_start = max(start, end - overlap)

        # Try to begin the next chunk at the start of a sentence
        previous_period = text.rfind(
            ". ",
            start,
            overlap_start
        )

        if previous_period != -1:
            new_start = previous_period + 2
        else:
            # Fallback: begin at a word boundary
            next_space = text.find(" ", overlap_start, end)

            if next_space != -1:
                new_start = next_space + 1
            else:
                new_start = end

        # Safety check
        if new_start <= start:
            new_start = end

        start = new_start

    return chunks

def create_chunks(
    text: str,
    filename: str = "unknown.pdf"
) -> List[Dict]:
    """
    Create final chunks from extracted PDF text.
    """

    sections = extract_sections(text)

    chunks = []
    chunk_index = 0

    for section in sections:
        title = section["title"]
        section_text = section["text"]

        smaller_chunks = split_large_text(section_text)

        for part in smaller_chunks:

            chunk_text = f"{title}\n\n{part}"

            chunks.append({
                "chunk_id": chunk_index,
                "filename": filename,
                "section": title,
                "text": chunk_text
            })

            chunk_index += 1

    return chunks


if __name__ == "__main__":

    sample_text = """
VACATION POLICY

Employees receive 20 paid vacation days every year.
Vacation requests must be submitted two weeks in advance.
Unused vacation days may be carried over to the following year.

SICK LEAVE

Employees receive 10 paid sick days every year.
Medical documentation may be required for extended sick leave.

REMOTE WORK POLICY

Employees may work remotely up to three days per week.
Remote work must be approved by the employee's manager.
Employees must follow company security policies while working remotely.
"""

    chunks = create_chunks(
        sample_text,
        filename="employee_handbook.pdf"
    )

    for chunk in chunks:
        print("\nCHUNK ID:", chunk["chunk_id"])
        print("FILE:", chunk["filename"])
        print("SECTION:", chunk["section"])
        print("TEXT:")
        print(chunk["text"])
        print("-" * 60)