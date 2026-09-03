# Pydantic Structured Data Extraction

A production-style AI mini-project that uses an LLM with Pydantic and LangChain to convert unstructured natural-language text into strongly typed, validated Python objects.

The purpose of this project is not just to demonstrate `with_structured_output()`. The project was built to understand the engineering problems around reliable structured LLM output: schema design, validation, missing and ambiguous information, invalid model output, retries, error handling, testing, and consuming structured data in an application.

---

## 1. Project Objective

Large Language Models are very good at understanding natural language, but application code usually needs predictable data structures.

For example, given:

```text
John Smith is 28 years old and works at Google as a Software Engineer.
He has 5 years of experience.
```

we want the LLM to produce data equivalent to:

```json
{
  "name": "John Smith",
  "age": 28,
  "company": "Google",
  "role": "Software Engineer",
  "experience_years": 5
}
```

Instead of allowing the model to return arbitrary text, this project converts the response into a Pydantic model.

---

## 2. Why Free-Form LLM Output Is a Problem

An LLM can return something like:

```text
John Smith is a 28-year-old Software Engineer at Google with 5 years of experience.
```

This is useful for humans, but it is inconvenient for an application.

The application would have to parse the text itself.

For example:

```python
person.name
person.age
person.company
person.role
person.experience_years
```

cannot be reliably accessed if the model only returns free-form text.

The model could also:

- change the wording
- return fields in a different order
- omit information
- invent information
- return invalid values
- return extra text
- return malformed JSON

This is why structured output is important when an LLM is part of an application pipeline.

---

## 3. Structured Output

The core idea is:

```text
Unstructured Text
       |
       v
      LLM
       |
       v
Structured Schema
       |
       v
Pydantic Object
       |
       v
Application
```

Instead of asking the model to simply "answer", we tell it what structure the application expects.

In this project, the expected structure is represented by a Pydantic model.

---

## 4. Why Pydantic?

Pydantic allows us to define the expected shape and validation rules of our data using Python types.

Conceptually:

```python
class Person(BaseModel):
    name: str
    age: int | None
    company: str
    role: str
    experience_years: int | None
```

This gives the application a contract.

The LLM is responsible for extracting information from natural language, while Pydantic gives the application a strongly typed representation of that information.

This separation is important:

```text
LLM
↓
Extract information
↓
Structured schema
↓
Validate data
↓
Application logic
```

---

# 5. Project Architecture

```text
                Natural Language Input
                         |
                         v
                  +--------------+
                  |   LangChain  |
                  +--------------+
                         |
                         v
                    Groq LLM
                         |
                         v
               Structured Output
                         |
                         v
                  +--------------+
                  |   Pydantic   |
                  |    Person    |
                  +--------------+
                         |
                         v
              Validated Python Object
                         |
                         v
                    Application
```

The project is intentionally small, but the architecture represents a pattern that can be used inside larger AI applications.

---

# 6. Technology Stack

- Python
- LangChain
- LangChain Groq integration
- Pydantic
- Groq
- pytest
- uv for Python environment and dependency management

The project uses environment variables for the Groq API key.

---

# 7. Project Structure

```text
01. Pydantic Structured Extraction/
│
├── app/
│   ├── __init__.py
│   ├── extractor.py
│   ├── main.py
│   └── schemas.py
│
├── test/
│   ├── test_extraction.py
│   └── test_schema.py
│
├── .gitignore
├── .python-version
├── README.md
├── pyproject.toml
├── requirements.txt
└── uv.lock
```

### `schemas.py`

Contains the Pydantic model that defines the expected structured data.

### `extractor.py`

Contains the LLM and extraction logic.

This is where the natural-language input is sent to the model and converted into the Pydantic structure.

### `main.py`

Provides a simple application entry point and demonstrates the extraction.

### `test_extraction.py`

Tests the behavior of the LLM-powered extraction pipeline.

### `test_schema.py`

Tests the Pydantic validation rules independently.

---

# 8. Pydantic Schema

The project extracts five pieces of information:

