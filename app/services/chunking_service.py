
def fixed_size_chunking(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> list[str]:

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "Overlap must be non-negative and smaller than chunk size."
        )

    chunks = []

    start = 0
    step = chunk_size - overlap

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += step

    return chunks


def recursive_character_chunking(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> list[str]:

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "Overlap must be non-negative and smaller than chunk size."
        )

    separators = ["\n\n", "\n", ". ", " ", ""]

    def split_text(text: str, separators: list[str]) -> list[str]:

        if len(text) <= chunk_size:
            return [text] if text.strip() else []

        separator = separators[0]

        if separator == "":
            parts = [
                text[i:i + chunk_size]
                for i in range(0, len(text), chunk_size)
            ]
        else:
            parts = text.split(separator)

        chunks = []
        current = ""

        for part in parts:

            candidate = (
                current + separator + part
                if current else part
            )

            if len(candidate) <= chunk_size:
                current = candidate

            else:
                if current:
                    chunks.append(current)

                if len(part) > chunk_size:
                    remaining_separators = (
                        separators[separators.index(separator) + 1:]
                    )

                    if remaining_separators:
                        chunks.extend(
                            split_text(part, remaining_separators)
                        )
                    else:
                        chunks.extend([
                            part[i:i + chunk_size]
                            for i in range(0, len(part), chunk_size)
                        ])

                    current = ""

                else:
                    current = part

        if current:
            chunks.append(current)

        return chunks

    raw_chunks = split_text(text, separators)

    # Add overlap between consecutive chunks
    final_chunks = []

    for index, chunk in enumerate(raw_chunks):

        if index == 0:
            final_chunks.append(chunk.strip())
            continue

        previous_chunk = raw_chunks[index - 1]

        overlap_text = previous_chunk[-overlap:] if overlap else ""

        combined_chunk = overlap_text + chunk

        final_chunks.append(combined_chunk.strip())

    return [chunk for chunk in final_chunks if chunk]
