from fastapi import HTTPException
from app.services.comparison_service import ComparisonService


class ComparisonController:
    def __init__(self, comparison_service: ComparisonService):
        self.comparison_service = comparison_service
    
    def compare_models(self, model1: str, model2: str, metric: str = "price",
                      make1: str = None, make2: str = None, years_to_use: int = 7):
        result, error = self.comparison_service.compare_models(
            model1, model2, metric, make1, make2, years_to_use
        )
        
        if error:
            raise HTTPException(status_code=400, detail=error)
        
        return result
