import ast
import re


def review_python(code):

    issues = []

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        issues.append({
            "type": "Syntax Error",
            "severity": "High",
            "line": e.lineno,
            "message": e.msg,
            "suggestion": "Check the syntax around this line."
        })

        return {
            "issues": issues,
            "score": 30,
            "summary": "The code contains a syntax error."
        }

    lines = code.splitlines()

    # Detect print statements
    for i, line in enumerate(lines, 1):

        if "print(" in line:
            issues.append({
                "type": "Code Quality",
                "severity": "Low",
                "line": i,
                "message": "Print statement found.",
                "suggestion": "Use logging instead of print statements in production applications."
            })

    # Detect very long lines
    for i, line in enumerate(lines, 1):

        if len(line) > 100:
            issues.append({
                "type": "Readability",
                "severity": "Low",
                "line": i,
                "message": "Line is longer than 100 characters.",
                "suggestion": "Break the line into smaller logical sections."
            })

    # Detect hardcoded passwords
    password_pattern = r"(password|passwd|pwd)\s*=\s*['\"].+['\"]"

    for i, line in enumerate(lines, 1):

        if re.search(password_pattern, line, re.IGNORECASE):
            issues.append({
                "type": "Security",
                "severity": "High",
                "line": i,
                "message": "Possible hardcoded password detected.",
                "suggestion": "Use environment variables or a secure secret manager."
            })

    # Detect eval()
    for i, line in enumerate(lines, 1):

        if "eval(" in line:
            issues.append({
                "type": "Security",
                "severity": "High",
                "line": i,
                "message": "Use of eval() detected.",
                "suggestion": "Avoid eval() because it can execute untrusted code."
            })

    # Detect unused-looking variables
    assigned_variables = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Assign):

            for target in node.targets:

                if isinstance(target, ast.Name):
                    assigned_variables.append(target.id)

    for variable in assigned_variables:

        if variable.startswith("_"):
            continue

        occurrences = code.count(variable)

        if occurrences == 1:

            issues.append({
                "type": "Code Quality",
                "severity": "Low",
                "line": 1,
                "message": f"Variable '{variable}' may be unused.",
                "suggestion": "Remove the variable if it is not required."
            })

    # Calculate score
    score = 100

    for issue in issues:

        if issue["severity"] == "High":
            score -= 20

        elif issue["severity"] == "Medium":
            score -= 10

        else:
            score -= 5

    score = max(score, 0)

    if score >= 90:
        quality = "Excellent"
    elif score >= 75:
        quality = "Good"
    elif score >= 50:
        quality = "Needs Improvement"
    else:
        quality = "Poor"

    return {
        "issues": issues,
        "score": score,
        "quality": quality,
        "summary": f"Found {len(issues)} potential issue(s)."
    }


def review_javascript(code):

    issues = []

    lines = code.splitlines()

    for i, line in enumerate(lines, 1):

        if "console.log(" in line:
            issues.append({
                "type": "Code Quality",
                "severity": "Low",
                "line": i,
                "message": "console.log() found.",
                "suggestion": "Remove debugging statements before production."
            })

        if "eval(" in line:
            issues.append({
                "type": "Security",
                "severity": "High",
                "line": i,
                "message": "eval() detected.",
                "suggestion": "Avoid eval() because it can execute arbitrary code."
            })

        if len(line) > 100:
            issues.append({
                "type": "Readability",
                "severity": "Low",
                "line": i,
                "message": "Very long line detected.",
                "suggestion": "Break the statement into smaller sections."
            })

    score = 100

    for issue in issues:

        if issue["severity"] == "High":
            score -= 20
        else:
            score -= 5

    score = max(score, 0)

    if score >= 90:
        quality = "Excellent"
    elif score >= 75:
        quality = "Good"
    elif score >= 50:
        quality = "Needs Improvement"
    else:
        quality = "Poor"

    return {
        "issues": issues,
        "score": score,
        "quality": quality,
        "summary": f"Found {len(issues)} potential issue(s)."
    }


def review_code(code, language):

    if language.lower() == "python":
        return review_python(code)

    elif language.lower() in ["javascript", "js"]:
        return review_javascript(code)

    else:
        return {
            "issues": [],
            "score": 0,
            "quality": "Unsupported",
            "summary": "This language is not currently supported."
        }