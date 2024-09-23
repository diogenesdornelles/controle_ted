import os
from pathlib import Path
from typing import Any

import pandas as pd
from pandas import DataFrame
from pydantic import BaseModel


class BaseDataframeHandler(BaseModel):
    """
    Classe base para manipulação de DataFrame. Fornece funcionalidades
    comuns como carregamento, salvamento e exclusão de DataFrame.
    """

    path: str = "planilha.xlsx"
    columns: list[str] = [
        "Termo",
        "SIAFI",
        "Unidade Gestora Proponente",
        "Unidade Gestora Concedente",
        "Título / Objeto da despesa",
        "Situação Documento",
        "Coordenação",
        "Vigência inicial",
        "Vigência fim",
        "Data para alerta",
        "Data de prestação de contas",
    ]

    class Config:
        arbitrary_types_allowed = True

    def load_dataframe(self, source: Any = "planilha.xlsx") -> DataFrame | bool:
        """_summary_

        Args:
            source (Any, optional): _description_. Defaults to "planilha.xlsx".

        Returns:
            DataFrame: _description_
        """
        try:
            df = pd.read_excel(
                source if source != self.path else self.path if Path(self.path).exists() else None,
                engine="openpyxl",
                usecols=list(range(9)),
                index_col=None,
                names=self.columns[:-2],
                na_values=["-"],
                header=None
            )
            return df
        except Exception as e:
            print(f"Erro ao carregar o arquivo: {e}")
            return False

    def save_dataframe(self, df: DataFrame) -> bool:
        """Salva o DataFrame no arquivo Excel.

        Args:
            df (DataFrame): _description_

        Returns:
            bool: _description_
        """
        try:
            if isinstance(df, DataFrame):
                df.to_excel(self.path, engine="openpyxl")
                return True
        except Exception as e:
            print(f"Erro ao salvar o arquivo: {e}")
        return False

    def delete_dataframe(self) -> bool:
        """Exclui o arquivo do DataFrame se ele existir."""
        try:
            if Path(self.path).exists():
                os.remove(self.path)
                return True
        except Exception as e:
            print(f"Erro ao excluir o arquivo: {e}")
        return False

    def preprocess_dataframe(self, df: DataFrame) -> DataFrame | bool:
        """Aplica as transformações e pré-processamentos ao DataFrame.

        Args:
            df (DataFrame): _description_

        Returns:
            DataFrame: _description_
        """
        try:
            # Ajusta datas de vigência
            df[self.columns[-3]] = pd.to_datetime(
                df[self.columns[-3]], errors="coerce", dayfirst=True, format="%d/%m/%Y"
            )
            df[self.columns[-4]] = pd.to_datetime(
                df[self.columns[-4]], errors="coerce", dayfirst=True, format="%d/%m/%Y"
            )

            # Calcular datas de alerta e prestação de contas
            df[self.columns[-2]] = df[self.columns[-3]] + pd.DateOffset(days=-35)
            df[self.columns[-1]] = df[self.columns[-3]] + pd.DateOffset(days=120)

            # Filtrar linhas com datas válidas
            df = df[df[self.columns[-1]].notna()]

            # Ordenar pelas datas
            df.sort_values(
                by=[
                    self.columns[-4],
                    self.columns[-3],
                    self.columns[-2],
                    self.columns[-1],
                ],
                inplace=True,
            )

            # Preencher dados faltantes e ajustar tipos
            df[self.columns[0]] = (
                pd.to_numeric(df[self.columns[0]], errors="coerce")
                .fillna(0)
                .astype("str")
                .fillna("")
            )
            df.reset_index(inplace=True, drop=True)
            df.set_index(self.columns[0], inplace=True)

            # Formatar datas para string
            for col in self.columns[-4:]:
                df[col] = df[col].dt.strftime("%d/%m/%Y")

            return df

        except Exception as e:
            print(f"Erro ao processar o DataFrame: {e}")
            return False
