import os
import toml
from pydantic_settings import BaseSettings, SettingsConfigDict


# Function to load environment variables from a TOML file
def load_toml_into_environment(toml_file: str) -> None:
    """load env variables from toml file

    Args:
        toml_file (str): URI toml file
    """
    try:
        # Try to load the TOML file
        secrets = toml.load(toml_file)
    except FileNotFoundError:
        # Handle case where the file is not found
        print(f"File {toml_file} not found.")
        return
    except toml.TomlDecodeError:
        # Handle errors if the TOML file is incorrectly formatted
        print(f"Error decoding the TOML file {toml_file}.")
        return

    # Set the environment variables from the loaded TOML file
    for key, value in secrets.items():
        os.environ[key] = value


# Define a settings class using Pydantic's BaseSettings
class Settings(BaseSettings):
    """Configuration for the settings model

    Args:
        BaseSettings (_type_): Pydantic's base classe
    """
    model_config = SettingsConfigDict(
        validate_default=False,  # Disable validation for default values
        env_file_encoding="utf-8",  # Set encoding for environment file
        extra="allow",  # Allow extra fields not defined in the model
    )

    # Define the expected environment variables with default values
    gmail_pwd: str = ""
    user_pwd: str = ""
    user_app: str = ""


# Load environment variables from the secrets TOML file
load_toml_into_environment("streamlit/secrets.toml")

# Initialize settings from environment variables
settings = Settings()

# Main execution block
if __name__ == "__main__":
    s = Settings()
    # Print the settings model as a dictionary
    print(s.model_dump())
