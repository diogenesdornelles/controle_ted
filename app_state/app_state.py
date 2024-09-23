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
    """
    Manages the application state, including user login status, session timeouts,
    file uploads, data processing, and task scheduling.

    Args:
        BaseModel (pydantic.BaseModel): The base model from Pydantic used for data validation and management.

    Attributes:
        username (str): The username of the logged-in user. Defaults to an empty string.
        timeout (int): The current timeout for the user session. Defaults to 0.
        max_timeout (int): The maximum timeout value allowed for the session. Defaults to 300 seconds.
        is_logged (bool): Indicates whether the user is logged in or not. Defaults to False.
        file_uploaded (UploadedFile | None): The file uploaded by the user, if any. Defaults to None.
        df (DataFrame | bool): A DataFrame containing data loaded into the app. Defaults to data from `statefull_dataframe_handler.get_df()`.
        task_process (TaskSettings): Manages the current task process, storing details such as the process itself,
            when it started, and whether it should be running. Defaults to {"since": "", "process": None, "should_run": False}.

    Returns:
        None
    """

    username: str = ""
    timeout: int = 0
    max_timeout: int = 300
    is_logged: bool = False
    file_uploaded: None | UploadedFile = None
    df: DataFrame | bool = statefull_dataframe_handler.get_df()
    task_process: TaskSettings = {"since": "", "process": None, "should_run": False}

    class Config:
        """
        Configuration for the AppState class.

        Attributes:
            arbitrary_types_allowed (bool): Allows for arbitrary types to be used in the Pydantic model,
                                            enabling usage of types like DataFrame and UploadedFile.
        """

        arbitrary_types_allowed = True

    def check_login(self, username: str, pwd: str) -> bool:
        """
        Validates the login credentials by checking if the provided username and password match the stored settings.

        Args:
            username (str): The username entered by the user.
            pwd (str): The password entered by the user.

        Returns:
            bool: True if the login is successful, False otherwise.
        """
        if username == settings.user_app and pwd == settings.user_pwd:
            self.is_logged = True
            self.username = username
            return True
        return False

    def restore_timeout(self) -> None:
        """
        Resets the session timeout to the maximum value.
        """
        self.timeout = self.max_timeout

    def kill_task(self) -> bool:
        """
        Terminates the currently running task process, if one exists and is active.

        Returns:
            bool: True if the task was successfully terminated, False otherwise.
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
        """
        Starts a new task process if no process is currently running and a file exists.

        Returns:
            bool: True if the task process was successfully started, False otherwise.
        """
        try:
            if not self.task_process["process"] and Path("planilha.xlsx").exists():  # type: ignore
                task_process = Process(target=run_schedule)
                task_process.start()  # Uncomment to start the process
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


# Initialize the state object in the session if it doesn't already exist
if "state" not in st.session_state:
    st.session_state.state = AppState()

# Assign state to the session state object
state = st.session_state.state
