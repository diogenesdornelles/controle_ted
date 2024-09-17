from pandas import DataFrame

from app_dataframe.base_dataframe_handler import BaseDataframeHandler


class DataframeHandlerStatelles(BaseDataframeHandler):
    """
    Manipulador de DataFrame sem estado global.
    Herda as funcionalidades da classe BaseDataframeHandler.
    """

    def get_df(self) -> DataFrame | bool:
        """Carrega e pré-processa o DataFrame."""
        df = self.load_dataframe()
        if isinstance(df, DataFrame) and not df.empty:
            return self.preprocess_dataframe(df)
        return False


# Inicializando o manipulador de DataFrame
statelles_dataframe_handler = DataframeHandlerStatelles()
