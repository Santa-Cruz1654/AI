# Stateful AI Workflow with LangGraph

A small but properly designed **stateful AI workflow built with
LangGraph and Groq**.

The project was developed incrementally to understand how LangGraph
maintains state across multiple nodes, routes execution conditionally,
and supports iterative plan revision.

The workflow accepts a user request, analyzes it, generates a plan,
reviews the plan, revises it when necessary, and finally generates a
response.

------------------------------------------------------------------------

## 1. Project Objective

The original goal was to build a workflow that follows this execution
pattern:

``` text
START
  |
  v
Analyze Request
  |
  v
Generate Plan
  |
  v
Review Plan
  |
  +---- Good ------> Final Response
  |
  +---- Bad -------> Generate Plan
                         |
                         +---- Review again
  |
  v
END
```

The important concept is that **state is maintained throughout the
workflow**.

The project was intentionally kept small so that the core LangGraph
concepts could be understood before moving toward production-grade AI
workflows.

------------------------------------------------------------------------

# 2. Technologies Used

-   Python
-   LangGraph
-   LangChain
-   Groq
-   GPT-OSS 120B
-   `TypedDict`
-   Structured LLM output
-   Conditional routing

------------------------------------------------------------------------

# 3. What I Wanted to Learn

The project was designed around the following LangGraph concepts:

-   `TypedDict`
-   State
-   Nodes
-   Edges
-   `START`
-   `END`
-   State updates
-   Conditional edges
-   Workflow execution
-   Reusable node functions
-   Error handling
-   State tracing / basic observability
-   Iterative workflow loops

------------------------------------------------------------------------

# 4. High-Level Architecture

The final workflow is:

``` text
                         +------------------+
                         |   START          |
                         +--------+---------+
                                  |
                                  v
                       +----------------------+
                       |  Analyze Request     |
                       |      Groq LLM        |
                       +----------+-----------+
                                  |
                                  v
                       +----------------------+
                       |   Generate Plan      |
                       |      Groq LLM        |
                       +----------+-----------+
                                  |
                                  v
                       +----------------------+
                       |     Review Plan      |
                       |      Groq LLM        |
                       +----------+-----------+
                                  |
                           Conditional Router
                                  |
                    +-------------+-------------+
                    |                           |
                 APPROVED                    REVISE
                    |                           |
                    v                           |
          +----------------------+              |
          |   Final Response     |              |
          |      Groq LLM        |              |
          +----------+-----------+              |
                     |                          |
                     v                          |
                    END <-----------------------+
```

There is also an error path:

``` text
Review / Generate / other node
            |
            v
       Error detected
            |
            v
      Error Handler
            |
            v
           END
```

------------------------------------------------------------------------

# 5. State: The Core of the Workflow

The workflow uses a `TypedDict` to define its state.

``` python
from typing_extensions import TypedDict


class State(TypedDict):
    request: str
    analysis: str
    plan: str
    review: str
    suggestions: list[str]
    approval: bool
    revision_count: int
    final_response: str
    error: str
```

The `State` object acts as the shared memory of the workflow.

Each node:

1.  Receives the current state.
2.  Reads the fields it needs.
3.  Performs its task.
4.  Returns a partial state update.
5.  LangGraph merges the update into the workflow state.

For example:

``` python
return {
    "analysis": "The request should be broken into clear steps."
}
```

Only the `analysis` field is updated.

The rest of the state remains available to subsequent nodes.

------------------------------------------------------------------------

# 6. State Fields

## `request`

The original user request.

Example:

``` text
Create a learning plan for LangGraph
```

------------------------------------------------------------------------

## `analysis`

The interpretation of the request produced by the analysis node.

Example:

``` text
The user request is: Create a learning plan for LangGraph.
The request should be broken into clear, structured steps.
```

------------------------------------------------------------------------

## `plan`

The plan generated by the planner node.

Example:

