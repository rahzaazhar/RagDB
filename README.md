## Project Setup

### Project Dependencies

To run the project, you will need to install the following dependencies:

```bash
pip install -r requirements.txt
```

### Project Structure

The project is structured as follows:

- `data_generator.py`: Generates synthetic bookstore datasets using the Amazon Popular Books dataset as the base catalog.
- `populate_db.py`: Populates the DBs with the generated datasets.
- `Gemini_Books.json`: Contains the generated datasets in JSON format.

## Data Setup

### Data Generation
We use the Amazon Popular Books dataset as the base catalog and synthesize two distinct bookstore datasets by applying randomized schema variations (different column names, missing fields, additional attributes). To enrich the records, we generate concise book summaries using a generative model (e.g., Gemini), creating semantically richer data that better supports retrieval-augmented generation (RAG) and natural language querying.

To create your own bookstore datasets, run the following command:

```bash
python data_generator.py --bookstore_name salims --num_books 2 --csv_path ./Amazon_popular_books_dataset.csv
```

two books store datasets bookstore_one.csv and bookstore_two.csv are created in the data directory for the purpose of this demo.

## System Architecture 

The system enables natural language interaction with a database by combining query translation, SQL generation, and language model reasoning.

1. **User Query**
   The process begins with a natural language query from the user (e.g., *“Show me the books published by 'Amazon' that have a rating of 4.8 or higher.”*).

2. **Query Translation**
   The system uses an LLM to interprets the user’s intent by identifying entities and conditions to ensure the query is semantically understood and remove any ambiguities.

3. **Query Construction**
   The system uses an LLM by givig it a persosna of an expert sql operator via instructions to convert the interpreted intent into an executable SQL query, For example, it might generate a `SELECT` statement that groups books by genre. Additionally the LLM is also given the schema of the database to ensure the query is valid. In our case since we are really with only two tables dumping the schema in the context of the LLM is okay. In cases where the schema is large we have to store the schema in a vector store and let the model dynamically select the schema based on user query. 

4. **SQL Executor**
   The generated SQL query is executed against the database and ensures safe execution. The executor fetches structured results, such as tables or numerical values.

5. **Generation**
   Since raw SQL results are not user-friendly, the LLM reformulates the results into natural language. Here a different persona based on the end user experince is given to the LLM to generate a more user-friendly response. In this case the persona is a helpful assistant that answers users inquiries about the books available in a book store front. 

6. **Answer**
   The final answer is presented to the user in a clear, natural language form.


<p align="center">
  <img src="images/system_design_small.png" alt="Alt text" width="600">
</p>

## Evaluation

### Eval Data
To evaluate the RAG system a set of question and answer pairs were sythtically created using the geimini cli and manually verified for correctness the purpose of this eexercise is to faithfully have coverage over the types of questions that can be asked of the system. The type of questions covered are classified into the following types:
1. single-hop: are simple retrival look up type questions that can be answered by looking up a single fact in the database.
2. multi-hop: Can the system combine multiple facts across docs/rows/tables?
3. faithfulnesss: questions that require the system to provide a faithful answer to the question and not hallucinated info.
4. aggregation: questions that require the system to provide an aggregated answer to the question(Counting, Group By, etc).

For each type 5 question answer pairs were created and the system was evaluated on them.
the following prompt was used to generate the eval set: the eval data can be found in data/eval_data.jsonl
```
 I am building a rag system for a book store front, this front has 2 book stores each book store has a collection of books and their own schema. @data/bookstore_one.csv and @data/bookstore_two.csv contain the data and schema for each book store. I want you to generate question, answer pairs for four types of questions grounded in the data. 1. single-hop:are simple retrival look up type questions that can be answered by looking up a single fact in the database. 2. multi-hop: Can the system combine multiple facts across docs/rows/tables? 3.questions that require the system to provide a faithful answer to the question and not hallucinated info. 4. aggregation: questions that require the system to provide an aggregated answer to the question(Counting, Group By, etc). For each type of question generate 5 question answer pairs also include the type of question. Give me the data in jsonl format. an example of how the data could look like is this {"question":"eragon book available in your store front?", "answer":"No we donot have eragon in any of our collections", "type":"faithfulness"}
```
### Evaluators
There are many ways to evaluate the effectiveness of a llm system depending on the task(chat, RAG etc) at hand, if the output is verifiable or not (i.e we have a ground truth or not) and if the review is manual(human review) or automatic(unit tests and llm as a judge). In our case of RAG over a database we have reference answers grounded in the database and we use the llm as a judge to evaluate system responses with the reference output. We mainly focus on two aspect to evaluate:
1. Correctness:  Measure "how similar/correct is the RAG chain answer, relative to a ground-truth answer"
2. Relevance: Measures "how relevant is the RAG chain answer, relative to the question"

The prompts for correctness and relevance are found in evaluation_prompts.py. To run system evaluation on our eval data run the following command:

```python
python evaluation.py
```

Note: we are using gemini-2.5-flash in all our evaluations as it has the best rate limits for the free tier, if you want to use another model you can change the model in evaluation.py. Also the project only supports google models but can be easily extended to support other models. 
### Demo

tasks
1. write and test eval script, update readme [HP] [1 hour]
2. fill in system design section [HP] [30 minutes]
3. dockerize the system and test it [LP] [1 hour]
4. record demo video [LP] [30 minutes]
5. improve the system via code + prompt engineering [MP] [2 hours] 

