from fastapi import APIRouter, Query
from typing import Optional
from app.controllers.ml_controller import MLController

router = APIRouter(prefix="/ml", tags=["Machine Learning"])
ml_controller = None


def init_routes(controller: MLController):
    global ml_controller
    ml_controller = controller


@router.get("/estimate-price")
def estimate_price(
    make: str = Query(..., description="Car make"),
    model: str = Query(..., description="Car model"),
    year: int = Query(..., description="Manufacturing year"),
    mileage: int = Query(..., description="Mileage in km"),
    transmission: str = Query(..., description="Transmission type (Automatic/Manual)"),
    fuel_type: str = Query(..., description="Fuel type (Petrol/Diesel/Hybrid/CNG/Electric)")
):
    """Estimate car price using ML model"""
    return ml_controller.estimate_price(make, model, year, mileage, transmission, fuel_type)


@router.get("/similar-cars")
def find_similar_cars(
    make: str = Query(..., description="Car make"),
    model: str = Query(..., description="Car model"),
    year: int = Query(..., description="Year"),
    price: Optional[float] = Query(None, description="Price (optional)"),
    engine_capacity: Optional[float] = Query(None, description="Engine capacity in cc (optional)"),
    limit: int = Query(10, ge=1, le=50, description="Number of results")
):
    """Find similar cars based on specifications (excludes same model)"""
    return ml_controller.find_similar_cars(make, model, year, price, engine_capacity, limit)


@router.get("/best-value")
def find_best_value_cars(
    budget_min: float = Query(..., description="Minimum budget"),
    budget_max: float = Query(..., description="Maximum budget"),
    year_min: Optional[int] = Query(None, description="Minimum year"),
    limit: int = Query(20, ge=1, le=100, description="Number of results")
):
    """Find best value cars (underpriced/good deals) in budget range"""
    return ml_controller.find_best_value_cars(budget_min, budget_max, year_min, limit)


@router.get("/market-trend")
def analyze_market_trend(
    make: Optional[str] = Query(None, description="Car make"),
    model: Optional[str] = Query(None, description="Car model (first word)")
):
    """Analyze market trends for make/model"""
    return ml_controller.analyze_market_trend(make, model)


@router.get("/demand-prediction")
def predict_demand(
    make: Optional[str] = Query(None, description="Car make"),
    model: Optional[str] = Query(None, description="Car model (first word)"),
    city: Optional[str] = Query(None, description="City")
):
    """Predict demand/popularity for make/model/city"""
    return ml_controller.predict_demand(make, model, city)


@router.get("/anomalies")
def detect_anomalies(
    limit: int = Query(50, ge=10, le=200, description="Number of results")
):
    """Detect overpriced and underpriced cars"""
    return ml_controller.detect_anomalies(limit)
