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
## System Design
### ML System Design
### Overall System Design
## Evaluation

### Eval Data
To evaluate the RAG system a set of question and answer pairs were sythtically created using the geimini cli and manually verified for correctness. The type of questions covered are classified into the following types:
single-hop: are simple retrival look up type questions that can be answered by looking up a single fact in the database.
multi-hop: Can the system combine multiple facts across docs/rows/tables?
faithfulnesss: questions that require the system to provide a faithful answer to the question and not hallucinated info.
aggregation: questions that require the system to provide an aggregated answer to the question(Counting, Group By, etc).

For each type 5 question answer pairs were created and the system was evaluated on them.
the following prompt was used to generate the eval set: the eval data can be found in data/eval_data.jsonl
```
 I am building a rag system for a book store front, this front has 2 book stores each book store has a collection of books and their own schema. @data/bookstore_one.csv and @data/bookstore_two.csv contain the data and schema for each book store. I want you to generate question, answer pairs for four types of questions grounded in the data. 1. single-hop:are simple retrival look up type questions that can be answered by looking up a single fact in the database. 2. multi-hop: Can the system combine multiple facts across docs/rows/tables? 3.questions that require the system to provide a faithful answer to the question and not hallucinated info. 4. aggregation: questions that require the system to provide an aggregated answer to the question(Counting, Group By, etc). For each type of question generate 5 question answer pairs also include the type of question. Give me the data in jsonl format. an example of how the data could look like is this {"question":"eragon book available in your store front?", "answer":"No we donot have eragon in any of our collections", "type":"faithfulness"}
```
### Evaluation
### Demo

tasks
1. write and test eval script, update readme [HP] [1 hour]
2. fill in system design section [HP] [30 minutes]
3. dockerize the system and test it [LP] [1 hour]
4. record demo video [LP] [30 minutes]
5. improve the system via code + prompt engineering [MP] [2 hours] 