``` text
1. Understand LangGraph fundamentals
2. Learn state and nodes
3. Build a simple graph
4. Add conditional routing
5. Implement a review loop
```

------------------------------------------------------------------------

## `review`

The reviewer's explanation of whether the plan is acceptable.

Example:

``` text
The plan needs more detail.
It should explicitly validate each task.
```

------------------------------------------------------------------------

## `suggestions`

Specific improvement instructions produced by the reviewer.

Example:

``` python
[
    "Add practical exercises",
    "Add validation criteria"
]
```

This field allows the planner to receive structured feedback when
revising the plan.

------------------------------------------------------------------------

## `approval`

Boolean decision produced by the reviewer.

``` text
True  -> plan accepted
False -> plan needs revision
```

------------------------------------------------------------------------

## `revision_count`

Tracks how many times the plan has been generated.

Example:

``` text
0 -> no plan yet
1 -> first plan
2 -> first revision
3 -> second revision
```

This also helps protect the workflow from an infinite revision loop.

------------------------------------------------------------------------

## `final_response`

The final response generated after the plan is approved.

------------------------------------------------------------------------

## `error`

Stores an error message if a node fails.

An empty value means no error occurred.

------------------------------------------------------------------------

# 7. Nodes

The workflow is divided into reusable node functions.

## 7.1 Analyze Request

Purpose:

-   Read the original request.
-   Understand what the user is asking for.
-   Produce an analysis that can be used by the planner.

Conceptually:

``` text
State
  |
  | request
  v
Analyze Request
  |
  | analysis
  v
Updated State
```

The node reads:

``` python
state["request"]
```

and updates:

``` python
{
    "analysis": ...
}
```

------------------------------------------------------------------------

# 8. Generate Plan

The planner creates a plan from the request and analysis.

On the first execution it generates the initial plan.

When the review rejects the plan, the same node is executed again.

During revision, it receives:

-   Original request
-   Analysis
-   Previous plan
-   Review feedback
-   Reviewer suggestions
-   Revision count

This allows the planner to improve the previous plan instead of simply
starting from scratch.

Conceptually:

``` text
             Previous State
                  |
        +---------+---------+
        |                   |
        v                   v
   Previous Plan       Review Feedback
        |                   |
        +---------+---------+
                  |
                  v
          Generate Plan
                  |
                  v
              New Plan
```

The planner updates:

``` python
{
    "plan": ...,
    "revision_count": revision_count + 1
}
```

------------------------------------------------------------------------

# 9. Review Plan

The reviewer evaluates the generated plan.

The reviewer determines:

``` text
APPROVED
```

or:

``` text
REVISE
```

The reviewer also produces feedback.

The output is stored in state as:

``` python
{
    "review": ...,
    "suggestions": [...],
    "approval": True/False
}
```

The reviewer therefore does not directly decide which node executes
next.

It only updates the state.

The router makes that decision.

------------------------------------------------------------------------

# 10. Conditional Routing

After the review node completes, a routing function checks the state.

Conceptually:

``` python
if state["error"]:
    return "handle_error"

if state["approval"]:
    return "final_response"

return "generate_plan"
```

Therefore:

``` text
Review
  |
  +---- error -------> Error Handler
  |
  +---- approved ----> Final Response
  |
  +---- rejected ----> Generate Plan
```

This is one of the most important LangGraph concepts demonstrated by the
project.

The workflow is not just a linear sequence.

It can make a decision based on the current state.

------------------------------------------------------------------------

# 11. Review Loop

The revision loop is the central feature of this project.

Suppose the first generated plan is:

``` text
Plan #1
```

The reviewer may return:

``` text
approval = False

review =
"The plan needs more detail."

suggestions =
[
    "Add practical exercises",
    "Add validation criteria"
]
```

The router sees:

``` text
approval = False
```

and routes execution back to:

``` text
Generate Plan
```

The planner now receives the review feedback and suggestions.

It generates:

``` text
Plan #2
```

The reviewer evaluates Plan #2.

If it is approved:

