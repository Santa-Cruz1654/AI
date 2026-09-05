# Context-Aware Production Agent

> A production-style AI engineering project focused on **Context Engineering** — controlling what information an LLM receives at each point during execution.

---

## 📌 Overview

This project builds a customer-support AI assistant using **LangChain, LangGraph, and Groq-hosted OpenAI OSS 120B**.

The purpose of this project is **not** to build another generic chatbot or tool-calling agent.

The central engineering problem is:

> **"What information should the model receive at this particular point in execution?"**

A conversational AI system can easily become inefficient when the entire conversation history is sent to the model on every request.

As conversations grow:

* Context becomes larger.
* Token usage increases.
* Latency can increase.
* Costs can increase.
* Irrelevant information can pollute the prompt.
* Old information can conflict with newer information.
* Important information can become harder for the model to identify.
* Eventually, context-window limits can become a problem.

This project demonstrates how an AI Engineer can build a **context lifecycle** around an LLM.

---

# 🎯 Project Objective

The objective is to learn and implement:

* Context Engineering
* Message History
* Short-Term State
* Conversation Summarization
* Runtime Context
* Middleware
* Dynamic Context
* System Instructions
* Tool Context
* Token Limits
* Context-Window Management
* Context Budgets
* Lifecycle Middleware
* Persistent vs Transient Context

Instead of blindly doing:

```text
Conversation History
        ↓
       LLM
```

the project evolves toward:

```text
                    ┌──────────────────────┐
                    │  Conversation State  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Context Engineering │
                    │      Middleware      │
                    └──────────┬───────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
        Recent Messages    Summary        Runtime Context
             │                 │                 │
             └─────────────────┼─────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Context Budget    │
                    └──────────┬───────────┘
                               │
                               ▼
                             LLM
                               │
                               ▼
                          AI Response
```

---

# 🏗️ Architecture

The final conceptual architecture is:

```text
                         USER
                           │
                           ▼
                  ┌─────────────────┐
                  │   Application   │
                  │     /main.py    │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Context Builder │
                  │  / Middleware   │
                  └────────┬────────┘
                           │
             ┌─────────────┼──────────────┐
             │             │              │
             ▼             ▼              ▼
       Recent History   Summary     Runtime Context
             │             │              │
             └─────────────┼──────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Context Budget  │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │      LLM        │
                  │ Groq / OpenAI   │
                  │    OSS 120B     │
                  └────────┬────────┘
                           │
                           ▼
                       RESPONSE
```

---

# 🧠 Core Engineering Question

The most important concept in this project is:

```text
The model does not need everything.

The model needs the RIGHT information.
```

Context engineering is therefore treated as an explicit engineering layer.

For every model call we ask:

1. What information is relevant?
2. What information is no longer necessary?
3. What information should remain persistent?
4. What information should only exist during execution?
5. What information should be summarized?
6. What information should be retrieved dynamically?
7. How much context can we afford to send?

---

# 📚 Concepts Covered

| Concept             | Purpose                                           |
| ------------------- | ------------------------------------------------- |
| Message History     | Maintains conversational continuity               |
| Short-Term State    | Stores the current conversation state             |
| Checkpointing       | Persists state between invocations                |
| Context Engineering | Selects the information sent to the model         |
| Summarization       | Compresses older conversation history             |
| Runtime Context     | Supplies execution-specific information           |
| Middleware          | Controls model execution lifecycle                |
| Dynamic Context     | Builds context at runtime                         |
| System Instructions | Defines model behavior                            |
| Context Budget      | Controls token allocation                         |
| Token Estimation    | Measures approximate context size                 |
| Context Window      | Limits how much information can be sent           |
| Context Pollution   | Prevents irrelevant information from accumulating |
| Transient Context   | Information used only for a particular execution  |
| Persistent Context  | Information retained across interactions          |

---

# 🛠️ Technology Stack

* **Python**
* **LangChain**
* **LangGraph**
* **Groq**
* **OpenAI OSS 120B**
* **python-dotenv**

The model is accessed through **Groq**, rather than directly through OpenAI.

---

