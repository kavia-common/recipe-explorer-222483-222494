# Recipe Explorer Backend

FastAPI service for recipes, categories, search, favorites, auth, and image upload.

Run:
- pip install -r requirements.txt
- cp .env.example .env (optional)
- uvicorn src.api.main:app --host 0.0.0.0 --port 3001

API:
- Health: GET /
- Auth: POST /auth/signup, POST /auth/login
- Categories: GET /categories/
- Recipes: GET /recipes/, GET /recipes/{id}, GET /recipes/search/by?q=...&ingredients=ing1,ing2
- Favorites: GET /users/{id}/favorites, POST /users/{id}/favorites, DELETE /users/{id}/favorites/{recipe_id}
- Images: POST /images/upload (multipart), GET /images/{filename}

Env:
- DATABASE_URL or POSTGRES_* fallbacks
- SECRET_KEY, TOKEN_TTL_SECONDS, PASSWORD_SALT
- FRONTEND_URL for CORS
- UPLOAD_DIR for images