| Field | Type | Meaning |
|---|---|---|
| `name` | `str` | Person's name |
| `age` | `int \| None` | Person's actual age |
| `company` | `str` | Company where the person works |
| `role` | `str` | Person's job role |
| `experience_years` | `int \| None` | Professional experience in years |

Some fields are optional because real-world text may not contain every piece of information.

For example:

```text
Michael works at Amazon as a Data Scientist.
```

does not provide age or professional experience.

The expected result is therefore conceptually:

```text
name = "Michael"
age = None
company = "Amazon"
role = "Data Scientist"
experience_years = None
```

---

# 9. Important Extraction Rule

One of the most important lessons from this project was that **not every number mentioned in a sentence represents the field we are extracting**.

For example:

```text
John is an experienced engineer at Google.
He joined the company when he was 25.
```

The number `25` describes John's age when he joined the company.

It does **not** necessarily represent John's current age.

The expected result is therefore:

```text
name = "John"
age = None
company = "Google"
role = "engineer"
experience_years = None
```

The prompt/schema instructions were adjusted so that contextual information is not incorrectly mapped to the requested field.

This is an important real-world lesson: structured output does not automatically mean semantically correct extraction.

---

# 10. Initial Working Version

The first goal was to build the smallest working pipeline:

```text
Input text
   ↓
Groq Chat Model
   ↓
LangChain structured output
   ↓
Person Pydantic object
```

The application successfully produced:

```text
name='John Smith'
age=28
company='Google'
role='Software Engineer'
experience_years=5
```

This proved that the basic structured extraction pipeline was working.

---

# 11. Problems We Encountered

This project was intentionally developed incrementally, and several real-world problems appeared during development.

## Problem 1 — Groq Model Error

The first model configuration used:

```text
llama-3.3-70b-versatile
```

The Groq API returned:

```text
404
model_not_found
```

The important lesson was that model names and availability can change.

The model configuration was updated to use a currently available Groq model.

### Lesson

Do not assume an LLM model name will always remain available.

Model configuration should be treated as a configurable part of the application.

---

## Problem 2 — Tool Choice / Structured Output Failure

At one point Groq returned:

```text
Tool choice is required, but model did not call a tool
```

The model generated a normal natural-language response instead of producing the required structured tool output.

The generated response also incorrectly interpreted the validation constraints and refused to extract the data.

### Lesson

Using structured output does not guarantee that every model invocation will succeed.

The application still needs to handle:

- model failures
- malformed responses
- tool-calling failures
- validation failures

---

## Problem 3 — Invalid Extraction

A test case contained:

```text
John Smith is -10 years old ...
He has -5 years of experience.
```

The desired behavior was not to accept negative values.

The schema validation rules therefore became an important part of the application.

Instead of allowing invalid values into the application, invalid values are handled as missing/invalid information according to the extraction behavior defined by the project.

### Lesson

LLM output should not be trusted just because it looks structured.

The structured result still needs validation.

---

## Problem 4 — Ambiguous Information

This was one of the most interesting failures:

```text
John is an experienced engineer at Google.
He joined the company when he was 25.
```

The model initially returned:

```text
age = 25
```

But this was incorrect for the application's definition of `age`.

The test expected:

```text
age = None
```

because the text did not provide John's current age.

The extraction instructions were refined to distinguish between:

```text
John is 25 years old.
```

and:

```text
John joined the company when he was 25.
```

### Lesson

A schema validates the structure and values, but semantic correctness still depends heavily on the extraction instructions and model behavior.

---

# 12. Error Handling and Retries

The application was then extended beyond a simple:

```python
structured_model.invoke(text)
```

call.

The extraction layer handles failures and uses bounded retry behavior when appropriate.

The application exposes a controlled extraction failure instead of allowing a low-level LLM exception to crash the entire application unexpectedly.

Conceptually:

```text
Input
  |
  v
LLM extraction
  |
  +---- Success ------> Pydantic object
  |
  +---- Failure
          |
          v
       Retry
          |
          +---- Success ------> Pydantic object
          |
          +---- Failure ------> ExtractionError
```

