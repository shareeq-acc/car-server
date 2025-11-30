from fastapi import APIRouter, Query
from typing import Optional
from app.controllers.comparison_controller import ComparisonController

router = APIRouter(prefix="/compare", tags=["Comparison"])
comparison_controller = None


def init_routes(controller: ComparisonController):
    global comparison_controller
    comparison_controller = controller


@router.get("/")
def compare_models(
    model1: str = Query(..., description="First car model (first word)"),
    model2: str = Query(..., description="Second car model (first word)"),
    metric: str = Query("price", description="Comparison metric: price, popularity, depreciation, features"),
    make1: Optional[str] = Query(None, description="First car make (optional, for filtering)"),
    make2: Optional[str] = Query(None, description="Second car make (optional, for filtering)"),
    years_to_use: int = Query(7, ge=3, le=20, description="Years to use for price predictions")
):
    """
    Compare two models based on specified metric.
    
    Metrics:
    - price: Compare price trends with ML predictions (past & future)
    - popularity: Compare market share and demand
    - depreciation: Compare value retention rates
    - features: Compare technical specifications
    """
    return comparison_controller.compare_models(model1, model2, metric, make1, make2, years_to_use)
