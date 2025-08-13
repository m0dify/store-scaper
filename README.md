## 실행 방법

1. **필수 패키지 설치**
    ```bash
    pip install requests pandas beautifulsoup4
    ```

2. **프로그램 실행**
    프로젝트 폴더에서 아래 명령어로 실행합니다.
    ```bash
    python main.py
    ```

3. **스토어 선택**
    실행 후 아래와 같은 안내가 출력됩니다.
    ```
    수집할 스토어를 선택하세요:
    1. Apple App Store
    2. Google Play Store
    3. 둘 다
    번호 입력 (1/2/3):
    ```
    원하는 번호를 입력하세요.

4. **옵션 입력**
    각 스토어별로 국가 코드, 차트 타입, 저장 형식(csv/json), 파일명 등을 입력하라는 안내가 나옵니다.  
    엔터만 입력하면 기본값이 적용됩니다.

5. **결과 확인**
    수집된 데이터는 `exports` 폴더 하위에 입력한 파일명으로 저장됩니다.

---

**예시 실행 흐름**
```
$ python main.py
수집할 스토어를 선택하세요:
1. Apple App Store
2. Google Play Store
3. 둘 다
번호 입력 (1/2/3): 1
앱스토어 국가 코드 입력 (예: kr, us, jp) [기본값: kr]:
수집할 앱 개수 입력 (최대 200) [기본값: 100]:
차트 타입 입력 (topfreeapplications, toppaidapplications, topgrossingapplications) [기본값: topfreeapplications]:
저장 형식 선택 (csv/json) [기본값: csv]:
저장 파일명 입력 (확장자 제외) [기본값: appstore_top_apps]:
```
입력이 끝나면 `exports/appstore_top_apps.csv` 파일이 생성됩니다.