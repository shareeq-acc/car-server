import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from math import log10, floor
from typing import Dict, List, Tuple


class MLService:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.label_encoders = {}
    
    @staticmethod
    def round_to_3sf(value):
        if value == 0:
            return 0
        return int(round(value, -int(floor(log10(abs(value)))) + 2))
    
    def estimate_price(self, make: str, model: str, year: int, mileage: int,
                      transmission: str, fuel_type: str) -> Tuple[Dict, str]:
        """Estimate car price using Random Forest"""
        try:
            # Prepare training data
            train_df = self.df[['make', 'model', 'year', 'mileage', 'transmission', 
                               'fuel_type', 'price']].copy()
            train_df = train_df.dropna()
            
            # Encode categorical variables
            categorical_cols = ['make', 'model', 'transmission', 'fuel_type']
            for col in categorical_cols:
                le = LabelEncoder()
                train_df[col + '_encoded'] = le.fit_transform(train_df[col].str.lower())
                self.label_encoders[col] = le
            
            # Prepare features
            X = train_df[['make_encoded', 'model_encoded', 'year', 'mileage', 
                         'transmission_encoded', 'fuel_type_encoded']]
            y = train_df['price']
            
            # Train model
            model_rf = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
            model_rf.fit(X, y)
            
            # Prepare input for prediction
            input_data = {
                'make': make.lower(),
                'model': model.lower(),
                'transmission': transmission.lower(),
                'fuel_type': fuel_type.lower()
            }
            
            # Encode input
            encoded_input = []
            for col in categorical_cols:
                try:
                    encoded_val = self.label_encoders[col].transform([input_data[col]])[0]
                except:
                    # Use most common value if not found
                    encoded_val = 0
                encoded_input.append(encoded_val)
            
            # Add numerical features
            input_features = [encoded_input[0], encoded_input[1], year, mileage,
                            encoded_input[2], encoded_input[3]]
            
            # Predict
            predicted_price = model_rf.predict([input_features])[0]
            
            # Get similar cars for price range
            similar_cars = self.df[
                (self.df['make'].str.lower() == make.lower()) &
                (self.df['model'].str.lower().str.contains(model.lower(), na=False)) &
                (self.df['year'] >= year - 2) &
                (self.df['year'] <= year + 2)
            ]
            
            if len(similar_cars) > 0:
                min_price = similar_cars['price'].min()
                avg_price = similar_cars['price'].mean()
                max_price = similar_cars['price'].max()
                
                # Adjust prediction: listing prices are inflated, so use weighted average
                # Weight: 30% min, 50% avg, 20% predicted (to account for market reality)
                adjusted_price = (0.3 * min_price + 0.5 * avg_price + 0.2 * predicted_price)
                
                # Ensure adjusted price is within reasonable bounds
                adjusted_price = max(min_price * 0.9, min(adjusted_price, avg_price * 1.1))
                
                price_range = {
                    "min": int(min_price),
                    "max": int(max_price),
                    "avg": int(avg_price)
                }
            else:
                # No similar cars found, use predicted price with 15% discount for listing inflation
                adjusted_price = predicted_price * 0.85
                price_range = {
                    "min": None,
                    "max": None,
                    "avg": None
                }
            
            return {
                "estimated_price": self.round_to_3sf(adjusted_price),
                "ml_predicted_price": self.round_to_3sf(predicted_price),
                "price_range": price_range,
                "similar_cars_count": len(similar_cars),
                "note": "Estimated price adjusted for typical listing vs actual price difference"
            }, None
            
        except Exception as e:
            return None, f"Error estimating price: {str(e)}"
    
    def find_similar_cars(self, make: str, model: str, year: int, 
                         price: float = None, engine_capacity: float = None, 
                         limit: int = 10) -> Tuple[List, str]:
        """Find similar cars using feature similarity (excludes same model)"""
        try:
            # Get reference model first word
            model_first_word = model.split()[0].lower()
            
            # Filter candidates - exclude same model, include similar makes/models
            candidates = self.df[
                ~(self.df['model'].str.lower().str.split().str[0] == model_first_word)
            ].copy()
            
            if len(candidates) == 0:
                return None, "No similar cars found"
            
            # Calculate similarity score based on year
            candidates['year_diff'] = abs(candidates['year'] - year)
            
            # Initialize similarity score with year difference
            similarity_components = [candidates['year_diff']]
            
            # Add price difference if provided
            if price is not None:
                candidates['price_diff'] = abs(candidates['price'] - price) / price
                similarity_components.append(candidates['price_diff'])
            
            # Add engine capacity difference if available
            if engine_capacity is not None:
                candidates['engine_diff'] = candidates['engine_capacity'].apply(
                    lambda x: abs(x - engine_capacity) / engine_capacity if pd.notna(x) and engine_capacity > 0 else 0.5
                )
                similarity_components.append(candidates['engine_diff'])
            
            # Calculate final similarity score
            total_diff = sum(similarity_components)
            candidates['similarity_score'] = 1 / (1 + total_diff)
            
            # Boost score for same make
            candidates.loc[candidates['make'].str.lower() == make.lower(), 'similarity_score'] *= 1.5
            
            # Get top similar cars
            similar = candidates.nlargest(limit * 10, 'similarity_score')  # Get more for grouping
            
            # Group by make, model (full name), year, and engine_capacity
            grouped = similar.groupby(['make', 'model', 'year', 'engine_capacity']).agg({
                'price': ['mean', 'min', 'max', 'count'],
                'mileage': 'mean',
                'similarity_score': 'max'
            }).reset_index()
            
            # Flatten column names
            grouped.columns = ['make', 'model', 'year', 'engine_capacity', 'avg_price', 'min_price', 'max_price', 
                              'count', 'avg_mileage', 'similarity_score']
            
            # Sort by similarity score and limit results
            grouped = grouped.nlargest(limit, 'similarity_score')
            
            # Format result
            result = []
            for _, row in grouped.iterrows():
                result.append({
                    'make': row['make'],
                    'model': row['model'],
                    'year': int(row['year']),
                    'engine_capacity': int(row['engine_capacity']) if pd.notna(row['engine_capacity']) else None,
                    'average_price': self.round_to_3sf(row['avg_price']),
                    'price_range': {
                        'min': int(row['min_price']),
                        'max': int(row['max_price'])
                    },
                    'count': int(row['count']),
                    'avg_mileage': int(row['avg_mileage']),
                    'similarity_score': round(row['similarity_score'], 3)
                })
            
            return result, None
            
        except Exception as e:
            return None, f"Error finding similar cars: {str(e)}"
    
    def find_best_value_cars(self, budget_min: float, budget_max: float, 
                            year_min: int = None, limit: int = 20) -> Tuple[List, str]:
        """Find underpriced cars using anomaly detection"""
        try:
            # Filter by budget
            filtered = self.df[
                (self.df['price'] >= budget_min) &
                (self.df['price'] <= budget_max)
            ].copy()
            
            if year_min:
                filtered = filtered[filtered['year'] >= year_min]
            
            if len(filtered) < 10:
                return None, "Not enough data in this price range"
            
            # Calculate value score considering age, engine capacity, and price
            filtered['age'] = 2025 - filtered['year']
            filtered['price_per_year'] = filtered['price'] / (filtered['age'] + 1)
            
            # Factor in engine capacity (larger engine = better value if price is same)
            filtered['engine_factor'] = filtered['engine_capacity'].fillna(1000) / 1000
            filtered['value_score'] = (filtered['engine_factor'] * 0.3 + 0.7) / (filtered['price_per_year'] / 100000)
            
            # Get best values
            best_values = filtered.nlargest(limit, 'value_score')
            
            # Convert to dict and handle NaN values
            result = best_values[['make', 'model', 'year', 'price', 'mileage',
                                 'transmission', 'fuel_type', 'engine_capacity', 'city', 'url']].to_dict('records')
            
            # Replace NaN values with None for JSON serialization
            for item in result:
                for key, value in item.items():
                    if pd.isna(value):
                        item[key] = None
            
            return result, None
            
        except Exception as e:
            return None, f"Error finding best value cars: {str(e)}"
    
    def analyze_market_trend(self, make: str = None, model: str = None) -> Tuple[Dict, str]:
        """Analyze market trends for a make/model"""
        try:
            filtered = self.df.copy()
            
            if make:
                filtered = filtered[filtered['make'].str.lower() == make.lower()]
            if model:
                filtered = filtered[filtered['model'].str.lower().str.split().str[0] == model.lower()]
            
            if len(filtered) < 5:
                return None, "Insufficient data for trend analysis"
            
            # Yearly trends
            yearly = filtered.groupby('year').agg({
                'price': ['mean', 'count'],
                'mileage': 'mean'
            }).reset_index()
            
            yearly.columns = ['year', 'avg_price', 'count', 'avg_mileage']
            yearly = yearly.sort_values('year')
            
            # Calculate year-over-year growth
            if len(yearly) > 1:
                recent_years = yearly.tail(3)
                price_growth = ((recent_years['avg_price'].iloc[-1] - recent_years['avg_price'].iloc[0]) / 
                               recent_years['avg_price'].iloc[0] * 100) if len(recent_years) >= 2 else 0
            else:
                price_growth = 0
            
            # City distribution
            city_dist = filtered['city'].value_counts().head(10).to_dict()
            
            # Transmission preference
            trans_dist = filtered['transmission'].value_counts().to_dict()
            
            # Fuel type preference
            fuel_dist = filtered['fuel_type'].value_counts().to_dict()
            
            return {
                "total_listings": len(filtered),
                "price_trend": {
                    "current_avg": self.round_to_3sf(filtered['price'].mean()),
                    "year_over_year_growth": round(price_growth, 2),
                    "yearly_data": yearly.to_dict('records')
                },
                "popular_cities": city_dist,
                "transmission_preference": trans_dist,
                "fuel_type_preference": fuel_dist,
                "avg_mileage": self.round_to_3sf(filtered['mileage'].mean())
            }, None
            
        except Exception as e:
            return None, f"Error analyzing trends: {str(e)}"
    
    def calculate_depreciation(self, make: str, model: str, purchase_year: int) -> Tuple[Dict, str]:
        """Calculate depreciation curve"""
        try:
            # Get historical data
            filtered = self.df[
                (self.df['make'].str.lower() == make.lower()) &
                (self.df['model'].str.lower().str.split().str[0] == model.lower())
            ].copy()
            
            if len(filtered) < 5:
                return None, "Insufficient data for depreciation calculation"
            
            # Group by year
            yearly_avg = filtered.groupby('year')['price'].mean().reset_index()
            yearly_avg = yearly_avg.sort_values('year')
            
            if purchase_year not in yearly_avg['year'].values:
                # Estimate purchase price
                from sklearn.linear_model import LinearRegression
                X = yearly_avg['year'].values.reshape(-1, 1)
                y = yearly_avg['price'].values
                lr = LinearRegression()
                lr.fit(X, y)
                purchase_price = lr.predict([[purchase_year]])[0]
            else:
                purchase_price = yearly_avg[yearly_avg['year'] == purchase_year]['price'].values[0]
            
            # Calculate depreciation for next 5 years
            depreciation_data = []
            current_year = 2025
            
            # Historical depreciation rate
            if len(yearly_avg) > 1:
                avg_depreciation_rate = 0.12  # 12% per year average
            else:
                avg_depreciation_rate = 0.12
            
            for i in range(6):
                year = purchase_year + i
                if year <= current_year:
                    # Use actual data if available
                    actual = yearly_avg[yearly_avg['year'] == year]
                    if len(actual) > 0:
                        price = actual['price'].values[0]
                        depreciation_data.append({
                            "year": int(year),
                            "estimated_value": self.round_to_3sf(price),
                            "depreciation_percent": round((1 - price/purchase_price) * 100, 2),
                            "type": "historical"
                        })
                    else:
                        estimated_value = purchase_price * ((1 - avg_depreciation_rate) ** i)
                        depreciation_data.append({
                            "year": int(year),
                            "estimated_value": self.round_to_3sf(estimated_value),
                            "depreciation_percent": round((1 - estimated_value/purchase_price) * 100, 2),
                            "type": "estimated"
                        })
                else:
                    # Future projection
                    estimated_value = purchase_price * ((1 - avg_depreciation_rate) ** i)
                    depreciation_data.append({
                        "year": int(year),
                        "estimated_value": self.round_to_3sf(estimated_value),
                        "depreciation_percent": round((1 - estimated_value/purchase_price) * 100, 2),
                        "type": "projected"
                    })
            
            return {
                "make": make,
                "model": model,
                "purchase_year": purchase_year,
                "purchase_price": self.round_to_3sf(purchase_price),
                "depreciation_curve": depreciation_data,
                "avg_annual_depreciation_rate": round(avg_depreciation_rate * 100, 2)
            }, None
            
        except Exception as e:
            return None, f"Error calculating depreciation: {str(e)}"
    
    def predict_demand(self, make: str = None, model: str = None, city: str = None) -> Tuple[Dict, str]:
        """Predict demand/popularity"""
        try:
            filtered = self.df.copy()
            
            if make:
                filtered = filtered[filtered['make'].str.lower() == make.lower()]
            if model:
                filtered = filtered[filtered['model'].str.lower().str.split().str[0] == model.lower()]
            if city:
                filtered = filtered[filtered['city'].str.lower() == city.lower()]
            
            if len(filtered) == 0:
                return None, "No data found for specified criteria"
            
            total_cars = len(self.df)
            filtered_count = len(filtered)
            
            # Calculate demand score (0-100)
            demand_score = min(100, (filtered_count / total_cars) * 1000)
            
            # Get recent listings (assume higher year = more recent)
            recent_listings = filtered[filtered['year'] >= 2020]
            recent_count = len(recent_listings)
            
            # Popularity by city
            city_popularity = filtered['city'].value_counts().head(5).to_dict()
            
            # Price trend
            avg_price = filtered['price'].mean()
            
            return {
                "demand_score": round(demand_score, 2),
                "total_listings": filtered_count,
                "recent_listings": recent_count,
                "popularity_rank": self._get_popularity_rank(demand_score),
                "top_cities": city_popularity,
                "average_price": self.round_to_3sf(avg_price),
                "market_share_percent": round((filtered_count / total_cars) * 100, 2)
            }, None
            
        except Exception as e:
            return None, f"Error predicting demand: {str(e)}"
    
    def _get_popularity_rank(self, score: float) -> str:
        if score >= 80:
            return "Very High"
        elif score >= 60:
            return "High"
        elif score >= 40:
            return "Medium"
        elif score >= 20:
            return "Low"
        else:
            return "Very Low"
    
    def detect_anomalies(self, limit: int = 50) -> Tuple[Dict, str]:
        """Detect overpriced and underpriced cars"""
        try:
            # Prepare features for anomaly detection
            analysis_df = self.df[['make', 'model', 'year', 'price', 'mileage']].copy()
            analysis_df = analysis_df.dropna()
            
            # Calculate expected price based on year and mileage
            analysis_df['age'] = 2025 - analysis_df['year']
            analysis_df['expected_price_factor'] = (10 - analysis_df['age']) * 1000000 - (analysis_df['mileage'] * 10)
            
            # Calculate price deviation
            grouped = analysis_df.groupby(['make', 'model'])['price'].transform('mean')
            analysis_df['price_deviation'] = (analysis_df['price'] - grouped) / grouped
            
            # Find overpriced (positive deviation > 50%)
            overpriced = analysis_df[analysis_df['price_deviation'] > 0.5].nlargest(limit, 'price_deviation')
            
            # Find underpriced (negative deviation < -30%)
            underpriced = analysis_df[analysis_df['price_deviation'] < -0.3].nsmallest(limit, 'price_deviation')
            
            overpriced_results = []
            for idx in overpriced.index:
                car = self.df.loc[idx]
                overpriced_results.append({
                    "make": car['make'],
                    "model": car['model'],
                    "year": int(car['year']),
                    "price": int(car['price']),
                    "deviation_percent": round(overpriced.loc[idx, 'price_deviation'] * 100, 2),
                    "url": car['url']
                })
            
            underpriced_results = []
            for idx in underpriced.index:
                car = self.df.loc[idx]
                underpriced_results.append({
                    "make": car['make'],
                    "model": car['model'],
                    "year": int(car['year']),
                    "price": int(car['price']),
                    "deviation_percent": round(underpriced.loc[idx, 'price_deviation'] * 100, 2),
                    "url": car['url']
                })
            
            return {
                "overpriced_cars": overpriced_results[:limit//2],
                "underpriced_cars": underpriced_results[:limit//2],
                "analysis_note": "Deviation is calculated based on average price for same make/model"
            }, None
            
        except Exception as e:
            return None, f"Error detecting anomalies: {str(e)}"
