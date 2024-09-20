from datetime import datetime as dt
from multiprocessing import Process
from pathlib import Path

from pandas import DataFrame
from pydantic import BaseModel
from streamlit.runtime.uploaded_file_manager import UploadedFile

import streamlit as st
from app_dataframe.statefull_dataframe_handler import \
    statefull_dataframe_handler
from app_models.models import TaskSettings
from app_schedule.end_schedule import end_schedule
from app_schedule.run_schedule import run_schedule
from settings import settings


class AppState(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_

    Returns:
        _type_: _description_
    """

    username: str = ""
    timeout: int = 0
    max_timeout: int = 300
    is_logged: bool = False
    pwd_ok: bool = False
    file_uploaded: None | UploadedFile = None
    df: DataFrame | bool = statefull_dataframe_handler.get_df()
    task_process: TaskSettings = {"since": "", "process": None, "should_run": False}

    class Config:
        """_summary_"""

        arbitrary_types_allowed = True

    def check_login(self, username: str, pwd: str) -> bool:

        if username == settings.user_app and pwd == settings.user_pwd:
            self.is_logged = True
            self.username = username
            return True
        return False

    def restore_timeout(self) -> None:
        self.timeout = self.max_timeout

    def kill_task(self) -> bool:
        """_summary_

        Returns:
            bool: _description_
        """
        try:
            if (
                self.task_process["process"]
                and isinstance(self.task_process["process"], Process)
                and self.task_process["process"].is_alive()  # type: ignore
            ):
                self.task_process["process"].terminate()  # type: ignore
                self.task_process["process"].join()  # type: ignore
                self.task_process = TaskSettings(
                    since="",
                    process=None,
                    should_run=False,
                )
                end_task_process = Process(target=end_schedule)
                end_task_process.start()  # Uncomment to start the process
                end_task_process.terminate()  # type: ignore
                end_task_process.join()  # type: ignore
                return True
            return False
        except Exception as err:
            print(err)
            return False

    def start_task(self) -> bool:
        """_summary_

        Returns:
            bool: _description_
        """
        try:
            if not self.task_process["process"] and Path("planilha.xlsx").exists():  # type: ignore

                task_process = Process(target=run_schedule)
                # task_process.start()  # Uncomment to start the process
                self.task_process = TaskSettings(
                    since=dt.now().strftime("%d/%m/%Y %H:%M:%S"),
                    process=task_process,
                    should_run=True,
                )
                return True
            return False
        except Exception as err:
            print(err)
            return False


if "state" not in st.session_state:
    st.session_state.state = AppState()

state = st.session_state.state
