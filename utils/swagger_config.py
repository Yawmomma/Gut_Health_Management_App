"""
OpenAPI 2.0 Swagger specification for Gut Health Management API.
This module defines the complete API documentation for all 136 endpoints.
"""

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Gut Health Management API",
        "description": "REST API for tracking diet, symptoms, and identifying FODMAP/histamine food triggers. Includes 136 endpoints covering diary, analytics, recipes, foods, education, and more.",
        "version": "1.0.0",
        "contact": {
            "name": "Gut Health App Support",
            "url": "http://localhost:5000"
        }
    },
    "host": "localhost:5000",
    "basePath": "/api/v1",
    "schemes": ["http"],
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "securityDefinitions": {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key for authentication. Obtain a key via POST /auth/api-keys (admin scope required). Pass the raw 64-character hex key."
        }
    },
    "tags": [
        {"name": "Diary", "description": "Health diary entries, meals, trends (9 endpoints)"},
        {"name": "Analytics", "description": "Health analytics, correlations, predictions (27 endpoints)"},
        {"name": "Recipes", "description": "Recipe management, meals, search (15 endpoints)"},
        {"name": "Foods", "description": "Food database, comparisons, substitutions (14 endpoints)"},
        {"name": "USDA", "description": "USDA nutrition database (4 endpoints)"},
        {"name": "AusNut", "description": "AusNut food database (2 endpoints)"},
        {"name": "FODMAP", "description": "FODMAP reference data (2 endpoints)"},
        {"name": "Search", "description": "Global search, recommendations (3 endpoints)"},
        {"name": "Export", "description": "Export diary, reports, shopping lists (3 endpoints)"},
        {"name": "Chat", "description": "AI chat conversations (5 endpoints)"},
        {"name": "Education", "description": "Educational content, chapters (9 endpoints)"},
        {"name": "Settings", "description": "Backup, help, integrity (10 endpoints)"},
        {"name": "Realtime", "description": "SSE streams, webhooks (8 endpoints)"},
        {"name": "Security", "description": "API keys, rate limits (4 endpoints)"},
        {"name": "Gamification", "description": "Challenges, badges (3 endpoints)"},
        {"name": "Notifications", "description": "Rules, scheduling (7 endpoints)"},
        {"name": "Integrations", "description": "Wearables, voice (3 endpoints)"},
        {"name": "Billing", "description": "Status, webhooks (2 endpoints)"},
        {"name": "Users", "description": "Multi-user analysis (3 endpoints)"},
        {"name": "Reintroduction", "description": "FODMAP reintroduction protocol (3 endpoints)"},
    ],
    "paths": {
        # ==================== DIARY (9) ====================
        "/diary/entries": {
            "get": {
                "tags": ["Diary"],
                "summary": "Get diary entries",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "date_from", "in": "query", "type": "string", "description": "Start date (YYYY-MM-DD)"},
                    {"name": "date_to", "in": "query", "type": "string", "description": "End date (YYYY-MM-DD)"},
                    {"name": "page", "in": "query", "type": "integer", "default": 1},
                    {"name": "per_page", "in": "query", "type": "integer", "default": 20}
                ],
                "responses": {
                    "200": {"description": "Success - returns paginated diary entries"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden - missing read:diary scope"}
                }
            }
        },
        "/diary/day/{date}": {
            "get": {
                "tags": ["Diary"],
                "summary": "Get diary entries for a specific day",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "date", "in": "path", "required": True, "type": "string", "description": "Date (YYYY-MM-DD)"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"},
                    "404": {"description": "Day not found"}
                }
            }
        },
        "/diary/trends": {
            "get": {
                "tags": ["Diary"],
                "summary": "Get symptom trends over time",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "days", "in": "query", "type": "integer", "default": 30}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/diary/weekly": {
            "get": {
                "tags": ["Diary"],
                "summary": "Get weekly diary summary",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "weeks", "in": "query", "type": "integer", "default": 4}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/diary/meals": {
            "post": {
                "tags": ["Diary"],
                "summary": "Create a meal entry",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "body", "in": "body", "required": True, "schema": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string", "description": "Date (YYYY-MM-DD)"},
                            "meal_type": {"type": "string", "enum": ["breakfast", "lunch", "dinner", "snack"]},
                            "foods": {"type": "array", "items": {"type": "object"}}
                        }
                    }}
                ],
                "responses": {
                    "201": {"description": "Created"},
                    "400": {"description": "Invalid input"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/diary/meals/{id}": {
            "put": {
                "tags": ["Diary"],
                "summary": "Update a meal entry",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "404": {"description": "Meal not found"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/diary/entries/bulk": {
            "post": {
                "tags": ["Diary"],
                "summary": "Create multiple diary entries",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "body", "in": "body", "required": True, "schema": {
                        "type": "object",
                        "properties": {
                            "entries": {"type": "array", "items": {"type": "object"}}
                        }
                    }}
                ],
                "responses": {
                    "201": {"description": "Created"},
                    "400": {"description": "Invalid input"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/diary/meal-plan": {
            "post": {
                "tags": ["Diary"],
                "summary": "Create a meal plan",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "201": {"description": "Created"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/diary/meal-plan/{id}": {
            "get": {
                "tags": ["Diary"],
                "summary": "Get a meal plan",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "404": {"description": "Meal plan not found"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },

        # ==================== ANALYTICS (27) ====================
        "/analytics/dashboard": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get dashboard overview",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/foods/risk-rating": {
            "post": {
                "tags": ["Analytics"],
                "summary": "Rate food risk",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/symptom-patterns": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get symptom patterns",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/food-reactions": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get food reactions",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/symptom-trends": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get symptom trends",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "days", "in": "query", "type": "integer", "default": 30}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/food-frequency": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get food frequency",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/trigger-foods": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get trigger foods",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/nutrition-summary": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get nutrition summary",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "date_from", "in": "query", "type": "string"},
                    {"name": "date_to", "in": "query", "type": "string"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/fodmap-exposure": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get FODMAP exposure metrics",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/histamine-exposure": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get histamine exposure metrics",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/fodmap-stacking": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get FODMAP stacking analysis",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/correlations": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get data correlations",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/gut-stability-score": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get gut stability score",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/tolerance-curves": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get tolerance curves",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/nutrient-rdi-status": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get nutrient RDI status",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/nutrient-gaps": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get nutrient gaps",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/nutrient-heatmap": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get nutrient heatmap",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/nutrient-sources": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get nutrient sources",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/nutrient-symptom-correlation": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get nutrient-symptom correlations",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/correlation-matrix": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get full correlation matrix",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/bristol-trends": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get Bristol stool trends",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/hydration": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get hydration metrics",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/meal-timing": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get meal timing analysis",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/dietary-diversity": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get dietary diversity score",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/flare-prediction": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get flare prediction",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/gut-health-score": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get overall gut health score",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/analytics/interactions": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Get medication/nutrient interactions",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },

        # ==================== RECIPES (15) ====================
        "/recipes": {
            "get": {
                "tags": ["Recipes"],
                "summary": "List recipes",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "page", "in": "query", "type": "integer", "default": 1},
                    {"name": "per_page", "in": "query", "type": "integer", "default": 20}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            },
            "post": {
                "tags": ["Recipes"],
                "summary": "Create a recipe",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "body", "in": "body", "required": True, "schema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "ingredients": {"type": "array"},
                            "instructions": {"type": "string"}
                        }
                    }}
                ],
                "responses": {
                    "201": {"description": "Created"},
                    "400": {"description": "Invalid input"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/recipes/search": {
            "get": {
                "tags": ["Recipes"],
                "summary": "Search recipes",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "q", "in": "query", "type": "string", "required": True}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/recipes/category/{category}": {
            "get": {
                "tags": ["Recipes"],
                "summary": "Get recipes by category",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "category", "in": "path", "required": True, "type": "string"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/recipes/{id}": {
            "get": {
                "tags": ["Recipes"],
                "summary": "Get recipe details",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "404": {"description": "Not found"},
                    "401": {"description": "Unauthorized"}
                }
            },
            "put": {
                "tags": ["Recipes"],
                "summary": "Update a recipe",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "404": {"description": "Not found"},
                    "401": {"description": "Unauthorized"}
                }
            },
            "delete": {
                "tags": ["Recipes"],
                "summary": "Delete a recipe",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "404": {"description": "Not found"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/recipes/{id}/context": {
            "get": {
                "tags": ["Recipes"],
                "summary": "Get recipe context (nutrition, safety info)",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "404": {"description": "Not found"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/meals": {
            "get": {
                "tags": ["Recipes"],
                "summary": "List meals",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            },
            "post": {
                "tags": ["Recipes"],
                "summary": "Create a meal",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "201": {"description": "Created"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/meals/{id}": {
            "put": {
                "tags": ["Recipes"],
                "summary": "Update a meal",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            },
            "delete": {
                "tags": ["Recipes"],
                "summary": "Delete a meal",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/recipes/import": {
            "post": {
                "tags": ["Recipes"],
                "summary": "Import a recipe",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "201": {"description": "Created"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/recipes/{id}/transform": {
            "post": {
                "tags": ["Recipes"],
                "summary": "Transform recipe (scale, etc)",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/recipes/share": {
            "post": {
                "tags": ["Recipes"],
                "summary": "Share a recipe",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "201": {"description": "Created"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },

        # ==================== FOODS (14) ====================
        "/compendium/search": {
            "get": {
                "tags": ["Foods"],
                "summary": "Search food database",
                "parameters": [
                    {"name": "q", "in": "query", "type": "string", "required": True},
                    {"name": "page", "in": "query", "type": "integer", "default": 1}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "400": {"description": "Invalid search"}
                }
            }
        },
        "/compendium/foods/{id}": {
            "get": {
                "tags": ["Foods"],
                "summary": "Get food details",
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "404": {"description": "Not found"}
                }
            },
            "put": {
                "tags": ["Foods"],
                "summary": "Update food",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            },
            "delete": {
                "tags": ["Foods"],
                "summary": "Delete food",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/compendium/compare": {
            "get": {
                "tags": ["Foods"],
                "summary": "Compare foods",
                "parameters": [
                    {"name": "ids", "in": "query", "type": "string", "description": "Comma-separated food IDs"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "400": {"description": "Invalid input"}
                }
            }
        },
        "/compendium/foods": {
            "post": {
                "tags": ["Foods"],
                "summary": "Create food",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "201": {"description": "Created"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/foods/quick-add": {
            "post": {
                "tags": ["Foods"],
                "summary": "Quick add food to diary",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "201": {"description": "Created"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/compendium/foods/{id}/link-ausnut": {
            "post": {
                "tags": ["Foods"],
                "summary": "Link food to AusNut",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/foods/batch": {
            "get": {
                "tags": ["Foods"],
                "summary": "Get foods batch",
                "parameters": [
                    {"name": "ids", "in": "query", "type": "string", "description": "Comma-separated IDs"}
                ],
                "responses": {
                    "200": {"description": "Success"}
                }
            }
        },
        "/foods/substitutes": {
            "get": {
                "tags": ["Foods"],
                "summary": "Get food substitutes",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "food_id", "in": "query", "type": "integer", "required": True}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/foods/unified-search": {
            "get": {
                "tags": ["Foods"],
                "summary": "Search all food databases",
                "parameters": [
                    {"name": "q", "in": "query", "type": "string", "required": True}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "400": {"description": "Invalid search"}
                }
            }
        },
        "/foods/scan-menu": {
            "post": {
                "tags": ["Foods"],
                "summary": "Scan restaurant menu",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/compendium/foods/{id}/link-usda": {
            "post": {
                "tags": ["Foods"],
                "summary": "Link food to USDA",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/foods/nutrient-boosters": {
            "get": {
                "tags": ["Foods"],
                "summary": "Get nutrient-boosting foods",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "nutrient", "in": "query", "type": "string", "required": True}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },

        # ==================== USDA (4) ====================
        "/usda/search": {
            "get": {
                "tags": ["USDA"],
                "summary": "Search USDA database",
                "parameters": [
                    {"name": "q", "in": "query", "type": "string", "required": True}
                ],
                "responses": {
                    "200": {"description": "Success"}
                }
            }
        },
        "/usda/foods": {
            "get": {
                "tags": ["USDA"],
                "summary": "List USDA foods",
                "parameters": [
                    {"name": "category_id", "in": "query", "type": "integer"},
                    {"name": "page", "in": "query", "type": "integer", "default": 1}
                ],
                "responses": {
                    "200": {"description": "Success"}
                }
            }
        },
        "/usda/foods/{id}": {
            "get": {
                "tags": ["USDA"],
                "summary": "Get USDA food details",
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "404": {"description": "Not found"}
                }
            }
        },
        "/usda/categories": {
            "get": {
                "tags": ["USDA"],
                "summary": "List USDA food categories",
                "responses": {
                    "200": {"description": "Success"}
                }
            }
        },

        # ==================== AUSNUT (2) ====================
        "/ausnut/search": {
            "get": {
                "tags": ["AusNut"],
                "summary": "Search AusNut database",
                "parameters": [
                    {"name": "q", "in": "query", "type": "string", "required": True}
                ],
                "responses": {
                    "200": {"description": "Success"}
                }
            }
        },
        "/ausnut/foods/{id}": {
            "get": {
                "tags": ["AusNut"],
                "summary": "Get AusNut food details",
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "404": {"description": "Not found"}
                }
            }
        },

        # ==================== FODMAP (2) ====================
        "/fodmap/categories": {
            "get": {
                "tags": ["FODMAP"],
                "summary": "List FODMAP categories",
                "responses": {
                    "200": {"description": "Success"}
                }
            }
        },
        "/fodmap/foods": {
            "get": {
                "tags": ["FODMAP"],
                "summary": "List FODMAP foods by category",
                "parameters": [
                    {"name": "category", "in": "query", "type": "string", "required": True},
                    {"name": "page", "in": "query", "type": "integer", "default": 1}
                ],
                "responses": {
                    "200": {"description": "Success"}
                }
            }
        },

        # ==================== SEARCH (3) ====================
        "/search/global": {
            "get": {
                "tags": ["Search"],
                "summary": "Global search",
                "parameters": [
                    {"name": "q", "in": "query", "type": "string", "required": True}
                ],
                "responses": {
                    "200": {"description": "Success"}
                }
            }
        },
        "/foods/recommendations": {
            "get": {
                "tags": ["Search"],
                "summary": "Get food recommendations",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/recipes/suitable": {
            "get": {
                "tags": ["Search"],
                "summary": "Get suitable recipes",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },

        # ==================== EXPORT (3) ====================
        "/export/diary": {
            "get": {
                "tags": ["Export"],
                "summary": "Export diary data",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "format", "in": "query", "type": "string", "enum": ["json", "csv"], "default": "json"},
                    {"name": "date_from", "in": "query", "type": "string"},
                    {"name": "date_to", "in": "query", "type": "string"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/export/report/pdf": {
            "get": {
                "tags": ["Export"],
                "summary": "Export PDF report",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success - returns PDF"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/export/shopping-list": {
            "get": {
                "tags": ["Export"],
                "summary": "Export shopping list",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },

        # ==================== CHAT (5) ====================
        "/chat": {
            "post": {
                "tags": ["Chat"],
                "summary": "Send chat message",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "body", "in": "body", "required": True, "schema": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string"},
                            "conversation_id": {"type": "integer"}
                        }
                    }}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/chat/conversations": {
            "get": {
                "tags": ["Chat"],
                "summary": "List conversations",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/chat/conversations/{id}": {
            "get": {
                "tags": ["Chat"],
                "summary": "Get conversation",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            },
            "delete": {
                "tags": ["Chat"],
                "summary": "Delete conversation",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/chat/conversations/{id}/rename": {
            "post": {
                "tags": ["Chat"],
                "summary": "Rename conversation",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },

        # ==================== EDUCATION (9) ====================
        "/education": {
            "get": {
                "tags": ["Education"],
                "summary": "List education chapters",
                "responses": {
                    "200": {"description": "Success"}
                }
            },
            "post": {
                "tags": ["Education"],
                "summary": "Create education chapter",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "201": {"description": "Created"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/education/{id}": {
            "get": {
                "tags": ["Education"],
                "summary": "Get chapter",
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "404": {"description": "Not found"}
                }
            },
            "put": {
                "tags": ["Education"],
                "summary": "Update chapter",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            },
            "delete": {
                "tags": ["Education"],
                "summary": "Delete chapter",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/education/upload": {
            "post": {
                "tags": ["Education"],
                "summary": "Upload education content",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "201": {"description": "Created"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/education/reorder": {
            "post": {
                "tags": ["Education"],
                "summary": "Reorder chapters",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/education/images": {
            "post": {
                "tags": ["Education"],
                "summary": "Upload images",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "201": {"description": "Created"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/education/preview-markdown": {
            "post": {
                "tags": ["Education"],
                "summary": "Preview markdown",
                "parameters": [
                    {"name": "body", "in": "body", "required": True, "schema": {
                        "type": "object",
                        "properties": {
                            "markdown": {"type": "string"}
                        }
                    }}
                ],
                "responses": {
                    "200": {"description": "Success"}
                }
            }
        },

        # ==================== SETTINGS (10) ====================
        "/settings/backup": {
            "get": {
                "tags": ["Settings"],
                "summary": "Backup database",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success - returns backup file"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/settings/integrity-check": {
            "get": {
                "tags": ["Settings"],
                "summary": "Check database integrity",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/settings/integrity-check/fix": {
            "post": {
                "tags": ["Settings"],
                "summary": "Fix database integrity issues",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/help": {
            "get": {
                "tags": ["Settings"],
                "summary": "List help topics",
                "responses": {
                    "200": {"description": "Success"}
                }
            },
            "post": {
                "tags": ["Settings"],
                "summary": "Create help topic",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "201": {"description": "Created"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/help/{id}": {
            "get": {
                "tags": ["Settings"],
                "summary": "Get help topic",
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "404": {"description": "Not found"}
                }
            },
            "put": {
                "tags": ["Settings"],
                "summary": "Update help topic",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            },
            "delete": {
                "tags": ["Settings"],
                "summary": "Delete help topic",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/help/upload": {
            "post": {
                "tags": ["Settings"],
                "summary": "Upload help content",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "201": {"description": "Created"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/help/preview-markdown": {
            "post": {
                "tags": ["Settings"],
                "summary": "Preview help markdown",
                "parameters": [
                    {"name": "body", "in": "body", "required": True, "schema": {
                        "type": "object",
                        "properties": {
                            "markdown": {"type": "string"}
                        }
                    }}
                ],
                "responses": {
                    "200": {"description": "Success"}
                }
            }
        },

        # ==================== REALTIME (8) ====================
        "/events/stream": {
            "get": {
                "tags": ["Realtime"],
                "summary": "SSE event stream",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Event stream"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/webhooks/register": {
            "post": {
                "tags": ["Realtime"],
                "summary": "Register webhook",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "201": {"description": "Created"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/webhooks": {
            "get": {
                "tags": ["Realtime"],
                "summary": "List webhooks",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/webhooks/{id}": {
            "get": {
                "tags": ["Realtime"],
                "summary": "Get webhook",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            },
            "put": {
                "tags": ["Realtime"],
                "summary": "Update webhook",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            },
            "delete": {
                "tags": ["Realtime"],
                "summary": "Delete webhook",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/webhooks/{id}/test": {
            "post": {
                "tags": ["Realtime"],
                "summary": "Test webhook",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/webhooks/external/receive": {
            "post": {
                "tags": ["Realtime"],
                "summary": "Receive external webhook (signature verified)",
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Invalid signature"}
                }
            }
        },

        # ==================== SECURITY (4) ====================
        "/auth/api-keys": {
            "post": {
                "tags": ["Security"],
                "summary": "Create API key",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "body", "in": "body", "required": True, "schema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "scopes": {"type": "string"},
                            "expires_at": {"type": "string"}
                        }
                    }}
                ],
                "responses": {
                    "201": {"description": "Created - returns key once"},
                    "401": {"description": "Unauthorized"}
                }
            },
            "get": {
                "tags": ["Security"],
                "summary": "List API keys",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/auth/api-keys/{id}": {
            "delete": {
                "tags": ["Security"],
                "summary": "Revoke API key",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/auth/rate-limit": {
            "get": {
                "tags": ["Security"],
                "summary": "Get rate limit status",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },

        # ==================== GAMIFICATION (3) ====================
        "/gamification/challenges": {
            "get": {
                "tags": ["Gamification"],
                "summary": "List challenges",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            },
            "post": {
                "tags": ["Gamification"],
                "summary": "Create challenge",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "201": {"description": "Created"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/gamification/badges": {
            "get": {
                "tags": ["Gamification"],
                "summary": "List badges",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },

        # ==================== NOTIFICATIONS (7) ====================
        "/notifications/settings": {
            "get": {
                "tags": ["Notifications"],
                "summary": "Get notification settings",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/notifications/send": {
            "post": {
                "tags": ["Notifications"],
                "summary": "Send notification",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/notifications/rules": {
            "get": {
                "tags": ["Notifications"],
                "summary": "List notification rules",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            },
            "post": {
                "tags": ["Notifications"],
                "summary": "Create notification rule",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "201": {"description": "Created"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/notifications/rules/{id}": {
            "put": {
                "tags": ["Notifications"],
                "summary": "Update notification rule",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            },
            "delete": {
                "tags": ["Notifications"],
                "summary": "Delete notification rule",
                "security": [{"ApiKeyAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "type": "integer"}
                ],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/notifications/schedule": {
            "post": {
                "tags": ["Notifications"],
                "summary": "Schedule notification",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "201": {"description": "Created"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },

        # ==================== INTEGRATIONS (3) ====================
        "/wearables/connect": {
            "post": {
                "tags": ["Integrations"],
                "summary": "Connect wearable device",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "201": {"description": "Created"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/wearables/sync": {
            "post": {
                "tags": ["Integrations"],
                "summary": "Sync wearable data",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/voice/log": {
            "post": {
                "tags": ["Integrations"],
                "summary": "Log voice entry",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "201": {"description": "Created"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },

        # ==================== BILLING (2) ====================
        "/billing/status": {
            "get": {
                "tags": ["Billing"],
                "summary": "Get billing status",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/billing/webhook": {
            "post": {
                "tags": ["Billing"],
                "summary": "Billing webhook (signature verified)",
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Invalid signature"}
                }
            }
        },

        # ==================== USERS (3) ====================
        "/users/cohort-analysis": {
            "get": {
                "tags": ["Users"],
                "summary": "Cohort analysis",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/users/compare": {
            "get": {
                "tags": ["Users"],
                "summary": "Compare users",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/users/phenotypes": {
            "get": {
                "tags": ["Users"],
                "summary": "Get phenotypes",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },

        # ==================== REINTRODUCTION (3) ====================
        "/reintroduction/protocol": {
            "post": {
                "tags": ["Reintroduction"],
                "summary": "Start reintroduction protocol",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "201": {"description": "Created"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/reintroduction/schedule": {
            "get": {
                "tags": ["Reintroduction"],
                "summary": "Get reintroduction schedule",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/reintroduction/evaluate": {
            "post": {
                "tags": ["Reintroduction"],
                "summary": "Evaluate reintroduction results",
                "security": [{"ApiKeyAuth": []}],
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
    }
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/api/v1/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs",
}
