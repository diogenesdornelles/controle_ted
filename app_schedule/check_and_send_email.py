from pandas import DataFrame

from app_schedule.get_email_body import get_email_body
from app_schedule.send_email import send_email


def check_and_send_email(df: DataFrame, column: str, today: str) -> None:
    """
    Verifica se há dados em uma coluna específica que correspondam à data atual e envia um email se houver.

    Esta função verifica uma coluna de um DataFrame para encontrar linhas que contenham a data fornecida.
    Se encontrar dados para a data atual, ela envia um email com essas informações.

    Args:
        df (DataFrame): O DataFrame contendo os dados a serem verificados.
        column (str): O nome da coluna onde as datas estão armazenadas.
        today (str): A data de hoje em formato de string, usada para filtrar os dados (deve estar no mesmo formato das datas na coluna).

    Raises:
        None
    """
    if column in df.columns:
        # Filtra o DataFrame para encontrar linhas onde o valor da coluna seja igual à data de hoje
        filtered_df = df[df[column] == today]

        # Verifica se existem linhas após o filtro
        if len(filtered_df) > 0:
            # Envia um email com os dados filtrados em formato HTML
            send_email(
                column,
                get_email_body(filtered_df.to_html(), column),
            )
