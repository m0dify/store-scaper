# Store Scraper

앱스토어(App Store)와 구글 플레이스토어(Google Play Store)의 인기 앱 정보를 수집하고, CSV 또는 JSON 파일로 저장할 수 있는 파이썬 프로젝트입니다.

## 주요 기능

- **Apple App Store 인기 앱 수집**
  - 국가, 차트 타입, 앱 개수 등 다양한 옵션 지원
  - 앱 상세 정보까지 수집 가능
- **Google Play Store 인기 앱 수집**
  - 인기 무료 앱 등 다양한 컬렉션 시도
- **CSV/JSON 파일로 저장**
  - 모든 결과는 `exports` 폴더 하위에 저장

## 설치 방법

1. Python 3.7 이상이 필요합니다.
2. 필요한 패키지 설치:
    ```bash
    pip install requests pandas beautifulsoup4
    ```

## 사용 방법

1. 터미널에서 프로젝트 폴더로 이동 후 실행:
    ```bash
    python main.py
    ```
2. 안내에 따라 수집할 스토어(앱스토어/플레이스토어/둘 다)를 선택합니다.
3. 각 스토어별로 국가, 차트, 저장 형식 등을 입력하면 결과가 `exports` 폴더에 저장됩니다.

## 파일 구조

- `main.py` : 실행 및 사용자 입력 처리
- `AppStoreTopScraper.py` : 앱스토어 인기 앱 수집 클래스
- `GooglePlayStoreTopScraper.py` : 구글 플레이스토어 인기 앱 수집 클래스
- `exports/` : 결과 파일 저장 폴더

## 참고

- Apple App Store 데이터는 iTunes RSS API를 사용합니다.
- Google Play Store 데이터는 웹 크롤링 방식으로 수집합니다(구글 정책에 따라 일부 정보가 누락될 수 있음).

##