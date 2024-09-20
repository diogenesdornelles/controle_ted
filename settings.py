import os

import toml
from pydantic_settings import BaseSettings, SettingsConfigDict


def load_toml_into_environment(toml_file: str):
    try:
        secrets = toml.load(toml_file)
    except FileNotFoundError:
        print(f"Arquivo {toml_file} não encontrado.")
        return
    except toml.TomlDecodeError:
        print(f"Erro ao decodificar o arquivo TOML {toml_file}.")
        return

    # Define as variáveis de ambiente
    for key, value in secrets.items():
        os.environ[key] = value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        validate_default=False,
        env_file_encoding="utf-8",
        extra="allow",
    )
    gmail_pwd: str = ""
    user_pwd: str = ""
    user_app: str = ""


load_toml_into_environment("streamlit/secrets.toml")

settings = Settings()

if __name__ == "__main__":
    s = Settings()
    print(s.model_dump())
