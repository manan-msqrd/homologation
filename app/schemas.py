# app/schemas.py

from pydantic import BaseModel, validator, ValidationError
from typing import List

class LoginSchema(BaseModel):
    employee_id: int
    password: str
    user_type: str

    @validator('user_type')
    def validate_user_type(cls, value):
        valid_user_types = {'operator', 'admin', 'superuser'}
        if value not in valid_user_types:
            raise ValueError(f"Invalid user_type. Valid options are: {', '.join(valid_user_types)}")
        return value
    
    
class RegistrationSchema(BaseModel):
    employee_id: int
    name: str
    designation: str
    password: str
    user_type: str

    @validator('user_type')
    def validate_user_type(cls, value):
        valid_user_types = {'operator', 'admin', 'superuser'}
        if value not in valid_user_types:
            raise ValueError(f"Invalid user_type. Valid options are: {', '.join(valid_user_types)}")
        return value

