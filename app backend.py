Let me start building this incredible app! 🚀

## **Phase 1: Backend Development**
Action: file_editor create /app/backend/server.py --file-text "from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone, date
from enum import Enum


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix=\"/api\")


# ==================== ENUMS ====================
class Priority(str, Enum):
    LOW = \"low\"
    MEDIUM = \"medium\"
    HIGH = \"high\"
    URGENT = \"urgent\"


class TaskStatus(str, Enum):
    TODO = \"todo\"
    IN_PROGRESS = \"in_progress\"
    COMPLETED = \"completed\"


class HabitFrequency(str, Enum):
    DAILY = \"daily\"
    WEEKLY = \"weekly\"
    CUSTOM = \"custom\"


# ==================== MODELS ====================

# Task Models
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.TODO
    due_date: Optional[str] = None
    category: Optional[str] = None


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.TODO
    due_date: Optional[str] = None
    category: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None


# Note Models
class NoteCreate(BaseModel):
    title: str
    content: str
    category: Optional[str] = None
    is_pinned: bool = False


class Note(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    category: Optional[str] = None
    is_pinned: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# Habit Models
class HabitCreate(BaseModel):
    name: str
    description: Optional[str] = None
    frequency: HabitFrequency = HabitFrequency.DAILY
    target_days: Optional[int] = None


class Habit(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    frequency: HabitFrequency = HabitFrequency.DAILY
    target_days: Optional[int] = None
    streak: int = 0
    last_completed: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    history: List[str] = []


# Link Models
class LinkCreate(BaseModel):
    title: str
    url: str
    description: Optional[str] = None
    category: Optional[str] = None


class Link(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    url: str
    description: Optional[str] = None
    category: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# Analytics Models
class DashboardStats(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    total_notes: int
    total_habits: int
    active_streaks: int
    total_links: int
    completion_rate: float


# ==================== TASK ENDPOINTS ====================
@api_router.get(\"/tasks\", response_model=List[Task])
async def get_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[Priority] = None,
    category: Optional[str] = None
):
    query = {}
    if status:
        query[\"status\"] = status
    if priority:
        query[\"priority\"] = priority
    if category:
        query[\"category\"] = category
    
    tasks = await db.tasks.find(query, {\"_id\": 0}).sort(\"created_at\", -1).to_list(1000)
    return tasks


@api_router.get(\"/tasks/{task_id}\", response_model=Task)
async def get_task(task_id: str):
    task = await db.tasks.find_one({\"id\": task_id}, {\"_id\": 0})
    if not task:
        raise HTTPException(status_code=404, detail=\"Task not found\")
    return task


@api_router.post(\"/tasks\", response_model=Task)
async def create_task(task_input: TaskCreate):
    task = Task(**task_input.model_dump())
    await db.tasks.insert_one(task.model_dump())
    return task


@api_router.put(\"/tasks/{task_id}\", response_model=Task)
async def update_task(task_id: str, task_input: TaskCreate):
    existing_task = await db.tasks.find_one({\"id\": task_id}, {\"_id\": 0})
    if not existing_task:
        raise HTTPException(status_code=404, detail=\"Task not found\")
    
    updated_data = task_input.model_dump()
    updated_data[\"updated_at\"] = datetime.now(timezone.utc).isoformat()
    
    # Set completed_at if status changed to completed
    if updated_data[\"status\"] == TaskStatus.COMPLETED and existing_task[\"status\"] != TaskStatus.COMPLETED:
        updated_data[\"completed_at\"] = datetime.now(timezone.utc).isoformat()
    elif updated_data[\"status\"] != TaskStatus.COMPLETED:
        updated_data[\"completed_at\"] = None
    
    await db.tasks.update_one({\"id\": task_id}, {\"$set\": updated_data})
    
    updated_task = await db.tasks.find_one({\"id\": task_id}, {\"_id\": 0})
    return updated_task


@api_router.delete(\"/tasks/{task_id}\")
async def delete_task(task_id: str):
    result = await db.tasks.delete_one({\"id\": task_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=\"Task not found\")
    return {\"message\": \"Task deleted successfully\"}


# ==================== NOTE ENDPOINTS ====================
@api_router.get(\"/notes\", response_model=List[Note])
async def get_notes(category: Optional[str] = None):
    query = {}
    if category:
        query[\"category\"] = category
    
    notes = await db.notes.find(query, {\"_id\": 0}).sort([(\"is_pinned\", -1), (\"updated_at\", -1)]).to_list(1000)
    return notes


@api_router.get(\"/notes/{note_id}\", response_model=Note)
async def get_note(note_id: str):
    note = await db.notes.find_one({\"id\": note_id}, {\"_id\": 0})
    if not note:
        raise HTTPException(status_code=404, detail=\"Note not found\")
    return note


@api_router.post(\"/notes\", response_model=Note)
async def create_note(note_input: NoteCreate):
    note = Note(**note_input.model_dump())
    await db.notes.insert_one(note.model_dump())
    return note


@api_router.put(\"/notes/{note_id}\", response_model=Note)
async def update_note(note_id: str, note_input: NoteCreate):
    existing = await db.notes.find_one({\"id\": note_id}, {\"_id\": 0})
    if not existing:
        raise HTTPException(status_code=404, detail=\"Note not found\")
    
    updated_data = note_input.model_dump()
    updated_data[\"updated_at\"] = datetime.now(timezone.utc).isoformat()
    
    await db.notes.update_one({\"id\": note_id}, {\"$set\": updated_data})
    updated_note = await db.notes.find_one({\"id\": note_id}, {\"_id\": 0})
    return updated_note


@api_router.delete(\"/notes/{note_id}\")
async def delete_note(note_id: str):
    result = await db.notes.delete_one({\"id\": note_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=\"Note not found\")
    return {\"message\": \"Note deleted successfully\"}


# ==================== HABIT ENDPOINTS ====================
@api_router.get(\"/habits\", response_model=List[Habit])
async def get_habits():
    habits = await db.habits.find({}, {\"_id\": 0}).sort(\"created_at\", -1).to_list(1000)
    return habits


@api_router.get(\"/habits/{habit_id}\", response_model=Habit)
async def get_habit(habit_id: str):
    habit = await db.habits.find_one({\"id\": habit_id}, {\"_id\": 0})
    if not habit:
        raise HTTPException(status_code=404, detail=\"Habit not found\")
    return habit


@api_router.post(\"/habits\", response_model=Habit)
async def create_habit(habit_input: HabitCreate):
    habit = Habit(**habit_input.model_dump())
    await db.habits.insert_one(habit.model_dump())
    return habit


@api_router.post(\"/habits/{habit_id}/complete\", response_model=Habit)
async def complete_habit(habit_id: str):
    habit = await db.habits.find_one({\"id\": habit_id}, {\"_id\": 0})
    if not habit:
        raise HTTPException(status_code=404, detail=\"Habit not found\")
    
    today = date.today().isoformat()
    
    # Check if already completed today
    if habit.get(\"last_completed\") == today:
        raise HTTPException(status_code=400, detail=\"Habit already completed today\")
    
    # Update streak
    last_completed = habit.get(\"last_completed\")
    streak = habit.get(\"streak\", 0)
    
    if last_completed:
        from datetime import timedelta
        last_date = date.fromisoformat(last_completed)
        today_date = date.today()
        diff = (today_date - last_date).days
        
        if diff == 1:
            streak += 1
        else:
            streak = 1
    else:
        streak = 1
    
    # Update history
    history = habit.get(\"history\", [])
    history.append(today)
    
    await db.habits.update_one(
        {\"id\": habit_id},
        {\"$set\": {
            \"streak\": streak,
            \"last_completed\": today,
            \"history\": history
        }}
    )
    
    updated_habit = await db.habits.find_one({\"id\": habit_id}, {\"_id\": 0})
    return updated_habit


@api_router.put(\"/habits/{habit_id}\", response_model=Habit)
async def update_habit(habit_id: str, habit_input: HabitCreate):
    existing = await db.habits.find_one({\"id\": habit_id}, {\"_id\": 0})
    if not existing:
        raise HTTPException(status_code=404, detail=\"Habit not found\")
    
    updated_data = habit_input.model_dump()
    await db.habits.update_one({\"id\": habit_id}, {\"$set\": updated_data})
    updated_habit = await db.habits.find_one({\"id\": habit_id}, {\"_id\": 0})
    return updated_habit


@api_router.delete(\"/habits/{habit_id}\")
async def delete_habit(habit_id: str):
    result = await db.habits.delete_one({\"id\": habit_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=\"Habit not found\")
    return {\"message\": \"Habit deleted successfully\"}


# ==================== LINK ENDPOINTS ====================
@api_router.get(\"/links\", response_model=List[Link])
async def get_links(category: Optional[str] = None):
    query = {}
    if category:
        query[\"category\"] = category
    
    links = await db.links.find(query, {\"_id\": 0}).sort(\"created_at\", -1).to_list(1000)
    return links


@api_router.get(\"/links/{link_id}\", response_model=Link)
async def get_link(link_id: str):
    link = await db.links.find_one({\"id\": link_id}, {\"_id\": 0})
    if not link:
        raise HTTPException(status_code=404, detail=\"Link not found\")
    return link


@api_router.post(\"/links\", response_model=Link)
async def create_link(link_input: LinkCreate):
    link = Link(**link_input.model_dump())
    await db.links.insert_one(link.model_dump())
    return link


@api_router.put(\"/links/{link_id}\", response_model=Link)
async def update_link(link_id: str, link_input: LinkCreate):
    existing = await db.links.find_one({\"id\": link_id}, {\"_id\": 0})
    if not existing:
        raise HTTPException(status_code=404, detail=\"Link not found\")
    
    updated_data = link_input.model_dump()
    await db.links.update_one({\"id\": link_id}, {\"$set\": updated_data})
    updated_link = await db.links.find_one({\"id\": link_id}, {\"_id\": 0})
    return updated_link


@api_router.delete(\"/links/{link_id}\")
async def delete_link(link_id: str):
    result = await db.links.delete_one({\"id\": link_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=\"Link not found\")
    return {\"message\": \"Link deleted successfully\"}


# ==================== ANALYTICS ENDPOINTS ====================
@api_router.get(\"/analytics/dashboard\", response_model=DashboardStats)
async def get_dashboard_stats():
    # Get all counts
    total_tasks = await db.tasks.count_documents({})
    completed_tasks = await db.tasks.count_documents({\"status\": TaskStatus.COMPLETED})
    pending_tasks = total_tasks - completed_tasks
    total_notes = await db.notes.count_documents({})
    total_habits = await db.habits.count_documents({})
    total_links = await db.links.count_documents({})
    
    # Get active streaks (habits with streak > 0)
    habits = await db.habits.find({}, {\"_id\": 0}).to_list(1000)
    active_streaks = sum(1 for h in habits if h.get(\"streak\", 0) > 0)
    
    # Calculate completion rate
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return DashboardStats(
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        total_notes=total_notes,
        total_habits=total_habits,
        active_streaks=active_streaks,
        total_links=total_links,
        completion_rate=round(completion_rate, 1)
    )


# ==================== SEARCH ENDPOINT ====================
@api_router.get(\"/search\")
async def search(q: str = Query(..., min_length=1)):
    results = {
        \"tasks\": [],
        \"notes\": [],
        \"habits\": [],
        \"links\": []
    }
    
    # Search tasks
    tasks = await db.tasks.find(
        {\"$or\": [
            {\"title\": {\"$regex\": q, \"$options\": \"i\"}},
            {\"description\": {\"$regex\": q, \"$options\": \"i\"}}
        ]},
        {\"_id\": 0}
    ).to_list(50)
    results[\"tasks\"] = tasks
    
    # Search notes
    notes = await db.notes.find(
        {\"$or\": [
            {\"title\": {\"$regex\": q, \"$options\": \"i\"}},
            {\"content\": {\"$regex\": q, \"$options\": \"i\"}}
        ]},
        {\"_id\": 0}
    ).to_list(50)
    results[\"notes\"] = notes
    
    # Search habits
    habits = await db.habits.find(
        {\"$or\": [
            {\"name\": {\"$regex\": q, \"$options\": \"i\"}},
            {\"description\": {\"$regex\": q, \"$options\": \"i\"}}
        ]},
        {\"_id\": 0}
    ).to_list(50)
    results[\"habits\"] = habits
    
    # Search links
    links = await db.links.find(
        {\"$or\": [
            {\"title\": {\"$regex\": q, \"$options\": \"i\"}},
            {\"description\": {\"$regex\": q, \"$options\": \"i\"}},
            {\"url\": {\"$regex\": q, \"$options\": \"i\"}}
        ]},
        {\"_id\": 0}
    ).to_list(50)
    results[\"links\"] = links
    
    return results


# ==================== ROOT ENDPOINT ====================
@api_router.get(\"/\")
async def root():
    return {
        \"message\": \"LifeFlow API\",
        \"version\": \"1.0.0\",
        \"endpoints\": {
            \"tasks\": \"/api/tasks\",
            \"notes\": \"/api/notes\",
            \"habits\": \"/api/habits\",
            \"links\": \"/api/links\",
            \"analytics\": \"/api/analytics/dashboard\",
            \"search\": \"/api/search\"
        }
    }


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=[\"*\"],
    allow_headers=[\"*\"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.on_event(\"shutdown\")
async def shutdown_db_client():
    client.close()
"
Observation: Overwrite successful: /app/backend/server.py
