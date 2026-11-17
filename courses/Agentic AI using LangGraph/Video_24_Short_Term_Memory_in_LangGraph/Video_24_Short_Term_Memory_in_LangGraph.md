# Short-Term Memory in LangGraph

**Agentic AI using LangGraph | Video 24 | CampusX**  
**Lesson:** [How To Implement Short Term Memory Using LangGraph](https://www.youtube.com/watch?v=FSBkTI1QuvY)

> **Core idea:** Short-term memory preserves the conversation state of a thread using checkpoints so later invocations can use earlier messages.

## 1. Learning goals

Understand thread IDs, checkpointers, RAM versus database persistence, context overflow, trimming, and summarization.

### Video chapter links

| Time | Chapter |
| --- | --- |
| [00:00](https://www.youtube.com/watch?v=FSBkTI1QuvY&t=0s) | Introduction and video overview |
| [01:38](https://www.youtube.com/watch?v=FSBkTI1QuvY&t=98s) | Recap: LLMs are stateless and memory fundamentals |
| [03:33](https://www.youtube.com/watch?v=FSBkTI1QuvY&t=213s) | Short-term memory concept and checkpointers in LangGraph |
| [04:46](https://www.youtube.com/watch?v=FSBkTI1QuvY&t=286s) | Implementing short-term memory with threads and in-memory storage |
| [09:22](https://www.youtube.com/watch?v=FSBkTI1QuvY&t=562s) | Limitations of in-memory memory storage |
| [11:16](https://www.youtube.com/watch?v=FSBkTI1QuvY&t=676s) | Need for persistence in production systems |
| [12:38](https://www.youtube.com/watch?v=FSBkTI1QuvY&t=758s) | Setting up PostgreSQL using Docker |
| [15:54](https://www.youtube.com/watch?v=FSBkTI1QuvY&t=954s) | Implementing persistent memory with PostgreSQL checkpointer |
| [17:36](https://www.youtube.com/watch?v=FSBkTI1QuvY&t=1056s) | Verifying persistence after application restart |
| [19:30](https://www.youtube.com/watch?v=FSBkTI1QuvY&t=1170s) | Context window and context overflow problem |
| [21:38](https://www.youtube.com/watch?v=FSBkTI1QuvY&t=1298s) | Trimming strategy to control token limits |
| [31:19](https://www.youtube.com/watch?v=FSBkTI1QuvY&t=1879s) | Limitations of trimming |
| [32:03](https://www.youtube.com/watch?v=FSBkTI1QuvY&t=1923s) | Summarization concept for long conversations |
| [35:24](https://www.youtube.com/watch?v=FSBkTI1QuvY&t=2124s) | Deletion and its role in summarization |
| [40:12](https://www.youtube.com/watch?v=FSBkTI1QuvY&t=2412s) | Implementing summarization workflow in LangGraph |
| [49:26](https://www.youtube.com/watch?v=FSBkTI1QuvY&t=2966s) | Testing summarization behavior in practice |
| [52:08](https://www.youtube.com/watch?v=FSBkTI1QuvY&t=3128s) | Final recap and key takeaways |

**Prerequisites:** Basic Python and the idea of an LLM workflow are helpful. New terms are explained when first used.

---

## 2. Short-term memory in a LangGraph chatbot

**Short-term memory** lets a chatbot use earlier messages from the **same conversation thread** when responding to the next message. The model does not acquire this ability on its own; the application keeps message history and makes that history available during later model calls.

Suppose a user says, “My preferred interview language is Python,” then later asks, “Give me a practice question for that language.” The second question depends on the earlier turn. A memory-enabled application can load the previous message and resolve “that language” correctly.

<p align="center"><img src="images/01_short_memory.png" alt="Conversation short-term memory lifecycle" width="515"></p>

The workflow is: accept the message → identify the correct conversation thread → load the saved state → call the assistant with context → append the new response → save the updated state. This is the basic loop behind a conversation that feels continuous.

## 3. Threads and checkpointers

A **thread** identifies one conversation history. A **checkpointer** saves snapshots of graph state as the workflow executes. To continue a conversation, the caller supplies the same `thread_id`; the runtime loads the appropriate state and applies the new updates.

<p align="center"><img src="images/02_thread_isolation.png" alt="Two users, separate thread histories" width="515"></p>

Imagine two conversations. In thread `student-A`, the user is practicing Python. In thread `student-B`, the user is practicing SQL. If the application uses separate thread IDs, each receives its own history. Reusing the same thread for unrelated users is a privacy and correctness bug, not a personalization feature.

<p align="center"><img src="images/03_checkpointer.png" alt="Checkpoint after graph updates" width="515"></p>

**State versus checkpoint:** state is what nodes work with, such as `messages`. A checkpoint is a stored snapshot of that state, along with execution metadata needed for continuation. The checkpoint does not produce an answer; it makes the earlier context recoverable.

## 4. A small memory demonstration without an LLM

The following demo uses `MessagesState` and `InMemorySaver`. Its responder is deterministic so you can inspect how history is stored without paying for a model API. Install `langgraph` first.

```python
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import AIMessage, HumanMessage


def responder(state: MessagesState):
    # Read the stored conversation so the example proves history exists.
    count = sum(isinstance(m, HumanMessage) for m in state["messages"])
    return {"messages": [AIMessage(content=f"I have seen {count} user turns.")]}

builder = StateGraph(MessagesState)
builder.add_node("respond", responder)
builder.add_edge(START, "respond")
builder.add_edge("respond", END)
app = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "student-A"}}
app.invoke({"messages": [HumanMessage(content="Hello")]}, config)
result = app.invoke({"messages": [HumanMessage(content="Again")]}, config)
print(result["messages"][-1].content)  # I have seen 2 user turns.
```

`MessagesState` provides a `messages` field with a reducer designed for chat messages. Adding a new message does not automatically throw away earlier messages. In a real chatbot, replace `responder` with a model call that receives the appropriate history. Be aware that long histories still need context management.

## 5. Memory in RAM versus memory in a database

`InMemorySaver` is convenient for learning and local tests, but the history is held in the running process. A server restart, new worker, or process crash can make it unavailable. Production applications commonly use a **durable checkpointer**, such as a PostgreSQL-backed implementation, to restore conversations across restarts.

<p align="center"><img src="images/04_mem_vs_db.png" alt="In-memory vs persistent backend" width="515"></p>

The diagram contrasts the two storage choices. With RAM storage, a restarted process may begin without the old history. With a durable database, a new process can load saved checkpoints when it has the same correct thread ID and access to the database.

In the lesson's practical progression, the in-memory prototype comes first; a persistent database becomes necessary once the chatbot must survive application restarts. Database persistence is a separate concern from the model's context limit: even if thousands of messages are stored safely, the model still cannot consume unlimited tokens at once.

### A conceptual production shape

```python
# Requires: pip install langgraph-checkpoint-postgres "psycopg[binary,pool]"
# The database must be created and reachable.
from langgraph.checkpoint.postgres import PostgresSaver

DB_URI = "postgresql://USER:PASSWORD@HOST:5432/DBNAME"
with PostgresSaver.from_conn_string(DB_URI) as saver:
    saver.setup()  # Create required tables for a new store.
    # Compile your graph with checkpointer=saver.
    # Reuse a stable, authorized thread_id for later turns.
```

The connection string is a **placeholder**; put real credentials in a secure configuration or environment variable, never inside shared notes or source control. For a production service, choose appropriate connection management and access controls.

## 6. The context overflow problem

A chatbot can preserve hundreds of turns, but the model receives a limited prompt window. If every message is always supplied, token use grows, latency rises, and eventually the model input can become too large. **Stored conversation history** and **the subset currently sent to the model** need not be identical.

<p align="center"><img src="images/05_context_limit.png" alt="Saved history can exceed model context" width="515"></p>

Consider a long tutoring conversation containing 80 turns. The user now asks for a quick definition. The model may only need the last few relevant turns and an important summary of earlier preferences; sending all 80 turns may not improve the answer. This leads to two common context-management strategies: **trimming** and **summarization**.

## 7. Strategy one: trimming messages

**Trimming** selects a smaller portion of conversation history, often favoring the latest complete turns or limiting the input to a token budget. The model then sees a manageable slice of recent interaction.

<p align="center"><img src="images/06_trimming.png" alt="Trimming keeps a window of recent turns" width="515"></p>

A simple illustration: save 100 turns, but construct the next model input using the last 8 turns. The database can still hold the full checkpoint history. The important distinction is that trimming **model input** need not delete **persistent storage**. A production trimmer should respect role boundaries and tool-call pairs rather than arbitrarily cutting messages in the middle of a tool exchange.

**Limitation:** an early but essential fact may disappear from the recent window. If the user said their preferred language 50 turns ago, a recent-only model may forget it even though the information is stored. A summary or long-term memory can help.

## 8. Strategy two: conversation summarization

**Summarization** compresses older dialogue into a shorter description of the important facts and progress. The next model call receives the summary plus recent messages rather than every old turn.

<p align="center"><img src="images/07_summarization.png" alt="Summarize older turns, keep recent detail" width="515"></p>

Example summary: “The user is preparing for Python backend interviews. Completed topics: functions, exceptions, generators. Still needs async programming and databases.” A new prompt can include this concise summary and the last few turns. It saves tokens while preserving the information that a simple recent-message cut might lose.

<p align="center"><img src="images/08_delete.png" alt="Delete only after saving a suitable summary" width="515"></p>

A summarization workflow may eventually remove older message entries from active state after successfully incorporating them into a summary. **Order matters:** generate and verify the summary → save the summary → only then remove redundant history. If you delete before summarizing, useful details may be lost. If summarization omits an important constraint, the next response can still be wrong.

## 9. Choosing the right context strategy

<p align="center"><img src="images/09_strategy.png" alt="Choose a context strategy" width="515"></p>

| Situation | Good starting choice | Watch out for |
| --- | --- | --- |
| Very short thread | Keep full history | Usually low overhead |
| Long repetitive conversation | Trim old low-value turns | Losing old necessary facts |
| Long project discussion | Summary + recent turns | Summary errors or missing detail |
| Durable preference across threads | Long-term store | Privacy, freshness, and user boundaries |
| Must survive restarts | Durable checkpointer | Database configuration and authorization |

**Practical advice:** first build a correct single-thread chatbot, then test thread isolation, then test process restart, then add context-size handling. Memory should be tested with explicit questions whose answers depend on earlier turns; a chat that only replies “Hello” does not prove that memory works.


## 10. Worked example: balancing continuity and token limits

Imagine a tutoring chatbot with 60 conversation turns. The original turns include the learner's goal, several lessons, examples, mistakes, and corrections. Sending all 60 turns to the model for every new question would be wasteful. The application could retain all checkpoints for continuity while preparing a smaller model input.

A useful prompt might contain: a short stable instruction, a **summary of completed topics**, the **last 4–6 turns**, and the current question. This separates the storage problem from the context-selection problem.

| Information | Keep in stored thread? | Include in next model prompt? |
| --- | --- | --- |
| Original question from the first day | Yes if retention allows | Only if needed |
| Summary of the course goal | Yes | Yes, when relevant |
| Last few turns | Yes | Usually yes |
| Long tool outputs from earlier lessons | Often yes for audit | Usually no |
| Current question | Yes | Yes |

### Why summarization needs care

Summaries can accidentally convert a temporary instruction into a permanent preference, lose a crucial exception, or merge two different topics. A well-designed summary preserves **unresolved questions, exact constraints, and important decisions**. For example, “Use Python 3.14 for this environment” is more actionable than “The user likes Python.”

Test summarization by asking the assistant to recall a fact introduced long before the recent-turn window. Also test whether it incorrectly repeats an old fact after the user corrects it. When memory is critical, maintain the exact source record or a pointer to it instead of trusting a compact summary as the sole authority.


---

## Key takeaways for quick revision

1. Explain how the same thread loads earlier messages.
2. Demonstrate two isolated conversation threads.
3. Compare InMemorySaver and a database checkpointer.
4. Explain why saved history can still overflow a prompt.
5. Trace trimming and summarization separately.
6. Explain when RemoveMessage and summary updates are safe.

## Revision checklist

- [ ] Explain how the same thread loads earlier messages.
- [ ] Demonstrate two isolated conversation threads.
- [ ] Compare InMemorySaver and a database checkpointer.
- [ ] Explain why saved history can still overflow a prompt.
- [ ] Trace trimming and summarization separately.
- [ ] Explain when RemoveMessage and summary updates are safe.

## Practice questions and mini exercises

1. Run the deterministic `MessagesState` example with two different thread IDs and predict the counts.
2. Design a summary that preserves an interview learner’s completed topics, goals, and unresolved questions.
3. Explain what should happen after an application restart with RAM versus a database backend.

## Interview questions and concise answers

**Q1. How is short-term memory implemented in LangGraph?**  
Store conversation state in checkpoints and reuse the thread ID for later turns.

**Q2. What is a checkpointer?**  
A component that saves and loads graph-state snapshots for a thread.

**Q3. Why choose PostgreSQL over in-memory saving?**  
To retain checkpoints beyond the lifetime of one application process.

**Q4. Does persistence remove the context-window limit?**  
No. The stored history may be larger than what one model call can read.

**Q5. What is trimming?**  
Selecting a smaller set of messages to send to the model, usually subject to a token or turn limit.

**Q6. What is summarization?**  
Compressing older turns into a concise representation of important context while keeping recent messages.


## Further learning

- [docs.langchain.com — Add Memory](https://docs.langchain.com/oss/python/langgraph/add-memory)
- [docs.langchain.com — Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)

**One-sentence summary:** Short-term memory preserves the conversation state of a thread using checkpoints so later invocations can use earlier messages.
