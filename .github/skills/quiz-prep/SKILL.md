---
name: quiz-prep
description: Summarize CS1066 class notes and generate practice questions to help a student study for an upcoming in-class quiz. Trigger on phrases like "prep me for the quiz", "study for quiz", "what should I know for", "summarize classnotes", "quiz prep", or any request to review or summarize class sessions before an assessment.
---

# CS1066 Quiz Prep

CS1066 quizzes are **20 minutes, closed book, written in pen, no notes or electronics**. Your job is to help the student internalize concepts — not look things up. Everything in this session should be something they can recall from memory under pressure.

## Workflow

### 1. Identify the sessions to cover

If the user does not specify which quiz or sessions to cover, ask. Each quiz typically spans:
- Two class sessions (`classnotes/cnNN.ipynb`)
- One section (`classnotes/secNN.ipynb`)
- One problem set (`psets/psetN.ipynb`)

Check the quiz directory (`quiz/`) for any existing quiz file for this quiz number. If a `.tex` file exists, read it — the problems in it are your ground truth for what will actually be tested. The student summary and practice questions should align tightly with the topics in that file.

### 2. Read the source material

Read all relevant files in full. Pay special attention to:
- Cells marked `**INSTRUCTOR_NOTES:**` — these carry the core framing and intended takeaways.
- Any bolded definitions, key comparisons, or numbered lists of principles.
- Code examples and what they're meant to illustrate.
- Section and pset questions, since those are the closest proxy to quiz questions.

### 3. Produce the study summary

Write a concise, structured summary organized by topic (not by file). Format:

```
## Topic: <name>

**What it is:** One or two sentences defining the concept.

**Why it matters / what to know cold:** The key idea the instructor emphasizes. Use the phrasing from class when possible.

**Common gotcha:** (Include only if the notes flag one explicitly.)
```

Keep the summary scannable. Bullet points over paragraphs. If two ideas are always contrasted in the notes (e.g., one-shot vs. scaffolded work), present them side by side.

### 4. Generate practice questions

After the summary, write **5–8 practice questions** modeled on the style of the actual quiz:

- Mix question types: short free-response, fill-in-the-blank, multiple choice, trace-the-code.
- Weight toward the topics with the most instructor emphasis and the most quiz `.tex` coverage.
- Keep questions closed-book appropriate — answerable from memory, not from lookup.
- Do not write answer keys unless the student explicitly asks. When they do, provide brief, direct answers that mirror the phrasing used in class.

Frame questions the way the quiz does: concrete scenarios, specific code, or forced choices — not vague "explain X" prompts.

### 5. Close with a checklist

End with a short "Before the quiz, make sure you can..." checklist — 4–6 bullet points of the specific things a student must be able to do cold, with no notes.
