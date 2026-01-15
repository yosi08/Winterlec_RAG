# 롤체(TFT) RAG 시스템

롤체 초보자를 위한 AI 전략 도우미 시스템입니다. 유튜브 영상에서 전략을 추출하고, 현재 게임 상황에 맞는 조언을 제공합니다.

## 📋 주요 기능

1. **유튜브 영상 처리**
   - 자막 자동 추출
   - 전략 단위로 분할
   - 메타데이터 자동 태깅

2. **지능형 검색**
   - Hybrid Search (벡터 + 메타데이터)
   - 게임 상태 기반 필터링
   - 최신 패치 우선 재정렬

3. **맞춤형 답변 생성**
   - Claude API 활용
   - 초보자 친화적 설명
   - 출처 정보 제공

## 🚀 설치 방법

### 1. 저장소 클론
```bash
git clone <repository_url>
cd tft_rag
```

### 2. 가상환경 생성 (권장)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. API 키 설정
```bash
# .env.template을 .env로 복사
cp .env.template .env

# .env 파일 편집하여 API 키 입력
# ANTHROPIC_API_KEY=your_actual_api_key
```

## 📖 사용 방법

### 1️⃣ 유튜브 영상 처리 (데이터 수집)

```bash
python main.py --mode process \
  --video_url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --metadata_file metadata.json
```

**metadata.json 예시:**
```json
{
  "season": "시즌13",
  "patch": "13.24",
  "composition_name": "6도전자",
  "difficulty": "초보",
  "video_source": "유튜버명_영상ID"
}
```

### 2️⃣ 질문하기 (단일 질문)

```bash
python main.py --mode query \
  --question "3-2에서 리롤해야 할까요?"
```

### 3️⃣ 대화형 모드 (추천)

```bash
python main.py --mode interactive
```

실행 후:
```
롤체 RAG 시스템 - 대화형 모드
==================================================
질문을 입력하세요 (종료: 'exit' 또는 'quit')
==================================================

게임 상태 정보를 입력하시겠습니까? (y/n): y
현재 라운드 (예: 3-2): 3-2
레벨: 5
골드: 48
체력: 72

질문> 지금 리롤해야 할까요?
```

### 4️⃣ 시스템 통계 확인

```bash
python main.py --mode stats
```

## 📂 프로젝트 구조

```
tft_rag/
├── config.py              # 설정 파일
├── requirements.txt       # 패키지 의존성
├── main.py               # 메인 실행 파일
│
├── data/                 # 데이터 처리 모듈
│   ├── youtube_processor.py   # 유튜브 자막 추출
│   ├── chunker.py             # 텍스트 분할
│   └── metadata_schema.py     # 데이터 스키마
│
├── rag/                  # RAG 시스템 모듈
│   ├── vector_store.py        # ChromaDB 벡터 저장소
│   ├── retriever.py           # 검색 엔진
│   └── generator.py           # Claude API 답변 생성
│
└── vector_db/            # 벡터 DB 저장 경로 (자동 생성)
```

## 🔧 설정 커스터마이징

`config.py`에서 다음 설정을 조정할 수 있습니다:

```python
# Chunking 설정
CHUNK_SIZE = 400          # 청크 크기 (토큰)
CHUNK_OVERLAP = 75        # 오버랩 크기

# 검색 설정
TOP_K = 5                 # 초기 검색 결과 수
RERANK_TOP_K = 3          # 재정렬 후 최종 선택 수

# 임베딩 모델
EMBEDDING_MODEL = "sentence-transformers/xlm-r-100langs-bert-base-nli-stsb-mean-tokens"
```

## 💡 사용 예시

### 예시 1: 연패 전략 질문
```
질문> 연패 중인데 어떻게 해야 해요?

답변:
1. **지금 바로 해야 할 일**
   골드를 최대한 모으세요. 불필요한 리롤이나 레벨업은 피하고,
   4-1까지 골드를 50+ 유지하는 게 목표입니다.

2. **그 이유**
   연패 전략은 초반 약한 조합으로 골드를 모아서 중반에 강력하게
   전환하는 전략입니다. 지금 무리하게 강해지려 하면 골드만 낭비됩니다.

3. **추가 팁**
   - 체력이 30 이하로 떨어지면 최소한의 방어는 하세요
   - 좋은 아이템 조합이 나오면 보관하세요
   - 4-1에서 레벨 7-8로 올리고 한번에 리롤하세요

참고 출처:
1. 롤체유튜버_abc123 (3:24-5:18)
   단계: 3-2, 전략: 연패
```

