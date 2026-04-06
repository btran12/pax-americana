#!/usr/bin/env python3
"""
Daily agent update for Operation Epic Fury (Iran War) entry in script.js.

Uses GitHub Copilot (via GitHub Models API) with a custom web_search tool
backed by DuckDuckGo to research the latest verified developments and update
the JavaScript data entry in place.

Required environment variable:
  GITHUB_TOKEN  — automatically provided by GitHub Actions (no extra secret needed)
"""

import datetime
import os
import re
import sys

from openai import OpenAI
from duckduckgo_search import DDGS

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SCRIPT_JS_PATH = "script.js"
IRAN_ENTRY_ID = 30
# gpt-4o is available on GitHub Models and fully supports tool/function calling
MODEL = "gpt-4o"
GITHUB_MODELS_BASE_URL = "https://models.inference.ai.azure.com"
MAX_AGENT_ITERATIONS = 20
MAX_TOKENS = 10_000


# ---------------------------------------------------------------------------
# Web search helper (DuckDuckGo — no API key required)
# ---------------------------------------------------------------------------

def search_news(query: str, max_results: int = 8, time_limit: str = "d") -> str:
    """
    Return a plain-text summary of DuckDuckGo news results for *query*.
    Falls back to weekly search if no daily results are found.
    """
    try:
        with DDGS() as ddgs:
            results = list(
                ddgs.news(
                    keywords=query,
                    region="wt-wt",
                    safesearch="moderate",
                    timelimit=time_limit,
                    max_results=max_results,
                )
            )
        # Fall back to past week if no daily results
        if not results and time_limit == "d":
            return search_news(query, max_results=max_results, time_limit="w")

        if not results:
            return f"No news results found for: {query}"

        sections = []
        for r in results:
            sections.append(
                f"TITLE: {r.get('title', '')}\n"
                f"DATE:  {r.get('date', '')}\n"
                f"SOURCE: {r.get('source', '')}\n"
                f"SUMMARY: {r.get('body', '')}\n"
                f"URL: {r.get('url', '')}"
            )
        return "\n\n---\n\n".join(sections)

    except Exception as exc:
        return f"Search error: {exc}"


# ---------------------------------------------------------------------------
# JavaScript entry extraction / replacement
# ---------------------------------------------------------------------------

def extract_iran_entry(content: str) -> tuple[str, int, int]:
    """
    Locate the JavaScript object with id: IRAN_ENTRY_ID inside *content*.

    Returns (entry_text, start_index, end_index_exclusive).
    Raises ValueError if the entry cannot be found.
    """
    pattern = rf"\{{\s*\n\s*id:\s*{IRAN_ENTRY_ID},"
    match = re.search(pattern, content)
    if not match:
        raise ValueError(
            f"Could not find entry with id: {IRAN_ENTRY_ID} in {SCRIPT_JS_PATH}"
        )

    start = match.start()
    depth = 0
    for i in range(start, len(content)):
        ch = content[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return content[start : i + 1], start, i + 1

    raise ValueError("Unbalanced braces — could not find end of Iran entry")


def extract_js_object(text: str) -> str | None:
    """
    Extract the outermost JS object literal from *text*.
    Strips leading/trailing markdown code fences if present.
    Returns None if no valid object is found.
    """
    # Strip markdown code fences
    text = re.sub(r"^```[a-z]*\n?", "", text.strip())
    text = re.sub(r"\n?```$", "", text.strip())
    text = text.strip()

    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]

    return None


# ---------------------------------------------------------------------------
# Agentic loop
# ---------------------------------------------------------------------------

