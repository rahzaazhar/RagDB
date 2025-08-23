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

To run the data generator, run the following command:

```bash
python data_generator.py --bookstore_name salims --num_books 2 --csv_path ./Amazon_popular_books_dataset.csv
```

### Data Ingestion

To populate the DBs, run the following command:

```bash
python populate_db.py --bookstore_name salims --num_books 2 --csv_path ./Amazon_popular_books_dataset.csv
