"""
Migration script to move help documents from file-based storage to database.

This script:
1. Reads existing help docs from data/help_docs/ directory
2. Creates HelpDocument database entries
3. Archives the old files (doesn't delete them)

Usage:
    python migrations/migrate_help_docs_to_db.py
"""

import os
import sys
import json
import shutil
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database import db
from models.education import HelpDocument
from utils import parse_markdown


def get_help_docs_dir():
    """Get help documents directory"""
    base_dir = app.root_path
    help_dir = os.path.join(base_dir, 'data', 'help_docs')
    return help_dir


def load_old_help_index():
    """Load old help documents index.json"""
    help_dir = get_help_docs_dir()
    index_path = os.path.join(help_dir, 'index.json')

    if not os.path.exists(index_path):
        print(f"No index.json found at {index_path}")
        return []

    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"Error reading index.json: {e}")
        return []


def split_front_matter(md_content):
    """Strip YAML front matter if present"""
    if not md_content or not md_content.startswith('---'):
        return {}, md_content

    lines = md_content.splitlines()
    if len(lines) < 3:
        return {}, md_content

    end_index = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_index = i
            break

    if end_index is None:
        return {}, md_content

    meta_lines = lines[1:end_index]
    body_lines = lines[end_index + 1:]
    metadata = {}
    for line in meta_lines:
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()
    return metadata, '\n'.join(body_lines).lstrip()


def migrate_help_docs():
    """Migrate help documents from files to database"""
    print("=" * 60)
    print("Help Documents Migration: Files → Database")
    print("=" * 60)

    help_dir = get_help_docs_dir()

    # Check if directory exists
    if not os.path.exists(help_dir):
        print(f"\nNo help docs directory found at {help_dir}")
        print("Nothing to migrate.")
        return

    # Load old index
    old_documents = load_old_help_index()

    if not old_documents:
        print("\nNo help documents found in index.json")
        print("Nothing to migrate.")
        return

    print(f"\nFound {len(old_documents)} help documents to migrate")

    migrated_count = 0
    skipped_count = 0
    error_count = 0

    with app.app_context():
        for entry in old_documents:
            doc_filename = entry.get('filename')
            doc_title = entry.get('title', 'Untitled')
            doc_category = entry.get('category', 'General')

            print(f"\nProcessing: {doc_title} ({doc_filename})")

            # Check if file exists
            doc_path = os.path.join(help_dir, doc_filename)
            if not os.path.exists(doc_path):
                print(f"  ⚠ File not found: {doc_filename} - Skipping")
                skipped_count += 1
                continue

            try:
                # Read markdown file
                with open(doc_path, 'r', encoding='utf-8') as f:
                    markdown_source = f.read()

                # Strip front matter and convert to HTML
                meta, body = split_front_matter(markdown_source)
                html_content = parse_markdown(body)

                # Parse dates
                created_at = None
                updated_at = None

                if entry.get('created_at'):
                    try:
                        created_at = datetime.fromisoformat(entry['created_at'])
                    except:
                        created_at = datetime.utcnow()

                if entry.get('updated_at'):
                    try:
                        updated_at = datetime.fromisoformat(entry['updated_at'])
                    except:
                        updated_at = datetime.utcnow()

                # Create database entry
                help_doc = HelpDocument(
                    category=doc_category,
                    title=doc_title,
                    content=html_content,
                    markdown_source=body,
                    filename=doc_filename,
                    is_markdown=True,
                    order_index=entry.get('order_index', 0),
                    created_at=created_at or datetime.utcnow(),
                    updated_at=updated_at or datetime.utcnow()
                )

                db.session.add(help_doc)
                db.session.commit()

                print(f"  ✓ Migrated successfully (ID: {help_doc.id})")
                migrated_count += 1

            except Exception as e:
                db.session.rollback()
                print(f"  ✗ Error migrating: {e}")
                error_count += 1

    # Archive old files
    if migrated_count > 0:
        archive_dir = os.path.join(help_dir, '_archived_files')
        os.makedirs(archive_dir, exist_ok=True)

        print(f"\n{'=' * 60}")
        print("Archiving old files...")
        print(f"{'=' * 60}")

        try:
            # Move index.json to archive
            index_path = os.path.join(help_dir, 'index.json')
            if os.path.exists(index_path):
                archive_index_path = os.path.join(archive_dir, f'index.json.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
                shutil.move(index_path, archive_index_path)
                print(f"✓ Archived index.json → {archive_index_path}")

            # Move markdown files to archive
            for entry in old_documents:
                doc_filename = entry.get('filename')
                doc_path = os.path.join(help_dir, doc_filename)

                if os.path.exists(doc_path):
                    archive_doc_path = os.path.join(archive_dir, doc_filename)
                    shutil.move(doc_path, archive_doc_path)
                    print(f"✓ Archived {doc_filename}")

            print(f"\nOld files archived to: {archive_dir}")

        except Exception as e:
            print(f"\n⚠ Error archiving files: {e}")
            print("Old files left in place for manual review")

    # Print summary
    print(f"\n{'=' * 60}")
    print("Migration Summary")
    print(f"{'=' * 60}")
    print(f"✓ Successfully migrated: {migrated_count}")
    print(f"⚠ Skipped (file not found): {skipped_count}")
    print(f"✗ Errors: {error_count}")
    print(f"{'=' * 60}\n")

    if migrated_count > 0:
        print("✓ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Verify help documents in the app (/settings/help)")
        print("2. If everything looks good, you can delete the archived files")
        print(f"   Archive location: {archive_dir}")
    else:
        print("No documents were migrated.")


if __name__ == '__main__':
    migrate_help_docs()
