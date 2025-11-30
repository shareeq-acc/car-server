import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from math import log10, floor


class DataService:
    def __init__(self, dataset_path: str):
        self.df = pd.read_excel(dataset_path)
    
    def get_all_makes(self):
        makes = self.df['make'].dropna().unique().tolist()
        return sorted(makes)
    
    def get_models_by_make(self, make: str, year_min=None, year_max=None, 
                           price_min=None, price_max=None):
        filtered_df = self.df[self.df['make'].str.lower() == make.lower()].copy()
        
        if year_min:
            filtered_df = filtered_df[filtered_df['year'] >= year_min]
        if year_max:
            filtered_df = filtered_df[filtered_df['year'] <= year_max]
        if price_min:
            filtered_df = filtered_df[filtered_df['price'] >= price_min]
        if price_max:
            filtered_df = filtered_df[filtered_df['price'] <= price_max]
        
        filtered_df['model_first_word'] = filtered_df['model'].str.split().str[0]
        unique_models = filtered_df['model_first_word'].dropna().unique().tolist()
        return sorted(unique_models)
    
    def search_cars(self, make=None, model=None, year_min=None, year_max=None,
                    price_min=None, price_max=None, mileage_min=None, mileage_max=None,
                    transmission=None, fuel_type=None, city=None, seller_type=None):
        filtered_df = self.df.copy()
        
        if make:
            filtered_df = filtered_df[filtered_df['make'].str.lower() == make.lower()]
        if model:
            filtered_df = filtered_df[filtered_df['model'].str.lower().str.contains(model.lower(), na=False)]
        if year_min:
            filtered_df = filtered_df[filtered_df['year'] >= year_min]
        if year_max:
            filtered_df = filtered_df[filtered_df['year'] <= year_max]
        if price_min:
            filtered_df = filtered_df[filtered_df['price'] >= price_min]
        if price_max:
            filtered_df = filtered_df[filtered_df['price'] <= price_max]
        if mileage_min:
            filtered_df = filtered_df[filtered_df['mileage'] >= mileage_min]
        if mileage_max:
            filtered_df = filtered_df[filtered_df['mileage'] <= mileage_max]
        if transmission:
            filtered_df = filtered_df[filtered_df['transmission'].str.lower() == transmission.lower()]
        if fuel_type:
            filtered_df = filtered_df[filtered_df['fuel_type'].str.lower() == fuel_type.lower()]
        if city:
            filtered_df = filtered_df[filtered_df['city'].str.lower() == city.lower()]
        if seller_type:
            filtered_df = filtered_df[filtered_df['seller_type'].str.lower() == seller_type.lower()]
        
        return filtered_df
    
    def get_statistics(self):
        return {
            "total_cars": len(self.df),
            "price_stats": {
                "min": int(self.df['price'].min()),
                "max": int(self.df['price'].max()),
                "average": int(self.df['price'].mean()),
                "median": int(self.df['price'].median())
            },
            "year_stats": {
                "min": int(self.df['year'].min()),
                "max": int(self.df['year'].max())
            },
            "mileage_stats": {
                "min": int(self.df['mileage'].min()),
                "max": int(self.df['mileage'].max()),
                "average": int(self.df['mileage'].mean())
            },
            "top_makes": self.df['make'].value_counts().head(10).to_dict(),
            "top_models": self.df['model'].value_counts().head(10).to_dict(),
            "top_cities": self.df['city'].value_counts().head(10).to_dict(),
            "transmission_distribution": self.df['transmission'].value_counts().to_dict(),
            "fuel_type_distribution": self.df['fuel_type'].value_counts().to_dict(),
            "seller_type_distribution": self.df['seller_type'].value_counts().to_dict()
        }
    
    def get_filters(self):
        return {
            "makes": sorted(self.df['make'].dropna().unique().tolist()),
            "transmissions": sorted(self.df['transmission'].dropna().unique().tolist()),
            "fuel_types": sorted(self.df['fuel_type'].dropna().unique().tolist()),
            "seller_types": sorted(self.df['seller_type'].dropna().unique().tolist()),
            "year_range": {
                "min": int(self.df['year'].min()),
                "max": int(self.df['year'].max())
            },
            "price_range": {
                "min": int(self.df['price'].min()),
                "max": int(self.df['price'].max())
            },
            "mileage_range": {
                "min": int(self.df['mileage'].min()),
                "max": int(self.df['mileage'].max())
            }
        }
    
    def price_analysis(self, group_by: str, make=None, model=None, year=None):
        filtered_df = self.df.copy()
        
        if make:
            filtered_df = filtered_df[filtered_df['make'].str.lower() == make.lower()]
        if model:
            filtered_df = filtered_df[filtered_df['model'].str.lower().str.split().str[0] == model.lower()]
        if year:
            filtered_df = filtered_df[filtered_df['year'] == year]
        
        grouped = filtered_df.groupby(group_by)['price'].agg(['mean', 'min', 'max', 'count']).reset_index()
        grouped.columns = [group_by, 'average_price', 'min_price', 'max_price', 'count']
        grouped = grouped.sort_values('average_price', ascending=False)
        
        result = grouped.to_dict('records')
        
        for item in result:
            item['average_price'] = int(item['average_price'])
            item['min_price'] = int(item['min_price'])
            item['max_price'] = int(item['max_price'])
            item['count'] = int(item['count'])
        
        return result
    
    @staticmethod
    def round_to_3sf(value):
        if value == 0:
            return 0
        return int(round(value, -int(floor(log10(abs(value)))) + 2))
    
    def predict_price(self, model: str, make=None, years_to_use=7):
        filtered_df = self.df.copy()
        
        filtered_df = filtered_df[filtered_df['model'].str.lower().str.split().str[0] == model.lower()]
        
        if make:
            filtered_df = filtered_df[filtered_df['make'].str.lower() == make.lower()]
        
        if len(filtered_df) == 0:
            return None, "No data found"
        
        yearly_data = filtered_df.groupby('year')['price'].mean().reset_index()
        yearly_data.columns = ['year', 'average_price']
        yearly_data = yearly_data.sort_values('year')
        
        if len(yearly_data) < 2:
            return None, "Insufficient data"
        
        max_year = int(yearly_data['year'].max())
        
        if max_year < 2024:
            return None, f"No recent data available. Latest data is from {max_year}"
        
        recent_years_data = yearly_data[yearly_data['year'] >= (max_year - years_to_use + 1)]
        
        if len(recent_years_data) < 2:
            return None, f"Insufficient recent data"
        
        X_train = recent_years_data['year'].values.reshape(-1, 1)
        y_train = recent_years_data['average_price'].values
        
        lr_model = LinearRegression()
        lr_model.fit(X_train, y_train)
        
        future_years = np.array([max_year + 1, max_year + 2, max_year + 3]).reshape(-1, 1)
        future_predictions = lr_model.predict(future_years)
        
        historical_data = []
        for _, row in yearly_data.iterrows():
            historical_data.append({
                "year": int(row['year']),
                "price": self.round_to_3sf(row['average_price']),
                "type": "historical"
            })
        
        future_data = []
        for year, price in zip(future_years.flatten(), future_predictions):
            future_data.append({
                "year": int(year),
                "price": self.round_to_3sf(max(0, price)),
                "type": "predicted"
            })
        
        all_data = historical_data + future_data
        
        return {
            "data": all_data,
            "model_stats": {
                "slope": float(lr_model.coef_[0]),
                "intercept": float(lr_model.intercept_),
                "total_data_points": len(yearly_data),
                "training_data_points": len(recent_years_data),
                "years_used_for_training": years_to_use,
                "latest_year": max_year
            }
        }, None
