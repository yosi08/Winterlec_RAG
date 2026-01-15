#!/bin/bash

echo "======================================"
echo "롤체 RAG 시스템 설치 스크립트"
echo "======================================"
echo ""

# Python 버전 확인
echo "[1/5] Python 버전 확인 중..."
python --version

if [ $? -ne 0 ]; then
    echo "❌ Python이 설치되어 있지 않습니다."
    echo "Python 3.8 이상을 설치해주세요."
    exit 1
fi

# 가상환경 생성
echo ""
echo "[2/5] 가상환경 생성 중..."
python -m venv venv

if [ $? -eq 0 ]; then
    echo "✓ 가상환경 생성 완료"
else
    echo "❌ 가상환경 생성 실패"
    exit 1
fi

# 가상환경 활성화
echo ""
echo "[3/5] 가상환경 활성화 중..."
source venv/bin/activate

if [ $? -eq 0 ]; then
    echo "✓ 가상환경 활성화 완료"
else
    echo "❌ 가상환경 활성화 실패"
    exit 1
fi

# 패키지 설치
echo ""
echo "[4/5] 패키지 설치 중..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ 패키지 설치 완료"
else
    echo "❌ 패키지 설치 실패"
    exit 1
fi

# .env 파일 확인
echo ""
echo "[5/5] 설정 파일 확인 중..."
if [ ! -f .env ]; then
    echo "⚠ .env 파일이 없습니다."
    echo ".env.template을 .env로 복사합니다..."
    cp .env.template .env
    echo ""
    echo "📝 다음 단계:"
    echo "1. .env 파일을 열어서 ANTHROPIC_API_KEY를 입력하세요"
    echo "2. https://console.anthropic.com/에서 API 키를 발급받을 수 있습니다"
    echo ""
else
    echo "✓ .env 파일 존재함"
fi

echo ""
echo "======================================"
echo "설치 완료!"
echo "======================================"
echo ""
echo "다음 명령어로 시작하세요:"
echo ""
echo "# 빠른 시작 데모"
echo "python quick_start.py"
echo ""
echo "# 대화형 모드"
echo "python main.py --mode interactive"
echo ""
echo "자세한 내용은 README.md를 참고하세요."
echo "======================================"
