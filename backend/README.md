# Vapi Webhook Backend

A production-ready FastAPI backend for receiving Vapi webhook requests and storing them in MongoDB Atlas.

## Tech Stack
- FastAPI (Python 3.12+)
- MongoDB Atlas
- Motor (Async MongoDB)
- Pydantic v2
- Uvicorn

## Features
- Handles Vapi webhooks (`end-of-call-report`, `conversation-ended`, `transcript`, etc.)
- Stores conversations and messages in separate MongoDB collections.
- Secure API endpoints using `X-API-Key` authentication.
- Pagination for fetching conversations.
- Soft-delete functionality.
- Global exception handling and logging.

## Local Setup

1. **Clone the repository and cd into `backend`**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up Environment Variables**:
   Copy `.env.example` to `.env` and fill in the values:
   ```env
   MONGODB_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/
   DATABASE_NAME=vapi_conversations
   API_KEY=your_secret_api_key_here
   PORT=8000
   ```
4. **Run the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints
- `GET /` - Health check
- `POST /api/v1/vapi/webhook` - Webhook receiver
- `GET /api/v1/conversations` - List conversations (paginated)
- `GET /api/v1/conversations/{callId}` - Get complete conversation
- `DELETE /api/v1/conversations/{callId}` - Soft delete a conversation

> All `/api/v1/*` endpoints require the `X-API-Key` header.

## Deployment to Render

1. Create a new "Web Service" on Render.
2. Connect your GitHub repository.
3. Render will automatically detect the `render.yaml` blueprint.
4. If not using Blueprint, set:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add your Environment Variables (`MONGODB_URI`, `DATABASE_NAME`, `API_KEY`) in the Render Dashboard.
6. After deployment, copy the URL and use it in Vapi's Server URL settings:
   `https://<your-render-url>.onrender.com/api/v1/vapi/webhook`