``` text
approval = True
```

the router sends execution to:

``` text
Final Response
```

This creates the following loop:

``` text
Generate Plan
      |
      v
 Review Plan
      |
      |
   REVISE
      |
      v
Generate Plan
      |
      v
 Review Plan
      |
      |
  APPROVED
      |
      v
Final Response
```

------------------------------------------------------------------------

# 12. Why the State Is Important

Without state, the planner would not have access to information from
previous nodes.

For example, after review:

``` text
review =
"The plan needs more detail."
```

and:

``` text
suggestions =
[
    "Add practical exercises",
    "Add validation criteria"
]
```

These values are stored in the state.

When execution returns to the planner, the planner can access:

``` python
state["review"]
state["suggestions"]
state["plan"]
```

Therefore the workflow has memory **within the execution**.

This is the fundamental idea behind a stateful LangGraph workflow.

------------------------------------------------------------------------

# 13. State Tracing

A basic tracing mechanism was added to make the state visible during
execution.

Before a node runs, the current state is printed.

Example:

``` text
============================================================
STATE ENTERING: GENERATE PLAN
============================================================
request:        Create a learning plan for LangGraph
analysis:       ...
plan:           ...
review:         ...
approval:       False
revision_count: 1
final_response:
error:
```

After the node runs, its state update is printed:

``` text
============================================================
STATE UPDATE FROM GENERATE PLAN:
============================================================
{
    "plan": "...",
    "revision_count": 2
}
```

This makes it possible to observe:

``` text
State Before Node
        |
        v
      Node
        |
        v
State Update
```

and then understand how LangGraph carries that updated state to the next
node.

------------------------------------------------------------------------

# 14. Example Execution

For the request:

``` text
Create a learning plan for LangGraph
```

the execution looked conceptually like this:

### Step 1 - Initial State

``` text
request:        Create a learning plan for LangGraph
analysis:
plan:
review:
approval:       False
revision_count: 0
final_response:
error:
```

------------------------------------------------------------------------

### Step 2 - Analyze Request

The analysis node produces:

``` text
analysis:
The user request is: Create a learning plan for LangGraph.
The request should be broken into clear, structured steps.
```

------------------------------------------------------------------------

### Step 3 - Generate Plan

The planner produces Plan #1.

State:

``` text
revision_count: 1
plan: Plan #1
```

------------------------------------------------------------------------

### Step 4 - Review Plan

The reviewer rejects the first plan.

``` text
review:
The plan needs more detail.
It should explicitly validate each task.

approval:
False
```

------------------------------------------------------------------------

### Step 5 - Conditional Routing

The router sees:

``` text
approval = False
```

and chooses:

``` text
generate_plan
```

------------------------------------------------------------------------

### Step 6 - Generate Plan Again

The planner receives the review feedback.

It increments:

``` text
revision_count: 2
```

and generates the revised plan.

------------------------------------------------------------------------

### Step 7 - Review Again

The reviewer now approves:

``` text
review:
The plan is sufficiently detailed.

approval:
True
```

------------------------------------------------------------------------

### Step 8 - Final Response

The final response node uses the approved plan and produces:

``` text
Request:
Create a learning plan for LangGraph

Analysis:
...

Approved Plan:
...

Review:
The plan is sufficiently detailed.

Revisions:
1
```

The workflow then reaches:

``` text
END
```

------------------------------------------------------------------------

# 15. Error Handling

Basic error handling was added to the workflow.

For example, if plan generation fails, a node can return:

``` python
{
    "error": str(e)
}
```

The router can then detect:

``` python
if state["error"]:
    return "handle_error"
```

This gives the workflow a failure path instead of allowing every failure
to become an uncontrolled exception.

A plan-generation failure therefore becomes:

``` text
Generate Plan
      |
      X
      |
      v
Error State
      |
      v
Error Handler
      |
      v
END
```

------------------------------------------------------------------------

# 16. Safety Against Infinite Loops

A review loop must have a termination strategy.

