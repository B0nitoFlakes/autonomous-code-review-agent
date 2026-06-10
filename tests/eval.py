import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

import asyncio
from deepeval import evaluate
from deepeval.evaluate import AsyncConfig, DisplayConfig
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams
from backend.reviewer import review_code

async def get_review(code: str)-> str:
    result = await review_code(code)
    return "\n\n".join([
        result["bug_result"],
        result["security_result"],
        result["style_result"],
        result["performance_result"],
        result["suggested_fixes"]
    ])

# ---- 1. VULNERABLE CODE ----

VULNERABLE_PYTHON = """
def login(username, password):
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    api_key = "sk-1234567890abcdef"
    os.system("rm -rf " + username)
    return query
"""

VULNERABLE_JS = """
function renderComment(userInput) {
    document.getElementById('comments').innerHTML = userInput
    var adminPassword = "admin123"
    eval(userInput)
}
"""

VULNERABLE_SQL = """
SELECT * FROM users WHERE username = '' + username + ''
DELETE FROM orders WHERE user_id = '' + user_id + ''
UPDATE users SET password = '' + newPassword + '' WHERE id = '' + id + ''
"""


# ---- 2. CLEAN CODE ----

CLEAN_PYTHON = """
def calculate_average(numbers: list[float]) -> float:
    \"\"\"Calculate the average of a list of numbers.\"\"\"
    if not numbers:
        raise ValueError("List cannot be empty")
    return sum(numbers) / len(numbers)
"""

CLEAN_JS = """
function sanitizeAndDisplay(message) {
    const text = document.createTextNode(message)
    const container = document.getElementById('output')
    if (container) {
        container.appendChild(text)
    }
}
"""

CLEAN_SQL = """
SELECT id, username, email
FROM users
WHERE id = ?
AND is_active = 1
LIMIT 1
"""


# ---- 3. EDGE CASES ----

EDGE_EMPTY_FUNCTION = """
def process():
    pass
"""

EDGE_SINGLE_LINE = """
result = [x**2 for x in range(1000000)]
"""

EDGE_MIXED_LANGUAGES = """
def run_query(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    subprocess.run(f"echo {user_id}", shell=True)
    return query
"""


# ---- 4. PARTIALLY VULNERABLE CODE ----

PARTIAL_PYTHON = """
def get_user_data(user_id: int) -> dict:
    \"\"\"Fetch user data from database.\"\"\"
    safe_query = "SELECT id, email FROM users WHERE id = ?"
    api_secret = "hardcoded_secret_key_123"
    print(f"Fetching user with secret: {api_secret}")
    return {"query": safe_query}
"""

PARTIAL_JS = """
function processUserData(userId) {
    fetch(`/api/users/${encodeURIComponent(userId)}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById('result').innerHTML = data.username
        })
}
"""


# ---- 5. MISLEADING CODE ----

MISLEADING_PYTHON = """
def authenticate(token):
    \"\"\"Authenticate user with token.\"\"\"
    if token == SECRET_TOKEN:
        return True
    return False
"""

MISLEADING_JS = """
function sanitize(input) {
    return input.replace('<script>', '')
        .replace('</script>', '')
}

function display(userInput) {
    document.getElementById('output').innerHTML = sanitize(userInput)
}
"""

