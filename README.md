# PyCon 2025 Demo - AI 채팅 롤플레잉 애플리케이션

OpenAI API를 활용한 Django 기반 AI 채팅 롤플레잉 웹 애플리케이션입니다. 사용자가 다양한 AI 캐릭터와 대화할 수 있는 채팅 세션을 생성하고 관리할 수 있습니다.

## 📋 주요 기능

- **🤖 AI 채팅**: OpenAI의 GPT 모델과 실시간 대화
- **📝 세션 관리**: 여러 채팅 세션 생성 및 관리
- **⚙️ 커스터마이징**: AI 모델, 온도(창의성), 최대 토큰 수 등 세부 설정 가능
- **💬 대화 히스토리**: 이전 대화 내용 저장 및 조회
- **🔐 사용자 인증**: 로그인 기반 개인화된 채팅 세션 관리

## 🚀 시작하기

### 사전 준비사항

1. **Python 3.13 이상** 설치되어 있어야 합니다.
   ```bash
   # Python 버전 확인
   python --version
   ```

2. **uv 설치** (빠른 Python 패키지 관리자)
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows (PowerShell)
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # 또는 pip로 설치
   pip install uv
   ```

### 🔧 설치 및 실행 방법

#### 1단계: 프로젝트 클론 (또는 다운로드)
```bash
# Git이 설치되어 있는 경우
git clone [프로젝트 URL]
cd pycon-2025-demo

# 또는 프로젝트 폴더로 이동
cd pycon-2025-demo
```

#### 2단계: 의존성 패키지 설치
```bash
# uv를 사용하여 모든 필요한 패키지 설치
uv sync
```

#### 3단계: OpenAI API 키 설정
```bash
# 환경 변수로 OpenAI API 키 설정
# macOS/Linux
export OPENAI_API_KEY="여기에_당신의_API_키를_입력하세요"

# Windows (PowerShell)
$env:OPENAI_API_KEY="여기에_당신의_API_키를_입력하세요"

# Windows (Command Prompt)
set OPENAI_API_KEY=여기에_당신의_API_키를_입력하세요
```

> 💡 **API 키 발급 방법**: 
> 1. [OpenAI 웹사이트](https://platform.openai.com/)에 가입
> 2. API Keys 메뉴에서 새 키 생성
> 3. 생성된 키를 안전하게 보관

#### 4단계: 데이터베이스 초기화
```bash
# 데이터베이스 마이그레이션 실행
uv run python manage.py migrate
```

#### 5단계: 관리자 계정 생성
```bash
# 슈퍼유저 계정 생성 (관리자 페이지 접속용)
uv run python manage.py createsuperuser

# 아래 정보 입력:
# - 사용자 이름: (원하는 이름 입력)
# - 이메일 주소: (선택사항, Enter로 건너뛰기 가능)
# - 비밀번호: (안전한 비밀번호 입력)
# - 비밀번호 확인: (동일한 비밀번호 재입력)
```

#### 6단계: 개발 서버 실행
```bash
# Django 개발 서버 시작
uv run python manage.py runserver

# 서버가 시작되면 아래와 같은 메시지가 표시됩니다:
# Starting development server at http://127.0.0.1:8000/
```

#### 7단계: 웹 브라우저에서 접속
1. 웹 브라우저를 열고 `http://127.0.0.1:8000/` 접속
2. 로그인 페이지에서 5단계에서 생성한 계정으로 로그인

## 💻 사용 방법

### 채팅 세션 시작하기

1. **로그인**: 생성한 계정으로 로그인합니다.

2. **새 세션 만들기**:
   - "새 세션 만들기" 버튼 클릭
   - 세션 정보 입력:
     - **제목**: 채팅 세션의 이름 (예: "친절한 상담사", "코딩 도우미")
     - **시스템 프롬프트**: AI의 역할과 성격 정의 (예: "당신은 친절한 상담사입니다")
     - **AI 모델**: GPT-4o 또는 GPT-4o-mini 선택
     - **온도**: 0.0(일관성) ~ 2.0(창의성) 사이 값
     - **최대 토큰**: 응답 길이 제한 (1~4096)

3. **채팅하기**:
   - 생성된 세션 클릭하여 채팅 시작
   - 메시지 입력 후 Enter 또는 전송 버튼 클릭
   - AI의 응답을 실시간으로 확인

4. **세션 관리**:
   - 세션 목록에서 이전 대화 계속하기
   - 세션 설정 수정하기
   - 필요 없는 세션 삭제하기

## 📁 프로젝트 구조

```
pycon-2025-demo/
├── manage.py           # Django 명령어 실행 파일
├── pyproject.toml      # 프로젝트 의존성 정의 (uv 사용)
├── uv.lock            # 의존성 버전 잠금 파일
├── db.sqlite3         # SQLite 데이터베이스 파일
│
├── mysite/            # Django 프로젝트 설정
│   ├── settings.py    # 프로젝트 설정
│   ├── urls.py        # URL 라우팅
│   └── wsgi.py        # WSGI 설정
│
└── roleplay/          # 채팅 애플리케이션
    ├── models.py      # 데이터베이스 모델 (ChatSession, ChatMessage)
    ├── views.py       # 뷰 로직
    ├── forms.py       # 폼 정의
    ├── core.py        # OpenAI API 연동 로직
    ├── templates/     # HTML 템플릿
    └── static/        # 정적 파일 (JavaScript, CSS)
```

## 🛠 기술 스택

- **Backend**: Django 5.2.4
- **AI Integration**: OpenAI API (GPT-4o, GPT-4o-mini)
- **Frontend**: HTMX (동적 상호작용), Tailwind CSS (스타일링)
- **Forms**: Django Crispy Forms with Tailwind
- **Database**: SQLite (개발용)
- **Package Manager**: uv (빠른 Python 패키지 관리)

## 🔍 문제 해결

### 자주 발생하는 문제들

1. **"OPENAI_API_KEY가 설정되지 않았습니다" 오류**
   - OpenAI API 키를 환경 변수로 설정했는지 확인
   - 터미널을 재시작하거나 새 터미널에서 다시 시도

2. **"포트 8000이 이미 사용 중입니다" 오류**
   ```bash
   # 다른 포트로 실행
   uv run python manage.py runserver 8080
   ```

3. **마이그레이션 오류**
   ```bash
   # 마이그레이션 파일 재생성
   uv run python manage.py makemigrations
   uv run python manage.py migrate
   ```

4. **uv 명령어를 찾을 수 없음**
   - uv 설치 후 터미널 재시작
   - 또는 `python -m uv` 형태로 실행

## 📝 개발 팁

- **디버그 모드**: `mysite/settings.py`의 `DEBUG = True`로 설정되어 있어 개발 중 오류 확인 가능
- **관리자 페이지**: `http://127.0.0.1:8000/admin/`에서 데이터 직접 관리 가능
- **데이터베이스 초기화**: `db.sqlite3` 파일 삭제 후 마이그레이션 재실행

## 📄 라이선스

이 프로젝트는 파이콘 2025 발표 목적으로 제작되었습니다.

