# tests/test_clex_importer_live.py

import pytest
import mysql.connector
import sys
import os

# Ensure the app directory is in the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.clex_importer import ClexImporter  # Import the service layer
from app.mysql_repository import MySQLRepository  # Import the MySQL repository

# Database connection configuration
connection_params = {
    'user': 'your_username',
    'password': 'your_password',
    'host': 'localhost',
    'database': 'stixd_corpus'
}

def get_lexicon_entry(lex_id):
    """Fetches a lexicon entry from the database by lex_id."""
    conn = mysql.connector.connect(**connection_params)
    cursor = conn.cursor()
    query = "SELECT lex_id, word_tag, word_form, logical_symbol, third_arg, tag_form_hash FROM lexicon WHERE lex_id = %s"
    cursor.execute(query, (lex_id,))
    result = cursor.fetchone()
    conn.close()
    return result

@pytest.fixture
def db_repo():
    """Fixture for database repository, setup and teardown."""
    # Setup database connection or repository instance
    repo = MySQLRepository(connection_params)
    yield repo
    # Teardown code here, if needed

@pytest.mark.parametrize("lex_id, word_tag, word_form, logical_symbol, third_arg, tag_form_hash", [
    (1, 'adv', 'fast', 'fast', None, '67e9b1c5cbd53045919deda792be49b18b41a09b3bd328f9cc406bb27d951f62'),
    (19, 'noun_pl', 'months', 'month', 'neutr', '6e7ab17fe3f242d10f360197f40646b443db6079d730e9d746c96824a2606336'),
    (39, 'iv_finsg', 'walks', 'walk', None, 'f02be7a15dcd7cca79dc9b1c141991d479120352658c50030c7268da9372e6ff'),
    (58, 'dv_pp', 'succeeded', 'succeed', 'as', '8ee745975fad537905042b710e2f602f6c6bbe6c72f123b3596ce0b962f2b23f')
])
def test_import_clex_entries(db_repo, lex_id, word_tag, word_form, logical_symbol, third_arg, tag_form_hash):
    """Tests the ClexImporter service layer function by importing and validating lexicon entries."""
    # Setup: Create an instance of the service layer
    importer = ClexImporter(db_repo)

    # Provide test input data
    test_input = {
        'lex_id': lex_id,
        'word_tag': word_tag,
        'word_form': word_form,
        'logical_symbol': logical_symbol,
        'third_arg': third_arg,
        'tag_form_hash': tag_form_hash
    }

    # Call the function with test input
    return_value = importer.import_clex_entries("http://example.com/test_clex.pl")  # Assuming this method takes a URI

    # Assertions
    assert return_value == "Import successful", f"Unexpected return value: {return_value}"

    # Validate the database change
    entry = get_lexicon_entry(lex_id)
    assert entry is not None, f"Entry with lex_id {lex_id} not found"

    db_lex_id, db_word_tag, db_word_form, db_logical_symbol, db_third_arg, db_tag_form_hash = entry

    assert db_lex_id == lex_id
    assert db_word_tag == word_tag
    assert db_word_form == word_form
    assert db_logical_symbol == logical_symbol

    # Adjusted comparison for third_arg
    if third_arg is None:
        assert db_third_arg is None or db_third_arg == 'NULL'
    else:
        assert db_third_arg == third_arg

    assert db_tag_form_hash == tag_form_hash