from typing import TypedDict

class ReviewState(TypedDict):
    code: str
    bug_result: str
    security_result: str
    style_result: str
    performance_result: str
    suggested_fixes: str
    fixed_code: str