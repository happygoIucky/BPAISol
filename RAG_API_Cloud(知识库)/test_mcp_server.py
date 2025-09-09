#!/usr/bin/env python3
"""
Test script for MCP Patient Database Server
Verifies that the server and database operations work correctly.
"""

import json
import sqlite3
import os
from mcp_patient_server import PatientDatabase

def test_database_initialization():
    """Test database initialization and sample data"""
    print("🧪 Testing database initialization...")
    
    # Remove existing test database
    test_db_path = "test_patients.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Initialize test database
    db = PatientDatabase(test_db_path)
    
    # Verify tables exist
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    assert 'patients' in tables, "Patients table not created"
    assert 'medical_records' in tables, "Medical records table not created"
    
    # Verify sample data
    cursor.execute("SELECT COUNT(*) FROM patients")
    patient_count = cursor.fetchone()[0]
    assert patient_count == 5, f"Expected 5 patients, got {patient_count}"
    
    cursor.execute("SELECT COUNT(*) FROM medical_records")
    record_count = cursor.fetchone()[0]
    assert record_count > 0, "No medical records found"
    
    conn.close()
    print("✅ Database initialization test passed")
    
    # Cleanup
    os.remove(test_db_path)

def test_get_patient_by_id():
    """Test retrieving patient by ID"""
    print("🧪 Testing get_patient_by_id...")
    
    db = PatientDatabase("test_patients.db")
    
    # Test existing patient
    patient = db.get_patient_by_id("P001")
    assert patient is not None, "Patient P001 not found"
    assert patient['name'] == 'John Smith', f"Expected John Smith, got {patient['name']}"
    assert 'medical_records' in patient, "Medical records not included"
    assert len(patient['medical_records']) > 0, "No medical records found for patient"
    
    # Test non-existing patient
    patient = db.get_patient_by_id("P999")
    assert patient is None, "Non-existing patient should return None"
    
    print("✅ Get patient by ID test passed")
    
    # Cleanup
    os.remove("test_patients.db")

def test_search_patients():
    """Test patient search functionality"""
    print("🧪 Testing search_patients...")
    
    db = PatientDatabase("test_patients.db")
    
    # Test search by diagnosis
    patients = db.search_patients(query="diabetes")
    assert len(patients) > 0, "No diabetes patients found"
    diabetes_patient = next((p for p in patients if 'diabetes' in p['diagnosis'].lower()), None)
    assert diabetes_patient is not None, "Diabetes patient not in search results"
    
    # Test search by status
    active_patients = db.search_patients(status="active")
    discharged_patients = db.search_patients(status="discharged")
    
    assert len(active_patients) > 0, "No active patients found"
    assert len(discharged_patients) > 0, "No discharged patients found"
    
    # Verify status filtering
    for patient in active_patients:
        assert patient['status'] == 'active', f"Patient {patient['patient_id']} should be active"
    
    for patient in discharged_patients:
        assert patient['status'] == 'discharged', f"Patient {patient['patient_id']} should be discharged"
    
    # Test combined search
    results = db.search_patients(query="John", status="active")
    if results:
        for patient in results:
            assert 'john' in patient['name'].lower(), "Patient name should contain 'john'"
            assert patient['status'] == 'active', "Patient should be active"
    
    print("✅ Search patients test passed")
    
    # Cleanup
    os.remove("test_patients.db")

def test_get_statistics():
    """Test database statistics"""
    print("🧪 Testing get_statistics...")
    
    db = PatientDatabase("test_patients.db")
    
    stats = db.get_patient_statistics()
    
    # Verify required fields
    required_fields = ['total_patients', 'active_patients', 'discharged_patients', 
                      'gender_distribution', 'recent_admissions_30_days']
    
    for field in required_fields:
        assert field in stats, f"Missing field: {field}"
    
    # Verify data consistency
    assert stats['total_patients'] == 5, f"Expected 5 total patients, got {stats['total_patients']}"
    assert stats['active_patients'] + stats['discharged_patients'] == stats['total_patients'], \
           "Active + discharged should equal total"
    
    # Verify gender distribution
    assert isinstance(stats['gender_distribution'], dict), "Gender distribution should be a dict"
    
    print("✅ Statistics test passed")
    print(f"📊 Statistics: {json.dumps(stats, indent=2)}")
    
    # Cleanup
    os.remove("test_patients.db")

def test_sample_data_integrity():
    """Test that sample data is complete and valid"""
    print("🧪 Testing sample data integrity...")
    
    db = PatientDatabase("test_patients.db")
    
    # Test each sample patient
    sample_patient_ids = ['P001', 'P002', 'P003', 'P004', 'P005']
    
    for patient_id in sample_patient_ids:
        patient = db.get_patient_by_id(patient_id)
        assert patient is not None, f"Patient {patient_id} not found"
        
        # Verify required fields
        required_fields = ['patient_id', 'name', 'age', 'gender', 'diagnosis', 'treatment']
        for field in required_fields:
            assert field in patient and patient[field], f"Patient {patient_id} missing {field}"
        
        # Verify data types
        assert isinstance(patient['age'], int), f"Patient {patient_id} age should be integer"
        assert patient['age'] > 0, f"Patient {patient_id} age should be positive"
        
        # Verify status
        assert patient['status'] in ['active', 'discharged'], f"Invalid status for patient {patient_id}"
    
    print("✅ Sample data integrity test passed")
    
    # Cleanup
    os.remove("test_patients.db")

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting MCP Patient Database Server Tests\n")
    
    try:
        test_database_initialization()
        test_get_patient_by_id()
        test_search_patients()
        test_get_statistics()
        test_sample_data_integrity()
        
        print("\n🎉 All tests passed successfully!")
        print("\n📋 Test Summary:")
        print("   ✅ Database initialization")
        print("   ✅ Get patient by ID")
        print("   ✅ Search patients")
        print("   ✅ Database statistics")
        print("   ✅ Sample data integrity")
        
        print("\n🔧 Next Steps:")
        print("   1. Install MCP dependencies: pip install -r mcp_requirements.txt")
        print("   2. Start the server: python mcp_patient_server.py")
        print("   3. Configure your MCP client with the server")
        print("   4. Test with agent queries")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    run_all_tests()