The project therefore uses a maximum revision limit.

Conceptually:

``` text
MAX_REVISIONS = 3
```

If the workflow keeps rejecting the plan beyond the allowed number of
revisions, the reviewer can produce an error such as:

``` text
Maximum revisions exceeded.
```

This prevents an accidental infinite loop.

------------------------------------------------------------------------

# 17. Project Structure

The project is organized as:

``` text
02. Stateful AI Workflow with LangGraph/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── graph.py
│   ├── state.py
│   ├── llm.py
│   │
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── analyzer.py
│   │   ├── planner.py
│   │   ├── reviewer.py
│   │   ├── response.py
│   │   └── error_handler.py
│   │
│   ├── routing/
│   │   ├── __init__.py
│   │   └── review_router.py
│   │
│   └── utils/
│       ├── __init__.py
│       └── tracing.py
│
├── .gitignore
├── .python-version
├── pyproject.toml
├── requirements.txt
├── uv.lock
└── README.md
```

The exact file set can evolve as the project is extended.

------------------------------------------------------------------------

# 18. Complete Execution Model

The complete execution can be understood as:

``` text
Initial State
     |
     v
START
     |
     v
Analyze Request
     |
     | analysis
     v
Generate Plan
     |
     | plan + revision_count
     v
Review Plan
     |
     | review + suggestions + approval
     v
Conditional Router
     |
     +-------------------+
     |                   |
     | approval=True     | approval=False
     v                   v
Final Response       Generate Plan
     |                   |
     v                   |
    END <----------------+
```

The state moves through the graph:

``` text
State
  |
  +--> Analyze
  |       |
  |       +--> analysis
  |
  +--> Generate Plan
  |       |
  |       +--> plan
  |       +--> revision_count
  |
  +--> Review
  |       |
  |       +--> review
  |       +--> suggestions
  |       +--> approval
  |
  +--> Final Response
          |
          +--> final_response
```

------------------------------------------------------------------------

# 19. Problems Faced During Development

The project was intentionally built incrementally, and several real
implementation issues occurred.

## Issue 1 - Missing `build_graph`

Initially, `main.py` attempted:

``` python
from app.graph import build_graph
```

but the function was not available from `app.graph`.

This produced:

``` text
ImportError: cannot import name 'build_graph'
```

The problem was an import/API mismatch between the graph module and the
main entry point.

### Lesson

When using a modular Python project, the exported function name and the
import statement must match.

------------------------------------------------------------------------

# 20. Issue 2 - Missing `review_plan`

After fixing the graph import, the next error was:

``` text
ImportError: cannot import name 'review_plan'
from 'app.nodes.reviewer'
```

The graph expected:

``` python
review_plan
```

but the reviewer module did not expose a function with that exact name.

### Lesson

Every node registered in the graph must exist and be importable from the
module used by the graph builder.

------------------------------------------------------------------------

# 21. Issue 3 - Missing `final_response`

The next import problem was:

``` text
ImportError: cannot import name 'final_response'
from 'app.nodes.response'
```

Again, the graph expected a specific node function while the module did
not expose the same function name.

### Lesson

The graph definition acts as the integration point between all node
modules. Naming consistency matters.

------------------------------------------------------------------------

# 22. Issue 4 - `approved` vs `approval`

A runtime error occurred:

``` text
KeyError: 'approved'
```

The router was trying to access:

``` python
state["approved"]
```

while the actual State definition used:

``` python
approval: bool
```

The reviewer also returned:

``` python
"approval": ...
```

The mismatch caused the runtime failure.

### Fix

The router was changed to use:

``` python
state["approval"]
```

instead of:

``` python
state["approved"]
```

### Lesson

State field names are contracts between nodes.

If one part of the workflow calls a field:

``` text
approval
```

another part cannot call it:

``` text
approved
```

unless both are intentionally defined.

This is a very important lesson for larger LangGraph systems.

------------------------------------------------------------------------

