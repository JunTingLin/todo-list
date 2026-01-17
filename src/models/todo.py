"""Todo Pydantic models for data validation."""

from pydantic import BaseModel, Field


class TodoCreate(BaseModel):
    """Model for creating a new todo item."""
    title: str = Field(..., min_length=1, max_length=200, description="待辦事項標題")
    completed: bool = Field(default=False, description="完成狀態")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "購買牛奶",
                    "completed": False
                }
            ]
        }
    }


class TodoUpdate(BaseModel):
    """Model for updating an existing todo item."""
    title: str | None = Field(None, min_length=1, max_length=200, description="待辦事項標題")
    completed: bool | None = Field(None, description="完成狀態")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "購買牛奶和麵包",
                    "completed": True
                }
            ]
        }
    }


class TodoResponse(BaseModel):
    """Model for todo item responses."""
    id: str = Field(..., description="唯一識別碼")
    title: str = Field(..., description="待辦事項標題")
    completed: bool = Field(..., description="完成狀態")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "1",
                    "title": "購買牛奶",
                    "completed": False
                }
            ]
        }
    }
