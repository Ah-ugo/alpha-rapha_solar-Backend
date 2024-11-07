from fastapi import APIRouter, Form, UploadFile, File, Depends, Response, FastAPI
from typing import List
from Services.project_services import getAllProjects, getProjectById, getProjectsByTitle, AddProject, updateProject, deleteProject
from Services.auth_services import verify_admin
from models import ProjectsBase

# from fastapi.

router = APIRouter()


@router.get("/")
def get_all_projects():
    return getAllProjects()


@router.get("/{id}")
def get_project_by_id(id: str):
    return getProjectById(id)


@router.get("/title/{title}")
def get_projects_by_title(title: str):
    return getProjectsByTitle(title)


@router.post("/")
def add_project(title: str = Form(...), description: str = Form(...), images: List[UploadFile] = File(None), current_user: dict = Depends(verify_admin)):
    return AddProject(title, description, images)


@router.patch("/{id}")
def edit_product(id: str, body: ProjectsBase, current_user: dict = Depends(verify_admin)):
    return updateProject(id=id, body=body)

@router.delete("/{id}")
def delete_product(id: str, current_user: dict = Depends(verify_admin)):
    return deleteProject(id)