# 📁 Project Structure

The project is organized around context engineering rather than around chatbot features.

```text
04 Context-Aware Production Agent/
│
├── app/
│   │
│   ├── main.py
│   │
│   ├── models/
│   │   └── model.py
│   │
│   ├── context/
│   │   ├── state.py
│   │   ├── middleware.py
│   │   ├── summarization.py
│   │   └── budget.py
│   │
│   └── ...
│
├── .env
├── pyproject.toml
└── README.md
```

> The exact files can evolve as the project progresses, but the architectural responsibility of each module remains centered around context management.

---

# 🔐 Environment Configuration

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_groq_api_key
```

The API key should never be committed to GitHub.

Add `.env` to `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

---

# 🚀 Running the Application

From the project root:

```bash
python -m app.main
```

The application starts an interactive customer-support session:

```text
Context-Aware Customer Support Agent
Type 'exit' to stop.

You:
```

Example:

```text
You: where is my order

Assistant: I’m happy to help track your order! Could you please provide the order number?
```

The important part is that the application is maintaining conversational state while also measuring and controlling the context sent to the model.

---

# Phase 1 — Baseline

## Objective

First, build the simplest possible conversational agent.

At this stage:

```text
User
 ↓
Conversation History
 ↓
LLM
 ↓
Response
```

There is intentionally **no optimization**.

The conversation is allowed to grow.

---

## Why Start With a Baseline?

Before optimizing context, we need to understand the problem.

Suppose the conversation looks like:

```text
User: Where is my order?

Assistant: Please provide your order number.

User: 123456

Assistant: Your order is being processed.

User: What is my user ID?

Assistant: customer-001

User: What address do you have?

Assistant: I don't have an address on file.

...
```

Every new request adds more messages to the conversation state.

If the complete history is eventually sent to the LLM:

```text
Message 1
Message 2
Message 3
Message 4
Message 5
...
Message N
       ↓
      LLM
```

then the context grows continuously.

---

# 📊 Context Measurement

The application measures approximately:

```text
message count
approximate token count
```

Example output:

```text
[State] messages=2 approx_tokens=46
```

As the conversation grows:

```text
[State] messages=4 approx_tokens=83

[State] messages=6 approx_tokens=133

[State] messages=8 approx_tokens=...
```

This gives us a simple way to observe the context-growth problem.

The token count is an **approximation**, not an exact tokenizer-level measurement.

---

# 💾 Conversation Persistence

A key concept in this project is the difference between:

```text
conversation history
```

and

```text
persistent application state
```

LangGraph provides checkpointing through:

```python
from langgraph.checkpoint.memory import InMemorySaver
```

and:

```python
checkpointer = InMemorySaver()
```

The agent is then created with:

```python
agent = create_agent(
    model=model,
    tools=[],
    checkpointer=checkpointer,
    ...
)
```

Each conversation is associated with a:

```text
thread_id
```

For example:

```python
config = {
    "configurable": {
        "thread_id": "customer-001"
    }
}
```

The important idea is:

```text
thread_id
     ↓
LangGraph checkpoint
     ↓
Conversation state
```

This allows multiple invocations to participate in the same conversation thread.

### Important distinction

`InMemorySaver` means the checkpointed state exists **in memory**.

It is useful for:

* learning
* development
* demonstrations
* local testing

It is **not** durable production storage.

A production system would normally use a persistent checkpoint backend.

---

# Phase 2 — Context Engineering

The baseline approach is:

```text
All History
     ↓
    LLM
```

We now introduce:

```text
All History
     ↓
Context Selection
     ↓
Relevant Context
     ↓
LLM
```

This is the beginning of **Context Engineering**.

---

# 🧠 What Is Context Engineering?

Context engineering is the process of deliberately constructing the information presented to the model for a particular execution.

Instead of asking:

> "How do I give the model more information?"

we ask:

> "What information does the model actually need right now?"

For example, if the user asks:

```text
Where is my order?
```

the model may need:

```text
Order number
Current order state
Recent conversation
User identity
Relevant account information
```

It may not need:

```text
A conversation from 50 messages ago about an unrelated topic.
```

