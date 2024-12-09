import os
from ollama import chat
from ollama import ChatResponse
from celery import Celery
from github import Github
from src.db.queries import update_result
from src.cache import cache_data

celery = Celery(__name__)
celery.conf.broker_url = os.getenv("CELERY_BROKER_URL")
celery.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND")


@celery.task(name="pr_analyzer")
def pr_analyzer(data):
    g = Github(data.get("github_token"))
    repo = g.get_repo(data["repo_url"].split("github.com/")[-1])
    pr = repo.get_pull(data["pr_number"])
    files = pr.get_files()

    ai_input_string = ""

    for file in files:
        file_name = file.filename
        patch_content = file.patch
        patch_lines = patch_content.split("\n")

        added_lines = []
        line_number = 0

        for line in patch_lines:
            if line.startswith("+ ") and not line.startswith("+++"):
                line_number += 1
                added_line = line[2:]
                added_lines.append(f"Line {line_number}: {added_line}")

        if added_lines:
            ai_input_string += f"File: {file_name}\n"
            ai_input_string += "\n".join(added_lines) + "\n\n"

    response: ChatResponse = chat(
        model="llama3.2",
        messages=[
            {
                "role": "system",
                "content": """
                You are an AI code reviewer. Review the code based on the following criteria:

                1. **Style**: Check for formatting issues, inconsistent naming, and code style violations.
                2. **Bugs**: Identify potential bugs, logical errors, or unhandled edge cases.
                3. **Performance**: Suggest optimizations for performance improvements.
                4. **Best Practices**: Ensure adherence to good coding practices (e.g., modularity, error handling).

                Output the review in this format:

                {
                        "files": [
                            {
                                "name": "<file_name>",
                                "issues": [
                                    {
                                        "type": "<issue_type>",
                                        "line": <line_number>,
                                        "description": "<issue_description>",
                                        "suggestion": "<suggestion_for_fix>"
                                    }
                                ]
                            }
                        ],
                        "summary": {
                            "total_files": <number_of_files>,
                            "total_issues": <total_number_of_issues>,
                            "critical_issues": <number_of_critical_issues>
                        }
                    }

                Output rules:
                1. Only return JSON format, don't mention any remark below or above the JSON output.
                2. Do not use ``` or any other delimiter to highlight the results.
            """,
            },
            {
                "role": "user",
                "content": ai_input_string,
            },
        ],
    )
    update_result(
        pr_analyzer.request.id,
        response.message.content,
    )
