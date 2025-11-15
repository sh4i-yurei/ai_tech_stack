#!/usr/bin/env python3
"""
Minimal ingestion test: discover repo docs, chunk, embed via FastEmbed, and persist to FAISS.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import List, Optional, Sequence

from fastembed import TextEmbedding
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

SUPPORTED_SUFFIXES = (".md", ".txt", ".py")


class FastEmbedWrapper(Embeddings):
    """Adapter that exposes FastEmbed as a callable for LangChain."""

    def __init__(
        self,
        model_name: str = "BAAI/bge-small-en-v1.5",
        cache_dir: str = ".cache/fastembed",
    ) -> None:
        cache_path = Path(cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)
        snapshot = self._find_snapshot(cache_path)
        init_kwargs = {}
        if snapshot:
            init_kwargs["specific_model_path"] = snapshot
        self.model = TextEmbedding(model_name=model_name, cache_dir=str(cache_path), **init_kwargs)

    def _embed(self, texts: Sequence[str]) -> List[List[float]]:
        return [list(vec) for vec in self.model.embed(list(texts))]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embed(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._embed([text])[0]

    def __call__(self, texts: Sequence[str]) -> List[List[float]]:
        return self._embed(texts)

    def _find_snapshot(self, cache_path: Path) -> Optional[str]:
        """Return path to existing HF snapshot to support offline runs."""
        for model_dir in sorted(cache_path.glob("models--*bge-small-en-v1.5*")):
            snapshots_root = model_dir / "snapshots"
            if not snapshots_root.exists():
                continue
            for snapshot_dir in sorted(snapshots_root.glob("*"), reverse=True):
                if (snapshot_dir / "model_optimized.onnx").exists():
                    return str(snapshot_dir)
        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest repo docs into a FAISS index.")
    parser.add_argument(
        "--source",
        default="docs",
        help="Directory to scan for files (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        default="faiss_index",
        help="Directory where the FAISS index will be saved (default: %(default)s)",
    )
    return parser.parse_args()


def discover_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            files.append(path)
    return sorted(files)


def read_file(path: Path) -> str:
    try:
        data = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    normalized = data.replace("\r\n", "\n").replace("\r", "\n")
    normalized = "\n".join(line.rstrip() for line in normalized.splitlines())
    return normalized.strip()


def main() -> None:
    args = parse_args()
    repo_root = Path.cwd()
    source_dir = (repo_root / args.source).resolve()
    if not source_dir.exists():
        raise SystemExit(f"Source directory not found: {source_dir}")

    files = discover_files(source_dir)
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

    texts: List[str] = []
    metadatas = []
    files_processed = 0
    total_chunks = 0
    for file_path in files:
        text = read_file(file_path)
        if not text:
            continue
        chunks = splitter.split_text(text)
        if not chunks:
            continue
        rel_path = os.path.relpath(file_path, repo_root)
        for idx, chunk in enumerate(chunks, start=1):
            texts.append(chunk)
            metadatas.append({"source": rel_path, "chunk_id": idx})
        files_processed += 1
        total_chunks += len(chunks)

    if not texts:
        raise SystemExit("No chunks generated. Ensure the source directory has supported files.")

    embedding_model = FastEmbedWrapper()
    vectorstore = FAISS.from_texts(
        texts=texts,
        embedding=embedding_model,
        metadatas=metadatas,
    )

    output_dir = (repo_root / args.output).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(output_dir))

    print(f"Files processed: {files_processed}")
    print(f"Chunks created: {total_chunks}")
    print(f"FAISS index saved to: {output_dir}")

    # TODO: Add multiprocessing for larger repositories.
    # TODO: Support vectorstore backends other than FAISS.


if __name__ == "__main__":
    main()
