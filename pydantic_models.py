from enum import Enum
from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationError
from datetime import date, datetime
from typing import Optional, Literal
import re

class UserLoginRegister(BaseModel):
    login: str = Field(default=..., min_length=5, max_length=30, description="Логин пользователя")
    password: str = Field(default=..., min_length=8, max_length=40, description="Пароль пользователя")

class Identity(BaseModel):
    sinner: Literal['Yi Sang', 'Faust', 'Don Quixote', 'Ryoshu', 'Meursault', 'Hong Lu', 'Heathcliff', 'Ishmael',
                    'Rodion', 'Dante', 'Sinclair', 'Outis', 'Gregor'
    ]
    title: str = Field(default=..., min_length=5, max_length=50, description="Название идентичности")
    rarity: Literal['0', '00', '000']
    file: Optional[str]  = Field(max_length=255, description="URL изображения")

