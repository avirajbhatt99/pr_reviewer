from fastapi import Response, status, APIRouter


health_router = APIRouter(prefix="/v1")


@health_router.get("/health")
def health_check():
    """
    Endpoint to check health of the server
    """
    return Response(content="Server is running", status_code=status.HTTP_200_OK)
