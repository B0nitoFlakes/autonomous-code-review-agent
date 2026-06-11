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
    Do NOT flag AsyncOpenAI, AsyncClient, or any OpenAI SDK class names as bugs.
    Do NOT flag gpt-4o, gpt-4, or any OpenAI model names as bugs.
    Do NOT recommend replacing existing library implementations with older or alternative patterns.
    If you are unsure whether a class or method exists in the latest version of a library, skip it entirely.
    Do NOT flag third-party libraries, class names, or model names as bugs unless you are 100% certain that they are universally recognized as incorrect.
    If you are unsure whether a library or class exists, do not flag it.
    Be specific with line numbers. Do NOT use any emojis.
    Use markdown formatting for clarity — bold for emphasis and numbered lists for findings.
    Do not add a header or title at the top of your response. The section title is already provided.""", code)

async def security_agent(code: str) -> str:
    return await run_agent("""You are a security specialist.
    ONLY look for real confirmed security vulnerabilities like SQL injection, hardcoded credentials, exposed secrets, command injection, XSS, and other unsafe patterns.
    Be specific with line numbers.
    
    Safe patterns that should NOT be flagged as vulnerabilities:
    - document.createTextNode() — safely inserts plain text, not vulnerable to XSS
    - parameterized SQL queries with ? placeholders — not vulnerable to injection
    - encodeURIComponent() — safe URL encoding
    
    Do not flag code as vulnerable based on speculation or missing context.
    Do NOT use any emojis.
    Use markdown formatting for clarity — bold for emphasis and numbered lists for findings.
    Do not add a header or title at the top of your response. The section title is already provided.""", code)

async def style_agent(code: str) -> str:
    return await run_agent("""You are a code style specialist.
    ONLY look for style issues like naming conventions, missing docstrings, and readability problems.
    Be specific with line numbers. Do NOT use any emojis.
    Use markdown formatting for clarity — bold for emphasis and numbered lists for findings.
    Do not add a header or title at the top of your response. The section title is already provided.""", code)

async def performance_agent(code: str) -> str:
    return await run_agent("""You are a performance specialist.
    ONLY look for performance issues like unnecessary loops, inefficient algorithms, and memory problems.
    Be specific with line numbers. Do NOT use any emojis. 
    Use markdown formatting for clarity — bold for emphasis and numbered lists for findings.
    Do not add a header or title at the top of your response. The section title is already provided.""", code)

async def suggester_agent(bug_result: str, security_result: str, style_result: str, performance_result: str) -> str:
    return await run_agent("""You are a code improvement suggester.
    You will receive findings from 4 specialist agents.
    Do NOT restate or summarize the findings.
    ONLY provide actionable fix suggestions based on the findings.
    Do NOT provide the code itself, only the suggestions.
    Use markdown formatting for clarity — bold for emphasis and numbered lists for findings.
    Do not add a header or title at the top of your response. The section title is already provided.""",
    f"""Bug findings: {bug_result}
    Security findings: {security_result}
    Style findings: {style_result}
    Performance findings: {performance_result}""")

async def autofix_agent(code: str, bug_result:str, security_result:str, style_result:str, performance_result:str, suggested_fixes: str) -> str:
    return await run_agent(f"""You are an expert code fixer.
    You will receive the original code.
    You will receive bug, security, style, and performance results highlighting the issues found.
    You will also receive suggested fixes that provide suggestions on how to correct the code.
    Rewrite the code with all the fixes applied.
    Only fix what is mentioned in the issues and suggestions.
    Do not change anything else.
    Use markdown formatting for clarity — bold for emphasis and numbered lists for findings.
    Do not add a header or title at the top of your response. The section title is already provided.
    Return ONLY the fixed code, NO EXPLANATIONS.""",
    f"""Original code:\n{code}\n\nBug Results\n{bug_result}\n\nSecurity Results\n{security_result}\n\nStyle Results\n{style_result}\nPerformance Result\n{performance_result}\n\nSuggested fixes:\n{suggested_fixes}""")