# 23. Issue 5 - GitHub Folder Was Not Opening

When uploading the project to the existing GitHub repository, the
project initially appeared as a folder but could not be opened normally.

The Git inspection showed:

``` text
160000 commit <commit-hash>
```

for:

``` text
02. Stateful AI Workflow with LangGraph
```

The `160000` mode indicated that Git was tracking the directory as a
**gitlink/submodule**, rather than as a normal directory containing
project files.

The project also had its own nested:

``` text
02. Stateful AI Workflow with LangGraph/.git/
```

### Fix

The nested Git repository was removed:

``` bash
rm -rf "02. Stateful AI Workflow with LangGraph/.git"
```

Then the incorrect gitlink was removed from the parent index:

``` bash
git rm --cached "02. Stateful AI Workflow with LangGraph"
```

The project directory was then added as normal files:

``` bash
git add "02. Stateful AI Workflow with LangGraph"
```

and committed/pushed to the parent repository.

### Lesson

For a repository containing multiple projects as folders, each project
should normally be a regular directory unless a submodule is
intentionally required.

------------------------------------------------------------------------

# 24. GitHub Repository Organization

The parent repository is:

``` text
AI
```

The intended structure is:

``` text
AI/
│
├── 01. Pydantic Structured Extraction/
│
└── 02. Stateful AI Workflow with LangGraph/
```

Project 02 is therefore a **folder inside the main AI repository**,
rather than a separate GitHub repository.

------------------------------------------------------------------------

# 25. Environment Variables and Security

The project uses a `.env` file for secrets such as the Groq API key.

The `.env` file should never be committed to GitHub.

The `.gitignore` contains entries such as:

``` gitignore
.env
.venv/
__pycache__/
*.pyc
```

The virtual environment is also excluded:

``` text
.venv/
```

This prevents credentials and local environment files from being
accidentally published.

------------------------------------------------------------------------

# 26. What This Project Demonstrates

This project demonstrates the difference between a simple sequential
Python program and a stateful graph workflow.

A traditional sequential program might look like:

``` text
function1()
function2()
function3()
function4()
```

The LangGraph version is state-driven:

``` text
State
  |
  v
Node
  |
  v
State Update
  |
  v
Conditional Routing
  |
  +----> Node
  |
  +----> Another Node
  |
  +----> Loop
```

The workflow can therefore:

-   preserve state
-   make decisions
-   branch
-   loop
-   retry a logical step
-   handle failures
-   maintain execution context

------------------------------------------------------------------------

# 27. Why This Is a Mini Project

The project qualifies as a small AI Engineering mini project because it
contains:

-   A real user request
-   LLM-powered processing
-   Multiple reusable nodes
-   Shared workflow state
-   Conditional routing
-   Iterative revision
-   Structured reviewer output
-   Error handling
-   State tracing
-   External LLM integration using Groq

It is intentionally small enough to understand completely while
demonstrating the fundamental architecture used in larger agentic
workflows.

------------------------------------------------------------------------

# 28. Production Improvements

The current implementation is a learning-focused workflow.

A production version could add:

## Checkpointing

Persist workflow state so execution can resume after failure.

``` text
Workflow
   |
   v
Checkpoint
   |
   v
Persistent Storage
```

------------------------------------------------------------------------

## State Persistence

Store state outside the process so it can survive application restarts.

Possible storage layers could include:

-   PostgreSQL
-   Redis
-   other durable state stores

------------------------------------------------------------------------

## Retries

Transient LLM/API failures should be retried using controlled retry
policies.

``` text
LLM Call
   |
   X
   |
Retry
   |
   +---- success
   |
   +---- failure -> error handling
```

------------------------------------------------------------------------

## Timeouts

LLM calls and external services should have bounded execution times.

------------------------------------------------------------------------

## Human Approval

A production workflow could pause before the final response:

``` text
Review
   |
   v
Human Approval
   |
   +---- Approve --> Final Response
   |
   +---- Reject --> Generate Plan
```

