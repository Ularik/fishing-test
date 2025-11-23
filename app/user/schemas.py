from ninja import Schema, Field
from typing import Optional
from datetime import datetime


class CurrentUserSchema(Schema):
    """Схема для вывода информации о текущем пользователе"""
    id: int
    user_name: str = Field(..., description='Имя пользователя')
    email: str = Field(..., description='Email пользователя')
    is_staff: bool = Field(..., description='Является ли пользователь сотрудником')
    is_active: bool = Field(..., description='Активен ли пользователь')
    is_superuser: bool = Field(..., description='Является ли пользователь суперпользователем')
    last_login: Optional[datetime] = Field(None, description='Последний вход')