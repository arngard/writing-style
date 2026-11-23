---
date created: 2026-04-18
date modified: 2026-11-23
tags: [소개]
description: Introduction to the formal-rules workspace for all of the user's writing. Polishing definition and workflow, rule files by genre, when to read each rule document, folder layout
---

[한국어](README.md) | English

# writing-style

A workspace that researches, reviews, and specifies the formal rules for all of the user's (Arngard's) writing. It covers every genre: plain-prose records (documents, reports), retrospectives, creative writing such as fiction, code comments, and commit messages. Writing rules kept elsewhere, such as the user's common guidelines and the scaffold's document-writing rules, are short-form rules applied to each task; this repository holds the formal rules, with their rationale and complete specification.

## When polishing text against this repository

Polishing (윤문) means refining the expression, sentences, and structure of existing text while keeping its meaning. Newly researching the facts of the content or changing its claims is not polishing but amendment (개정). The definition is in [epistemic-structure/ontology/polishing.md](epistemic-structure/ontology/polishing.md).

An agent polishing text in another repository follows the polishing workflow [implementation/polishing/workflows/polish.md](implementation/polishing/workflows/polish.md). To get only a report of places that break the rules, without changing the text, follow the detection workflow [implementation/polishing/workflows/detect.md](implementation/polishing/workflows/detect.md).

First determine the genre of the text. Genres are defined in [epistemic-structure/ontology/writing-genres.md](epistemic-structure/ontology/writing-genres.md). The rule files for each genre are as follows.

| Genre | Rule files |
|-------|------------|
| Plain-prose records (documents, reports, analyses, commit messages, conversational replies that convey facts and judgments) | [plain-prose-rules.md](epistemic-structure/architecture/plain-prose-rules.md) and its rule documents |
| Retrospectives | None |
| Creative writing | None |
| Comments | None |

How to handle a genre without rule files is in the first step of the polishing workflow.

When polishing plain-prose records, read the following rule documents at the times listed. Examples for each rule are in the explanation documents that the rule's `### 설명` (explanation) section links to.

| Rule document | When to read |
|---------------|--------------|
| [polishing-principles.md](epistemic-structure/architecture/plain-prose-rules/polishing-principles.md) | Every polishing pass. Reviewers assigned to other rule documents read it too |
| [vocabulary.md](epistemic-structure/architecture/plain-prose-rules/vocabulary.md) | When choosing terms, loanwords, words, and abbreviations |
| [sentence.md](epistemic-structure/architecture/plain-prose-rules/sentence.md) | When checking register, the construction of a single sentence, and date and time notation |
| [format.md](epistemic-structure/architecture/plain-prose-rules/format.md) | When checking emphasis formatting, symbols, and punctuation |
| [bullets-and-prose.md](epistemic-structure/architecture/plain-prose-rules/bullets-and-prose.md) | When deciding between bullet points and running prose |
| [reference.md](epistemic-structure/architecture/plain-prose-rules/reference.md) | When checking links, reference markers, and wording that points to parts of a document |
| [composition.md](epistemic-structure/architecture/plain-prose-rules/composition.md) | When checking the structure of the text, summaries and quotations, and the separation of fact and opinion |
| [document-temporality.md](epistemic-structure/architecture/plain-prose-rules/document-temporality.md) | When checking the point in time a whole document describes and where reasons and narrative belong |

When the reason for a rule is needed, find the rationale documents through the document list in [epistemic-structure/strategy/INDEX.md](epistemic-structure/strategy/INDEX.md).

The target of polishing is the text in that repository; this repository is read only. If this repository's rules and the short-form rules the target repository follows disagree, get the user's decision before polishing. If you find something to fix in this repository's rules, hand it over as work for this repository.

## Structure

This repository inherits the [epistemic workspace scaffold](https://github.com/arngard/epistemic-workspace-scaffold) as `upstream`. What each area holds is set by [epistemic-structure/architecture/category-placement.md](epistemic-structure/architecture/category-placement.md).

| Area | Holds |
|------|-------|
| `epistemic-structure/ontology/` | Definitions of writing genres and writing concepts |
| `epistemic-structure/knowledge/` | External facts, reviews of external writing guidelines |
| `epistemic-structure/strategy/` | Rationale for the rules, rejected alternatives, retrospectives |
| `epistemic-structure/architecture/` | The formal rules for each genre |
| `implementation/` | Means of applying the rules to text (rule explanations, polishing tools, polishing workflows, the polishing skill source) |

The single entry point for operating guidelines is [AGENTS.md](AGENTS.md).
