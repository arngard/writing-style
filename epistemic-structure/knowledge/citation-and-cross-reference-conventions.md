---
date created: 2026-10-24
date modified: 2026-10-28
tags: [knowledge, 참조, 인용, 외부관례]
description: 학술, 법률, 백과사전, 코드 문서 주석에서 다른 글을 가리키는 표기의 외부 관례
---

# 인용과 상호 참조 표기의 외부 관례

학술 인용, 법률 인용, 백과사전, 코드 문서 주석이 다른 글을 가리킬 때 쓰는 표기 관례를 모은다. 2026-10-24에 웹 검색으로 확인했다.

## 학술 인용에서 `cf.`는 비교를 뜻한다

- `cf.`는 라틴어 confer(비교하라)의 약어다.[^cf-wiki]
- 시카고 매뉴얼(CMOS; Chicago Manual of Style)은 `cf.`를 비교를 권할 때만 쓰고, 출처를 단순히 가리킬 때는 "see"를 쓰라고 권한다. 대개 다른 견해와 견주어 보라는 함의가 있다.[^cf-wiki][^sbl]
- 사전 가운데에는 "see also"의 뜻을 싣는 것이 있다. 시카고 매뉴얼 편집진은 이를 그 오용이 널리 퍼졌다는 기록으로 보고, 저자는 "see"를 뜻할 때 `cf.`를 쓰는 경우가 많다고 답한다.[^cmos-qa]

## `ref.`는 참조 일반의 약어이고, 번호식 인용에서 참고문헌 항목을 가리킨다

- `ref.`는 reference의 약어다. Wiktionary는 이것이 법률 인용에서 관용적인 약어라고 적는다.[^ref-wikt]
- 미국물리학회(APS; American Physical Society) 학술지의 번호식 인용에서는 본문의 `Refs. 1 and 4` 같은 표기가 참고문헌 목록의 항목을 가리킨다. 학술지 조판 양식 REVTeX의 예시 파일에서 확인한 형태이며, 공식 스타일 가이드의 해당 규정 원문은 확인하지 못했다.[^revtex]
- 학술 인용의 지시어로서 `ref.`가 특정 관계(근거, 비교 등)를 뜻하도록 정립된 쓰임은 확인되지 않았다.

## 법률 인용의 지시어는 인용 자료의 입장으로 나뉜다

미국 법률 인용 규범(Bluebook)의 인용 지시어(signal)는 네 계열로 나뉜다.[^citation-signal][^tarlton]

| 계열 | 지시어 | 뜻 |
|------|--------|-----|
| 지지 | `see`, `see also`, `cf.` | 인용 자료가 본문 주장을 뒷받침한다. `cf.`는 본문 주장과 다르지만 유추할 만한 주장을 뒷받침한다 |
| 비교 | `compare ... with ...`, `contrast` | 자료를 나란히 놓아 비슷함이나 다름을 보인다. contrast는 22판에서 따로 나뉘었다 |
| 반대 | `contra`, `but see` | 인용 자료가 본문 주장과 반대되거나 상반된 입장을 뒷받침한다 |
| 배경 | `see generally` | 본문 주장과 직접 맞닿지는 않지만 배경이 되는 자료다 |

## 위키백과의 안내문은 콜론 이름표로 다른 문서를 가리킨다

위키백과는 절 제목 바로 아래에 다른 문서를 가리키는 짧은 안내문(hatnote)을 둔다. 안내문은 대부분의 화면에서 들여쓰기와 기울임으로 표시된다.[^hatnote]

| 안내문 | 쓰임 |
|--------|------|
| `Main article: 문서` | 요약 서술 방식에서 이 절이 요약한 하위 문서를 가리킨다. 본문 링크를 대신하는 용도로 쓰지 않는다.[^template-main] |
| `Further information: 문서` | 이 절이 다룬 특정 측면을 더 자세히 다루는 문서를 가리킨다.[^template-main] |
| `See also: 문서` | 절과 관련된 소수의 다른 문서를 가리킨다. 문서 끝의 "See also" 절과는 다른 용도다.[^template-see-also] |

## 코드 문서 주석은 `see` 계열 태그를 쓴다

- KDoc은 Javadoc식 블록 태그를 쓰며, `@see` 태그로 다른 함수나 클래스 같은 요소를 가리킨다.[^kdoc]
- Swift의 문서 주석은 `- SeeAlso:` 형태의 필드를 쓴다. DocC 이전 방식의 표기이며, 현재 DocC가 이를 어떻게 표시하는지는 확인하지 못했다.[^swiftrocks][^swift-markdown]

[^cf-wiki]: ref: [Cf. - Wikipedia](https://en.wikipedia.org/wiki/Cf.)
[^sbl]: ref: [cf see also - SBL Handbook of Style](https://sblhs2.com/2017/01/12/cf-see-also/)
[^cmos-qa]: ref: [Chicago Manual of Style Q&A: Usage and Grammar](https://www.chicagomanualofstyle.org/qanda/data/faq/topics/Usage/faq0220.html)
[^ref-wikt]: ref: [Ref. - Wiktionary](https://en.wiktionary.com/wiki/Ref.)
[^revtex]: ref: [REVTeX APS sample](https://ctan.csail.mit.edu/macros/latex2e/contrib/revtex/sample/aps/apssamp.pdf)
[^citation-signal]: ref: [Citation signal - Wikipedia](https://en.wikipedia.org/wiki/Citation_signal)
[^tarlton]: ref: [Bluebook intro signals - Tarlton Law Library](https://tarlton.law.utexas.edu/bluebook-legal-citation/intro-signals)
[^hatnote]: ref: [Template:Hatnote (mirror)](https://wiki.wcpl.info/wiki/Template:Hatnote)
[^template-main]: ref: [Template:Main (mirror)](https://lnf-wiki.eecs.umich.edu/wiki/Template:Main)
[^template-see-also]: ref: [Template:See also - MediaWiki](https://www.mediawiki.org/wiki/Template:See_also)
[^kdoc]: ref: [KDoc overview - Baeldung](https://www.baeldung.com/kotlin/kdoc)
[^swiftrocks]: ref: [Swift's Documentation Markup - SwiftRocks](https://swiftrocks.com/swifts-documentation-markup)
[^swift-markdown]: ref: [swift-markdown PR #96](https://github.com/swiftlang/swift-markdown/pull/96)
