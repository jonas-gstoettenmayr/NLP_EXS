from fastmcp import FastMCP
from datetime import datetime
from typing import Annotated
from pydantic import Field
import json

# used AI to quickly annotate the different parameters of the tools

class Task:
    def __init__(self: "Task",
                 title: Annotated[str, Field(..., description="Title of the task")],
                 assignee: Annotated[str, Field(..., description="Person assigned to the task")],
                 due: Annotated[datetime, Field(..., description="Due date/time in ISO format")],
                 description: Annotated[str, Field(..., description="Detailed description of the task")]):
        self._title = title
        self._assignee = assignee
        self._due = due
        self._status = "Pending"
        self._description = description
    
    def __json__(self):
        return {
            "title": self._title,
            "assignee": self._assignee,
            "due": self._due.isoformat(),
            "status":self._status,
            "description": self._description,
        }

task_list: dict[int, Task] = {}

def id_generator():
    current_id = 1
    while True:
        yield current_id
        current_id += 1
ids = id_generator()

# Create MCP server
mcp = FastMCP("ProjectManagementTools",
              instructions="""
              This is a project management tool that helps teams organize tasks, track progress, and collaborate effectively.
              It provides features such as task creation, assignment, status updates, and deadline tracking.""")

# Define tools
@mcp.tool()
def create_task(
    title: Annotated[str, Field(..., description="Task title")],
    assignee: Annotated[str, Field(..., description="Assignee name")],
    due: Annotated[datetime, Field(..., description="Due date/time in ISO format")],
    description: Annotated[str, Field(..., description="Task description")],
) -> int:
    """Creates a new Pending task with the given title, due date and description, and returns the task ID.

    Args:
        title (str): the title of the task card
        assignee (str): name of who the task is assigned to
        due (datetime): when the task is due, date in ISO format
        description (str): a short description of the task

    Returns:
        int: the id if the newly created task
    """
    print(f"Creating task: {title}, Assignee: {assignee}, Due: {due}")
    id = next(ids)
    newTask = Task(title=title, assignee= assignee, due= due, description=description) 
    task_list[id] = (newTask)
    return id  # Return the task ID

@mcp.tool()
def list_tasks() -> Annotated[dict[int, str], Field(..., description="A dictionary listing the id and the task belonging to the id")]:
    """List all tasks.

    Returns:
        dict[int, Task]: a dictionary of the task id and the task belonging to it
    """
    return {k:json.dumps(v.__json__()) for k, v in task_list.items()}

@mcp.tool()
def update_task(
    task_id: Annotated[int, Field(..., description="ID of the task to update")],
    status: Annotated[str, Field(..., description="New status, e.g. Pending, In Progress, Done")],
) -> str:
    """Updates the status of a task.

    Args:
        task_id (int): the id of the task to change
        status (str): the new status of the task

    Returns:
        str: a message of succes or an error
    """
    if task_id in task_list.keys():
        print(f"Updating task {task_id} to status: {status}")
        task_list[task_id]._status = status
        return "Success"
    return "Task id invalid"

# Run as HTTP server
if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000
    )