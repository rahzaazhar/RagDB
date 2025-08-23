import csv
import random
import argparse
import dotenv
import time
from google import genai

dotenv.load_dotenv()

# --- Configuration: Canonical Fields and Their Aliases ---
CANONICAL_TO_ALIASES = {
    "title": ["title", "book_title", "name", "bookName"],
    "author": ["author", "writer", "author_name"],
    "price": ["price", "cost", "retail_price"],
    "rating": ["rating", "stars", "review_score", "avg_rating"],
    "publisher": ["publisher", "published_by", "imprint"],
    "summary": ["summary", "description", "overview", "plot_summary"],
    "genre": ["genre", "category", "subject"],
    "stock": ["stock", "availability"]
}

CSV_MAPPINGS = {
    "title": "title",
    "author": "brand",
    "price": "final_price",
    "rating": "rating",
    "publisher": "seller_name",
    "genre": "categories",
    "stock": "availability"
}

LLM_GENERATED_FIELDS = {"summary"}

# --- Gemini API Integration ---
def get_gemini_summary(title, author):
    """
    Calls the Gemini API to generate a book summary.
    """
    try:
        # The client gets the API key from the environment variable `GEMINI_API_KEY`.
        client = genai.Client()
        prompt = f"Provide a concise, one-sentence summary for the book '{title}' by {author}."
        response = client.models.generate_content(model="gemini-2.5-flash-lite", contents=prompt)
        return response.text.strip().replace('\n', ' ')
    except Exception as e:
        print(f"\nWarning: Could not generate summary for '{title}'. Error: {e}")
        return "[Summary not available]"

# --- Core Logic ---
def load_seed_data(csv_path):
    """Loads book data from the source CSV file."""
    with open(csv_path, mode='r', encoding='utf-8') as infile:
        return list(csv.DictReader(infile))

def generate_schema():
    """
    Generates a dynamic, heterogeneous schema.
    """
    schema = {}
    fields_to_include = {"title", "author", "price"}
    optional_fields = list((set(CSV_MAPPINGS.keys()) | LLM_GENERATED_FIELDS) - fields_to_include)
    num_optional_to_add = random.randint(1, len(optional_fields))
    for _ in range(num_optional_to_add):
        fields_to_include.add(optional_fields.pop(random.randrange(len(optional_fields))))
    for canonical_name in fields_to_include:
        schema[canonical_name] = random.choice(CANONICAL_TO_ALIASES[canonical_name])
    return schema

def generate_bookstore_data(bookstore_name, num_books, seed_data):
    """
    Generates the full, enriched dataset and saves it as a CSV file.
    """
    print(f"Generating data for '{bookstore_name}'...")
    schema = generate_schema()
    print(f"Generated schema: {list(schema.values())}")

    if len(seed_data) < num_books:
        print(f"Warning: Requested {num_books} books, but only {len(seed_data)} available.")
        num_books = len(seed_data)

    sampled_books = random.sample(seed_data, num_books)
    output_data = []

    for i, book_row in enumerate(sampled_books):
        print(f"Processing book {i + 1}/{num_books}...", end='\r')
        if i % 10 == 0:
            time.sleep(60)
        new_book_record = {}
        for canonical_name, alias_name in schema.items():
            if canonical_name in CSV_MAPPINGS:
                if canonical_name == 'rating':
                    rating = book_row.get(CSV_MAPPINGS[canonical_name], "")
                    new_book_record[alias_name] = float(rating.split(" ")[0])
                    continue
                new_book_record[alias_name] = book_row.get(CSV_MAPPINGS[canonical_name], "")
            elif canonical_name in LLM_GENERATED_FIELDS:
                if canonical_name == 'summary':
                    title = book_row.get(CSV_MAPPINGS["title"], "Unknown Title")
                    author = book_row.get(CSV_MAPPINGS["author"], "Unknown Author")
                    new_book_record[alias_name] = get_gemini_summary(title, author)
        output_data.append(new_book_record)

    output_filename = f"{bookstore_name.replace(' ', '_')}.csv"
    try:
        with open(output_filename, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=list(schema.values()))
            writer.writeheader()
            writer.writerows(output_data)
        print(f"\nSuccessfully generated {num_books} records.")
        print(f"Data saved to '{output_filename}'")
    except IOError as e:
        print(f"\nError writing to file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic bookstore data using the Gemini API.")
    parser.add_argument("--bookstore_name", type=str, help="The name of the bookstore.")
    parser.add_argument("--num_books", type=int, help="The number of books to generate.")
    parser.add_argument("--csv_path", type=str, default="Amazon_popular_books_dataset.csv", help="Path to the seed CSV file.")
    parser.add_argument("--output_path", type=str, default="data/", help="Path to the output directory.")
    args = parser.parse_args()


    try:
        seed_data = load_seed_data(args.csv_path)
        generate_bookstore_data(args.bookstore_name, args.num_books, seed_data)
    except FileNotFoundError:
        print(f"Error: The file '{args.csv_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()