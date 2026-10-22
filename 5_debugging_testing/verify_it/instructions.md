# ✅ Verify It — Section 5 Checkpoint

This is the formal checkpoint for the whole section. Everything you
practiced comes together here: reading tracebacks bottom-up, the AI
debugging loop, and judging the AI's fix — real fix versus
symptom-suppressor.

**The scenario:** you asked an AI to draft a small expense summarizer for
your team. The draft is `broken_script.py`. It looks completely plausible.
It contains **exactly 2 bugs**. It is your job to find them, fix them,
and be able to explain every change you made.

## The rules

1. **Your only debugging tools are the traceback and your LLM.** No
   solution-peeking, no rewriting the script from scratch, no asking the
   AI to "just fix the whole file".
2. **One bug at a time.** Run the script, read the traceback bottom-up,
   fix that one bug, run again. The second bug only shows itself after the
   first is fixed.
3. **Document each fix in a comment** directly above the changed line:

   ```python
   # FIX 1: <what was wrong, why it broke, what I changed>
   ```

4. **Smallest possible change wins.** If your fix adds a `try/except`
   without changing anything inside it, re-read Lecture 5 — you just
   suppressed a symptom.

## The workflow

```bash
# from the 5_debugging_testing folder, venv activated —
# your prompt shows (.venv):
python verify_it/broken_script.py
```

It crashes. Read the traceback **bottom-up**: error type and message
first, then the file + line, then walk up the call chain. Form a guess.
Then take it to your LLM with the prompt pattern from Lecture 5 — paste
the traceback AND the context:

```
I'm debugging a Python script. It should: [WHAT THE SCRIPT IS SUPPOSED TO DO].

Here is the full traceback:
[PASTE THE ENTIRE TRACEBACK]

Here is the function it points to, plus the data it runs on:
[PASTE THE FUNCTION + THE RELEVANT DATA]

Explain what is causing this error BEFORE proposing a fix. Then propose
the smallest fix that repairs the CAUSE (not a try/except around the
symptom), and explain why it works.
```

Before applying what the AI suggests, run its answer through the
Lecture 6 litmus test: _can it explain why the error happened?_ Does the
fix change the actual faulty logic, or just wrap it in a blanket?

Apply the fix, add your `# FIX n:` comment, run again. Repeat until the
script runs clean. When both bugs are fixed, the summary should be
arithmetically consistent — check it by hand: do the category totals add
up to the total spent?

## Done when

- [ ] `broken_script.py` runs clean, start to finish
- [ ] Both fixes carry a `# FIX n:` comment explaining cause and change
- [ ] Neither fix is a bare `try/except` wrapper
- [ ] You can explain both bugs out loud, without looking at the code

Only then compare with `solution/fixed_script.py` — the solution names
each bug and shows one clean way to fix it. Your comments may differ; the
_causes_ you found must not.

That hand-check at the end — "do the totals add up?" — is a real test you
ran with your eyes. In Section 6 you'll make a machine run it for you,
every time, with pytest: a script that _proves itself_ is what the rest of
this course is built on.
