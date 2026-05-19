---
date created: 2026-05-19
date modified: 2026-05-19
tags: [strategy, 프로젝트]
importance: 상
urgency: 중
---

# 프로젝트 수준 결정 — 란다의 문체

## 상황

사용자(아릉)는 오랫동안 하나의 픽션 세상(작품명 [란다](../_ontology/landa.md))에 관한 글을 누적해 왔다. 원본은 여러 형태로 흩어져 있다 — 옵시디언 vault·블로그 백업·웹 게시판 크롤링 자료 등 (cf. [_knowledge/about-landa-record.md](../_knowledge/about-landa-record.md)).

인간과 AI 협업에서 AI가 사용자의 글쓰기 스타일을 그대로 따라 글을 쓰게 하려면 사용자 문체의 특징을 명시 정보로 추출해 두어야 한다. 본 추출이 없으면 AI는 일반 어휘·일반 문장 구조로 글을 쓰게 되고, 사용자 본인의 글과의 일관성이 깨진다.

importance 상 — 본 레포의 산출물은 사용자의 다른 모든 글쓰기 작업의 메타 도구로 쓰일 수 있다. urgency 중 — 즉시 시급한 운영 마감은 없으나 누적 자체에 시간이 들어 일찍 시작할수록 좋다.

## 대응

본 레포의 유일한 목적: 사용자의 글쓰기 스타일을 명시 정보로 추출하여, AI가 사용자처럼 글을 쓰는 데 활용할 수 있는 가이드를 만든다.

### 입력 흐름

본 자식은 작품 원본을 직접 다루지 않는다. 입력 흐름:

```
원본들 (옵시디언 vault · 블로그 백업 · 웹 게시판 크롤링 자료 등)
   ↓ 정리본 흡수 (원본은 훼손하지 않음)
landa 레포 (devCode 산하 `landa/`, arngard/landa, private)
   ↓ 문체 추출
landa-writing-style (본 레포)
```

본 자식의 SSOT 입력은 [landa 레포](https://github.com/arngard/landa)이며, 원본 자료 자체는 본 자식의 영역 외다.

### 포함 범위

- 사용자 문체의 특징 추출 (어휘·문장 구조·시점·리듬·수사 패턴 등).
- 추출한 특징을 AI가 활용 가능한 형태(스타일 가이드·프롬프트 패턴 등)로 가공.
- 추출 작업의 운영 절차 (어떤 자료를 어떻게 읽고 어떻게 특징으로 환원할지).

### 미포함 범위

- 작품의 장르·세계관·플롯·캐릭터 등 콘텐츠 분석. 본 레포는 문체에만 집중한다. 작품 콘텐츠의 SSOT는 [landa 레포](https://github.com/arngard/landa).
- 원본 자료 자체의 보관·관리. 원본은 사용자 외부 도구가, 정리본은 landa 레포가 담당한다.

## 참고

- [_ontology/landa.md](../_ontology/landa.md) — "란다" 용어 정의 (작품 명명)
- [_knowledge/about-landa-record.md](../_knowledge/about-landa-record.md) — 작품에 대한 외부 사실
- [arngard/landa](https://github.com/arngard/landa) — 본 자식의 SSOT 입력 레포
