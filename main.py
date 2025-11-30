from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.data_service import DataService
from app.services.ml_service import MLService
from app.services.comparison_service import ComparisonService
from app.controllers.car_controller import CarController
from app.controllers.ml_controller import MLController
from app.controllers.comparison_controller import ComparisonController
from app.routes import car_routes, ml_routes, comparison_routes

app = FastAPI(
    title="PakWheels API",
    version="2.0.0",
    description="Car marketplace API with ML-powered features"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Initialize services
data_service = DataService('pakwheels_main_dataset.xlsx')
ml_service = MLService(data_service.df)
comparison_service = ComparisonService(data_service.df)

# Initialize controllers
car_controller = CarController(data_service)
ml_controller = MLController(ml_service)
comparison_controller = ComparisonController(comparison_service)

# Initialize routes with controllers
car_routes.init_routes(car_controller)
ml_routes.init_routes(ml_controller)
comparison_routes.init_routes(comparison_controller)

# Include routes
app.include_router(car_routes.router, tags=["Cars"])
app.include_router(ml_routes.router)
app.include_router(comparison_routes.router)
