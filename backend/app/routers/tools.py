"""
Tools router — utility endpoints for agents.
POST /v1/tools/solve-challenge — decodes and solves Moltbook verification math challenges.
"""
import re
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.auth import require_api_key

router = APIRouter(prefix="/v1/tools", tags=["tools"])

# Number words → integers
NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90, "hundred": 100,
}

TENS = {"twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"}
UNITS = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine"}


def clean_challenge(text: str) -> str:
    """Strip scrambling chars — keep only letters and spaces."""
    cleaned = re.sub(r"[^a-zA-Z\s]", " ", text).lower()
    return re.sub(r"\s+", " ", cleaned).strip()


def extract_numbers(words: list[str]) -> list[float]:
    """Parse number words into integers, handling compounds like 'twenty five'."""
    numbers = []
    i = 0
    while i < len(words):
        word = words[i]
        if word in NUMBER_WORDS:
            val = NUMBER_WORDS[word]
            # compound: "twenty five", "thirty two" etc
            if word in TENS and i + 1 < len(words) and words[i + 1] in UNITS:
                val += NUMBER_WORDS[words[i + 1]]
                i += 2
            else:
                i += 1
            # handle "X hundred [and] Y"
            if numbers and i < len(words) and words[i] == "hundred":
                val = val * 100
                i += 1
                if i < len(words) and words[i] == "and":
                    i += 1
            numbers.append(float(val))
        else:
            i += 1
    return numbers


def detect_operation(text: str) -> str:
    """Infer math operation from context words."""
    subtract_words = ["slows", "slow", "loses", "lose", "remaining", "subtract",
                      "minus", "reduced", "decrease", "lost", "removed", "less"]
    multiply_words = ["times", "multiplied", "multiply", "product", "per", "each",
                      "rate", "during", "dominance"]
    add_words = ["total", "combined", "together", "adds", "plus", "sum",
                 "combined", "both", "exerts", "pushes", "force"]

    # multiply takes priority when "times" or "rate" present
    for w in multiply_words:
        if w in text:
            return "multiply"
    for w in subtract_words:
        if w in text:
            return "subtract"
    return "add"


def solve(challenge_text: str) -> str | None:
    cleaned = clean_challenge(challenge_text)
    words = cleaned.split()
    numbers = extract_numbers(words)
    operation = detect_operation(cleaned)

    if len(numbers) < 2:
        return None

    a, b = numbers[0], numbers[1]

    if operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    else:
        result = a + b

    return f"{result:.2f}"


# --- Endpoint ---

class ChallengeRequest(BaseModel):
    challenge_text: str


class ChallengeResponse(BaseModel):
    answer: str
    operation: str
    numbers: list[float]
    cleaned_text: str


@router.post("/solve-challenge", response_model=ChallengeResponse,
             dependencies=[Depends(require_api_key)])
def solve_challenge(payload: ChallengeRequest):
    cleaned = clean_challenge(payload.challenge_text)
    words = cleaned.split()
    numbers = extract_numbers(words)
    operation = detect_operation(cleaned)
    answer = solve(payload.challenge_text)

    return ChallengeResponse(
        answer=answer or "0.00",
        operation=operation,
        numbers=numbers,
        cleaned_text=cleaned,
    )
