from pydantic import BaseModel, Field

class InputSchema(BaseModel):
    tool_name: str 
    tool_input_data: str = Field(..., description="Path to the file to be converted to markdown")
