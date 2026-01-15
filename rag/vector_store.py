import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
from pathlib import Path
import json


class TFTVectorStore:
    """롤체 전략을 위한 Vector Store (ChromaDB)"""
    
    def __init__(
        self,
        collection_name: str = "tft_strategies",
        persist_directory: str = "./vector_db",
        embedding_model: str = "sentence-transformers/xlm-r-100langs-bert-base-nli-stsb-mean-tokens"
    ):
        """
        Args:
            collection_name: 컬렉션 이름
            persist_directory: DB 저장 경로
            embedding_model: 임베딩 모델 (한국어 지원)
        """
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # ChromaDB 클라이언트 초기화
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory)
        )
        
        # 컬렉션 가져오기 또는 생성
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"기존 컬렉션 '{collection_name}' 로드됨")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"새 컬렉션 '{collection_name}' 생성됨")
        
        # 임베딩 모델 로드
        print(f"임베딩 모델 로드 중: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        print("임베딩 모델 로드 완료")
    
    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        """텍스트를 임베딩 벡터로 변환"""
        embeddings = self.embedding_model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return embeddings.tolist()
    
    def add_chunks(self, chunks: List[Dict]):
        """
        청크를 Vector Store에 추가
        
        Args:
            chunks: [{"id": "...", "text": "...", "metadata": {...}}, ...]
        """
        if not chunks:
            print("추가할 청크가 없습니다.")
            return
        
        ids = [chunk['id'] for chunk in chunks]
        texts = [chunk['text'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        
        # 메타데이터를 문자열로 변환 (ChromaDB 요구사항)
        for metadata in metadatas:
            for key, value in metadata.items():
                if isinstance(value, list):
                    metadata[key] = json.dumps(value, ensure_ascii=False)
        
        # 임베딩 생성
        print(f"{len(texts)}개 청크 임베딩 생성 중...")
        embeddings = self._embed_texts(texts)
        
        # Vector Store에 추가
        print("Vector Store에 추가 중...")
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        print(f"{len(chunks)}개 청크 추가 완료")
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        쿼리로 관련 청크 검색
        
        Args:
            query: 검색 쿼리
            n_results: 반환할 결과 개수
            filters: 메타데이터 필터 (예: {"game_stage": "3-2"})
            
        Returns:
            검색 결과 리스트
        """
        # 쿼리 임베딩
        query_embedding = self._embed_texts([query])[0]
        
        # 검색 파라미터
        search_kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": n_results
        }
        
        # 필터 적용 (ChromaDB where 문법)
        if filters:
            where_clause = {}
            for key, value in filters.items():
                where_clause[key] = value
            search_kwargs["where"] = where_clause
        
        # 검색 실행
        results = self.collection.query(**search_kwargs)
        
        # 결과 포맷팅
        formatted_results = []
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i].copy()
            
            # JSON 문자열을 리스트로 변환
            for key, value in metadata.items():
                if isinstance(value, str) and value.startswith('['):
                    try:
                        metadata[key] = json.loads(value)
                    except:
                        pass
            
            formatted_results.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': metadata,
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict:
        """컬렉션 통계 정보"""
        count = self.collection.count()
        return {
            'collection_name': self.collection_name,
            'total_chunks': count,
            'persist_directory': str(self.persist_directory)
        }
    
    def delete_collection(self):
        """컬렉션 삭제 (주의!)"""
        self.client.delete_collection(name=self.collection_name)
        print(f"컬렉션 '{self.collection_name}' 삭제됨")


# 사용 예시
if __name__ == "__main__":
    # Vector Store 초기화
    vector_store = TFTVectorStore()
    
    # 테스트 청크
    test_chunks = [
        {
            'id': 'test_001',
            'text': '2-1에서는 연패 전략을 가져가세요. 야스오가 나오면 픽업하세요.',
            'metadata': {
                'season': '시즌13',
                'patch': '13.24',
                'game_stage': '2-1',
                'strategy_type': '연패',
                'key_champions': ['야스오'],
                'difficulty': '초보'
            }
        },
        {
            'id': 'test_002',
            'text': '3-2가 되면 레벨 6을 올려야 합니다. 골드 50 이상이면 리롤을 고려하세요.',
            'metadata': {
                'season': '시즌13',
                'patch': '13.24',
                'game_stage': '3-2',
                'strategy_type': '레벨링',
                'key_champions': [],
                'difficulty': '초보'
            }
        }
    ]
    
    # 청크 추가
    vector_store.add_chunks(test_chunks)
    
    # 통계 출력
    stats = vector_store.get_collection_stats()
    print(f"\n=== 컬렉션 통계 ===")
    print(stats)
    
    # 검색 테스트
    print(f"\n=== 검색 테스트 ===")
    results = vector_store.search(
        query="2-1에서 뭐 해야 해?",
        n_results=2
    )
    
    for i, result in enumerate(results):
        print(f"\n결과 {i+1}:")
        print(f"텍스트: {result['text']}")
        print(f"단계: {result['metadata']['game_stage']}")
        print(f"전략: {result['metadata']['strategy_type']}")
