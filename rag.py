import os
import shutil
import tempfile
from pathlib import Path
import chromadb
from git import Repo
from sentence_transformers import SentenceTransformer


# ============================================================
# RAG CONFIGURATION
# ============================================================

# rag.py is in:
# Autonomous Github Code Review Agent/
#
# Therefore .parent is the project root.

BASE_DIR = Path(__file__).resolve().parent

VECTOR_DB_PATH = BASE_DIR / "chroma_db"

COLLECTION_NAME = "github_code"

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2"
)


# ============================================================
# INITIALIZE EMBEDDING MODEL
# ============================================================

print()
print("Loading embedding model...")

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)

print(
    "Embedding model loaded:",
    EMBEDDING_MODEL
)


# ============================================================
# INITIALIZE CHROMADB
# ============================================================

chroma_client = chromadb.PersistentClient(
    path=str(VECTOR_DB_PATH)
)

collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME
)


# ============================================================
# FILE EXTENSIONS TO INDEX
# ============================================================

SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".cs",
    ".swift",
    ".kt",
    ".kts",
    ".sql",
    ".html",
    ".css",
    ".scss",
    ".json",
    ".yaml",
    ".yml",
    ".md",
    ".txt"
}


# ============================================================
# DIRECTORIES TO IGNORE
# ============================================================

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".idea",
    ".pytest_cache",
    ".mypy_cache",
    "chroma_db",
    "dist",
    "build"
}


# ============================================================
# PREPARE REPOSITORY
# ============================================================

def prepare_repository(repository_input):
    """
    Accept either:

    1. A local repository path
    2. A GitHub/Git repository URL

    If a URL is supplied, the repository is cloned
    into a temporary directory.
    """

    repository_input = repository_input.strip()

    # Remove accidental surrounding quotes.
    repository_input = repository_input.strip('"').strip("'")

    # ========================================================
    # LOCAL REPOSITORY
    # ========================================================

    if not repository_input.startswith(
        ("http://", "https://")
    ):

        repository_path = Path(
            repository_input
        ).expanduser().resolve()

        if not repository_path.exists():

            raise FileNotFoundError(
                f"Repository not found: "
                f"{repository_path}"
            )

        if not repository_path.is_dir():

            raise NotADirectoryError(
                f"Repository path is not a directory: "
                f"{repository_path}"
            )

        print()
        print(
            "Using local repository:"
        )

        print(
            repository_path
        )

        return repository_path, None

    # ========================================================
    # REMOTE GIT REPOSITORY
    # ========================================================

    print()
    print(
        "Git repository URL detected."
    )

    print(
        "Cloning repository..."
    )

    temporary_directory = Path(
        tempfile.mkdtemp(
            prefix="rag_repo_"
        )
    )

    try:

        Repo.clone_from(
            repository_input,
            temporary_directory
        )

    except Exception as e:

        shutil.rmtree(
            temporary_directory,
            ignore_errors=True
        )

        raise RuntimeError(
            f"Could not clone repository: {e}"
        )

    print(
        "Repository cloned successfully."
    )

    print(
        "Temporary repository:"
    )

    print(
        temporary_directory
    )

    return (
        temporary_directory,
        temporary_directory
    )


# ============================================================
# READ FILE
# ============================================================

def read_file(file_path):
    """
    Read a source file safely.
    """

    try:

        return file_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

    except Exception as e:

        print(
            f"Could not read {file_path}: {e}"
        )

        return None


# ============================================================
# SPLIT CODE INTO CHUNKS
# ============================================================

def chunk_code(
    content,
    chunk_size=1200,
    overlap=200
):
    """
    Split source code into overlapping chunks.

    chunk_size and overlap are measured
    in characters.
    """

    if not content:

        return []

    chunks = []

    start = 0

    content_length = len(content)

    while start < content_length:

        end = start + chunk_size

        chunk = content[start:end]

        if chunk.strip():

            chunks.append(
                chunk
            )

        start = end - overlap

        if start < 0:

            start = 0

    return chunks


# ============================================================
# FIND SOURCE FILES
# ============================================================

def find_source_files(
    repository_path
):
    """
    Find supported source files inside
    the repository.
    """

    repository_path = Path(
        repository_path
    )

    files = []

    for root, directories, filenames in os.walk(
        repository_path
    ):

        # Remove ignored directories.
        directories[:] = [
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
        ]

        for filename in filenames:

            file_path = (
                Path(root) / filename
            )

            if (
                file_path.suffix.lower()
                in SUPPORTED_EXTENSIONS
            ):

                files.append(
                    file_path
                )

    return files


# ============================================================
# INDEX REPOSITORY
# ============================================================

