from multiprocessing import Process
from typing import TypedDict


class TaskSettings(TypedDict):
    since: str
    process: Process | None
    should_run: bool
