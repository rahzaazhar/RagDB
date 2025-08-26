#!/bin/sh

# Run the database population script
echo "Populating database..."
python populate_db.py
echo "Database population complete."

# Execute the command passed to this script
exec "$@"
