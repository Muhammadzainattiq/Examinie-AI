from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI

from app.utils.llm import get_chat_openai_client

def generate_profile_summary(profile_dict: str) -> str:
    """Generates a personalized summary based on the provided profile dictionary."""
    # Define the prompt template
    prompt_template = (
        "Summarize the student's profile details into a concise, personalized paragraph, highlighting key strengths, interests, and any exam-related focus areas. "
        "Only use the information provided in the following profile data: {profile_dict}."
    )
    
    # Create the prompt with the template
    prompt = PromptTemplate(
        input_variables=["profile_dict"], template=prompt_template
    )
    
    # Initialize the OpenAI model
    llm = get_chat_openai_client()
    
    # Define the chain
    chain = prompt | llm | StrOutputParser()
    
    # Invoke the chain with the profile data
    result = chain.invoke(profile_dict)
    
    return result


