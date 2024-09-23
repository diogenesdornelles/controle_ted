from pathlib import Path
from typing import Any

from pandas import DataFrame
from streamlit.runtime.uploaded_file_manager import UploadedFile
from app_dataframe.base_dataframe_handler import BaseDataframeHandler


class DataframeHandlerStateFull(BaseDataframeHandler):
    """
    Manipulador de DataFrame com estado (integrado à aplicação).
    Usa o estado global para manipular o DataFrame.
    """

    def save_df(self, df: Any) -> bool:
        """Salva o DataFrame e atualiza o estado da aplicação."""
        if isinstance(df, DataFrame):
            self.delete_dataframe()
            if self.save_dataframe(df):
                return True
        return False

    def get_df(self, file: UploadedFile | None = None) -> DataFrame | bool:
        """Carrega e processa o DataFrame, atualizando o estado.

        Args:
            file (Any, optional): _description_. Defaults to None.

        Returns:
            bool: _description_
        """
        source = (
            file
            if isinstance(file, UploadedFile)
            else self.path if Path(self.path).exists() else None
        )
        if source:
            df = self.load_dataframe(source)
            if isinstance(df, DataFrame) and not df.empty:
                return self.preprocess_dataframe(df)
        return False


# Inicializando o manipulador de DataFrame
statefull_dataframe_handler = DataframeHandlerStateFull()
