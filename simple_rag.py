import os
from langchain_community.utilities import SQLDatabase
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph import START, StateGraph
from langchain_core.rate_limiters import InMemoryRateLimiter

rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.1,  # <-- Super slow! We can only make a request once every 10 seconds!!
    check_every_n_seconds=0.1,  # Wake up every 100 ms to check whether allowed to make a request,
    max_bucket_size=10,  # Controls the maximum burst size.
)

SYSTEM_MESSAGE = """
Given an input question, create a syntactically correct {dialect} query to
run to help find the answer. Unless the user specifies in his question a
specific number of examples they wish to obtain, always limit your query to
at most {top_k} results. You can order the results by a relevant column to
return the most interesting examples in the database.

Never query for all the columns from a specific table, only ask for a the
few relevant columns given the question. Always use quotes around column names.

Pay attention to use only the column names that you can see in the schema
description. Be careful to not query for columns that do not exist. Also,
pay attention to which column is in which table.

Only use the following tables:
{table_info}
"""

USER_PROMPT = "Question: {input}"

class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str

class QueryOutput(TypedDict):
    """Generated SQL query."""
    query: Annotated[str, ..., "Syntactically valid SQL query."]

class RAGSystem:
    def __init__(self, db_uri, model="gemini-2.5-flash"):
        self.db = SQLDatabase.from_uri(db_uri)
        self.llm = init_chat_model(model, model_provider='google_genai', rate_limiter=rate_limiter)
        self.query_prompt_template = self._create_query_prompt_template()
        self.graph = self._build_graph()

    def _create_query_prompt_template(self):
        
        return ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_MESSAGE),
                ("user", USER_PROMPT),
            ]
        )

    def _build_graph(self):
        graph_builder = StateGraph(State).add_sequence(
            [self.query_construction, self.query_execution, self.generate_answer]
        )
        graph_builder.add_edge(START, "query_construction")
        return graph_builder.compile()

    def query_construction(self, state: State):
        prompt = self.query_prompt_template.invoke(
            {
                "input": state["question"],
                "dialect": self.db.dialect,
                "top_k": 5,
                "table_info": self.db.table_info,
            }
        )
        structured_llm = self.llm.with_structured_output(QueryOutput)
        result = structured_llm.invoke(prompt)
        return {"query": result["query"]}

    def query_execution(self, state: State):
        """Execute SQL query."""
        execute_query_tool = QuerySQLDatabaseTool(db=self.db)
        return {"result": execute_query_tool.invoke(state["query"])}

    def generate_answer(self, state: State):
        """Answer question using retrieved information as context."""
        prompt = (
            "You are a helpful assistant that answers users inquiries about the books available in different bookstores."
            "Given the following user question, corresponding SQL query, database schema information"
            "and SQL result as context, answer the user question. if the information in the context is strictly"
            "not enough to answer the users question give the user a reason why the information is not enough to answer the users question."
            "The end user does not need to know about how the information was retrieved or how the query was generated. The user only needs to know the answer to his question or why it was not met.\n\n"
            f"Question: {state['question']}\n"
            f"SQL Query: {state['query']}\n"
            f"Database Schema Information: {self.db.table_info}\n"
            f"SQL Result: {state['result']}"
        )
        response = self.llm.invoke(prompt)
        return {"answer": response.content}

    def run(self, question: str):
        result = self.graph.invoke({"question": question})
        return result["answer"]
