import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import Dict, Tuple
from math import log10, floor


class ComparisonService:
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    @staticmethod
    def round_to_3sf(value):
        if value == 0:
            return 0
        return int(round(value, -int(floor(log10(abs(value)))) + 2))
    
    def compare_models(self, model1: str, model2: str, metric: str = "price", 
                      make1: str = None, make2: str = None, 
                      years_to_use: int = 7) -> Tuple[Dict, str]:
        """Compare two models based on specified metric"""
        try:
            if metric == "price":
                return self._compare_price_trends(model1, model2, make1, make2, years_to_use)
            elif metric == "popularity":
                return self._compare_popularity(model1, model2, make1, make2)
            elif metric == "depreciation":
                return self._compare_depreciation(model1, model2, make1, make2)
            elif metric == "features":
                return self._compare_features(model1, model2, make1, make2)
            else:
                return None, "Invalid metric. Choose from: price, popularity, depreciation, features"
        
        except Exception as e:
            return None, f"Error comparing models: {str(e)}"
    
    def _compare_price_trends(self, model1: str, model2: str, make1: str = None, 
                             make2: str = None, years_to_use: int = 7) -> Tuple[Dict, str]:
        """Compare price trends with predictions"""
        
        # Get data for both models
        data1 = self._get_price_prediction_data(model1, make1, years_to_use)
        data2 = self._get_price_prediction_data(model2, make2, years_to_use)
        
        if data1 is None or data2 is None:
            return None, "Insufficient data for one or both models"
        
        # Calculate insights
        insights = []
        
        # Current price comparison
        current_price1 = data1['current_price']
        current_price2 = data2['current_price']
        price_diff = abs(current_price1 - current_price2)
        price_diff_percent = (price_diff / min(current_price1, current_price2)) * 100
        
        label1 = f"{make1 + ' ' if make1 else ''}{model1}"
        label2 = f"{make2 + ' ' if make2 else ''}{model2}"
        
        if current_price1 > current_price2:
            insights.append(f"{label1} is {price_diff_percent:.1f}% more expensive than {label2}")
        else:
            insights.append(f"{label2} is {price_diff_percent:.1f}% more expensive than {label1}")
        
        # Future price prediction comparison
        future_price1 = data1['future_prices'][-1]
        future_price2 = data2['future_prices'][-1]
        
        if future_price1 > future_price2:
            insights.append(f"In 3 years, {label1} is predicted to be more expensive")
        else:
            insights.append(f"In 3 years, {label2} is predicted to be more expensive")
        
        # Growth rate comparison
        growth1 = ((future_price1 - current_price1) / current_price1) * 100
        growth2 = ((future_price2 - current_price2) / current_price2) * 100
        
        if growth1 > growth2:
            insights.append(f"{label1} has higher predicted price growth ({growth1:.1f}% vs {growth2:.1f}%)")
        else:
            insights.append(f"{label2} has higher predicted price growth ({growth2:.1f}% vs {growth1:.1f}%)")
        
        return {
            "metric": "price",
            "comparison": {
                model1: {
                    "make": make1,
                    "current_price": current_price1,
                    "predicted_price_3y": future_price1,
                    "growth_rate": round(growth1, 2),
                    "historical_data": data1['historical'],
                    "future_predictions": data1['future']
                },
                model2: {
                    "make": make2,
                    "current_price": current_price2,
                    "predicted_price_3y": future_price2,
                    "growth_rate": round(growth2, 2),
                    "historical_data": data2['historical'],
                    "future_predictions": data2['future']
                }
            },
            "insights": insights,
            "recommendation": self._get_price_recommendation(growth1, growth2, current_price1, current_price2, label1, label2)
        }, None
    
    def _get_price_prediction_data(self, model: str, make: str = None, years_to_use: int = 7):
        """Get price prediction data for a model"""
        filtered = self.df[self.df['model'].str.lower().str.split().str[0] == model.lower()].copy()
        
        if make:
            filtered = filtered[filtered['make'].str.lower() == make.lower()]
        
        if len(filtered) < 5:
            return None
        
        yearly_data = filtered.groupby('year')['price'].mean().reset_index()
        yearly_data.columns = ['year', 'average_price']
        yearly_data = yearly_data.sort_values('year')
        
        max_year = int(yearly_data['year'].max())
        
        if max_year < 2024:
            return None
        
        # Use recent years for prediction
        recent_data = yearly_data[yearly_data['year'] >= (max_year - years_to_use + 1)]
        
        if len(recent_data) < 2:
            return None
        
        # Train model
        X = recent_data['year'].values.reshape(-1, 1)
        y = recent_data['average_price'].values
        
        lr = LinearRegression()
        lr.fit(X, y)
        
        # Predict future
        future_years = np.array([max_year + 1, max_year + 2, max_year + 3]).reshape(-1, 1)
        future_predictions = lr.predict(future_years)
        
        historical = [{"year": int(row['year']), "price": self.round_to_3sf(row['average_price'])} 
                     for _, row in yearly_data.iterrows()]
        
        future = [{"year": int(year), "price": self.round_to_3sf(max(0, price))} 
                 for year, price in zip(future_years.flatten(), future_predictions)]
        
        return {
            "current_price": self.round_to_3sf(yearly_data.iloc[-1]['average_price']),
            "future_prices": [self.round_to_3sf(max(0, p)) for p in future_predictions],
            "historical": historical,
            "future": future
        }
    
    def _get_price_recommendation(self, growth1, growth2, price1, price2, label1, label2):
        """Generate recommendation based on price comparison"""
        if growth1 > growth2 and price1 < price2:
            return f"{label1} offers better value - lower current price with higher growth potential"
        elif growth2 > growth1 and price2 < price1:
            return f"{label2} offers better value - lower current price with higher growth potential"
        elif price1 < price2:
            return f"{label1} is more affordable currently"
        elif price2 < price1:
            return f"{label2} is more affordable currently"
        else:
            return "Both options are similarly priced"
    
    def _compare_popularity(self, model1: str, model2: str, make1: str = None, 
                           make2: str = None) -> Tuple[Dict, str]:
        """Compare popularity/market share"""
        
        filtered1 = self.df[self.df['model'].str.lower().str.split().str[0] == model1.lower()]
        filtered2 = self.df[self.df['model'].str.lower().str.split().str[0] == model2.lower()]
        
        if make1:
            filtered1 = filtered1[filtered1['make'].str.lower() == make1.lower()]
        if make2:
            filtered2 = filtered2[filtered2['make'].str.lower() == make2.lower()]
        
        count1 = len(filtered1)
        count2 = len(filtered2)
        total = len(self.df)
        
        market_share1 = (count1 / total) * 100
        market_share2 = (count2 / total) * 100
        
        # Recent listings (2020+)
        recent1 = len(filtered1[filtered1['year'] >= 2020])
        recent2 = len(filtered2[filtered2['year'] >= 2020])
        
        label1 = f"{make1 + ' ' if make1 else ''}{model1}"
        label2 = f"{make2 + ' ' if make2 else ''}{model2}"
        
        insights = []
        
        if count1 > count2:
            diff = ((count1 - count2) / count2) * 100
            insights.append(f"{label1} has {diff:.1f}% more listings than {label2}")
        else:
            diff = ((count2 - count1) / count1) * 100
            insights.append(f"{label2} has {diff:.1f}% more listings than {label1}")
        
        if recent1 > recent2:
            insights.append(f"{label1} has more recent listings, indicating higher current demand")
        else:
            insights.append(f"{label2} has more recent listings, indicating higher current demand")
        
        return {
            "metric": "popularity",
            "comparison": {
                model1: {
                    "make": make1,
                    "total_listings": count1,
                    "recent_listings": recent1,
                    "market_share": round(market_share1, 2)
                },
                model2: {
                    "make": make2,
                    "total_listings": count2,
                    "recent_listings": recent2,
                    "market_share": round(market_share2, 2)
                }
            },
            "insights": insights,
            "recommendation": f"{label1 if count1 > count2 else label2} is more popular in the market"
        }, None
    
    def _compare_depreciation(self, model1: str, model2: str, make1: str = None, 
                             make2: str = None) -> Tuple[Dict, str]:
        """Compare depreciation rates"""
        
        dep1 = self._calculate_depreciation_rate(model1, make1)
        dep2 = self._calculate_depreciation_rate(model2, make2)
        
        if dep1 is None or dep2 is None:
            return None, "Insufficient data for depreciation comparison"
        
        label1 = f"{make1 + ' ' if make1 else ''}{model1}"
        label2 = f"{make2 + ' ' if make2 else ''}{model2}"
        
        insights = []
        
        if dep1 < dep2:
            insights.append(f"{label1} retains value better ({dep1:.1f}% vs {dep2:.1f}% annual depreciation)")
        else:
            insights.append(f"{label2} retains value better ({dep2:.1f}% vs {dep1:.1f}% annual depreciation)")
        
        return {
            "metric": "depreciation",
            "comparison": {
                model1: {
                    "make": make1,
                    "annual_depreciation_rate": round(dep1, 2),
                    "value_retention": round(100 - dep1, 2)
                },
                model2: {
                    "make": make2,
                    "annual_depreciation_rate": round(dep2, 2),
                    "value_retention": round(100 - dep2, 2)
                }
            },
            "insights": insights,
            "recommendation": f"{label1 if dep1 < dep2 else label2} is a better investment for value retention"
        }, None
    
    def _calculate_depreciation_rate(self, model: str, make: str = None):
        """Calculate average annual depreciation rate"""
        filtered = self.df[self.df['model'].str.lower().str.split().str[0] == model.lower()]
        
        if make:
            filtered = filtered[filtered['make'].str.lower() == make.lower()]
        
        if len(filtered) < 10:
            return None
        
        yearly_avg = filtered.groupby('year')['price'].mean().reset_index()
        yearly_avg = yearly_avg.sort_values('year')
        
        if len(yearly_avg) < 3:
            return None
        
        # Calculate year-over-year depreciation
        yearly_avg['depreciation'] = yearly_avg['price'].pct_change() * -100
        avg_depreciation = yearly_avg['depreciation'].mean()
        
        return max(0, avg_depreciation)
    
    def _compare_features(self, model1: str, model2: str, make1: str = None, 
                         make2: str = None) -> Tuple[Dict, str]:
        """Compare features like transmission, fuel type, engine capacity"""
        
        filtered1 = self.df[self.df['model'].str.lower().str.split().str[0] == model1.lower()]
        filtered2 = self.df[self.df['model'].str.lower().str.split().str[0] == model2.lower()]
        
        if make1:
            filtered1 = filtered1[filtered1['make'].str.lower() == make1.lower()]
        if make2:
            filtered2 = filtered2[filtered2['make'].str.lower() == make2.lower()]
        
        label1 = f"{make1 + ' ' if make1 else ''}{model1}"
        label2 = f"{make2 + ' ' if make2 else ''}{model2}"
        
        insights = []
        
        # Engine capacity
        avg_engine1 = filtered1['engine_capacity'].mean()
        avg_engine2 = filtered2['engine_capacity'].mean()
        
        if pd.notna(avg_engine1) and pd.notna(avg_engine2):
            if avg_engine1 > avg_engine2:
                insights.append(f"{label1} has larger average engine ({avg_engine1:.0f}cc vs {avg_engine2:.0f}cc)")
            else:
                insights.append(f"{label2} has larger average engine ({avg_engine2:.0f}cc vs {avg_engine1:.0f}cc)")
        
        # Transmission
        auto1 = (filtered1['transmission'] == 'Automatic').sum() / len(filtered1) * 100
        auto2 = (filtered2['transmission'] == 'Automatic').sum() / len(filtered2) * 100
        
        insights.append(f"{label1}: {auto1:.1f}% automatic, {label2}: {auto2:.1f}% automatic")
        
        # Fuel type
        fuel1 = filtered1['fuel_type'].value_counts().to_dict()
        fuel2 = filtered2['fuel_type'].value_counts().to_dict()
        
        return {
            "metric": "features",
            "comparison": {
                model1: {
                    "make": make1,
                    "avg_engine_capacity": round(avg_engine1, 0) if pd.notna(avg_engine1) else None,
                    "automatic_percentage": round(auto1, 1),
                    "fuel_types": fuel1
                },
                model2: {
                    "make": make2,
                    "avg_engine_capacity": round(avg_engine2, 0) if pd.notna(avg_engine2) else None,
                    "automatic_percentage": round(auto2, 1),
                    "fuel_types": fuel2
                }
            },
            "insights": insights
        }, None
