import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Project Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data" / "processed"
VECTOR_DB_DIR = BASE_DIR / "vector_db"

# Chunking Configuration
CHUNK_SIZE = 400  # tokens
CHUNK_OVERLAP = 75  # tokens

# Retrieval Configuration
TOP_K = 5  # 검색할 chunk 개수
RERANK_TOP_K = 3  # 재정렬 후 최종 선택 개수

# Vector Store
COLLECTION_NAME = "tft_strategies"
EMBEDDING_MODEL = "sentence-transformers/xlm-r-100langs-bert-base-nli-stsb-mean-tokens"  # 한국어 지원
EMBEDDING_DEVICE = "cpu"  # "cuda" for GPU, "cpu" for CPU

# Game Stages
GAME_STAGES = [
    "2-1", "2-2", "2-3", "2-4", "2-5", "2-6", "2-7",
    "3-1", "3-2", "3-3", "3-4", "3-5", "3-6", "3-7",
    "4-1", "4-2", "4-3", "4-4", "4-5", "4-6", "4-7",
    "5-1", "5-2", "5-3", "5-4", "5-5", "5-6", "5-7"
]

# Strategy Types
STRATEGY_TYPES = [
    "리롤",
    "레벨링",
    "연승",
    "연패",
    "전환",
    "고정",
    "아이템 판단",
    "기물 선택"
]

# Current Season & Patch
CURRENT_SEASON = "시즌13"
CURRENT_PATCH = "13.24"
