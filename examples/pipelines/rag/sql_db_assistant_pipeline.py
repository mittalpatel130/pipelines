from typing import List, Union, Generator, Iterator
from pydantic import BaseModel
import os
import urllib.parse
import requests  # ✅ FIXED: Import requests for API calls
from langchain.agents import create_sql_agent, AgentType
from langchain.sql_database import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import AzureOpenAI
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from sqlalchemy import create_engine


class Pipeline:
    """Text-to-SQL Pipeline for Open Web UI using Azure OpenAI + PostgreSQL"""

    class Valves(BaseModel):
        """Stores all required environment variables for PostgreSQL."""
        AZURE_OPENAI_API_KEY: str
        AZURE_OPENAI_ENDPOINT: str
        AZURE_OPENAI_API_VERSION: str
        AZURE_OPENAI_MODEL: str
        SQL_SERVER: str
        SQL_DATABASE: str
        SQL_USERNAME: str
        SQL_PASSWORD: str
        SQL_DRIVER: str

    def __init__(self):
        """Initialize the pipeline by setting up PostgreSQL and OpenAI."""
        self.type = "manifold"
        self.name = "Azure OpenAI Text-to-SQL Pipeline"

        # ✅ Load environment variables
        self.valves = self.Valves(
            **{
                "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY", "your-azure-openai-api-key"),
                "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT", "your-azure-openai-endpoint"),
                "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
                "AZURE_OPENAI_MODEL": os.getenv("AZURE_OPENAI_MODEL", "gpt-4"),
                "SQL_SERVER": os.getenv("SQL_SERVER", "localhost"),  # Use PostgreSQL host
                "SQL_DATABASE": os.getenv("SQL_DATABASE", "testdb"),
                "SQL_USERNAME": os.getenv("SQL_USERNAME", "testuser"),
                "SQL_PASSWORD": os.getenv("SQL_PASSWORD", "testpassword"),
                "SQL_DRIVER": os.getenv("SQL_DRIVER", "PostgreSQL Driver"),  # Dummy value for UI
            }
        )

        # ✅ Register the pipeline for Open Web UI
        self.set_pipelines()

    def set_pipelines(self):
        """Register the pipeline in Open Web UI."""
        self.pipelines = [
            {"id": "azure-text-to-sql", "name": "Azure OpenAI Text-to-SQL"}
        ]
        
        # ✅ Add environment variables as parameters to Open Web UI
        self.parameters = [
            {"name": "AZURE_OPENAI_API_KEY", "type": "string", "secret": True},
            {"name": "AZURE_OPENAI_ENDPOINT", "type": "string"},
            {"name": "AZURE_OPENAI_API_VERSION", "type": "string"},
            {"name": "AZURE_OPENAI_MODEL", "type": "string"},
            {"name": "SQL_SERVER", "type": "string"},
            {"name": "SQL_DATABASE", "type": "string"},
            {"name": "SQL_USERNAME", "type": "string"},
            {"name": "SQL_PASSWORD", "type": "string", "secret": True},
            {"name": "SQL_DRIVER", "type": "string"}
        ]
        
        print(f"✅ DEBUG: Pipeline registered in Open Web UI: {self.pipelines}")

    async def on_valves_updated(self):
        """Ensure Open Web UI updates the available models when valves are changed."""
        print("🔄 DEBUG: Valves updated, re-registering pipelines in Open Web UI...")
        self.set_pipelines()

    async def on_startup(self):
        """Called when Open Web UI starts."""
        print(f"🚀 on_startup: {__name__}")

    async def on_shutdown(self):
        """Called when Open Web UI shuts down."""
        print(f"🛑 on_shutdown: {__name__}")

    def pipe(self, user_message: str, model_id: str, messages: List[dict], body: dict) -> Union[str, Generator, Iterator]:
        """Process a natural language query and convert it to SQL using Open Web UI."""
        print(f"pipe:{__name__}")
        print(messages)
        print(user_message)

        headers = {
            "api-key": self.valves.AZURE_OPENAI_API_KEY,
            "Content-Type": "application/json",
        }

        # ✅ Generate SQL query from natural language prompt
        url = f"{self.valves.AZURE_OPENAI_ENDPOINT}/openai/deployments/{self.valves.AZURE_OPENAI_MODEL}/chat/completions?api-version={self.valves.AZURE_OPENAI_API_VERSION}"
        prompt = (
            "Convert the following user request into a syntactically correct SQL query for PostgreSQL. "
            "Make sure the query is safe and uses best practices. If filtering by a date, use YYYY-MM-DD format. "
            f"User Request: {user_message}"
        )
        payload = {
            "model": self.valves.AZURE_OPENAI_MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            r = requests.post(url=url, json=payload, headers=headers)  # ✅ FIXED: Added `requests`
            r.raise_for_status()
            sql_query = r.json()["choices"][0]["message"]["content"].strip()
            print(f"✅ Generated SQL Query: {sql_query}")
        except requests.exceptions.RequestException as e:
            return f"❌ API Request Failed: {e}"
        except KeyError:
            return f"❌ OpenAI API response missing expected fields"

        return sql_query


# ✅ Run the pipeline for Open Web UI
if __name__ == "__main__":
    pipeline = Pipeline()

    print("\n🔍 Running Test Query for Open Web UI...")
    test_body = {
        "messages": [{"content": "List all employees whose name starts with 'M'"}]
    }
    response = pipeline.pipe(
        user_message="List all employees whose name starts with 'M'",
        model_id="azure-text-to-sql",
        messages=test_body["messages"],
        body={}
    )

    print("\n🔹 Open Web UI Test Query Response:")
    print(response)
