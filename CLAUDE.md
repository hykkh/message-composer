# H 메시지 작성기

개인용 메시지 작성 보조 도구. 모바일 PWA + 데스크탑 tkinter 두 형태로 존재.

## 구성
- **index.html + manifest.json** — 모바일 PWA (hykkh.github.io/message-composer 에 배포)
- **message_composer.py** — 데스크탑 tkinter GUI (로컬 실행용)
- **icon-192.png / icon-512.png / favicon.ico** — PWA 아이콘

## 배포 URL
- 프로덕션: https://hykkh.github.io/message-composer/
- 바로가기 파일: `C:\Users\admin\OneDrive\Desktop\H 메시지 작성기.url`

## 실행 (데스크탑)
```
python message_composer.py
```

## 수정 시
- 웹 버전 (PWA) 수정 → `index.html`, `manifest.json` 편집 → hykkh.github.io 리포지토리로 배포 필요
- 데스크탑 버전 수정 → `message_composer.py` 편집 후 바로 실행 가능
- 아이콘 교체 시 PWA manifest 의 `icons[]` 경로와 일치하는지 확인
