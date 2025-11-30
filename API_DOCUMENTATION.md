# PakWheels API Documentation

Base URL: `http://localhost:8000`

All endpoints are public and do not require authentication.

---

## Table of Contents
1. [General Endpoints](#general-endpoints)
2. [Car Data Endpoints](#car-data-endpoints)
3. [Machine Learning Endpoints](#machine-learning-endpoints)
4. [Comparison Endpoints](#comparison-endpoints)

---

## General Endpoints

### 1. Root
**GET** `/`

Returns a welcome message.

**Response:**
```json
{
  "message": "Hello World"
}
```

---

### 2. Health Check
**GET** `/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy"
}
```

---

## Car Data Endpoints

### 3. Get All Makes
**GET** `/makes`

Get list of all car makes sorted alphabetically.

**Query Parameters:** None

**Response:**
```json
{
  "makes": ["Honda", "Toyota", "Suzuki", ...],
  "count": 45
}
```

---

### 4. Get Models by Make
**GET** `/models`

Get unique car models for a specific make (first word only, e.g., "City" for "City 5th Gen").

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| make | string | Yes | Car make (case insensitive) |
| year_min | integer | No | Minimum year |
| year_max | integer | No | Maximum year |
| price_min | float | No | Minimum price |
| price_max | float | No | Maximum price |
| page | integer | No | Page number (default: 1) |
| limit | integer | No | Items per page (default: 10, max: 100) |

**Response:**
```json
{
  "make": "Honda",
  "models": ["City", "Civic", "Accord", ...],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_count": 25,
    "total_pages": 3
  },
  "filters": {
    "year_min": null,
    "year_max": null,
    "price_min": null,
    "price_max": null
  }
}
```

---

### 5. Search Cars
**GET** `/cars`

Search and filter cars with multiple criteria.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| make | string | No | Car make (case insensitive) |
| model | string | No | Car model (case insensitive, partial match) |
| year_min | integer | No | Minimum year |
| year_max | integer | No | Maximum year |
| price_min | float | No | Minimum price |
| price_max | float | No | Maximum price |
| mileage_min | integer | No | Minimum mileage |
| mileage_max | integer | No | Maximum mileage |
| transmission | string | No | Transmission type (Automatic/Manual) |
| fuel_type | string | No | Fuel type (Petrol/Diesel/Hybrid/CNG/Electric) |
| city | string | No | City (case insensitive) |
| seller_type | string | No | Seller type (Featured/Individual) |
| page | integer | No | Page number (default: 1) |
| limit | integer | No | Items per page (default: 10, max: 100) |

**Response:**
```json
{
  "cars": [
    {
      "make": "Honda",
      "model": "City",
      "year": 2020,
      "price": 3500000,
      "mileage": 45000,
      "transmission": "Automatic",
      "fuel_type": "Petrol",
      "engine_capacity": 1500,
      "city": "Lahore",
      "seller_type": "Individual",
      "url": "https://..."
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_count": 150,
    "total_pages": 15
  }
}
```

---

### 6. Get Statistics
**GET** `/statistics`

Get overall market statistics.

**Query Parameters:** None

**Response:**
```json
{
  "total_cars": 7380,
  "price_stats": {
    "min": 180000,
    "max": 171000000,
    "average": 4250000,
    "median": 3200000
  },
  "year_stats": {
    "min": 1965,
    "max": 2025
  },
  "mileage_stats": {
    "min": 0,
    "max": 500000,
    "average": 65000
  },
  "top_makes": {
    "Toyota": 1500,
    "Honda": 1200,
    ...
  },
  "top_models": {
    "Corolla": 450,
    "City": 380,
    ...
  },
  "top_cities": {
    "Lahore": 2000,
    "Karachi": 1800,
    ...
  },
  "transmission_distribution": {
    "Automatic": 4500,
    "Manual": 2880
  },
  "fuel_type_distribution": {
    "Petrol": 5000,
    "Hybrid": 1500,
    ...
  },
  "seller_type_distribution": {
    "Individual": 5000,
    "Featured": 2380
  }
}
```

---

### 7. Get Filter Options
**GET** `/filters`

Get all available filter options for building filter UIs.

**Query Parameters:** None

**Response:**
```json
{
  "makes": ["Honda", "Toyota", ...],
  "transmissions": ["Automatic", "Manual"],
  "fuel_types": ["CNG", "Diesel", "Electric", "Hybrid", "Petrol"],
  "seller_types": ["Featured", "Individual"],
  "year_range": {
    "min": 1965,
    "max": 2025
  },
  "price_range": {
    "min": 180000,
    "max": 171000000
  },
  "mileage_range": {
    "min": 0,
    "max": 500000
  }
}
```

---

### 8. Price Analysis
**GET** `/price-analysis`

Analyze prices grouped by make, model, year, or city.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| group_by | string | No | Group by: make, model, year, city (default: make) |
| make | string | No | Filter by make (case insensitive) |
| model | string | No | Filter by model (first word, case insensitive) |
| year | integer | No | Filter by year |

**Response:**
```json
{
  "group_by": "make",
  "filters": {
    "make": null,
    "model": null,
    "year": null
  },
  "analysis": [
    {
      "make": "Mercedes",
      "average_price": 15000000,
      "min_price": 5000000,
      "max_price": 50000000,
      "count": 120
    },
    ...
  ]
}
```

---

### 9. Price Prediction
**GET** `/price-prediction`

Predict future prices for a model using Linear Regression.

**ML Model:** Linear Regression  
**Technique:** Uses recent years (default: 7) to train model and predict next 3 years  
**Approach:** 
- Filters data by model (first word match)
- Groups by year and calculates average price
- Trains Linear Regression on recent years only
- Predicts next 3 years
- Rounds prices to 3 significant figures

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| model | string | Yes | Model name (first word, case insensitive) |
| make | string | No | Filter by make (case insensitive) |
| years_to_use | integer | No | Years to use for training (default: 7, min: 3, max: 20) |

**Response:**
```json
{
  "model": "city",
  "make": "Honda",
  "data": [
    {
      "year": 2019,
      "price": 3200000,
      "type": "historical"
    },
    {
      "year": 2020,
      "price": 3500000,
      "type": "historical"
    },
    ...
    {
      "year": 2026,
      "price": 8500000,
      "type": "predicted"
    },
    {
      "year": 2027,
      "price": 8900000,
      "type": "predicted"
    },
    {
      "year": 2028,
      "price": 9300000,
      "type": "predicted"
    }
  ],
  "model_stats": {
    "slope": 450000.5,
    "intercept": -905000000.2,
    "total_data_points": 45,
    "training_data_points": 7,
    "years_used_for_training": 7,
    "latest_year": 2025
  }
}
```

---

## Machine Learning Endpoints

### 10. Estimate Price
**GET** `/ml/estimate-price`

Estimate car price using Random Forest Regressor.

**ML Model:** Random Forest Regressor (100 estimators, max_depth=10)  
**Technique:** Supervised learning with categorical encoding  
**Approach:**
- Encodes categorical features (make, model, transmission, fuel_type) using LabelEncoder
- Trains Random Forest on all available data
- Adjusts prediction using weighted average: 30% min price + 50% avg price + 20% ML prediction
- Accounts for listing price inflation (typically 10-15% higher than actual)

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| make | string | Yes | Car make |
| model | string | Yes | Car model |
| year | integer | Yes | Manufacturing year |
| mileage | integer | Yes | Mileage in km |
| transmission | string | Yes | Transmission type (Automatic/Manual) |
| fuel_type | string | Yes | Fuel type (Petrol/Diesel/Hybrid/CNG/Electric) |

**Response:**
```json
{
  "input": {
    "make": "Honda",
    "model": "City",
    "year": 2020,
    "mileage": 50000,
    "transmission": "Automatic",
    "fuel_type": "Petrol"
  },
  "estimated_price": 3600000,
  "ml_predicted_price": 3800000,
  "price_range": {
    "min": 3200000,
    "max": 4200000,
    "avg": 3700000
  },
  "similar_cars_count": 45,
  "note": "Estimated price adjusted for typical listing vs actual price difference"
}
```

---

### 11. Find Similar Cars
**GET** `/ml/similar-cars`

Find similar cars based on specifications (excludes same model).

**ML Technique:** Feature similarity scoring  
**Approach:**
- Excludes same model (first word match)
- Calculates similarity based on year, price (optional), engine capacity (optional)
- Boosts score by 1.5x for same make
- Groups by make, model, year, and engine_capacity
- Returns aggregated statistics

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| make | string | Yes | Car make |
| model | string | Yes | Car model |
| year | integer | Yes | Year |
| price | float | No | Price (optional) |
| engine_capacity | float | No | Engine capacity in cc (optional) |
| limit | integer | No | Number of results (default: 10, max: 50) |

**Response:**
```json
{
  "reference": {
    "make": "Honda",
    "model": "City",
    "year": 2020,
    "price": 3500000,
    "engine_capacity": 1500
  },
  "similar_cars": [
    {
      "make": "Honda",
      "model": "Civic 10th Generation",
      "year": 2019,
      "engine_capacity": 1500,
      "average_price": 4500000,
      "price_range": {
        "min": 4200000,
        "max": 4800000
      },
      "count": 12,
      "avg_mileage": 45000,
      "similarity_score": 0.856
    },
    ...
  ],
  "count": 10
}
```

---

### 12. Best Value Cars
**GET** `/ml/best-value`

Find best value cars (underpriced/good deals) in budget range.

**ML Technique:** Value scoring algorithm  
**Approach:**
- Calculates value score based on: (engine_capacity_factor * 0.3 + 0.7) / (price_per_year / 100000)
- Considers car age (2025 - year)
- Factors in engine capacity (larger engines get bonus)
- Returns cars with highest value scores

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| budget_min | float | Yes | Minimum budget |
| budget_max | float | Yes | Maximum budget |
| year_min | integer | No | Minimum year |
| limit | integer | No | Number of results (default: 20, max: 100) |

**Response:**
```json
{
  "budget_range": {
    "min": 2000000,
    "max": 3000000
  },
  "best_value_cars": [
    {
      "make": "Honda",
      "model": "City",
      "year": 2018,
      "price": 2800000,
      "mileage": 60000,
      "transmission": "Automatic",
      "fuel_type": "Petrol",
      "engine_capacity": 1500,
      "city": "Lahore",
      "url": "https://..."
    },
    ...
  ],
  "count": 20
}
```

---

### 13. Market Trend Analysis
**GET** `/ml/market-trend`

Analyze market trends for make/model.

**ML Technique:** Time series analysis and aggregation  
**Approach:**
- Groups data by year to identify trends
- Calculates year-over-year growth rates
- Analyzes distribution across cities, transmission types, fuel types
- Provides insights on market dynamics

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| make | string | No | Car make |
| model | string | No | Car model (first word) |

**Response:**
```json
{
  "make": "Honda",
  "model": "City",
  "total_listings": 450,
  "price_trend": {
    "current_avg": 3700000,
    "year_over_year_growth": 12.5,
    "yearly_data": [
      {
        "year": 2020,
        "avg_price": 3200000,
        "count": 45,
        "avg_mileage": 50000
      },
      ...
    ]
  },
  "popular_cities": {
    "Lahore": 150,
    "Karachi": 120,
    ...
  },
  "transmission_preference": {
    "Automatic": 350,
    "Manual": 100
  },
  "fuel_type_preference": {
    "Petrol": 400,
    "Hybrid": 50
  },
  "avg_mileage": 55000
}
```

---

## Comparison Endpoints

### 14. Compare Models
**GET** `/compare/`

Compare two models based on specified metric.

**ML Models Used:**
- **Price metric:** Linear Regression for predictions
- **Depreciation metric:** Statistical analysis of historical data
- **Popularity metric:** Aggregation and market share analysis
- **Features metric:** Statistical comparison

**Approach:**
- Filters data by model (first word match)
- Optional filtering by make for specific variants
- Applies metric-specific analysis
- Generates insights and recommendations

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| model1 | string | Yes | First car model (first word) |
| model2 | string | Yes | Second car model (first word) |
| metric | string | No | Comparison metric (default: price) |
| make1 | string | No | First car make (optional) |
| make2 | string | No | Second car make (optional) |
| years_to_use | integer | No | Years for price predictions (default: 7) |

**Metrics:** `price`, `popularity`, `depreciation`, `features`

**Response (metric=price):**
```json
{
  "metric": "price",
  "comparison": {
    "City": {
      "make": "Honda",
      "current_price": 3700000,
      "predicted_price_3y": 4500000,
      "growth_rate": 21.6,
      "historical_data": [
        {"year": 2019, "price": 3200000},
        {"year": 2020, "price": 3500000},
        ...
      ],
      "future_predictions": [
        {"year": 2026, "price": 4100000},
        {"year": 2027, "price": 4300000},
        {"year": 2028, "price": 4500000}
      ]
    },
    "Corolla": {
      "make": "Toyota",
      "current_price": 4200000,
      "predicted_price_3y": 5000000,
      "growth_rate": 19.0,
      "historical_data": [...],
      "future_predictions": [...]
    }
  },
  "insights": [
    "Honda City is 13.5% less expensive than Toyota Corolla",
    "In 3 years, Honda City is predicted to be less expensive",
    "Honda City has higher predicted price growth (21.6% vs 19.0%)"
  ],
  "recommendation": "Honda City offers better value - lower current price with higher growth potential"
}
```

**Response (metric=popularity):**
```json
{
  "metric": "popularity",
  "comparison": {
    "City": {
      "make": "Honda",
      "total_listings": 450,
      "recent_listings": 180,
      "market_share": 6.1
    },
    "Corolla": {
      "make": "Toyota",
      "total_listings": 520,
      "recent_listings": 200,
      "market_share": 7.0
    }
  },
  "insights": [
    "Toyota Corolla has 15.6% more listings than Honda City",
    "Toyota Corolla has more recent listings, indicating higher current demand"
  ],
  "recommendation": "Toyota Corolla is more popular in the market"
}
```

**Response (metric=depreciation):**
```json
{
  "metric": "depreciation",
  "comparison": {
    "City": {
      "make": "Honda",
      "annual_depreciation_rate": 12.5,
      "value_retention": 87.5
    },
    "Corolla": {
      "make": "Toyota",
      "annual_depreciation_rate": 10.8,
      "value_retention": 89.2
    }
  },
  "insights": [
    "Toyota Corolla retains value better (10.8% vs 12.5% annual depreciation)"
  ],
  "recommendation": "Toyota Corolla is a better investment for value retention"
}
```

**Response (metric=features):**
```json
{
  "metric": "features",
  "comparison": {
    "City": {
      "make": "Honda",
      "avg_engine_capacity": 1500,
      "automatic_percentage": 78.5,
      "fuel_types": {
        "Petrol": 400,
        "Hybrid": 50
      }
    },
    "Corolla": {
      "make": "Toyota",
      "avg_engine_capacity": 1800,
      "automatic_percentage": 82.3,
      "fuel_types": {
        "Petrol": 450,
        "Hybrid": 70
      }
    }
  },
  "insights": [
    "Toyota Corolla has larger average engine (1800cc vs 1500cc)",
    "Honda City: 78.5% automatic, Toyota Corolla: 82.3% automatic"
  ]
}
```

---

## Notes

### Model Name Matching
- When a parameter specifies "first word", it means the API matches the first word of the model name
- Example: `model=city` matches "City", "City 5th Gen", "City 6th Gen", "City Aspire", etc.

### Price Rounding
- All prices are rounded to 3 significant figures for readability
- Example: 3,456,789 → 3,460,000

### Data Freshness
- Price predictions require data from 2024 or later
- If latest data is before 2024, predictions will not be generated

### Pagination
- Default page size is 10 items
- Maximum page size varies by endpoint (typically 50-100)

### Case Sensitivity
- All text searches are case-insensitive
- Make, model, city, transmission, fuel_type parameters ignore case

---

## Error Responses

All endpoints return standard HTTP status codes:

**400 Bad Request:**
```json
{
  "detail": "Error message describing the issue"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```