def index_repository(
    repository_input
):
    """
    Read repository files, split them into chunks,
    generate embeddings, and store them in ChromaDB.

    Supports both local repositories and Git URLs.
    """

    print()
    print(
        "========================================"
    )

    print(
        "RAG: INDEXING REPOSITORY"
    )

    print(
        "========================================"
    )

    # --------------------------------------------------------
    # Prepare local or remote repository
    # --------------------------------------------------------

    repository_path, temporary_directory = (
        prepare_repository(
            repository_input
        )
    )

    try:

        # ----------------------------------------------------
        # Find files
        # ----------------------------------------------------

        files = find_source_files(
            repository_path
        )

        print()
        print(
            "Files found:",
            len(files)
        )

        # ----------------------------------------------------
        # Prepare documents
        # ----------------------------------------------------

        documents = []

        metadatas = []

        ids = []

        document_id = 0

        # ----------------------------------------------------
        # Process files
        # ----------------------------------------------------

        for file_path in files:

            content = read_file(
                file_path
            )

            if not content:

                continue

            chunks = chunk_code(
                content
            )

            relative_path = (
                file_path.relative_to(
                    repository_path
                )
            )

            for chunk_number, chunk in enumerate(
                chunks
            ):

                documents.append(
                    chunk
                )

                metadatas.append({
                    "file": str(
                        relative_path
                    ),
                    "chunk": chunk_number
                })

                ids.append(
                    f"{relative_path}:"
                    f"{chunk_number}:"
                    f"{document_id}"
                )

                document_id += 1

        # ----------------------------------------------------
        # Check documents
        # ----------------------------------------------------

        if not documents:

            print()
            print(
                "No documents found to index."
            )

            return 0

        print()
        print(
            "Code chunks created:",
            len(documents)
        )

        # ----------------------------------------------------
        # Create embeddings
        # ----------------------------------------------------

        print()
        print(
            "Creating embeddings..."
        )

        embeddings = embedding_model.encode(
            documents,
            show_progress_bar=True
        )

        # ----------------------------------------------------
        # Store in ChromaDB
        # ----------------------------------------------------

        print()
        print(
            "Storing embeddings in ChromaDB..."
        )

        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings.tolist(),
            metadatas=metadatas
        )

        # ----------------------------------------------------
        # Success
        # ----------------------------------------------------

        print()
        print(
            "========================================"
        )

        print(
            "Repository indexing complete."
        )

        print(
            "========================================"
        )

        print(
            "Chunks stored:",
            len(documents)
        )

        return len(documents)

    finally:

        # ----------------------------------------------------
        # Remove temporary cloned repository
        # ----------------------------------------------------

        if temporary_directory:

            print()
            print(
                "Removing temporary repository..."
            )

            shutil.rmtree(
                temporary_directory,
                ignore_errors=True
            )

            print(
                "Temporary repository removed."
            )


# ============================================================
# SEARCH REPOSITORY
# ============================================================

def search_repository(
    query,
    top_k=5
):
    """
    Search the vector database for code
    semantically related to the query.
    """

    print()
    print(
        "========================================"
    )

    print(
        "RAG: SEMANTIC SEARCH"
    )

    print(
        "========================================"
    )

    print(
        "Query:",
        query
    )

    # --------------------------------------------------------
    # Create query embedding
    # --------------------------------------------------------

    query_embedding = embedding_model.encode(
        [query]
    )[0]

    # --------------------------------------------------------
    # Search ChromaDB
    # --------------------------------------------------------

    results = collection.query(
        query_embeddings=[
            query_embedding.tolist()
        ],
        n_results=top_k
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    retrieved = []

    # --------------------------------------------------------
    # Process results
    # --------------------------------------------------------

    for index, document in enumerate(
        documents
    ):

        metadata = (
            metadatas[index]
            if index < len(metadatas)
            else {}
        )

        distance = (
            distances[index]
            if index < len(distances)
            else None
        )

        retrieved.append({
            "content": document,
            "file": metadata.get(
                "file"
            ),
            "chunk": metadata.get(
                "chunk"
            ),
            "distance": distance
        })

    print()
    print(
        "Relevant chunks found:",
        len(retrieved)
    )

    for result in retrieved:

        print(
            "File:",
            result["file"]
        )

        print(
            "Chunk:",
            result["chunk"]
        )

    return retrieved


# ============================================================
# BUILD RAG CONTEXT
# ============================================================

def build_rag_context(
    query,
    top_k=5
):
    """
    Retrieve relevant repository code and
    format it for the AI reviewer.
    """

    results = search_repository(
        query=query,
        top_k=top_k
    )

    if not results:

        return (
            "No relevant repository context "
            "was found."
        )

    context = []

    context.append(
        "RELEVANT REPOSITORY CONTEXT"
    )

    context.append(
        "========================================"
    )

    for result in results:

        context.append(
            f"\nFILE: {result['file']}"
        )

        context.append(
            f"CHUNK: {result['chunk']}"
        )

        context.append(
            "----------------------------------------"
        )

        context.append(
            result["content"]
        )

    return "\n".join(
        context
    )


# ============================================================
# TEST RAG
# ============================================================

if __name__ == "__main__":

    print()
    print(
        "========================================"
    )

    print(
        "RAG TEST"
    )

    print(
        "========================================"
    )

    repository = input(
        "Enter repository path or Git URL: "
    ).strip()

    if not repository:

        print(
            "Repository path or URL is required."
        )

        raise SystemExit(1)

    # --------------------------------------------------------
    # Index repository
    # --------------------------------------------------------

    index_repository(
        repository
    )

    # --------------------------------------------------------
    # Search repository
    # --------------------------------------------------------

    query = input(
        "\nEnter search query: "
    ).strip()

    if query:

        context = build_rag_context(
            query,
            top_k=5
        )

        print()
        print(
            "========================================"
        )

        print(
            "RETRIEVED RAG CONTEXT"
        )

        print(
            "========================================"
        )

        print(
            context
        )