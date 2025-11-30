from fastapi import HTTPException
from app.services.ml_service import MLService


class MLController:
    def __init__(self, ml_service: MLService):
        self.ml_service = ml_service
    
    def estimate_price(self, make: str, model: str, year: int, mileage: int,
                      transmission: str, fuel_type: str):
        result, error = self.ml_service.estimate_price(
            make, model, year, mileage, transmission, fuel_type
        )
        
        if error:
            raise HTTPException(status_code=400, detail=error)
        
        return {
            "input": {
                "make": make,
                "model": model,
                "year": year,
                "mileage": mileage,
                "transmission": transmission,
                "fuel_type": fuel_type
            },
            **result
        }
    
    def find_similar_cars(self, make: str, model: str, year: int, 
                         price: float = None, engine_capacity: float = None, 
                         limit: int = 10):
        result, error = self.ml_service.find_similar_cars(
            make, model, year, price, engine_capacity, limit
        )
        
        if error:
            raise HTTPException(status_code=400, detail=error)
        
        return {
            "reference": {
                "make": make,
                "model": model,
                "year": year,
                "price": price,
                "engine_capacity": engine_capacity
            },
            "similar_cars": result,
            "count": len(result)
        }
    
    def find_best_value_cars(self, budget_min: float, budget_max: float,
                            year_min: int = None, limit: int = 20):
        result, error = self.ml_service.find_best_value_cars(
            budget_min, budget_max, year_min, limit
        )
        
        if error:
            raise HTTPException(status_code=400, detail=error)
        
        return {
            "budget_range": {
                "min": budget_min,
                "max": budget_max
            },
            "best_value_cars": result,
            "count": len(result)
        }
    
    def analyze_market_trend(self, make: str = None, model: str = None):
        result, error = self.ml_service.analyze_market_trend(make, model)
        
        if error:
            raise HTTPException(status_code=400, detail=error)
        
        return {
            "make": make,
            "model": model,
            **result
        }
    
    def calculate_depreciation(self, make: str, model: str, purchase_year: int):
        result, error = self.ml_service.calculate_depreciation(make, model, purchase_year)
        
        if error:
            raise HTTPException(status_code=400, detail=error)
        
        return result
    
    def predict_demand(self, make: str = None, model: str = None, city: str = None):
        result, error = self.ml_service.predict_demand(make, model, city)
        
        if error:
            raise HTTPException(status_code=400, detail=error)
        
        return {
            "filters": {
                "make": make,
                "model": model,
                "city": city
            },
            **result
        }
    
    def detect_anomalies(self, limit: int = 50):
        result, error = self.ml_service.detect_anomalies(limit)
        
        if error:
            raise HTTPException(status_code=400, detail=error)
        
        return result