---

# Phase 3 — Summarization

As conversations grow, simply trimming messages can lose important information.

We therefore introduce summarization.

The conceptual flow becomes:

```text
Older Messages
       ↓
  Summarization
       ↓
Conversation Summary
       +
Recent Messages
       ↓
      LLM
```

For example:

```text
Older conversation:

User: My order is 123456.

Assistant: Please provide the delivery address.

User: Los Angeles.

Assistant: Thank you.

User: The package was supposed to arrive yesterday.

...
```

can become:

```text
Conversation Summary:

Customer is asking about order #123456.
The delivery address is Los Angeles.
The package was expected yesterday and has not arrived.
```

Then only the summary plus recent messages need to be supplied.

---

# ✂️ Trimming vs Summarization

These are different strategies.

## Trimming

```text
A
B
C
D
E
F
G
H

        ↓ trim

E
F
G
H
```

Old information is simply removed.

### Advantage

Very simple and predictable.

### Disadvantage

Important information in older messages can disappear.

---

## Summarization

```text
A
B
C
D
E
F
G
H

        ↓ summarize A-D

Summary(A-D)
E
F
G
H
```

Important information can survive in compressed form.

### Advantage

Preserves important historical information.

### Disadvantage

The summarization itself can introduce:

* omissions
* incorrect details
* stale information
* loss of nuance

Therefore summarization is itself part of the context-engineering problem.

---

# Persistent State vs Model Context

This distinction is extremely important.

The system may persist information:

```text
Conversation State
```

without sending all of it to the model.

Therefore:

```text
Persistent State
        ≠
Model Context
```

For example:

```text
Persistent State
├── Full conversation
├── User metadata
├── Application state
└── Other information

                ↓ context engineering

Model Context
├── Summary
├── Recent messages
├── Relevant user information
└── Runtime information
```

The state can be larger than the context sent to the model.

---

# Phase 4 — Runtime Context

Not every piece of information should become a chat message.

Examples include:

```text
user_id
permissions
account_type
environment
application configuration
feature flags
```

This is **runtime context**.

For example:

```text
user_id = customer-001
account_type = premium
permissions = ["orders:read"]
environment = production
```

This information can be supplied to the agent execution without pretending that the user typed it.

---

# Why Runtime Context?

Consider:

```text
User:

What is my user ID?
```

The user does not need to have typed:

```text
My user ID is customer-001.
```

Instead, the application can provide:

```text
Runtime Context
       ↓
user_id = customer-001
       ↓
Middleware / Agent
       ↓
LLM
```

This is much cleaner.

---

# Runtime Context vs Conversation History

### Conversation History

Represents:

> What happened in the conversation?

### Runtime Context

Represents:

> What does the application know about this execution?

Example:

```text
Conversation:

User: Where is my order?

Runtime Context:

user_id = customer-001
account_type = premium
environment = production
permissions = orders:read
```

These are different categories of information.

---

# Phase 5 — Middleware

Middleware provides a lifecycle layer around the agent/model execution.

Conceptually:

```text
Request
   ↓
Middleware
   ↓
Context Construction
   ↓
Model
   ↓
Response
```

The middleware can inspect or modify what happens during execution.

---

# Why Middleware?

Without middleware, context logic can become scattered throughout the application.

For example:

```text
main.py
    ├── trim messages
    ├── add user information
    ├── create summary
    ├── enforce token limit
    └── modify system instructions
```

This becomes difficult to maintain.

Middleware allows these concerns to be centralized.

```text
Agent
  │
  └── Middleware
        ├── Context selection
        ├── Runtime information
        ├── Dynamic instructions
        └── Context management
```

---

# Middleware Lifecycle

The important conceptual lifecycle is:

```text
User Request
     ↓
Agent Invocation
     ↓
Middleware
     ↓
Inspect State
     ↓
Construct / Modify Context
     ↓
Model Call
     ↓
Response
```

Middleware can therefore act as a control point between application state and model execution.

---

# Phase 6 — Context Budget

We now introduce a context budget.

Example:

```text
Maximum Context = 8000 tokens
```

