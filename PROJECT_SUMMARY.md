# 🎮 롤체 RAG 시스템 - 프로젝트 요약

## 📋 프로젝트 개요

**목표**: 롤체 초보자들이 유튜브 영상을 단순 따라하기가 아닌, 현재 게임 상황에 맞는 실시간 전략 조언을 받을 수 있도록 지원

**핵심 기능**:
- 유튜브 롤체 전략 영상 자동 처리
- 게임 상황 기반 지능형 전략 검색
- Claude AI를 활용한 맞춤형 조언 생성

## 🏗️ 시스템 아키텍처

```
[유튜브 영상] → [자막 추출] → [전략 단위 분할] → [벡터 임베딩]
                                                           ↓
[사용자 질문] → [쿼리 분석] → [하이브리드 검색] → [Claude API] → [답변]
                 ↓              ↓
            [필터 생성]    [재정렬]
```

## 📁 파일 구조

```
tft_rag/
├── config.py                    # 전체 시스템 설정
├── main.py                      # 메인 실행 파일
├── quick_start.py              # 빠른 시작 데모
│
├── data/                       # 데이터 처리
│   ├── youtube_processor.py   # 유튜브 자막 추출/정제
│   ├── chunker.py             # 전략 단위 분할
│   └── metadata_schema.py     # 데이터 스키마 정의
│
├── rag/                        # RAG 시스템
│   ├── vector_store.py        # ChromaDB 벡터 저장소
│   ├── retriever.py           # 하이브리드 검색 + 재정렬
│   └── generator.py           # Claude API 답변 생성
│
└── docs/
    ├── README.md              # 전체 문서
    └── GETTING_STARTED_KR.md  # 시작 가이드
```

## 🎯 RAG 담당자 핵심 구현 사항

### 1. 데이터 전처리 (data/)
```python
# chunker.py - 핵심 로직
- 전략 단위 정의 (게임 단계별 분할)
- 메타데이터 자동 태깅
  - game_stage 추출 (2-1, 3-2 등)
  - strategy_type 감지 (리롤, 연패 등)
  - key_champions 추출
```

### 2. 벡터 저장소 (rag/vector_store.py)
```python
# ChromaDB 사용
- 한국어 임베딩 모델
- 메타데이터 기반 필터링 지원
- Persistent 저장
```

### 3. 검색 엔진 (rag/retriever.py)
```python
# 하이브리드 검색
1. 쿼리 분석 → 필터 생성
2. 벡터 검색 + 메타데이터 필터
3. 재정렬 (최신 패치, 난이도, 거리 점수)
4. Top-K 선택
```

### 4. 답변 생성 (rag/generator.py)
```python
# Claude API
- 환각 방지 시스템 프롬프트
- 게임 상태 컨텍스트 포함
- 출처 정보 추적
```

## 🔑 핵심 설계 결정

### 메타데이터 스키마
```python
{
    "season": "시즌13",           # 시즌 정보
    "patch": "13.24",            # 패치 버전
    "game_stage": "3-2",         # 게임 단계 (필터링)
    "strategy_type": "리롤",      # 전략 유형 (필터링)
    "composition_name": "6도전자", # 조합명
    "key_champions": [...],       # 핵심 챔피언
    "difficulty": "초보",         # 난이도 (재정렬)
    "video_source": "...",        # 출처 (저작권)
}
```

### 청킹 전략
- **크기**: 300-500 토큰
- **오버랩**: 50-100 토큰
- **기준**: 전략 단위 (게임 단계 + 전략 유형)

### 검색 전략
```python
# 3단계 검색
1. 필터링: game_stage, strategy_type
2. 벡터 검색: 의미적 유사도
3. 재정렬: 최신 패치, 초보자 우선, 거리 점수
```

## 🚀 실행 방법

### 설치
```bash
# Windows
install.bat

# Mac/Linux
./install.sh
```

### 빠른 시작
```bash
python quick_start.py
```

### 대화형 모드
```bash
python main.py --mode interactive
```

### 영상 처리
```bash
python main.py --mode process \
  --video_url "https://youtube.com/..." \
  --metadata_file example_metadata.json
```

## 📊 성능 지표

**목표 성능**:
- 검색 정확도: 85%+ (Top-3)
- 응답 시간: < 3초
- 청크 커버리지: 90%+

**평가 방법**:
1. 질문 → 답변 → 사용된 청크 확인
2. 잘못된 청크 → 원인 분석 → 개선
3. A/B 테스트: 필터 유무 비교

## 🔧 개선 포인트

### 단기 (MVP)
- [x] 기본 RAG 파이프라인
- [x] 메타데이터 필터링
- [x] Claude API 연동
- [ ] 10개 영상 처리
- [ ] 사용자 테스트

### 중기
- [ ] BM25 하이브리드 검색
- [ ] 크로스 인코더 재정렬
- [ ] 패치 자동 업데이트
- [ ] 챔피언 목록 DB

### 장기
- [ ] 파인튜닝 임베딩 모델
- [ ] 실시간 게임 API 연동
- [ ] 멀티 유저 지원

## 🎓 학습 자료

### RAG 개념
- Retrieval: 관련 정보 검색
- Augmented: 검색 정보로 강화
- Generation: 답변 생성

### 핵심 기술
1. **Vector Embeddings**: 텍스트 → 숫자 벡터
2. **Semantic Search**: 의미 기반 검색
3. **Metadata Filtering**: 조건부 검색
4. **Reranking**: 검색 결과 재정렬
5. **Prompt Engineering**: AI 답변 품질 향상

## 📝 팀 역할

**Backend (김지아)**:
- API 서버 구축
- DB 관리
- 프론트엔드 연동

**RAG (권기범)**:
- 데이터 전처리
- 검색 엔진 구현
- 프롬프트 최적화
- 성능 평가

## 🔗 참고 자료

- LangChain 문서
- ChromaDB 문서
- Anthropic API 문서
- TFT 공식 정보

---

**Created by**: Backend 김지아, RAG 권기범
**Version**: 1.0.0
**Date**: 2025-01-16