This is much closer to how an LLM component should behave inside a real application.

---

# 13. Testing Strategy

The project was not considered complete after one successful example.

Tests were added for different categories of input.

## Normal extraction

```text
John Smith is 28 years old and works at Google
as a Software Engineer. He has 5 years of experience.
```

Expected:

```text
John Smith
28
Google
Software Engineer
5
```

---

## Different wording

```text
Sarah is a 32-year-old backend engineer at Microsoft.
She has been working professionally for 8 years.
```

Expected:

```text
Sarah
32
Microsoft
backend engineer
8
```

This verifies that the system is not dependent on exactly one sentence structure.

---

## Missing information

```text
Michael works at Amazon as a Data Scientist.
```

Expected:

```text
name = Michael
company = Amazon
role = Data Scientist
age = None
experience_years = None
```

This verifies that missing information does not have to be invented.

---

## Ambiguous information

```text
John is an experienced engineer at Google.
He joined the company when he was 25.
```

Expected:

```text
name = John
company = Google
role = engineer
age = None
experience_years = None
```

This verifies contextual ambiguity.

---

## Invalid information

```text
John Smith is -10 years old and works at Google
as a Software Engineer. He has -5 years of experience.
```

Expected:

```text
name = John Smith
company = Google
role = Software Engineer
age = None
experience_years = None
```

This verifies validation behavior.

---

# 14. Test Result

The final test suite contains:

```text
13 passed
```

The important point is not just the number of tests.

The tests cover different failure and edge-case categories:

```text
Normal input
Different wording
Missing information
Ambiguous information
Invalid information
Schema validation
Error behavior
```

The project was only considered complete after the complete test suite passed.

---

# 15. Running the Application

From the project directory:

```bash
uv run python -m app.main
```

Example output:

```text
name='John Smith' age=28 company='Google' role='Software Engineer' experience_years=5
```

---

# 16. Running the Tests

Run:

```bash
uv run python -m pytest
```

Expected result:

```text
13 passed
```

Using:

```bash
uv run python -m pytest
```

also ensures that pytest runs through the uv-managed Python environment.

---

# 17. Environment Variables

The application uses a Groq API key through an environment variable.

Local `.env`:

```text
GROQ_API_KEY=your_actual_key
```

The `.env` file must never be committed to GitHub.

A safe `.env.example` can contain:

```text
GROQ_API_KEY=your_groq_api_key_here
```

---

# 18. GitHub Secret Scanning Incident

While pushing the project to GitHub, GitHub Push Protection detected that the original Git commit contained the Groq API key inside:

```text
01. Pydantic Structured Extraction/.env
```

GitHub rejected the push with:

```text
GH013: Repository rule violations found
Push cannot contain secrets
```

This was an important practical security lesson.

Simply deleting `.env` from the current working directory is not enough if the secret already exists inside Git history.

The commit was amended so that `.env` was no longer tracked, and the project was successfully pushed afterward.

### Lesson

API keys must be protected at both levels:

```text
Local development
      |
      +---- .env

Git
      |
      +---- .gitignore

GitHub
      |
      +---- Secret scanning / Push Protection
```

Secrets should never be committed to source control.

If a real API key is accidentally exposed, it should be rotated/revoked.

---

# 19. What This Project Demonstrates

This mini-project demonstrates a complete basic structured extraction pipeline:

```text
Natural Language
      ↓
Prompt / Extraction Instructions
      ↓
Groq Chat Model
      ↓
LangChain Structured Output
      ↓
Pydantic Schema
      ↓
Validation
      ↓
Retry / Error Handling
      ↓
Validated Python Object
      ↓
Application / API
```

This is more representative of a real AI engineering component than simply calling an LLM and printing its response.

---

# 20. How Another Application Could Consume the Result

The extraction function returns a typed Pydantic object.

For example:

```python
person = extract_person(text)
```

The application can then use:

```python
person.name
person.age
person.company
person.role
person.experience_years
```

