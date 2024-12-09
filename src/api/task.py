from fastapi import status, APIRouter
from fastapi.responses import JSONResponse
from src.db.queries import get_task_status, get_results
from src.cache import get_cached_data, cache_data

task_router = APIRouter(prefix="/v1")


@task_router.get("/status/{task_id}")
def task_status(task_id):
    """
    Endpoint to check status of a task
    """

    task_status = get_task_status(task_id)
    if task_status:
        return JSONResponse(task_status, status_code=status.HTTP_200_OK)
    else:
        return JSONResponse(
            {"error": "Task not found"}, status_code=status.HTTP_404_NOT_FOUND
        )


@task_router.get("/results/{task_id}")
def task_results(task_id):
    """
    Endpoint to retrieve results of a task
    """
    # get data from cache
    cache_key = f"pr_analysis_results:{task_id}"
    cached_results = get_cached_data(cache_key)
    if cached_results:
        return JSONResponse(cached_results, status_code=status.HTTP_200_OK)

    results = get_results(task_id)
    if results:
        cache_data(
            cache_key, {"task_id": task_id, "status": "completed", "results": results}
        )

        return JSONResponse(
            {"task_id": task_id, "status": "completed", "results": results},
            status_code=status.HTTP_200_OK,
        )
    else:
        return JSONResponse(
            {"error": "Task not found"}, status_code=status.HTTP_404_NOT_FOUND
        )
