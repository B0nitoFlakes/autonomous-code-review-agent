from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def run_agent(system_prompt: str, code: str)-> str:
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role":"system", "content":system_prompt},
            {"role":"user", "content": f"Review this code: \n\n{code}"}
        ]
    )
    return response.choices[0].message.content

async def bug_agent(code:str)-> str:
    return await run_agent("""You are a bug detection specialist. 
    ONLY look for bugs, logic errors, null pointer issues, and incorrect implementations.
    Be specific with line numbers. Do NOT use any emojis. Format your response under: BUGS FOUND""", code)

async def security_agent(code: str) -> str:
    return await run_agent("""You are a security specialist.
    ONLY look for real confirmed security vulnerabilities like SQL injection, hardcoded credentials, exposed secrets, command injection, XSS, and other unsafe patterns.
    Be specific with line numbers.
    
    Safe patterns that should NOT be flagged as vulnerabilities:
    - document.createTextNode() — safely inserts plain text, not vulnerable to XSS
    - parameterized SQL queries with ? placeholders — not vulnerable to injection
    - encodeURIComponent() — safe URL encoding
    
    Do not flag code as vulnerable based on speculation or missing context.
    Do NOT use any emojis. Format your response under: SECURITY ISSUES""", code)

async def style_agent(code: str) -> str:
    return await run_agent("""You are a code style specialist.
    ONLY look for style issues like naming conventions, missing docstrings, and readability problems.
    Be specific with line numbers. Do NOT use any emojis. Format your response under: CODE STYLE""", code)

async def performance_agent(code: str) -> str:
    return await run_agent("""You are a performance specialist.
    ONLY look for performance issues like unnecessary loops, inefficient algorithms, and memory problems.
    Be specific with line numbers. Do NOT use any emojis. Format your response under: PERFORMANCE""", code)

async def synthesizer_agent(bug_result: str, security_result: str, style_result: str, performance_result: str) -> str:
    return await run_agent("""You are a code review synthesizer.
    You will receive findings from 4 specialist agents. Combine them into one clean structured report and add a SUGGESTED FIXES section at the end.
    Format: BUGS FOUND, SECURITY ISSUES, CODE STYLE, PERFORMANCE, SUGGESTED FIXES. Do NOT use any emojis""",
    f"""Bug findings: {bug_result}
    Security findings: {security_result}
    Style findings: {style_result}
    Performance findings: {performance_result}""")

async def autofix_agent(code: str, review_report: str) -> str:
    return await run_agent(f"""You are an expert code fixer.
    You will receive the original code and a review report highlighting issues.
    Rewrite the code with all the fixes applied.
    Only fix what is mentioned in the review report.
    Do not change anything else.
    Return only the fixed code, no explanations.""",
    f"""Original code:\n{code}\n\nReview report:\n{review_report}""")