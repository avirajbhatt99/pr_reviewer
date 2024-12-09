from fastapi import status, APIRouter
from fastapi.responses import JSONResponse
from src.models.analyze import AnalyzePRRequest
from src.worker import pr_analyzer
from src.db.queries import insert_task
from src.cache import get_cached_data, cache_data


analyzer_router = APIRouter(prefix="/v1")


@analyzer_router.post("/analyze-pr")
def analyze_pr(request: AnalyzePRRequest):
    """
    Endpoint to analyze PR
    """
    # check data in cache
    cache_key = f"pr_analysis:{request.repo_url}:{request.pr_number}"
    cached_data = get_cached_data(cache_key)
    if cached_data:
        return JSONResponse(
            {"task_id": cached_data["task_id"]},
            status_code=status.HTTP_200_OK,
        )

    # send task to celery
    task = pr_analyzer.apply_async(args=[request.model_dump()])
    cache_data(cache_key, {"task_id": task.id})
    insert_task(request.repo_url, request.pr_number, task_id=task.id, status="running")
    return JSONResponse({"task_id": task.id}, status_code=status.HTTP_202_ACCEPTED)
