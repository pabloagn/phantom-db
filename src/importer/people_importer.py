#!/usr/bin/env python3
"""
People importer module for the phantom project.
Handles importing people data from CSV files to the PostgreSQL database.
"""
import os
import pandas as pd
import psycopg2
from typing import Dict, List, Tuple, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PeopleImporter:
    """Importer for people data."""
    
    def __init__(self, db_params: Dict[str, Any]):
        """Initialize the importer with database parameters."""
        self.db_params = db_params
    
    def check_duplicates(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Check for potential duplicates based on complete name fields.
        Returns a list of duplicate entries.
        """
        duplicates = []
        
        # Connect to database
        conn = psycopg2.connect(**self.db_params)
        cursor = conn.cursor()
        
        try:
            for _, row in df.iterrows():
                name_surname = f"{row['Name']}, {row['Surname']}" if pd.notna(row['Surname']) else f"{row['Name']}, "
                surname_name = f"{row['Surname']}, {row['Name']}" if pd.notna(row['Surname']) else f", {row['Name']}"
                
                cursor.execute(
                    """
                    SELECT id, name, surname FROM people 
                    WHERE complete_name_ns = %s OR complete_name_sn = %s
                    """,
                    (name_surname, surname_name)
                )
                
                matches = cursor.fetchall()
                if matches:
                    for match in matches:
                        duplicates.append({
                            'existing_id': match[0],
                            'existing_name': match[1],
                            'existing_surname': match[2],
                            'new_name': row['Name'],
                            'new_surname': row['Surname'] if pd.notna(row['Surname']) else None
                        })
        finally:
            cursor.close()
            conn.close()
            
        return duplicates
    
    def import_people(self, csv_path: str, check_only: bool = False) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Import people data from CSV file.
        
        Args:
            csv_path: Path to the CSV file
            check_only: If True, only check for duplicates without importing
            
        Returns:
            Tuple of (number of imported records, list of duplicates)
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found at {csv_path}")
        
        # Read CSV file with explicit UTF-8 encoding
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        # Check for duplicates
        duplicates = self.check_duplicates(df)
        
        if check_only or duplicates:
            return 0, duplicates
        
        # Connect to database
        conn = psycopg2.connect(**self.db_params)
        cursor = conn.cursor()
        
        imported_count = 0
        
        try:
            # Process each person
            for _, row in df.iterrows():
                # Insert person basic info
                cursor.execute(
                    """
                    INSERT INTO people (name, surname, real_name, gender, has_image) 
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        row['Name'], 
                        row['Surname'] if pd.notna(row['Surname']) else None,
                        row['Real Name'] if pd.notna(row['Real Name']) else None,
                        row['Gender'] if pd.notna(row['Gender']) else None,
                        True if pd.notna(row['Have Image [Y/N]']) and row['Have Image [Y/N]'] == 'Y' else False
                    )
                )
                
                person_id = cursor.fetchone()[0]
                imported_count += 1
                
                # Process types (comma separated)
                if pd.notna(row['Type']):
                    types = [t.strip() for t in row['Type'].split(',')]
                    for type_name in types:
                        # Insert type if not exists
                        cursor.execute(
                            """
                            INSERT INTO ref.person_types (name) 
                            VALUES (%s) 
                            ON CONFLICT (name) DO NOTHING
                            """,
                            (type_name,)
                        )
                        
                        # Get type id
                        cursor.execute(
                            "SELECT id FROM ref.person_types WHERE name = %s",
                            (type_name,)
                        )
                        type_id = cursor.fetchone()[0]
                        
                        # Link person to type
                        cursor.execute(
                            """
                            INSERT INTO person_types_junction (person_id, type_id)
                            VALUES (%s, %s)
                            ON CONFLICT DO NOTHING
                            """,
                            (person_id, type_id)
                        )
                
                # Process nationalities (comma separated)
                if pd.notna(row['Nationality']):
                    nationalities = [n.strip() for n in row['Nationality'].split(',')]
                    for nationality in nationalities:
                        # Insert nationality if not exists
                        cursor.execute(
                            """
                            INSERT INTO ref.nationalities (name) 
                            VALUES (%s) 
                            ON CONFLICT (name) DO NOTHING
                            """,
                            (nationality,)
                        )
                        
                        # Get nationality id
                        cursor.execute(
                            "SELECT id FROM ref.nationalities WHERE name = %s",
                            (nationality,)
                        )
                        nationality_id = cursor.fetchone()[0]
                        
                        # Link person to nationality
                        cursor.execute(
                            """
                            INSERT INTO person_nationalities_junction (person_id, nationality_id)
                            VALUES (%s, %s)
                            ON CONFLICT DO NOTHING
                            """,
                            (person_id, nationality_id)
                        )
            
            # Commit the transaction
            conn.commit()
            logger.info(f"Successfully imported {imported_count} people records")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error importing people: {str(e)}")
            raise
            
        finally:
            cursor.close()
            conn.close()
            
        return imported_count, duplicates