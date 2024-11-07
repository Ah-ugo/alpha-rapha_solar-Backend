from DB.db import projects_db
from models import Project, ObjectId
from fastapi import HTTPException, UploadFile
from typing import Optional, List
from utils.cloudinary_upload import UploadToCloudinary


def getAllProjects():
    query = projects_db.find({})
    arr = []

    for project in query:
        arr.append(Project(**project))

    return arr


def getProjectById(id):
    query = projects_db.find_one({"_id": ObjectId(id)})

    if query:
        query["_id"] = str(query["_id"])
        return query
    else:
        raise HTTPException(status_code=404, detail=f"Project with id {id} not found")


def getProjectsByTitle(title):
    query = projects_db.find({"title": {"$regex": title, "$options": "i"}})
    arr = []

    for project in query:
        project["_id"] = str(project["_id"])
        arr.append(Project(**project))
    if not arr:
        raise HTTPException(status_code=404, detail=f"No products found containing '{title}'")

    return arr

def AddProject(title: Optional[str], description: Optional[str], images: List[UploadFile]):
    productDict = {
        "title": title,
        "description": description,
        "images": UploadToCloudinary(images)
    }

    insertQuery = projects_db.insert_one(productDict)

    get_inserted_data = projects_db.find_one({"_id": insertQuery.inserted_id})

    return Project(**get_inserted_data)


def updateProject(id, body):
    update_data = {k: v for k, v in body.dict().items() if v is not None}
    find_query = projects_db.find_one({"_id": ObjectId(id)})

    if find_query:
        projects_db.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        get_updated = projects_db.find_one({"_id": ObjectId(id)})
        get_updated["_id"] = str(get_updated["_id"])
        return get_updated
    else:
        raise HTTPException(status_code=404, detail=f"Project with id {id} not found")


def deleteProject(id):
    del_query = projects_db.delete_one({"_id": ObjectId(id)})

    if del_query:
        return f"Project with ID: {id} was deleted successfully"
    else:
        return "Something went wrong"