Instead of allowing context to grow indefinitely:

```text
Context
   ↓
Token Budget
   ↓
Maximum Allowed Context
```

---

# Context Budget Allocation

A conceptual allocation might be:

```text
8000 tokens
│
├── System Instructions
│
├── Conversation Summary
│
├── Recent Messages
│
└── Tool / Runtime Context
```

For example:

```text
System Instructions     1000
Summary                 2000
Recent Messages         4000
Runtime / Tool Context  1000
────────────────────────────
Total                   8000
```

These values are illustrative rather than fixed requirements.

---

# Why Have a Budget?

Because context has an engineering cost.

Larger context can mean:

* More tokens
* More latency
* Higher cost
* More irrelevant information
* Greater probability of context pollution

Therefore:

```text
More Context
     ≠
Better Context
```

The objective is:

```text
Maximum useful information
within a controlled context budget
```

---

# Context Pollution

Context pollution occurs when irrelevant information accumulates in the model's prompt.

Example:

```text
Current question:

Where is my order?

Context:

100 messages about:
- an old refund
- unrelated product questions
- previous conversations
- irrelevant troubleshooting
- outdated addresses
```

The model now has to process information that does not contribute to the current task.

This is why context selection matters.

---

# Context Quality

A good context strategy should optimize more than just token count.

We care about:

```text
Context Quality
├── Relevance
├── Completeness
├── Freshness
├── Correctness
└── Efficiency
```

A context containing only 500 tokens is not necessarily better than a context containing 2,000 tokens.

If those 500 tokens omit critical information, the answer quality may be worse.

Therefore:

> **Context engineering is an information-selection problem, not merely a token-reduction problem.**

---

# Final Context Lifecycle

The complete lifecycle developed in this project is:

```text
                    USER REQUEST
                         │
                         ▼
                 ┌───────────────┐
                 │ Conversation   │
                 │    State       │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │  Summarize /  │
                 │    Trim       │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │    Context    │
                 │    Builder    │
                 └───────┬───────┘
                         │
             ┌───────────┼────────────┐
             │           │            │
             ▼           ▼            ▼
          Summary     Recent       Runtime
                      Messages      Context
             │           │            │
             └───────────┼────────────┘
                         │
                         ▼
                 ┌───────────────┐
                 │ Context Budget│
                 └───────┬───────┘
                         │
                         ▼
                       LLM
                         │
                         ▼
                     RESPONSE
```

---

# 🔬 Context Quality Experiment

An important part of the project is comparing different context strategies.

The experiment compares:

### Strategy A — Full History

```text
All conversation messages
        ↓
       LLM
```

### Strategy B — Recent Only

```text
Last N messages
        ↓
       LLM
```

### Strategy C — Summary + Recent

```text
Conversation Summary
        +
Recent Messages
        ↓
       LLM
```

---

# 📊 Experiment Metrics

The experiment can measure:

```text
Message count
Character count
Approximate token count
Latency
Response quality
```

The primary goal is not simply to find the smallest prompt.

Instead, we want to understand the trade-off:

```text
Context Size
     ↕
Answer Quality
     ↕
Latency
     ↕
Cost
```

---

# Example Experiment

A conversation containing order information might produce:

```text
Strategy: full_history

Messages: 11
Approx tokens: 125
Latency: 2.22s
```

while a recent-only strategy might produce:

```text
Strategy: recent_only

Messages: 2
Approx tokens: 22
Latency: 0.80s
```

and summary + recent might produce:

```text
Strategy: summary_plus_recent

Messages: 3
Approx tokens: 84
Latency: 2.06s
```

These numbers are **illustrative measurements from a particular execution**, not universal benchmarks.

The important observation is that context strategies can produce different:

* context sizes
* latency
* responses
* information retention

---

# ⚠️ Why Full History Is Not Always Better

Full history provides maximum historical information.

But it also creates problems.

```text
Full History
    │
    ├── More tokens
    ├── More latency
    ├── More cost
    ├── More irrelevant information
    └── Greater context pollution
```

---

# ⚠️ Why Recent Messages Are Not Always Better

