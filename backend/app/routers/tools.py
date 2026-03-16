"""
Tools router — utility endpoints for agents.
POST /v1/tools/solve-challenge — decodes and solves Moltbook verification math challenges.
POST /v1/tools/post-and-verify — posts to Moltbook and solves the verification challenge atomically.
"""
import re
import os
import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.auth import require_api_key

MOLTBOOK_BASE = "https://www.moltbook.com/api/v1"
MOLTBOOK_API_KEY = os.getenv("MOLTBOOK_API_KEY", "")

router = APIRouter(prefix="/v1/tools", tags=["tools"])

NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90, "hundred": 100,
}

TENS = ["twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
UNITS = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]

# Add compound numbers to NUMBER_WORDS (e.g. "twenty five" = 25)
for _t in TENS:
    for _u in UNITS:
        NUMBER_WORDS[f"{_t} {_u}"] = NUMBER_WORDS[_t] + NUMBER_WORDS[_u]

_SINGLES = sorted((k for k in NUMBER_WORDS if " " not in k), key=len, reverse=True)

# Ordered so compounds (twenty five) are tried before singles (two, five)
ORDERED_WORDS = [f"{t} {u}" for t in TENS for u in UNITS] + _SINGLES


def make_fuzzy(word: str) -> re.Pattern:
    """Build pattern that matches a word with arbitrary non-alpha chars between letters."""
    parts = [re.escape(c) + r"[^a-zA-Z]*" for c in word if c != " "]
    # allow arbitrary junk between the two sub-words for compound numbers
    if " " in word:
        left, right = word.split(" ", 1)
        left_pat = "".join(re.escape(c) + r"[^a-zA-Z]*" for c in left)
        right_pat = "".join(re.escape(c) + r"[^a-zA-Z]*" for c in right)
        pattern = left_pat + r"[^a-zA-Z\s]*\s*" + right_pat
    else:
        pattern = "".join(re.escape(c) + r"[^a-zA-Z]*" for c in word)
    return re.compile(pattern, re.IGNORECASE)


# Pre-compile patterns for performance
PATTERNS = [(word, make_fuzzy(word)) for word in ORDERED_WORDS]


def extract_numbers(text: str) -> list[float]:
    """Find all number words in scrambled text using fuzzy matching."""
    remaining = text
    numbers = []
    positions = []

    for word, pattern in PATTERNS:
        for m in pattern.finditer(remaining):
            start, end = m.start(), m.end()
            # skip if overlaps with already-found number
            if any(s <= start < e or s < end <= e for s, e in positions):
                continue
            positions.append((start, end))
            numbers.append((start, float(NUMBER_WORDS[word])))

    numbers.sort(key=lambda x: x[0])
    return [v for _, v in numbers]


def detect_operation(text: str) -> str:
    """Infer math operation from key words in challenge."""
    subtract_words = ["slow", "lose", "los", "remaining", "minus", "less",
                      "reduced", "decrease", "removed", "subtract", "new velocity",
                      "new speed", "new force"]
    multiply_words = ["times", "multiplied", "multiply", "product",
                      "during", "dominance", "per second times", "rate"]

    lower = text.lower()
    for w in multiply_words:
        if w in lower:
            return "multiply"
    for w in subtract_words:
        if w in lower:
            return "subtract"
    return "add"


