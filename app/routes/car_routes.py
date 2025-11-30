from fastapi import APIRouter, Query
from typing import Optional
from app.controllers.car_controller import CarController

router = APIRouter()
car_controller = None


def init_routes(controller: CarController):
    global car_controller
    car_controller = controller


@router.get("/")
def read_root():
    return {"message": "Hello World"}


@router.get("/health")
def health_check():
    return {"status": "healthy"}


@router.get("/makes")
def get_makes():
    return car_controller.get_makes()


@router.get("/models")
def get_models(
    make: str = Query(..., description="Car make (case insensitive)"),
    year_min: Optional[int] = Query(None, description="Minimum year"),
    year_max: Optional[int] = Query(None, description="Maximum year"),
    price_min: Optional[float] = Query(None, description="Minimum price"),
    price_max: Optional[float] = Query(None, description="Maximum price"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
):
    return car_controller.get_models(make, year_min, year_max, price_min, price_max, page, limit)


@router.get("/cars")
def search_cars(
    make: Optional[str] = Query(None, description="Car make (case insensitive)"),
    model: Optional[str] = Query(None, description="Car model (case insensitive)"),
    year_min: Optional[int] = Query(None, description="Minimum year"),
    year_max: Optional[int] = Query(None, description="Maximum year"),
    price_min: Optional[float] = Query(None, description="Minimum price"),
    price_max: Optional[float] = Query(None, description="Maximum price"),
    mileage_min: Optional[int] = Query(None, description="Minimum mileage"),
    mileage_max: Optional[int] = Query(None, description="Maximum mileage"),
    transmission: Optional[str] = Query(None, description="Transmission type"),
    fuel_type: Optional[str] = Query(None, description="Fuel type"),
    city: Optional[str] = Query(None, description="City (case insensitive)"),
    seller_type: Optional[str] = Query(None, description="Seller type"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
):
    return car_controller.search_cars(
        make, model, year_min, year_max, price_min, price_max,
        mileage_min, mileage_max, transmission, fuel_type, city, seller_type,
        page, limit
    )


@router.get("/statistics")
def get_statistics():
    return car_controller.get_statistics()


@router.get("/filters")
def get_filters():
    return car_controller.get_filters()


@router.get("/price-analysis")
def price_analysis(
    group_by: str = Query("make", description="Group by: make, model, year, city"),
    make: Optional[str] = Query(None, description="Filter by make (case insensitive)"),
    model: Optional[str] = Query(None, description="Filter by model (matches first word, case insensitive)"),
    year: Optional[int] = Query(None, description="Filter by year")
):
    return car_controller.price_analysis(group_by, make, model, year)


@router.get("/price-prediction")
def price_prediction(
    model: str = Query(..., description="Model name (matches first word, case insensitive)"),
    make: Optional[str] = Query(None, description="Filter by make (case insensitive)"),
    years_to_use: int = Query(7, ge=3, le=20, description="Number of recent years to use for prediction")
):
    return car_controller.predict_price(model, make, years_to_use)