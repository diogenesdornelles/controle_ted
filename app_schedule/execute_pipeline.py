from pandas import DataFrame

from app_dataframe.stateless_dataframe_handler import \
    statelles_dataframe_handler
from app_schedule.check_and_send_email import check_and_send_email
from utils.return_today_str import return_today_str


def execute_pipeline():
    """Executa o pipeline de verificação e envio de emails"""
    df = statelles_dataframe_handler.get_df()
    today = return_today_str()

    if isinstance(df, DataFrame):
        # Colunas para verificar em ordem de prioridade
        columns_to_check = [
            statelles_dataframe_handler.columns[-1],  # Data de prestação de contas
            statelles_dataframe_handler.columns[-2],  # Data de aviso
            statelles_dataframe_handler.columns[-3],  # Vigência final
        ]

        for column in columns_to_check:
            check_and_send_email(df, column, today)