def solve(challenge_text: str) -> tuple[str, str, list[float]]:
    """Decode challenge and return (answer, operation, numbers)."""
    numbers = extract_numbers(challenge_text)
    operation = detect_operation(challenge_text)

    if len(numbers) < 2:
        raise ValueError(f"Could not extract 2 numbers from challenge. Found: {numbers}")

    # When "total" + subtract: "Two lobsters, first=X, second slows by Y → total = X + (X-Y)"
    # "Two" at start gets extracted as 2.0 — skip leading small integers that are counts not values
    if "total" in challenge_text.lower() and operation == "subtract" and len(numbers) >= 3:
        # drop leading small count words (1, 2, 3) and take last two
        operands = [n for n in numbers if n > 3] or numbers
        a, b = operands[0], operands[1] if len(operands) >= 2 else (numbers[-2], numbers[-1])
    else:
        a, b = numbers[0], numbers[1]

    if operation == "subtract":
        # Special case: "total speed of two lobsters where second slows"
        # e.g. lobster1=25, slows by 7 → total = 25 + (25-7) = 43
        if "total" in challenge_text.lower():
            result = a + (a - b)
            # But if subtract gives negative or the numbers suggest simple sub, use simple
            if result <= 0 or b >= a:
                result = a - b
        else:
            result = a - b
    elif operation == "multiply":
        result = a * b
    else:
        result = a + b

    return f"{result:.2f}", operation, numbers


# --- Endpoint ---

class ChallengeRequest(BaseModel):
    challenge_text: str


class ChallengeResponse(BaseModel):
    answer: str
    operation: str
    numbers: list[float]


@router.post("/solve-challenge", response_model=ChallengeResponse,
             dependencies=[Depends(require_api_key)])
def solve_challenge(payload: ChallengeRequest):
    try:
        answer, operation, numbers = solve(payload.challenge_text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return ChallengeResponse(answer=answer, operation=operation, numbers=numbers)


# --- post-and-verify ---

class PostAndVerifyRequest(BaseModel):
    submolt_name: str
    title: str
    content: Optional[str] = None


class PostAndVerifyResponse(BaseModel):
    success: bool
    post_id: Optional[str] = None
    verification_status: str
    detail: Optional[str] = None


@router.post("/post-and-verify", response_model=PostAndVerifyResponse,
             dependencies=[Depends(require_api_key)])
def post_and_verify(payload: PostAndVerifyRequest):
    """
    Atomically post to Moltbook and solve the verification challenge.
    Eliminates the 5-minute window problem by doing POST → solve → verify in one call.
    """
    if not MOLTBOOK_API_KEY:
        raise HTTPException(status_code=500, detail="MOLTBOOK_API_KEY not configured")

    headers = {
        "Authorization": f"Bearer {MOLTBOOK_API_KEY}",
        "Content-Type": "application/json",
    }

    # Step 1 — create the post
    post_body = {"submolt_name": payload.submolt_name, "title": payload.title}
    if payload.content:
        post_body["content"] = payload.content

    with httpx.Client(timeout=15) as client:
        post_resp = client.post(f"{MOLTBOOK_BASE}/posts", json=post_body, headers=headers)

    if post_resp.status_code not in (200, 201):
        raise HTTPException(
            status_code=502,
            detail=f"Moltbook post failed: {post_resp.status_code} {post_resp.text[:200]}"
        )

    post_data = post_resp.json()
    post_id = post_data.get("id")
    verification = post_data.get("verification", {})
    verification_code = verification.get("verification_code")
    challenge_text = verification.get("challenge_text")

    if not verification_code or not challenge_text:
        return PostAndVerifyResponse(
            success=True,
            post_id=post_id,
            verification_status="no_challenge",
            detail="Post created but no verification challenge returned",
        )

    # Step 2 — solve the challenge
    try:
        answer, _, _ = solve(challenge_text)
    except ValueError as e:
        return PostAndVerifyResponse(
            success=False,
            post_id=post_id,
            verification_status="solve_failed",
            detail=f"Post created but challenge solve failed: {e}",
        )

    # Step 3 — submit the answer
    with httpx.Client(timeout=15) as client:
        verify_resp = client.post(
            f"{MOLTBOOK_BASE}/verify",
            json={"verification_code": verification_code, "answer": answer},
            headers=headers,
        )

    if verify_resp.status_code in (200, 201):
        return PostAndVerifyResponse(
            success=True,
            post_id=post_id,
            verification_status="verified",
        )
    else:
        return PostAndVerifyResponse(
            success=False,
            post_id=post_id,
            verification_status="verify_failed",
            detail=f"Verify call failed: {verify_resp.status_code} {verify_resp.text[:200]}",
        )
