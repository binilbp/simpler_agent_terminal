# this file is used to return llm runnable configured with neccessary settings. 

from config.settings import SETTINGS
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama



def get_llm():
    service = SETTINGS.agent_llm.service

    match service:
        case "groq":
            return get_groq_agent()

        case "ollama":
            return get_ollama_agent()



def get_groq_agent():
    llm = ChatGroq(
        model = SETTINGS.agent_llm.model_name,
        temperature = SETTINGS.agent_llm.model_temp,
        max_retries = SETTINGS.agent_llm.max_retry,
        max_tokens = SETTINGS.agent_llm.max_tokens

    )

    return llm



def get_ollama_agent():
    llm = ChatOllama(
        model = SETTINGS.agent_llm.model_name,
        temperature = SETTINGS.agent_llm.model_temp,
        max_retries = SETTINGS.agent_llm.max_retry,
        max_tokens = SETTINGS.agent_llm.max_tokens
    )

    return llm
    
