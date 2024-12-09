from pydantic import BaseModel


class AnalyzePRRequest(BaseModel):
    """
    Analyze model to validate payload
    """

    repo_url: str
    pr_number: int
    github_token: str | None = None