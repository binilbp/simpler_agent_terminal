import json
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError, model_validator
from typing import Literal

# load secrets from .env file
load_dotenv()



class LLMParams(BaseModel):
    #defining the possible services to user
    service: Literal["groq_api", "ollama" ] 
    model_name: str
    model_temp: float = Field(ge=0.0, le=2.0) # Temperature constraints
    max_retry: int = Field(default=2, ge=0)
    max_tokens: int = Field(default=300, gt=0, le=600)



class Settings(BaseModel):
    name: str
    default_dir: str
    debug: bool
    classifier_llm: LLMParams
    agent_llm: LLMParams
    


    # custom setup logic
    @model_validator(mode='after')
    def validate_and_setup(self):

        # Setup and check default directory
        if self.default_dir == "default":
            # Overwrite the string with the user's actual home directory
            self.default_dir = f'{(Path.home())}/'
        else:
            # Check if the custom directory setup is present in system
            if not os.path.exists(self.default_dir):
                raise ValueError(f"Provided default directory path '{self.default_dir}' doesn't seem to exist in system.")

        # Check Classifier Service api key
        if self.classifier_llm.service == "groq_api" and not os.getenv("GROQ_API_KEY"):
            raise ValueError("Configuration asks for 'groq_api' in classifier_llm, but GROQ_API_KEY is missing in .env")
            
        # Check Command Gen Service api key
        if self.agent_llm.service == "groq_api" and not os.getenv("GROQ_API_KEY"):
            raise ValueError("Configuration asks for 'groq_api' in command_gen_llm, but GROQ_API_KEY is missing in .env")
            
        return self




BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_PATH = os.path.join(BASE_DIR, "config", "settings.json")



def load_settings() -> Settings:
    if not os.path.exists(SETTINGS_PATH):
        raise FileNotFoundError(f"settings.json missing at {SETTINGS_PATH}")


    with open(SETTINGS_PATH, "r") as f:
        data = json.load(f)

    try:
        # Pydantic validates types and runs the @model_validator above
        settings = Settings(**data)
        return settings
    except ValidationError as e:
        print("\n!!! CONFIGURATION ERROR !!!")
        print(f"Validation failed:\n{e}")
        # Exit or re-raise depending on preference
        raise



# Instantiate globally
SETTINGS = load_settings()
