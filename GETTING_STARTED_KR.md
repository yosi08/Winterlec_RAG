# 🎮 롤체 RAG 시스템 - 시작 가이드

## 📦 설치 방법

### Windows 사용자
1. `install.bat` 파일을 더블클릭하여 실행
2. 설치가 완료되면 `.env` 파일을 열어서 API 키 입력
3. 완료!

### Mac/Linux 사용자
```bash
chmod +x install.sh
./install.sh
```

### 수동 설치
```bash
# 1. 가상환경 생성
python -m venv venv

# 2. 가상환경 활성화
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. .env 파일 설정
cp .env.template .env
# .env 파일을 열어서 API 키 입력
```

## 🚀 빠른 시작

### 1단계: 데모 실행
```bash
python quick_start.py
```
이 명령어는:
- 시스템 초기화
- 테스트 데이터 추가
- 샘플 질문 실행

### 2단계: 대화형 모드
```bash
python main.py --mode interactive
```

대화 예시:
```
질문> 2-1에서 뭐 해야 해?
답변> [AI가 전략 조언 제공]

질문> 3-2에서 리롤해야 할까요?
답변> [현재 상황에 맞는 조언]
```

## 📝 실제 데이터 추가하기

### 유튜브 영상 처리
```bash
python main.py --mode process \
  --video_url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --metadata_file example_metadata.json
```

### 메타데이터 파일 수정
`example_metadata.json`을 열어서 실제 정보로 수정:
```json
{
  "season": "시즌13",
  "patch": "13.24",
  "composition_name": "6도전자",
  "difficulty": "초보"
}
```

## 🎯 주요 명령어

### 통계 확인
```bash
python main.py --mode stats
```

### 단일 질문
```bash
python main.py --mode query --question "초반 전략 알려줘"
```

### 대화형 모드 (추천)
```bash
python main.py --mode interactive
```

## ⚙️ 커스터마이징

### config.py 수정
```python
# 검색 결과 개수 조정
TOP_K = 5              # 초기 검색 결과
RERANK_TOP_K = 3       # 최종 선택 개수

# 청크 크기 조정
CHUNK_SIZE = 400       # 더 크게 하면 컨텍스트 많아짐
CHUNK_OVERLAP = 75     # 청크 간 겹침
```

## 🔧 문제 해결

### Q: "ANTHROPIC_API_KEY가 설정되지 않았습니다"
**A**: `.env` 파일을 열어서 다음과 같이 수정:
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

### Q: "자막을 가져올 수 없습니다"
**A**: 영상에 한국어 자막이 있는지 확인하세요

### Q: "모듈을 찾을 수 없습니다"
**A**: 가상환경이 활성화되었는지 확인:
```bash
# 가상환경 활성화
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# 패키지 재설치
pip install -r requirements.txt
```

## 📚 더 알아보기

- **README.md**: 전체 문서
- **quick_start.py**: 데모 코드
- **example_metadata.json**: 메타데이터 예시

## 💡 팁

1. **처음에는 데모로 시작**: `python quick_start.py`
2. **대화형 모드 사용**: 가장 직관적
3. **여러 영상 추가**: 데이터가 많을수록 답변 품질 향상
4. **메타데이터 정확히 입력**: 검색 정확도에 영향

## 🎓 학습 추천 순서

1. ✅ `quick_start.py` 실행해보기
2. ✅ 대화형 모드로 질문해보기
3. ✅ 실제 유튜브 영상 1개 처리해보기
4. ✅ 코드 살펴보기 (`main.py`, `rag/retriever.py`)
5. ✅ 커스터마이징 시도

## 📧 도움이 필요하신가요?

- GitHub Issues
- [이메일]
- [Discord/Slack]

---
즐거운 롤체 되세요! 🎮✨