### 예시 2: 리롤 타이밍 질문
```
질문> 3-2에서 골드 50인데 리롤 해야 할까요?

현재 상태: 야스오 2개, 요네 1개, 도전자 2 활성

답변:
1. **지금 바로 해야 할 일**
   리롤을 시작하세요! 야스오 2성 또는 요네 2성을 만드는 걸 목표로
   골드 30-40까지 써도 괜찮습니다.

2. **그 이유**
   이미 도전자 조합의 핵심 기물들이 있고, 골드도 충분합니다.
   3-2는 리롤 타이밍이 좋은 구간이며, 2성을 만들면 중반까지
   안정적으로 갈 수 있습니다.

3. **추가 팁**
   - 야스오나 요네 둘 중 하나만 집중하세요
   - 골드 20 이하로는 떨어뜨리지 마세요
   - 2성이 완성되면 레벨업으로 전환하세요
```

## 🔍 RAG 시스템 동작 원리

1. **데이터 수집**: 유튜브 영상 → 자막 추출 → 텍스트 정제
2. **전처리**: 전략 단위 분할 → 메타데이터 부착 → 벡터 임베딩
3. **검색**: 질문 분석 → 필터 생성 → 하이브리드 검색 → 재정렬
4. **생성**: 검색 결과 → 프롬프트 구성 → Claude API → 답변 생성

## 🎯 메타데이터 필드

각 전략 청크는 다음 메타데이터를 포함합니다:

| 필드 | 설명 | 예시 |
|------|------|------|
| season | 시즌 | "시즌13" |
| patch | 패치 버전 | "13.24" |
| game_stage | 게임 단계 | "3-2" |
| strategy_type | 전략 유형 | "리롤" |
| composition_name | 조합명 | "6도전자" |
| key_champions | 핵심 챔피언 | ["야스오", "요네"] |
| difficulty | 난이도 | "초보" |
| video_source | 출처 영상 | "유튜버명_abc123" |

## ⚙️ 고급 기능

### 커스텀 Retriever 만들기

```python
from rag.retriever import TFTRetriever
from rag.vector_store import TFTVectorStore

# Vector Store 초기화
vector_store = TFTVectorStore()

# 커스텀 Retriever
retriever = TFTRetriever(
    vector_store=vector_store,
    top_k=10,              # 더 많은 초기 검색 결과
    rerank_top_k=5         # 더 많은 최종 선택
)

# 검색
results = retriever.retrieve(
    query="초반 전략 추천해주세요",
    game_state=None
)
```

### 배치 처리

```python
from main import TFTRAGSystem

system = TFTRAGSystem()

# 여러 영상 한번에 처리
videos = [
    {
        "url": "https://youtube.com/watch?v=VIDEO1",
        "metadata": {"composition_name": "6도전자", "patch": "13.24"}
    },
    {
        "url": "https://youtube.com/watch?v=VIDEO2",
        "metadata": {"composition_name": "8탐험가", "patch": "13.24"}
    }
]

for video in videos:
    system.process_video(video["url"], video["metadata"])
```

## 🐛 문제 해결

### Q1: API 키 오류
```
ValueError: ANTHROPIC_API_KEY가 설정되지 않았습니다.
```
**해결**: `.env` 파일에 올바른 API 키를 입력했는지 확인하세요.

### Q2: 자막을 찾을 수 없음
```
자막을 가져올 수 없습니다
```
**해결**: 영상에 한국어 자막이 있는지 확인하세요. 없으면 자동 생성 자막이 사용됩니다.

### Q3: 검색 결과가 없음
```
관련된 전략을 찾을 수 없습니다.
```
**해결**: 먼저 `--mode stats`로 데이터가 저장되었는지 확인하세요.

### Q4: 임베딩 모델 다운로드 느림
첫 실행 시 임베딩 모델을 다운로드합니다 (~500MB). 인터넷 연결을 확인하세요.

## 📊 성능 최적화

1. **청크 크기 조정**: `config.CHUNK_SIZE`를 300-500 사이로 조정
2. **검색 수 조정**: `TOP_K`를 늘리면 정확도 ↑, 속도 ↓
3. **임베딩 모델 변경**: 더 빠른 모델로 교체 가능

## 🤝 기여 방법

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

This project is licensed under the MIT License.

## 👥 팀

- **Backend**: 김지아
- **RAG**: 권기범

## 📧 문의

프로젝트 관련 문의: [이메일 주소]

---

**주의**: 이 프로젝트는 교육 목적으로 제작되었습니다. 유튜브 영상 사용 시 저작권을 확인하세요.