Recent-only context is efficient:

```text
Recent Messages
       ↓
Small Context
       ↓
Low Token Usage
```

But important historical information can disappear.

For example:

```text
Earlier:

Order number = 123456

Later:

User: Can you track it?
```

If the order number is outside the recent window, the model may no longer know which order the user is referring to.

---

# ⚠️ Why Summary + Recent Is Often Useful

Summary + recent provides two layers:

```text
Summary
   ↓
Long-term conversational meaning

Recent Messages
   ↓
Current conversational details
```

This gives the model:

```text
Historical meaning
       +
Current context
```

But summaries must be maintained carefully because they can become:

* stale
* incomplete
* incorrect
* contradictory

---

# 🧩 Production Considerations

## 1. Context Pollution

Avoid sending irrelevant historical information.

---

## 2. Context-Window Limits

Every model has a maximum context capacity.

Applications must prevent uncontrolled context growth.

---

## 3. Token Cost

More input tokens generally mean more model-processing cost.

---

## 4. Latency

Larger prompts can increase model processing time.

---

## 5. Summarization Errors

A summary can accidentally remove or change important facts.

---

## 6. Stale Information

Old information can become incorrect.

For example:

```text
Old address
     ↓
New address
```

The context strategy must prioritize the current value.

---

## 7. Permissions

Runtime context can include authorization information.

For example:

```text
permissions = ["orders:read"]
```

The model should not be trusted to enforce authorization by itself.

Authorization should be enforced by the application/tool layer.

---

## 8. Dynamic System Instructions

System instructions can be constructed dynamically using runtime information.

For example:

```text
User account:

Premium customer

Environment:

Production
```

The resulting system behavior can adapt without modifying the conversation history.

---

## 9. Persistent vs Transient Context

A production system should clearly distinguish:

```text
Persistent
──────────
Conversation state
User profile
Account information
Long-term preferences
Business records


Transient
─────────
Current request
Current tool results
Temporary instructions
Execution-specific information
```

Not everything should be permanently stored.

---

# 🏭 Production Architecture

A more realistic production implementation could evolve into:

```text
                         USER
                           │
                           ▼
                    API / Gateway
                           │
                           ▼
                 ┌──────────────────┐
                 │ Conversation     │
                 │ State Store      │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Context          │
                 │ Engineering      │
                 │ Middleware       │
                 └────────┬─────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
   Recent History     Summary Store     Runtime Context
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                          ▼
                  Context Budget
                          │
                          ▼
                     ┌─────────┐
                     │   LLM   │
                     └────┬────┘
                          │
                          ▼
                      Response
```

---

# 🎓 What This Project Teaches

The key lesson is not:

> "How do I build a chatbot?"

The key lesson is:

> **"How do I control the information an LLM sees?"**

The project demonstrates that an AI Engineer needs to think about context as a managed resource.

The model receives a deliberately constructed context rather than an uncontrolled dump of application state.

---

# 💡 Key Takeaways

### 1. State is not the same as context

```text
State
=
Everything the application remembers.

Context
=
What the model receives for this execution.
```

---

### 2. More context is not necessarily better

```text
Useful Context > Maximum Context
```

---

### 3. Summarization is compression

It attempts to preserve important meaning while reducing the amount of raw history.

---

### 4. Runtime context is different from conversation

Application metadata does not need to become a user message.

---

### 5. Middleware is a control point

Middleware allows context behavior to be applied consistently around model execution.

---

### 6. Context budgets make context management explicit

Instead of allowing context to grow indefinitely:

```text
Maximum Context
       ↓
Allocation
       ↓
Selection
```

---

### 7. Context quality must be evaluated

A context strategy should be evaluated using both:

```text
Efficiency
+
Answer Quality
```

---

# 🧪 Possible Future Extensions

The current project establishes the core context-engineering architecture.

Possible future production extensions include:

* Semantic retrieval of relevant historical messages
* Long-term user memory
* Tool-result filtering
* Permission-aware context construction
* Context caching
* Context freshness policies
* Structured user profiles
* Retrieval ranking
* More accurate tokenization
* Context observability
* Prompt/version tracking
* Context regression tests
* Automatic context-quality evaluation
* Persistent production checkpoint storage

