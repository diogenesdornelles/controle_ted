from pandas import DataFrame

from app_schedule.get_email_body import get_email_body
from app_schedule.send_email import send_email


def check_and_send_email(df: DataFrame, column: str, today: str) -> None:
    """Verifica se há dados na coluna para a data atual e envia email se houver

    Args:
        df (DataFrame): _description_
        column (str): _description_
        today (str): _description_
    """
    if column in df.columns:
        filtered_df = df[df[column] == today]
        if len(filtered_df) > 0:
            send_email(
                column,
                get_email_body(filtered_df.to_html(), column),
            )
