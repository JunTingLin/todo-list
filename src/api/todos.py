"""Todo API endpoints."""

from typing import List
from fastapi import APIRouter, HTTPException, status
from src.models.todo import TodoCreate, TodoUpdate, TodoResponse
from src.storage.memory import get_todo_store

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoCreate):
    """
    建立新的待辦事項

    - **title**: 待辦事項標題 (1-200字元)
    - **completed**: 完成狀態 (預設為 false)
    """
    store = get_todo_store()
    return store.create(todo)


@router.get("", response_model=List[TodoResponse])
async def list_todos():
    """
    取得所有待辦事項清單

    回傳所有待辦事項，若無待辦事項則回傳空陣列。
    """
    store = get_todo_store()
    return store.list_all()


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: str):
    """
    取得單一待辦事項

    - **todo_id**: 待辦事項唯一識別碼

    若待辦事項不存在，回傳 404 錯誤。
    """
    store = get_todo_store()
    todo = store.get(todo_id)

    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with id '{todo_id}' not found"
        )

    return todo


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: str, todo_update: TodoUpdate):
    """
    更新待辦事項

    - **todo_id**: 待辦事項唯一識別碼
    - **title**: 新的標題 (選填)
    - **completed**: 新的完成狀態 (選填)

    若待辦事項不存在，回傳 404 錯誤。
    """
    store = get_todo_store()
    updated_todo = store.update(todo_id, todo_update)

    if updated_todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with id '{todo_id}' not found"
        )

    return updated_todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: str):
    """
    刪除待辦事項

    - **todo_id**: 待辦事項唯一識別碼

    若待辦事項不存在，回傳 404 錯誤。
    成功刪除回傳 204 No Content。
    """
    store = get_todo_store()
    deleted = store.delete(todo_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with id '{todo_id}' not found"
        )

    return None
