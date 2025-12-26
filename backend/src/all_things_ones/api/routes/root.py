from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def read_root():
    return {
        "message": "All Things Ones API",
        "version": "1.0.0",
        "endpoints": {
            "/process-image": "POST - Process an image through shattering pipeline"
        },
    }
