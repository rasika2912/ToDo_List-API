from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from bson.objectid import ObjectId
from typing import Optional

# Initialize FastAPI app
app = FastAPI()

# MongoDB Configuration
client = MongoClient("mongodb+srv://rasikadehankar2912:Dehankar%402912@cluster0.xzmmx.mongodb.net")
db = client["todolist"]
collection = db["tasks"]

# Pydantic model for task input
class Task(BaseModel):
    task: str
    description: str
    status: bool = True  # Default to True for active tasks

class UpdateTask(BaseModel):
    task: Optional[str] = None
    description: Optional[str] = None

# POST: Add a new task
@app.post("/tasks")
async def create_task(task: Task):
    task_data = task.dict()  # Convert task to dictionary
    result = collection.insert_one(task_data)  # Only store task and description
    response = {
        "id": str(result.inserted_id),
        "task": task.task,
        "description": task.description,
        "status": task.status,
    }
    return response

# GET: Retrieve all active tasks
@app.get("/tasks")
async def get_tasks():
    tasks = []
    for task in collection.find({"status": True}):  # Only retrieve tasks where status is True
        task["_id"] = str(task["_id"])  # Convert _id to string
        tasks.append(task)
    return tasks

# PATCH: Update specific fields of a task
@app.patch("/tasks/{task_id}")
async def update_task(task_id: str, update_data: UpdateTask):
    updated_fields = {k: v for k, v in update_data.dict().items() if v is not None}
    if not updated_fields:
        raise HTTPException(status_code=400, detail="No valid fields provided for update")

    result = collection.update_one(
        {"_id": ObjectId(task_id)}, {"$set": updated_fields}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")

    task = collection.find_one({"_id": ObjectId(task_id)})
    task["_id"] = str(task["_id"])
    return task

# PUT: Update the status of a task (Mark as completed)
@app.put("/tasks/{task_id}")
async def mark_task_completed(task_id: str):
    result = collection.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": {"status": True}}  # Mark the task as completed (status remains True)
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")

    task = collection.find_one({"_id": ObjectId(task_id)})
    task["_id"] = str(task["_id"])
    return task

# DELETE: Soft Delete a task (set status to False)
@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    result = collection.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": {"status": False}}  # Soft delete: set status to False
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task soft deleted successfully"}