async def run_evals():
    print("Starting evaluation... \n")
    print("Fetching agent outputs...\n")

    # run in batches of 3 to avoid rate limits
    batch1 = await asyncio.gather(
        get_review(VULNERABLE_PYTHON),
        get_review(VULNERABLE_JS),
        get_review(VULNERABLE_SQL),
    )
    print("Batch 1 done...\n")
    await asyncio.sleep(30)  # wait 30 seconds before next batch

    batch2 = await asyncio.gather(
        get_review(CLEAN_PYTHON),
        get_review(CLEAN_JS),
        get_review(CLEAN_SQL),
    )
    print("Batch 2 done...\n")
    await asyncio.sleep(30)

    batch3 = await asyncio.gather(
        get_review(EDGE_EMPTY_FUNCTION),
        get_review(EDGE_SINGLE_LINE),
        get_review(EDGE_MIXED_LANGUAGES),
    )
    print("Batch 3 done...\n")
    await asyncio.sleep(30)

    batch4 = await asyncio.gather(
        get_review(PARTIAL_PYTHON),
        get_review(PARTIAL_JS),
        get_review(MISLEADING_PYTHON),
        get_review(MISLEADING_JS),
    )
    print("Batch 4 done...\n")

    (out_vuln_py, out_vuln_js, out_vuln_sql) = batch1
    (out_clean_py, out_clean_js, out_clean_sql) = batch2
    (out_edge_empty, out_edge_single, out_edge_mixed) = batch3
    (out_partial_py, out_partial_js, out_mislead_py, out_mislead_js) = batch4

    print("Building test cases...\n")

    test_cases = [

        # 1. VULNERABLE CODE
        LLMTestCase(
            input="Python login function with SQL injection, hardcoded API key, and dangerous os.system call",
            actual_output=out_vuln_py,
            expected_output="Must identify SQL injection, hardcoded API key, and dangerous os.system command injection as critical issues"
        ),
        LLMTestCase(
            input="JavaScript function with XSS via innerHTML, hardcoded password, and dangerous eval",
            actual_output=out_vuln_js,
            expected_output="Must identify XSS vulnerability, hardcoded password, and dangerous eval usage as critical security issues"
        ),
        LLMTestCase(
            input="SQL queries with direct string concatenation on SELECT, DELETE, and UPDATE statements",
            actual_output=out_vuln_sql,
            expected_output="Must identify SQL injection vulnerabilities across all three queries as critical security issues"
        ),

        # 2. CLEAN CODE
        LLMTestCase(
            input="Clean Python function with type hints, docstring, empty list check, and safe math operation",
            actual_output=out_clean_py,
            expected_output="No critical bugs or security issues. Minor style suggestions acceptable but no critical flags."
        ),
        LLMTestCase(
            input="Clean JavaScript using createTextNode for safe DOM manipulation with null check",
            actual_output=out_clean_js,
            expected_output="No critical bugs or security issues. Safe DOM handling should not be flagged as vulnerable."
        ),
        LLMTestCase(
            input="Clean parameterized SQL query selecting specific columns with LIMIT",
            actual_output=out_clean_sql,
            expected_output="No critical issues. Parameterized query is the correct secure approach."
        ),

        # 3. EDGE CASES
        LLMTestCase(
            input="Empty Python function with just a pass statement",
            actual_output=out_edge_empty,
            expected_output="Should note the function is empty and does nothing. No false critical issues."
        ),
        LLMTestCase(
            input="Single line Python list comprehension generating 1 million squares",
            actual_output=out_edge_single,
            expected_output="Should identify memory concern for large list generation. No false security issues."
        ),
        LLMTestCase(
            input="Python function mixing SQL query via f-string and subprocess shell=True",
            actual_output=out_edge_mixed,
            expected_output="Must identify SQL injection via f-string and command injection via subprocess shell=True as critical issues"
        ),

        # 4. PARTIALLY VULNERABLE CODE
        LLMTestCase(
            input="Python function with good parameterized query but hardcoded secret and sensitive data logging",
            actual_output=out_partial_py,
            expected_output="Should flag hardcoded secret and sensitive logging as issues. Should NOT flag the parameterized query as vulnerable."
        ),
        LLMTestCase(
            input="JavaScript with safe fetch call but XSS via innerHTML when rendering response",
            actual_output=out_partial_js,
            expected_output="Should flag innerHTML XSS as critical. Should NOT flag the encodeURIComponent fetch as vulnerable."
        ),

        # 5. MISLEADING CODE
        LLMTestCase(
            input="Python token comparison that looks safe but is vulnerable to timing attacks",
            actual_output=out_mislead_py,
            expected_output="Ideally identifies timing attack vulnerability. If missed, acceptable since it is a subtle issue. Should not flag non-issues."
        ),
        LLMTestCase(
            input="JavaScript sanitize function that only strips script tags but still vulnerable to other XSS vectors",
            actual_output=out_mislead_js,
            expected_output="Should identify that the sanitization is incomplete and innerHTML assignment is still vulnerable to XSS via other vectors like onerror or img tags"
        ),
    ]

    print("Running evaluations...\n")

    accuracy_metric = GEval(
        name="Code Review Accuracy",
        model="gpt-4o-mini",
        criteria="""
        Evaluate the quality of the AI code review agent based on
        the accuracy of critical issue detection and avoidance of false positives.

        For vulnerable code:
        - Reward identification of real security vulnerabilities, bugs, or unsafe patterns
        - Reduce the score if critical issues are missed

        For clean code:
        - Reward correctly recognizing safe and secure code
        - Minor style or readability suggestions are acceptable
        - Reduce the score if non-existent critical vulnerabilities are falsely flagged

        For edge-case or unusual code:
        - Reward cautious and accurate reasoning
        - Reward identifying genuine performance or memory concerns when relevant
        - Reduce the score for hallucinated critical issues

        For partially vulnerable code:
        - Reward correctly distinguishing vulnerable sections from safe sections
        - Reduce the score if secure patterns are incorrectly flagged
        - Reduce the score if dangerous patterns are missed

        For misleading or subtle cases:
        - Reward identifying hidden or non-obvious issues
        - Reduce the score if the agent hallucinates unrelated critical problems

        Focus primarily on:
        - Security analysis accuracy
        - Correctness of reasoning
        - False positive avoidance
        - Quality of issue identification
        """,
        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
            SingleTurnParams.EXPECTED_OUTPUT
        ],
        threshold=0.7
    )

    evaluate(
        test_cases=test_cases,
        metrics=[accuracy_metric],
        hyperparameters={
            "model": "gpt-4o",
            "agents": "bug, security, style, performance, synthesizer, autofix",
            "evaluation_model": "gpt-4o-mini"
        },
        async_config=AsyncConfig(
            run_async=True,
            throttle_value=10,
            max_concurrent=3
        ),
        display_config=DisplayConfig(results_folder="./results")
    )

if __name__ == "__main__":
    asyncio.run(run_evals())