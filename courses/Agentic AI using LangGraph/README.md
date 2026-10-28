---
title: Agentic AI using LangGraph
slug: langgraph
description: LangGraph workflows, tools, memory, subgraphs, and advanced RAG.
hide:
  - toc
---

# Agentic AI using LangGraph

CampusX · Videos 3–8, 11, 13, 16–18, 21–25, and 27–28

[Course playlist](https://www.youtube.com/playlist?list=PLKnIA16_RmvYsvB8qkUQuJmJNuiCUJFPL)

<a class="md-button md-button--primary" href="downloads/all-notes.zip" download>Download all notes (ZIP)</a>
<a class="md-button" href="../../">All courses</a>

## Lessons

| Video | Read online | PDF | Word | Markdown |
|---|---|---|---|---|
| 3 | [LangChain vs LangGraph](Video_03_LangChain_vs_LangGraph/CampusX_LangChain_vs_LangGraph_Expanded_Notes.md) | <a href="Video_03_LangChain_vs_LangGraph/CampusX_LangChain_vs_LangGraph_Expanded_Notes.pdf" download>PDF</a> | <a href="Video_03_LangChain_vs_LangGraph/CampusX_LangChain_vs_LangGraph_Expanded_Notes.docx" download>Word</a> | <a href="downloads/Video_03_LangChain_vs_LangGraph/CampusX_LangChain_vs_LangGraph_Expanded_Notes-markdown.zip" download>Markdown (ZIP)</a> |
| 4 | [LangGraph core concepts](Video_04_LangGraph_Core_Concepts/CampusX_LangGraph_Core_Concepts_Expanded_Notes.md) | <a href="Video_04_LangGraph_Core_Concepts/CampusX_LangGraph_Core_Concepts_Expanded_Notes.pdf" download>PDF</a> | <a href="Video_04_LangGraph_Core_Concepts/CampusX_LangGraph_Core_Concepts_Expanded_Notes.docx" download>Word</a> | <a href="downloads/Video_04_LangGraph_Core_Concepts/CampusX_LangGraph_Core_Concepts_Expanded_Notes-markdown.zip" download>Markdown (ZIP)</a> |
| 5 | [Sequential workflows](Video_05_Sequential/Video_05_Sequential.md) | <a href="Video_05_Sequential/Video_05_Sequential.pdf" download>PDF</a> | <a href="Video_05_Sequential/Video_05_Sequential.docx" download>Word</a> | <a href="downloads/Video_05_Sequential/Video_05_Sequential-markdown.zip" download>Markdown (ZIP)</a> |
| 6 | [Parallel workflows](Video_06_Parallel/Video_06_Parallel.md) | <a href="Video_06_Parallel/Video_06_Parallel.pdf" download>PDF</a> | <a href="Video_06_Parallel/Video_06_Parallel.docx" download>Word</a> | <a href="downloads/Video_06_Parallel/Video_06_Parallel-markdown.zip" download>Markdown (ZIP)</a> |
| 7 | [Conditional workflows](Video_07_Conditional/Video_07_Conditional.md) | <a href="Video_07_Conditional/Video_07_Conditional.pdf" download>PDF</a> | <a href="Video_07_Conditional/Video_07_Conditional.docx" download>Word</a> | <a href="downloads/Video_07_Conditional/Video_07_Conditional-markdown.zip" download>Markdown (ZIP)</a> |
| 8 | [Iterative workflows](Video_08_Iterative/Video_08_Iterative.md) | <a href="Video_08_Iterative/Video_08_Iterative.pdf" download>PDF</a> | <a href="Video_08_Iterative/Video_08_Iterative.docx" download>Word</a> | <a href="downloads/Video_08_Iterative/Video_08_Iterative-markdown.zip" download>Markdown (ZIP)</a> |
| 11 | [Persistence and time travel](Video_11_Persistence_and_Time_Travel/01_Persistence_Time_Travel_CampusX_Notes.md) | <a href="Video_11_Persistence_and_Time_Travel/01_Persistence_Time_Travel_CampusX_Notes.pdf" download>PDF</a> | <a href="Video_11_Persistence_and_Time_Travel/01_Persistence_Time_Travel_CampusX_Notes.docx" download>Word</a> | <a href="downloads/Video_11_Persistence_and_Time_Travel/01_Persistence_Time_Travel_CampusX_Notes-markdown.zip" download>Markdown (ZIP)</a> |
| 13 | [Streaming in LangGraph](Video_13_Streaming_in_LangGraph/02_Streaming_CampusX_Notes.md) | <a href="Video_13_Streaming_in_LangGraph/02_Streaming_CampusX_Notes.pdf" download>PDF</a> | <a href="Video_13_Streaming_in_LangGraph/02_Streaming_CampusX_Notes.docx" download>Word</a> | <a href="downloads/Video_13_Streaming_in_LangGraph/02_Streaming_CampusX_Notes-markdown.zip" download>Markdown (ZIP)</a> |
| 16 | [LangSmith crash course](Video_16_LangSmith_Crash_Course/03_LangSmith_Crash_Course_CampusX_Notes.md) | <a href="Video_16_LangSmith_Crash_Course/03_LangSmith_Crash_Course_CampusX_Notes.pdf" download>PDF</a> | <a href="Video_16_LangSmith_Crash_Course/03_LangSmith_Crash_Course_CampusX_Notes.docx" download>Word</a> | <a href="downloads/Video_16_LangSmith_Crash_Course/03_LangSmith_Crash_Course_CampusX_Notes-markdown.zip" download>Markdown (ZIP)</a> |
| 17 | [LangGraph observability and LangSmith integration](Video_17_LangGraph_LangSmith_Observability/04_LangGraph_LangSmith_Integration_CampusX_Notes.md) | <a href="Video_17_LangGraph_LangSmith_Observability/04_LangGraph_LangSmith_Integration_CampusX_Notes.pdf" download>PDF</a> | <a href="Video_17_LangGraph_LangSmith_Observability/04_LangGraph_LangSmith_Integration_CampusX_Notes.docx" download>Word</a> | <a href="downloads/Video_17_LangGraph_LangSmith_Observability/04_LangGraph_LangSmith_Integration_CampusX_Notes-markdown.zip" download>Markdown (ZIP)</a> |
| 18 | [Tools and ToolNode](Video_18_Tools_and_ToolNode/05_Tools_ToolNode_CampusX_Notes.md) | <a href="Video_18_Tools_and_ToolNode/05_Tools_ToolNode_CampusX_Notes.pdf" download>PDF</a> | <a href="Video_18_Tools_and_ToolNode/05_Tools_ToolNode_CampusX_Notes.docx" download>Word</a> | <a href="downloads/Video_18_Tools_and_ToolNode/05_Tools_ToolNode_CampusX_Notes-markdown.zip" download>Markdown (ZIP)</a> |
| 21 | [Human-in-the-Loop (HITL) using LangGraph](Video_21_Human_in_the_Loop/Notes.md) | <a href="Video_21_Human_in_the_Loop/Notes.pdf" download>PDF</a> | <a href="Video_21_Human_in_the_Loop/Notes.docx" download>Word</a> | <a href="downloads/Video_21_Human_in_the_Loop/Notes-markdown.zip" download>Markdown (ZIP)</a> |
| 22 | [Subgraphs in LangGraph](Video_22_Subgraphs_in_LangGraph/Notes.md) | <a href="Video_22_Subgraphs_in_LangGraph/Notes.pdf" download>PDF</a> | <a href="Video_22_Subgraphs_in_LangGraph/Notes.docx" download>Word</a> | <a href="downloads/Video_22_Subgraphs_in_LangGraph/Notes-markdown.zip" download>Markdown (ZIP)</a> |
| 23 | [Why LLMs Need Application Memory](Video_23_Memory_in_LLMs/Notes.md) | <a href="Video_23_Memory_in_LLMs/Notes.pdf" download>PDF</a> | <a href="Video_23_Memory_in_LLMs/Notes.docx" download>Word</a> | <a href="downloads/Video_23_Memory_in_LLMs/Notes-markdown.zip" download>Markdown (ZIP)</a> |
| 24 | [Short-Term Memory in LangGraph](Video_24_Short_Term_Memory/Notes.md) | <a href="Video_24_Short_Term_Memory/Notes.pdf" download>PDF</a> | <a href="Video_24_Short_Term_Memory/Notes.docx" download>Word</a> | <a href="downloads/Video_24_Short_Term_Memory/Notes-markdown.zip" download>Markdown (ZIP)</a> |
| 25 | [Long-Term Memory in LangGraph](Video_25_Long_Term_Memory/Notes.md) | <a href="Video_25_Long_Term_Memory/Notes.pdf" download>PDF</a> | <a href="Video_25_Long_Term_Memory/Notes.docx" download>Word</a> | <a href="downloads/Video_25_Long_Term_Memory/Notes-markdown.zip" download>Markdown (ZIP)</a> |
| 27 | [Corrective RAG (CRAG)](Video_27_Corrective_RAG/Notes.md) | <a href="Video_27_Corrective_RAG/Notes.pdf" download>PDF</a> | <a href="Video_27_Corrective_RAG/Notes.docx" download>Word</a> | <a href="downloads/Video_27_Corrective_RAG/Notes-markdown.zip" download>Markdown (ZIP)</a> |
| 28 | [Self-RAG: Reflection and Verification](Video_28_Self_RAG/Notes.md) | <a href="Video_28_Self_RAG/Notes.pdf" download>PDF</a> | <a href="Video_28_Self_RAG/Notes.docx" download>Word</a> | <a href="downloads/Video_28_Self_RAG/Notes-markdown.zip" download>Markdown (ZIP)</a> |

<details class="course-details" markdown="1">
<summary>Combined PDF and chapter links</summary>

- [Combined theory notes PDF — videos 11, 13, 16, 17, and 18](00_All_5_LangGraph_Notes_Combined.pdf)
- [Full chapter timestamps and YouTube links for those five videos](VIDEO_CHAPTER_LINKS.md)

</details>

<details class="course-details" markdown="1">
<summary>Course videos</summary>

| Video | Topic | Duration | Open lesson |
|---|---|---|---|
| 3 | LangChain vs LangGraph | 1:27:29 | [Watch](https://www.youtube.com/watch?v=31qyMKNB2RA) |
| 4 | LangGraph Core Concepts | — | [Watch](https://www.youtube.com/watch?v=D5KhiCDM9XQ) |
| 5 | Sequential Workflows | 49:13 | [Watch](https://www.youtube.com/watch?v=bAWujyAl1Kk) |
| 6 | Parallel Workflows | 59:29 | [Watch](https://www.youtube.com/watch?v=O6ryuSpqdOw) |
| 7 | Conditional Workflows | 47:38 | [Watch](https://www.youtube.com/watch?v=I-dvZqTz-Wc) |
| 8 | Iterative Workflows | 37:14 | [Watch](https://www.youtube.com/watch?v=7CbSqrovcsE) |
| 11 | Persistence and Time Travel | ~58 min | [Watch](https://www.youtube.com/watch?v=_IPP7_Bi8uA) |
| 13 | Streaming in LangGraph | ~25 min | [Watch](https://www.youtube.com/watch?v=D1PcZaeQ2eg) |
| 16 | LangSmith Crash Course | ~2 hr 8 min | [Watch](https://www.youtube.com/watch?v=4FFspU4riHk) |
| 17 | LangGraph Observability / LangSmith Integration | ~22 min | [Watch](https://www.youtube.com/watch?v=ikzN6byFNWw) |
| 18 | Tools and ToolNode | ~34 min | [Watch](https://www.youtube.com/watch?v=_UuUigoM9MA) |
| 21 | Human-in-the-Loop (HITL) using LangGraph | — | [Watch](https://www.youtube.com/watch?v=xxqZzVZ4gE0&list=PLKnIA16_RmvYsvB8qkUQuJmJNuiCUJFPL&index=21) |
| 22 | Subgraphs in LangGraph | — | [Watch](https://www.youtube.com/watch?v=wcHcocpAoX4&list=PLKnIA16_RmvYsvB8qkUQuJmJNuiCUJFPL&index=22) |
| 23 | Why LLMs Need Application Memory | — | [Watch](https://www.youtube.com/watch?v=DcPKJrOF9Wo&list=PLKnIA16_RmvYsvB8qkUQuJmJNuiCUJFPL&index=23) |
| 24 | Short-Term Memory in LangGraph | — | [Watch](https://www.youtube.com/watch?v=FSBkTI1QuvY&list=PLKnIA16_RmvYsvB8qkUQuJmJNuiCUJFPL&index=24) |
| 25 | Long-Term Memory in LangGraph | — | [Watch](https://www.youtube.com/watch?v=KrXBcokM3Tc&list=PLKnIA16_RmvYsvB8qkUQuJmJNuiCUJFPL&index=25) |
| 27 | Corrective RAG (CRAG) | — | [Watch](https://www.youtube.com/watch?v=41XDn81nR5c&list=PLKnIA16_RmvYsvB8qkUQuJmJNuiCUJFPL&index=27) |
| 28 | Self-RAG: Reflection and Verification | — | [Watch](https://www.youtube.com/watch?v=BbO_XaEjzaA&list=PLKnIA16_RmvYsvB8qkUQuJmJNuiCUJFPL&index=28) |

</details>

<details class="course-details" markdown="1">
<summary>References</summary>

- [CampusX tutorial notebooks](https://github.com/campusx-official/langgraph-tutorials)
- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [LangGraph workflows and agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents)

</details>

<details class="course-details" markdown="1">
<summary>Formats and source notes</summary>

Each lesson has its own folder containing a PDF, a Word document with white-page formatting, a Markdown file, and its illustrations. Keep the Markdown file alongside its image directory when working with the source files. The website's Markdown ZIP includes both.

The theory notes for videos 11, 13, 16, 17, and 18 are independently written, concept-focused study guides rather than transcripts. Their illustrations are original concept diagrams, not YouTube screenshots. Their published chapter lists and timestamp URLs are collected in [VIDEO_CHAPTER_LINKS.md](VIDEO_CHAPTER_LINKS.md).

</details>

<details class="course-details" markdown="1">
<summary>Later theory notes: coverage and chapter links</summary>

Videos 21–25, 27, and 28 cover human-in-the-loop workflows, subgraphs, application memory, and advanced RAG. Each lesson folder contains `Notes.md`, `Notes.docx`, `Notes.pdf`, and two original diagrams in `images/`: `workflow.png` and `concept_map.png`.

The notes use original explanations and small teaching examples rather than recreating tutorial projects or transcribing the videos. PDF and Word copies embed the diagrams inline and use white-page formatting. Markdown uses relative image paths, and its download ZIP includes those images.

Verified chapter timestamps are linked in the individual lessons. **Video 25 links to the full video:** verified chapter timings were unavailable, so none were invented.

The following videos are outside the scope of this theory-note selection:

- **19 — MCP Client in LangGraph:** primarily MCP client implementation and application integration.
- **20 — RAG using LangGraph:** primarily integrating RAG into an existing chatbot project; related retrieval concepts appear in videos 27–28.
- **26 — AI Blog Writing Agent:** an end-to-end project build.

This later set contains 7 Markdown files, 7 Word documents, 7 PDFs, and 14 original diagrams. Chapter links appear where verified; the diagrams are not screenshots from copyrighted video footage.

</details>
