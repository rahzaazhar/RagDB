import os
from dotenv import load_dotenv
import json
from langsmith import Client
from simple_rag import RAGSystem
from langchain.chat_models import init_chat_model
from typing_extensions import Annotated, TypedDict
from evaluation_prompts import correctness_instructions, relevance_instructions

load_dotenv()

eval_data_path = "data/eval_data.jsonl"
dataset_name = "bookstore_eval"
model = "gemini-2.5-flash"
DB_URI = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@localhost:5432/{os.getenv('DB_NAME')}"


client = Client()
llm_as_judge = init_chat_model(model, model_provider='google_genai')
rag_system = RAGSystem(DB_URI, model)


#schemas for structured output
class CorrectnessGrade(TypedDict):
    explanation: Annotated[str, ..., "Explain your reasoning for the score"]
    correct: Annotated[bool, ..., "True if the answer is correct, False otherwise."]

class RelevanceGrade(TypedDict):
    explanation: Annotated[str, ..., "Explain your reasoning for the score"]
    relevant: Annotated[bool, ..., "Provide the score on whether the answer addresses the question"]


def correctness(inputs: dict, outputs: dict, reference_outputs: dict) -> bool:
    """An evaluator for RAG answer accuracy"""
    answers = f"""\
    QUESTION: {inputs['question']}
    GROUND TRUTH ANSWER: {reference_outputs['answer']}
    STUDENT ANSWER: {outputs['answer']}"""

    grader_llm = llm_as_judge.with_structured_output(CorrectnessGrade, method="json_schema", strict=True)
    # Run evaluator
    grade = grader_llm.invoke([
        {"role": "system", "content": correctness_instructions}, 
        {"role": "user", "content": answers}
    ])
    return grade["correct"]

def relevance(inputs: dict, outputs: dict) -> bool:
    """An evaluator for RAG answer relevance"""
    answers = f"""\
    QUESTION: {inputs['question']}
    STUDENT ANSWER: {outputs['answer']}"""

    grader_llm = llm_as_judge.with_structured_output(RelevanceGrade, method="json_schema", strict=True)
    # Run evaluator
    grade = grader_llm.invoke([
        {"role": "system", "content": relevance_instructions}, 
        {"role": "user", "content": answers}
    ])
    return grade["relevant"]

def read_jsonl(file_path):
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():  # avoid empty lines
                data.append(json.loads(line))
    return data

def setup_eval_data():
    eval_data = read_jsonl(eval_data_path)
    result = {k: [d[k] for d in eval_data] for k in eval_data[0].keys()}
    datasets = list(client.list_datasets(dataset_name=dataset_name))
    if datasets:
        print("Dataset already exists")
    else:
        dataset = client.create_dataset(dataset_name=dataset_name)
        client.create_examples(inputs= [{'question': q} for q in result['question']],
                        outputs= [{"answer": a} for a in result['answer']],
                        dataset_id=dataset.id)

def target(inputs: dict) -> dict:
    return {"answer": rag_system.run(inputs["question"])}
    
def eval():
    setup_eval_data()
    experiment_results = client.evaluate(
    target,
    data=dataset_name,
    evaluators=[correctness, relevance],
    experiment_prefix="rag-doc-relevance",
    metadata={"version": "LCEL context, gemini-2.5-flash"},
    )
    experiment_results = experiment_results.to_pandas()
    experiment_results.to_csv("eval_results.csv")
    
if __name__ == "__main__":
    eval()
