# set-opus-language

OPUS: Echo of Starsong 의 **게임 내 언어(currentLanguage)** 를 세이브 폴더의
`OPTIONINFO` 파일에서 안전하게 바꾸는 단독 실행 도구.

한글 패치 언어(KR=8)로 저장된 상태에서 원본으로 되돌리면 텍스트가 안 보이는데,
게임 안에서는 그 텍스트가 안 보여 언어를 못 바꾼다. 이 도구로 파일에서 직접 바꾼다.

## 쓰는 법 (누구나)

1. `..\set-opus-language.exe` 를 **더블클릭**
2. 목록에서 원하는 언어 번호 입력 → Enter
3. 끝. (게임은 꺼둔 상태에서 실행할 것)

`OPTIONINFO` 경로는 자동으로 찾는다:
`%USERPROFILE%\AppData\LocalLow\SIGONO\OPUS_ Echo of Starsong\Save\OPTIONINFO`

## 명령줄 옵션 (선택)

```
set-opus-language.exe -lang 1          # 메뉴 없이 바로 EN 으로
set-opus-language.exe -file "<경로>"   # OPTIONINFO 위치 수동 지정
```

## 언어 enum (Sigono.Utilities.Localization.EnumLanguage)

| 값 | 코드 | 언어 | 비고 |
|---|---|---|---|
| 0 | CHT | 번체 중국어 | 원본 지원 |
| 1 | EN | 영어 | 원본 지원 |
| 2 | CHS | 간체 중국어 | 원본 지원 |
| 3 | JP | 일본어 | 원본 지원 |
| 8 | KR | 한국어 | **한글 패치 적용 시에만** 텍스트 표시 |
| 4·5·6·7·9·10 | FR/BR/ES/PT/DE/JPSWITCH | — | 원본에 데이터 없음(빈 화면) |

## 동작 원리 / 안전장치

- `OPTIONINFO` = Base64 인코딩된 UTF-8 JSON(CRLF).
- 정규식으로 `"currentLanguage"` 정수값 **딱 하나만** 교체 — 다른 옵션/줄바꿈은 바이트 그대로 보존.
- `"currentLanguage"` 항목이 정확히 1개가 아니면 중단.
- 변경 전 타임스탬프 백업 생성: `OPTIONINFO.bak-YYYYMMDD-HHMMSS`.
- 쓰기 후 다시 디코드해 값 검증.

## 다시 빌드하려면

```
cd set-opus-language
go build -ldflags="-s -w" -o ..\set-opus-language.exe .
```

> 주의: 변경이 게임 실행 후 되돌아가면 **Steam 클라우드**가 옛 설정을 덮어쓴 것.
> Steam > 게임 속성 > 일반 > Steam 클라우드 를 끄고 다시 실행.