def run_update_agent(current_entry: str, today_str: str) -> str | None:
    """
    Run the GitHub Copilot agent (via GitHub Models API) with web-search tool use.

    Returns the updated JavaScript object string, or None if no update
    was produced.
    """
    client = OpenAI(
        base_url=GITHUB_MODELS_BASE_URL,
        api_key=os.environ["GITHUB_TOKEN"],
    )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": (
                    "Search the web for the latest news about the US-Iran war "
                    "(Operation Epic Fury, April 2026), Iranian retaliation, "
                    "U.S. airstrikes on Iran, Iran nuclear, Iran casualties, "
                    "Iran oil, Iran ceasefire, or related developments."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query string",
                        }
                    },
                    "required": ["query"],
                },
            },
        }
    ]

    system_prompt = (
        "You are a military journalist maintaining an accurate, up-to-date historical "
        "record of the U.S.-Iran war (Operation Epic Fury) for a public website. "
        "You ONLY add factual, verified, sourced information. "
        "You NEVER fabricate events, casualty figures, or quotes. "
        "You maintain the exact JavaScript object syntax of the existing entry."
    )

    user_message = f"""Today is {today_str}.

Below is the current JavaScript entry for Operation Epic Fury (id: {IRAN_ENTRY_ID}):

```javascript
{current_entry}
```

TASK:
1. Use web_search to find the latest confirmed developments in the US-Iran war from
   the past 72 hours. Search for at least 3 different angles:
   - U.S. airstrikes / Operation Epic Fury latest
   - Iran retaliation attacks / missiles drones
   - Iran war casualties / diplomacy / ceasefire
   - Oil prices / Strait of Hormuz / Ras Tanura
2. Update the entry applying ONLY these rules:
   a. APPEND new dated events chronologically to the `description` string.
   b. UPDATE `stats` numbers when new figures appear; append "(as of {today_str})" to changed values.
   c. ADD new `keyFacts` bullets for significant events (keep list ≤ 20; drop oldest if needed).
   d. REWRITE the `outcome` paragraph to reflect the current status as of {today_str}.
   e. Update `years` only if the format needs changing (keep "Feb 28, 2026–Present").
   f. Preserve ALL existing verified facts — do not delete or alter past events.
3. If there are NO significant new developments in the past 72 hours, return the entry
   EXACTLY as given, unchanged.

OUTPUT: Return ONLY the complete, updated JavaScript object literal — starting with `{{`
and ending with `}}`.  No explanation. No markdown fences. No extra text."""

    messages: list[dict] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    for iteration in range(MAX_AGENT_ITERATIONS):
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            tools=tools,
            tool_choice="auto",
            messages=messages,
        )

        choice = response.choices[0]

        if choice.finish_reason == "stop":
            text = choice.message.content or ""
            obj = extract_js_object(text)
            if obj and f"id: {IRAN_ENTRY_ID}" in obj:
                return obj
            if obj:
                print(
                    "Warning: extracted object does not contain "
                    f"id: {IRAN_ENTRY_ID} — skipping",
                    file=sys.stderr,
                )
            print("Agent finished but produced no valid JS object.", file=sys.stderr)
            return None

        if choice.finish_reason == "tool_calls":
            # Append assistant turn with tool_calls
            messages.append(choice.message.model_dump())

            for tool_call in choice.message.tool_calls or []:
                import json
                query = json.loads(tool_call.function.arguments).get("query", "")
                print(f"[iter {iteration + 1}] Searching: {query!r}")
                search_result = search_news(query)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": search_result,
                    }
                )
            continue

        # Unexpected finish reason
        print(
            f"Unexpected finish_reason: {choice.finish_reason!r}", file=sys.stderr
        )
        break

    print("Agent loop exhausted without producing a result.", file=sys.stderr)
    return None


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    api_key = os.environ.get("GITHUB_TOKEN", "")
    if not api_key:
        print("Error: GITHUB_TOKEN environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    today_str = datetime.date.today().strftime("%B %d, %Y")
    print(f"=== Iran war update agent — {today_str} ===")

    with open(SCRIPT_JS_PATH, "r", encoding="utf-8") as fh:
        content = fh.read()

    current_entry, start, end = extract_iran_entry(content)
    print(f"Found Iran entry: {len(current_entry):,} chars (positions {start}–{end})")

    updated_entry = run_update_agent(current_entry, today_str)

    if updated_entry is None:
        print("No update produced — script.js left unchanged.")
        sys.exit(0)

    if updated_entry.strip() == current_entry.strip():
        print("Agent returned entry unchanged — no new developments.")
        sys.exit(0)

    new_content = content[:start] + updated_entry + content[end:]

    with open(SCRIPT_JS_PATH, "w", encoding="utf-8") as fh:
        fh.write(new_content)

    print(f"script.js updated successfully as of {today_str}.")


if __name__ == "__main__":
    main()
