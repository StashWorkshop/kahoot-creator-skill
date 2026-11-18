---
name: kahoot-creator
description: Creates a complete Kahoot for the teacher, directly in the Kahoot editor in the browser (Edge or Chrome). It covers scoping the topic, questions, timers suited to the question type, illustrations, switching to private, filing and checking. Use this skill as soon as the user wants to create, prepare or complete a kahoot, a Kahoot quiz or a revision quiz for a class, even if they misspell "kahoot" and even if they only provide a module, a course PDF or a topic.
---

# Create a Kahoot

Kahoot's AI produces mediocre questions. This skill replaces it: Claude designs the quiz with the teacher, then builds it itself in the editor. Speak to the teacher in their own language.

Before driving the browser, load the `anthropic-skills:chrome-browser` skill. The `mcp__claude-in-chrome__*` tools also work on Edge. If no browser is connected, say so and ask the teacher to open the extension. The teacher logs in to Kahoot personally: never type their password.

Read [references/kahoot-editor.md](references/kahoot-editor.md) just before building the quiz: it contains the actions that work in the editor and their pitfalls.

## 1. Scope

First read `~/.claude/kahoot-preferences.json` if it exists. It contains the settings of each class: level, any deviation from the timer scale, Kahoot folder. Do not ask again a question whose answer is in it, and state in one line the settings you reused.

Then read the material provided. For a PDF that cannot be read directly, extract the text and images with PyMuPDF. If you do not know where a file is, ask for the path instead of searching personal folders.

Then ask the missing questions with AskUserQuestion, four at most per round, your recommendation first:

- the topic and the part of the material to cover;
- the class and the number of questions;
- the question types wanted;
- the image sources: Kahoot image library, images from the material, drawn diagrams, Internet, or a mix;
- **if the quiz contains calculations**, whether to show formulas on the illustration (asked only once for the whole kahoot).

## 2. Write and get approval

Present a table before typing anything: number, question, answers with the correct one in bold, type, timer, illustration and source. The quiz is built only after this table is approved, because fixing things in the editor costs far more than fixing them in writing. For an image from the Internet, the table gives the exact URL and the license: approval counts as permission to download it.

Writing rules:

- **Progression**: order the questions from the simplest to the hardest.
- **Balance**: spread the correct answer across the four boxes, with no predictable pattern.
- **Realistic traps**: each wrong answer must match a plausible student mistake (forgotten conversion, wrong unit, confusion between quantities). Tell the teacher which one.
- **Consistent numbers**: the value in the question must match the one visible on the image.
- **Errors in the material**: report any error found in the document, without repeating it in the quiz.
- **Subscripts and superscripts**: write quantities and units as in a lesson, in the questions, the answers and the images: U₁, I₂, L₃, m³/s, 10⁶. A flat "U1" is not accepted. In the editor, use Kahoot's format (see the reference), because the Unicode characters ₁ and ² display too small there.
- **Lengths**: aim for at most 120 characters for a question and 75 for an answer, then let the editor confirm the limit of your subscription.

**Checked calculations**: run the calculation of each correct answer and each trap in a Python script before presenting the table. A mental calculation can produce a false correct answer, and it would show in front of the whole class.

### Timer by question type

Choose it yourself and apply it; the teacher corrects it in the table if they wish.

| Question type | Timer |
|---|---|
| Memory, vocabulary, true or false | 20 s |
| Reading a diagram, a graph or a symbol | 30 s |
| One-step calculation | 60 s |
| Calculation with a conversion | 90 s |
| Multi-step calculation, problem | 120 s |
| Puzzle (putting in order) | 30 to 60 s depending on the length |

A timer left at the default 20 s on a calculation measures typing speed and not understanding. Use only the values offered by Kahoot.

### Question types

The four-answer quiz remains the base. Suggest true or false for a common misconception, the puzzle for a sequence, the slider for a numeric value and the open answer for a precise word. Some types depend on the subscription: if the editor blocks one, replace it with a quiz and report it.

## 3. Prepare the illustrations

The source determines how the background is handled:

| Source | Background |
|---|---|
| Diagram, symbol or formula drawn by Claude | **Transparent** (PNG) |
| Image from the Internet | Kept |
| Image from the teacher's material | Kept |
| Kahoot image library | Kept |

For a circuit, use [scripts/circuit_schema.py](scripts/circuit_schema.py). In its labels and formulas, and also in `formula_card.py`, `_` makes a subscript and `^` a superscript: `U_1`, `10^{6}`. For any drawn diagram, use dark, thick ink with a white outline: the image is displayed small in class, and the details page places it directly on the purple background of the theme. Check the result by opening the image, on a colored background. The illustration must never give the answer, for example by labeling the component asked for.

**Formulas**: if the teacher wants them, add them to the illustration with [scripts/formula_card.py](scripts/formula_card.py). Show the general relation (`E = P · Δt`), never the solved calculation.

**Internet**: prefer sources under a free license, such as Wikimedia Commons or the Unsplash tab of the editor. Note the source and the license for the report. Put each download in a new, empty folder.

## 4. Build

Follow [references/kahoot-editor.md](references/kahoot-editor.md). The order to respect:

1. Open a blank canvas, never Kahoot's AI assistants.
2. Enter each question: text, answers, correct answer, timer, image.
3. In the settings: clear title, empty or plain description, **visibility "Privé" (Private)**, class folder.
4. Save.

Kahoot sets new quizzes to Public and fills in the title and description with AI: these three fields must be corrected every time. Leave the kahoot private unless the teacher explicitly asks otherwise. Do not start a game and do not share anything.

From 15 questions, import the text with a spreadsheet (details in the reference), then add the images by hand. For a small quiz, direct entry remains simpler.

## 5. Check

Open the details page of the kahoot, click "Afficher les réponses" (Show answers) and compare with the approved table: number of questions, texts, correct answers, timers, images and visibility. This check catches misplaced clicks that saving does not report.

## 6. Report and preferences

Finish with a short report:

- link to the kahoot, folder and visibility;
- questions, with the page of the material used;
- sources and licenses of the images;
- differences from the approved table, replaced types and points to review;
- what you did not check, in particular if the quiz was not played as a demo.

Then update `~/.claude/kahoot-preferences.json` with the settings of the class (create the file if it does not exist), in this form:

```json
{
  "classes": {
    "Class name": {
      "niveau": "year and track",
      "dossier_kahoot": "name of the Kahoot folder of the class",
      "chronos": "standard scale",
      "formules_sur_illustration": "ask"
    }
  }
}
```
