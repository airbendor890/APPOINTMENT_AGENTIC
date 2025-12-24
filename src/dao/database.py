import sqlite3
import psycopg2
import os

DB_CONFIG = {
                'host': 'coordinaite-db.c856ouoewepl.us-east-1.rds.amazonaws.com',
                'port': 5432,
                'database': 'coordinaite_db',
                'user': 'postgres',
                'password': 'JohnIsAGoodBadGuy'
            }

class Database:
    def __init__(self, db_config=DB_CONFIG):
        self.db_config = db_config
        # self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        
        conn = psycopg2.connect(**self.db_config)
        print("connection established succefully")
        return conn
    
    def init_database(self):
        """Initialize database with required tables"""
        # conn = sqlite3.connect(self.db_path)
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()
        
        # Create tables
        cursor.executescript('''
            
            -- Provider availability slots (matching your schema)
            CREATE TABLE IF NOT EXISTS availability_slots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_id INTEGER REFERENCES users(id),
                date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                status VARCHAR(20) DEFAULT 'available',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
  
            
            -- Main appointments (matching your schema)
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_id INTEGER REFERENCES appointment_types(id),
                seeker_id INTEGER REFERENCES users(id),
                provider_id INTEGER REFERENCES users(id),
                slot_id INTEGER REFERENCES availability_slots(id),
                scheduled_time TIMESTAMP NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
   
        ''')
        
        conn.commit()
        conn.close()
