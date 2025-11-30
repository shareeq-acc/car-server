from fastapi import HTTPException
from app.services.data_service import DataService


class CarController:
    def __init__(self, data_service: DataService):
        self.data_service = data_service
    
    def get_makes(self):
        makes = self.data_service.get_all_makes()
        return {"makes": makes, "count": len(makes)}
    
    def get_models(self, make: str, year_min=None, year_max=None, 
                   price_min=None, price_max=None, page=1, limit=10):
        available_makes = [m.lower() for m in self.data_service.get_all_makes()]
        if make.lower() not in available_makes:
            raise HTTPException(status_code=404, detail=f"Make '{make}' not found")
        
        models = self.data_service.get_models_by_make(
            make, year_min, year_max, price_min, price_max
        )
        
        total_count = len(models)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_models = models[start_idx:end_idx]
        
        return {
            "make": make,
            "models": paginated_models,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": (total_count + limit - 1) // limit
            },
            "filters": {
                "year_min": year_min,
                "year_max": year_max,
                "price_min": price_min,
                "price_max": price_max
            }
        }
    
    def search_cars(self, make=None, model=None, year_min=None, year_max=None,
                    price_min=None, price_max=None, mileage_min=None, mileage_max=None,
                    transmission=None, fuel_type=None, city=None, seller_type=None,
                    page=1, limit=10):
        filtered_df = self.data_service.search_cars(
            make, model, year_min, year_max, price_min, price_max,
            mileage_min, mileage_max, transmission, fuel_type, city, seller_type
        )
        
        total_count = len(filtered_df)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_df = filtered_df.iloc[start_idx:end_idx]
        
        cars = paginated_df[['make', 'model', 'year', 'price', 'mileage', 'transmission',
                              'fuel_type', 'engine_capacity', 'city', 'seller_type', 'url']].to_dict('records')
        
        return {
            "cars": cars,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": (total_count + limit - 1) // limit
            }
        }
    
    def get_statistics(self):
        return self.data_service.get_statistics()
    
    def get_filters(self):
        return self.data_service.get_filters()
    
    def price_analysis(self, group_by: str, make=None, model=None, year=None):
        if group_by not in ['make', 'model', 'year', 'city']:
            raise HTTPException(status_code=400, detail="group_by must be one of: make, model, year, city")
        
        analysis = self.data_service.price_analysis(group_by, make, model, year)
        
        return {
            "group_by": group_by,
            "filters": {"make": make, "model": model, "year": year},
            "analysis": analysis
        }
    
    def predict_price(self, model: str, make=None, years_to_use=7):
        result, error = self.data_service.predict_price(model, make, years_to_use)
        
        if error:
            raise HTTPException(status_code=404 if "No data" in error else 400, detail=error)
        
        return {
            "model": model,
            "make": make,
            **result
        }