These are natural extensions of the same central problem:

> **What information should be provided to the model at this point in execution?**

---

# 🎤 Interview Questions

## 1. What is context engineering?

**Answer:**

Context engineering is the deliberate process of selecting, constructing, and managing the information provided to an LLM for a particular execution.

---

## 2. Why shouldn't we always send the full conversation history?

Because it increases token usage, latency, cost, and context pollution, while also potentially introducing irrelevant or stale information.

---

## 3. What is the difference between state and context?

State represents information maintained by the application, while context is the subset of information selected for a particular model invocation.

---

## 4. What is conversation summarization?

Summarization compresses older conversation history into a smaller representation that preserves important information.

---

## 5. What is the difference between trimming and summarization?

Trimming removes old messages, while summarization attempts to preserve their important information in compressed form.

---

## 6. What is runtime context?

Runtime context contains execution-specific application information such as user identity, permissions, account type, environment, or configuration.

---

## 7. Why use middleware?

Middleware provides a reusable lifecycle layer where cross-cutting behavior such as context construction, dynamic instructions, logging, and model-call control can be implemented.

---

## 8. What is context pollution?

Context pollution occurs when irrelevant, stale, or unnecessary information is included in the model's context.

---

## 9. Why do we need a context budget?

To control token usage and ensure that the context remains within model limits while prioritizing the most useful information.

---

## 10. Is the smallest context always the best context?

No.

A smaller context may remove information necessary to answer the user's question.

The goal is:

```text
Optimal Context
=
Relevant + Complete + Fresh + Efficient
```

---

# 📝 Resume Description

### Context-Aware Production Agent

Built a production-style customer-support AI agent focused on context engineering using **LangChain, LangGraph, Groq, and OpenAI OSS 120B**, implementing conversation state management, checkpointing, context selection, summarization, runtime context, lifecycle middleware, and token-budget controls to dynamically construct relevant model context and reduce unnecessary historical information.

---

# 📌 Short Resume Version

**Context-Aware Production Agent** — Designed a context-engineering pipeline using LangChain/LangGraph and Groq-hosted OpenAI OSS 120B to dynamically manage conversation history, summarization, runtime context, middleware, and token budgets for efficient LLM execution.

---

# 🏁 Final Architecture Summary

The complete learning progression is:

```text
PHASE 1
Baseline
    ↓
Full Conversation History
    ↓
LLM


PHASE 2
Context Engineering
    ↓
Context Selection
    ↓
Relevant Context
    ↓
LLM


PHASE 3
Summarization
    ↓
Older Messages
    ↓
Summary
    +
Recent Messages
    ↓
LLM


PHASE 4
Runtime Context
    ↓
Application Information
    +
Conversation Context
    ↓
LLM


PHASE 5
Middleware
    ↓
Lifecycle Control
    ↓
Dynamic Context Construction
    ↓
LLM


PHASE 6
Context Budget
    ↓
Token Allocation
    ↓
Context Selection
    ↓
LLM


FINAL
┌───────────────────────────────────────────┐
│           Context-Aware Agent             │
│                                           │
│  Persistent State                         │
│        ↓                                  │
│  Summarization / Selection               │
│        ↓                                  │
│  Runtime Context                          │
│        ↓                                  │
│  Middleware                               │
│        ↓                                  │
│  Context Budget                           │
│        ↓                                  │
│  Relevant Model Context                   │
│        ↓                                  │
│  OpenAI OSS 120B via Groq                 │
│        ↓                                  │
│  Response                                 │
└───────────────────────────────────────────┘
```

---

# ⭐ Project Philosophy

This project is built around one principle:

> **An AI Engineer should not blindly pass application state to an LLM.**

Instead:

```text
Application State
       ↓
Understand what matters
       ↓
Select relevant information
       ↓
Compress when necessary
       ↓
Add runtime information
       ↓
Apply context budget
       ↓
Send only useful context
       ↓
LLM
```

That is the core of **Context Engineering**.