The result can also be converted into a dictionary/JSON representation for an API or database.

Conceptually:

```text
LLM Extraction Service
        |
        v
   Person object
        |
        +------> REST API
        |
        +------> Database
        |
        +------> Search Index
        |
        +------> Another AI Pipeline
        |
        +------> Business Application
```

This is one of the main advantages of structured LLM output.

---

# 21. Production Improvements

This project is intentionally small, but a production implementation could add:

### Input validation

Validate the input before sending it to the model.

For example:

- empty input
- excessively large input
- unsupported content
- invalid request format

### Schema versioning

Schemas can change over time.

For example:

```text
PersonV1
PersonV2
PersonV3
```

Versioning helps maintain compatibility with downstream applications.

### Better retry strategy

Production retries could include:

- exponential backoff
- maximum retry count
- retry only for retryable errors
- model fallback

### Observability

Track:

- request count
- successful extractions
- failed extractions
- validation failures
- retry count
- latency
- token usage
- model name
- schema version

### Model fallback

If the primary model fails:

```text
Model A
   |
   X
   |
Model B
```

A fallback model can improve availability.

### Latency optimization

LLM calls can be expensive and slow.

Production systems can consider:

- smaller models
- shorter prompts
- batching
- caching
- asynchronous execution

### Cost control

Track:

```text
requests
tokens
model pricing
retries
average cost/request
```

Retries should be bounded because repeated LLM calls increase cost.

### Security

Never expose:

- API keys
- secrets
- sensitive user information

Logs should also be designed carefully so that sensitive input is not accidentally recorded.

---

# 22. Important Concepts Learned

### 1. Structured output

LLMs can be constrained to produce data that follows an expected structure.

### 2. Pydantic

Pydantic provides a typed data contract and validation layer.

### 3. Schema design

The schema determines what information the application expects.

### 4. Semantic correctness

A response can be structurally valid but semantically wrong.

Example:

```text
He joined the company when he was 25.
```

does not necessarily mean:

```text
current_age = 25
```

### 5. Missing information

The system should represent unknown information as `None` rather than forcing the LLM to guess.

### 6. Validation

LLM output should be validated before it reaches business logic.

### 7. Retries

LLM calls can fail and need controlled retry behavior.

### 8. Testing

LLM applications need more than one happy-path example.

### 9. Error handling

Low-level provider errors should be converted into controlled application-level failures where appropriate.

### 10. Secret management

API keys must never be committed to Git repositories.

---

# 23. Interview Perspective

This project can lead to questions such as:

- Why use Pydantic with an LLM?
- What problem does structured output solve?
- Is structured output enough to guarantee correctness?
- How do you handle missing information?
- How do you handle invalid LLM output?
- How would you retry failed LLM calls?
- When should a request be retried?
- How would you monitor an extraction service?
- How would you reduce LLM latency?
- How would you control LLM cost?
- How would you version an extraction schema?
- What happens if the model stops supporting structured output?
- How would you expose this extractor as an API?
- How would you protect API keys in production?

---

# 24. Final Outcome

The final application is a small but complete AI engineering component:

```text
                 ┌─────────────────────┐
                 │ Natural Language    │
                 │ Input               │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ LangChain + Groq    │
                 │ Chat Model          │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Structured Output   │
                 │ / Extraction        │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Pydantic Person     │
                 │ Schema              │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Validation + Error  │
                 │ Handling / Retry    │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Validated Person    │
                 │ Object              │
                 └─────────────────────┘
```

The project started as a simple structured-output experiment and evolved into a more realistic extraction component by testing failure modes, ambiguity, validation, retries, and security.

---

## Resume Description

**Production-Style Pydantic Structured Data Extraction** — Built a LangChain and Groq-powered information extraction pipeline that converts unstructured natural-language text into validated Pydantic objects. Implemented schema validation, handling for missing/ambiguous/invalid information, bounded retry and error handling, and a 13-test automated test suite. Secured API credentials using environment variables and GitHub secret protection.
