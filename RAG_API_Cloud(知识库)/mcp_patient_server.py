#!/usr/bin/env python3
"""
MCP Server for Patient Database Access
Allows authorized agents to query patient data securely.
"""

import asyncio
import json
import sqlite3
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PatientDatabase:
    """Simple SQLite database for patient data"""
    
    def __init__(self, db_path: str = "patients.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the patient database with sample data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create patients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                diagnosis TEXT,
                treatment TEXT,
                admission_date TEXT,
                discharge_date TEXT,
                status TEXT DEFAULT 'active',
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create medical records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medical_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                record_type TEXT NOT NULL,
                description TEXT,
                date_recorded TEXT,
                doctor_name TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
            )
        """)
        
        # Insert sample data if tables are empty
        cursor.execute("SELECT COUNT(*) FROM patients")
        if cursor.fetchone()[0] == 0:
            sample_patients = [
                ('P001', 'John Smith', 45, 'Male', 'Hypertension', 'Medication therapy', '2024-01-15', None, 'active', 'Regular checkups needed'),
                ('P002', 'Mary Johnson', 32, 'Female', 'Diabetes Type 2', 'Insulin therapy', '2024-01-20', None, 'active', 'Diet monitoring required'),
                ('P003', 'Robert Brown', 67, 'Male', 'Heart Disease', 'Cardiac surgery', '2024-01-10', '2024-01-25', 'discharged', 'Recovery going well'),
                ('P004', 'Sarah Davis', 28, 'Female', 'Pregnancy', 'Prenatal care', '2024-02-01', None, 'active', 'First trimester'),
                ('P005', 'Michael Wilson', 55, 'Male', 'Cancer', 'Chemotherapy', '2024-01-05', None, 'active', 'Treatment ongoing')
            ]
            
            cursor.executemany("""
                INSERT INTO patients (patient_id, name, age, gender, diagnosis, treatment, admission_date, discharge_date, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_patients)
            
            # Sample medical records
            sample_records = [
                ('P001', 'Blood Pressure', 'BP: 140/90 mmHg', '2024-01-15', 'Dr. Anderson'),
                ('P001', 'Medication', 'Prescribed Lisinopril 10mg daily', '2024-01-15', 'Dr. Anderson'),
                ('P002', 'Blood Sugar', 'Fasting glucose: 180 mg/dL', '2024-01-20', 'Dr. Martinez'),
                ('P002', 'Diet Plan', 'Low carb diet recommended', '2024-01-20', 'Dr. Martinez'),
                ('P003', 'Surgery', 'Successful bypass surgery completed', '2024-01-12', 'Dr. Thompson'),
                ('P004', 'Ultrasound', 'Healthy fetal development observed', '2024-02-01', 'Dr. Lee'),
                ('P005', 'Chemotherapy', 'First cycle completed successfully', '2024-01-08', 'Dr. Garcia')
            ]
            
            cursor.executemany("""
                INSERT INTO medical_records (patient_id, record_type, description, date_recorded, doctor_name)
                VALUES (?, ?, ?, ?, ?)
            """, sample_records)
        
        conn.commit()
        conn.close()
        logger.info("Patient database initialized successfully")
    
    def get_patient_by_id(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Get patient information by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
        patient = cursor.fetchone()
        
        if patient:
            result = dict(patient)
            
            # Get medical records for this patient
            cursor.execute("""
                SELECT * FROM medical_records 
                WHERE patient_id = ? 
                ORDER BY date_recorded DESC
            """, (patient_id,))
            
            records = [dict(row) for row in cursor.fetchall()]
            result['medical_records'] = records
            
            conn.close()
            return result
        
        conn.close()
        return None
    
    def search_patients(self, query: str = None, status: str = None) -> List[Dict[str, Any]]:
        """Search patients by name, diagnosis, or status"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        sql = "SELECT * FROM patients WHERE 1=1"
        params = []
        
        if query:
            sql += " AND (name LIKE ? OR diagnosis LIKE ? OR treatment LIKE ?)"
            params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
        
        if status:
            sql += " AND status = ?"
            params.append(status)
        
        sql += " ORDER BY admission_date DESC"
        
        cursor.execute(sql, params)
        patients = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return patients
    
    def get_patient_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total patients
        cursor.execute("SELECT COUNT(*) FROM patients")
        total_patients = cursor.fetchone()[0]
        
        # Active patients
        cursor.execute("SELECT COUNT(*) FROM patients WHERE status = 'active'")
        active_patients = cursor.fetchone()[0]
        
        # Patients by gender
        cursor.execute("SELECT gender, COUNT(*) FROM patients GROUP BY gender")
        gender_stats = dict(cursor.fetchall())
        
        # Recent admissions (last 30 days)
        cursor.execute("""
            SELECT COUNT(*) FROM patients 
            WHERE admission_date >= date('now', '-30 days')
        """)
        recent_admissions = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_patients': total_patients,
            'active_patients': active_patients,
            'discharged_patients': total_patients - active_patients,
            'gender_distribution': gender_stats,
            'recent_admissions_30_days': recent_admissions
        }

# Initialize database
patient_db = PatientDatabase()

# Create MCP server
server = Server("patient-database-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools for patient database operations"""
    return [
        types.Tool(
            name="get_patient",
            description="Retrieve detailed patient information by patient ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "The unique patient ID (e.g., P001)"
                    }
                },
                "required": ["patient_id"]
            }
        ),
        types.Tool(
            name="search_patients",
            description="Search patients by name, diagnosis, treatment, or status",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term for name, diagnosis, or treatment"
                    },
                    "status": {
                        "type": "string",
                        "description": "Filter by patient status (active, discharged)",
                        "enum": ["active", "discharged"]
                    }
                }
            }
        ),
        types.Tool(
            name="get_statistics",
            description="Get patient database statistics and summary information",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls for patient database operations"""
    
    try:
        if name == "get_patient":
            patient_id = arguments.get("patient_id")
            if not patient_id:
                return [types.TextContent(
                    type="text",
                    text="Error: patient_id is required"
                )]
            
            patient = patient_db.get_patient_by_id(patient_id)
            if patient:
                return [types.TextContent(
                    type="text",
                    text=json.dumps(patient, indent=2, default=str)
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Patient with ID {patient_id} not found"
                )]
        
        elif name == "search_patients":
            query = arguments.get("query")
            status = arguments.get("status")
            
            patients = patient_db.search_patients(query=query, status=status)
            
            if patients:
                # Return summary for multiple patients
                summary = []
                for patient in patients:
                    summary.append({
                        'patient_id': patient['patient_id'],
                        'name': patient['name'],
                        'age': patient['age'],
                        'gender': patient['gender'],
                        'diagnosis': patient['diagnosis'],
                        'status': patient['status']
                    })
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps(summary, indent=2)
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text="No patients found matching the criteria"
                )]
        
        elif name == "get_statistics":
            stats = patient_db.get_patient_statistics()
            return [types.TextContent(
                type="text",
                text=json.dumps(stats, indent=2)
            )]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        logger.error(f"Error handling tool call {name}: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]

async def main():
    """Main function to run the MCP server"""
    # Run the server using stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="patient-database-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())