import sqlite3
import pandas as pd
from typing import List, Dict, Any
import json
from datetime import datetime

class MedicalProductDatabase:
    def __init__(self, db_path: str = "medical_products.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize comprehensive medical products database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced medical products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medical_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                brand_name TEXT,
                generic_name TEXT,
                description TEXT,
                indications TEXT,
                contraindications TEXT,
                dosage_forms TEXT,
                strength TEXT,
                dosage_adult TEXT,
                dosage_pediatric TEXT,
                side_effects TEXT,
                drug_interactions TEXT,
                warnings TEXT,
                manufacturer TEXT,
                ndc_number TEXT,
                price REAL,
                insurance_coverage TEXT,
                availability TEXT,
                prescription_required BOOLEAN DEFAULT 1,
                controlled_substance BOOLEAN DEFAULT 0,
                fda_approval_date TEXT,
                expiry_date TEXT,
                storage_conditions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Voice interactions log for real-time sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_speech_text TEXT,
                agent_response_text TEXT,
                products_discussed TEXT,
                interaction_type TEXT,
                response_time_ms INTEGER,
                satisfaction_score INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Real-time agent performance metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS realtime_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                latency_ms INTEGER,
                audio_quality_score REAL,
                transcription_accuracy REAL,
                agent_response_relevance REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def search_products_advanced(self, query: str, filters: Dict = None) -> List[Dict]:
        """Advanced product search with filtering"""
        conn = sqlite3.connect(self.db_path)
        
        base_query = '''
            SELECT * FROM medical_products 
            WHERE (name LIKE ? OR generic_name LIKE ? OR brand_name LIKE ? 
                   OR indications LIKE ? OR description LIKE ?)
        '''
        
        params = [f'%{query}%'] * 5
        
        # Add filters
        if filters:
            if filters.get('category'):
                base_query += ' AND category = ?'
                params.append(filters['category'])
            if filters.get('prescription_required') is not None:
                base_query += ' AND prescription_required = ?'
                params.append(filters['prescription_required'])
            if filters.get('price_range'):
                min_price, max_price = filters['price_range']
                base_query += ' AND price BETWEEN ? AND ?'
                params.extend([min_price, max_price])
        
        base_query += ' ORDER BY name LIMIT 20'
        
        df = pd.read_sql_query(base_query, conn, params=params)
        conn.close()
        
        return df.to_dict('records')
    
    def log_voice_interaction(self, session_id: str, user_speech: str, 
                            agent_response: str, products: str, 
                            response_time: int = 0):
        """Log voice interaction for analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO voice_interactions 
            (session_id, user_speech_text, agent_response_text, products_discussed, 
             interaction_type, response_time_ms)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, user_speech, agent_response, products, 'voice', response_time))
        
        conn.commit()
        conn.close()
    
    def add_sample_medical_data(self):
        """Add comprehensive sample medical product data"""
        sample_products = [
            {
                'name': 'Acetaminophen 500mg',
                'category': 'Pain Relief',
                'brand_name': 'Tylenol',
                'generic_name': 'Acetaminophen',
                'description': 'Over-the-counter pain reliever and fever reducer',
                'indications': 'Headache, muscle aches, arthritis, backache, toothache, cold, flu, fever',
                'contraindications': 'Severe liver disease, alcohol dependence',
                'dosage_forms': 'Tablets, capsules, liquid, chewable tablets',
                'strength': '500mg',
                'dosage_adult': '500-1000mg every 4-6 hours, maximum 4000mg daily',
                'dosage_pediatric': '10-15mg/kg every 4-6 hours',
                'side_effects': 'Rare: nausea, stomach upset, allergic reactions',
                'drug_interactions': 'Warfarin, isoniazid, phenytoin, carbamazepine',
                'warnings': 'Do not exceed recommended dose, avoid alcohol',
                'manufacturer': 'Johnson & Johnson',
                'ndc_number': '50580-488-01',
                'price': 8.99,
                'insurance_coverage': 'Most insurance plans',
                'availability': 'In Stock',
                'prescription_required': False,
                'controlled_substance': False,
                'fda_approval_date': '1955-01-01',
                'storage_conditions': 'Store at room temperature, protect from moisture'
            },
            {
                'name': 'Ibuprofen 400mg',
                'category': 'Pain Relief',
                'brand_name': 'Advil',
                'generic_name': 'Ibuprofen',
                'description': 'Nonsteroidal anti-inflammatory drug (NSAID)',
                'indications': 'Pain, inflammation, fever, menstrual cramps, arthritis',
                'contraindications': 'Peptic ulcer disease, severe heart failure, severe kidney disease',
                'dosage_forms': 'Tablets, capsules, liquid gel, suspension',
                'strength': '400mg',
                'dosage_adult': '400-600mg every 6-8 hours with food, maximum 2400mg daily',
                'dosage_pediatric': '5-10mg/kg every 6-8 hours',
                'side_effects': 'Stomach upset, heartburn, dizziness, increased bleeding risk',
                'drug_interactions': 'Aspirin, warfarin, ACE inhibitors, diuretics',
                'warnings': 'Take with food, avoid if allergic to aspirin',
                'manufacturer': 'Pfizer',
                'ndc_number': '0573-0164-40',
                'price': 12.49,
                'insurance_coverage': 'Most insurance plans',
                'availability': 'In Stock',
                'prescription_required': False,
                'controlled_substance': False,
                'fda_approval_date': '1961-01-01',
                'storage_conditions': 'Store at room temperature, protect from light'
            },
            {
                'name': 'Lisinopril 10mg',
                'category': 'Blood Pressure',
                'brand_name': 'Prinivil',
                'generic_name': 'Lisinopril',
                'description': 'ACE inhibitor for high blood pressure and heart failure',
                'indications': 'Hypertension, heart failure, post-myocardial infarction',
                'contraindications': 'Pregnancy, angioedema, bilateral renal artery stenosis',
                'dosage_forms': 'Tablets',
                'strength': '10mg',
                'dosage_adult': '10-40mg once daily, adjust based on blood pressure',
                'dosage_pediatric': 'Consult pediatric cardiologist',
                'side_effects': 'Dry cough, dizziness, hyperkalemia, angioedema',
                'drug_interactions': 'NSAIDs, potassium supplements, diuretics',
                'warnings': 'Monitor kidney function, avoid pregnancy',
                'manufacturer': 'Merck & Co',
                'ndc_number': '0006-0207-31',
                'price': 15.99,
                'insurance_coverage': 'Covered by most insurance',
                'availability': 'In Stock',
                'prescription_required': True,
                'controlled_substance': False,
                'fda_approval_date': '1987-12-29',
                'storage_conditions': 'Store at room temperature, protect from moisture'
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for product in sample_products:
            cursor.execute('''
                INSERT INTO medical_products 
                (name, category, brand_name, generic_name, description, indications, 
                 contraindications, dosage_forms, strength, dosage_adult, dosage_pediatric,
                 side_effects, drug_interactions, warnings, manufacturer, ndc_number,
                 price, insurance_coverage, availability, prescription_required, 
                 controlled_substance, fda_approval_date, storage_conditions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product['name'], product['category'], product['brand_name'],
                product['generic_name'], product['description'], product['indications'],
                product['contraindications'], product['dosage_forms'], product['strength'],
                product['dosage_adult'], product['dosage_pediatric'], product['side_effects'],
                product['drug_interactions'], product['warnings'], product['manufacturer'],
                product['ndc_number'], product['price'], product['insurance_coverage'],
                product['availability'], product['prescription_required'],
                product['controlled_substance'], product['fda_approval_date'],
                product['storage_conditions']
            ))
        
        conn.commit()
        conn.close() 