------------------------------------------------------------------------

## Observability

The basic state tracing in this project could be replaced or extended
with production observability containing:

-   execution IDs
-   node timings
-   LLM latency
-   token usage
-   model information
-   failures
-   retries
-   state transitions
-   trace IDs

------------------------------------------------------------------------

## Long-Running Workflows

A production workflow may execute over minutes, hours, or days.

Checkpointing and resumability become important in such systems.

------------------------------------------------------------------------

## API Integration

The workflow could be exposed through:

``` text
Client
  |
  v
FastAPI
  |
  v
LangGraph Workflow
  |
  v
Groq
```

The API could accept a request such as:

``` json
{
  "request": "Create a learning plan for LangGraph"
}
```

and return:

``` json
{
  "response": "...",
  "revision_count": 2
}
```

------------------------------------------------------------------------

## Scaling

For multiple users, the workflow should be designed so that:

-   each execution has its own state
-   state is persisted independently
-   workers can execute workflows concurrently
-   external services are protected with rate limits
-   retries are controlled
-   observability is available

------------------------------------------------------------------------

# 29. Interview Questions

This project can be used to discuss the following interview questions.

### LangGraph Basics

1.  What is LangGraph?
2.  Why use LangGraph instead of a normal Python workflow?
3.  What is a node?
4.  What is an edge?
5.  What are `START` and `END`?
6.  What is a conditional edge?

### State

7.  Why does an AI workflow need state?
8.  Why did you use `TypedDict`?
9.  What happens when a node updates only one state field?
10. How is state passed between nodes?
11. What happens if a required state field is missing?

### Workflow Design

12. How does your review loop work?
13. How does the router decide whether to revise the plan?
14. How do you prevent an infinite loop?
15. How would you handle an LLM failure?
16. How would you persist state?

### Production

17. How would you add checkpointing?
18. How would you add retries?
19. How would you add human approval?
20. How would you monitor the workflow?
21. How would you scale this system?
22. How would you expose it as an API?
23. How would you handle long-running workflows?

------------------------------------------------------------------------

# 30. Resume-Worthy Project Description

### Stateful AI Workflow with LangGraph

**Built a stateful AI workflow using LangGraph and Groq's GPT-OSS 120B
model that analyzes user requests, generates and reviews structured
plans, conditionally routes execution, and iteratively revises plans
using reviewer feedback. Implemented typed workflow state, reusable
nodes, conditional edges, revision-loop control, structured LLM outputs,
error handling, and execution-level state tracing.**

### Short Resume Version

> Built a stateful LangGraph workflow using Groq GPT-OSS 120B with typed
> state, conditional routing, LLM-based plan generation/review,
> iterative revision loops, structured outputs, error handling, and
> state tracing.

------------------------------------------------------------------------

# 31. Key Learning

The most important concept learned from this project is:

> **LangGraph is not just about calling an LLM multiple times. It is
> about defining how state moves through a graph of computation and how
> that state determines what happens next.**

The core pattern is:

``` text
State
  |
  v
Node
  |
  v
State Update
  |
  v
Routing Decision
  |
  +---------> Next Node
  |
  +---------> Different Node
  |
  +---------> Loop
  |
  +---------> END
```

That pattern is the foundation for building more advanced stateful AI
and agentic systems.

------------------------------------------------------------------------

# 32. Final Project Status

**Project: Stateful AI Workflow with LangGraph**

Status:

``` text
Mini Project: COMPLETE
```

Core workflow:

``` text
START
  ↓
Analyze Request
  ↓
Generate Plan
  ↓
Review Plan
  ↓
Conditional Routing
  ├── Revise → Generate Plan
  ├── Approve → Final Response
  └── Error → Error Handler
  ↓
END
```

The project provides a complete foundation for moving from simple LLM
calls toward more advanced LangGraph workflows involving persistence,
checkpointing, human-in-the-loop approval, observability, retries, APIs,
and scalable long-running execution.
