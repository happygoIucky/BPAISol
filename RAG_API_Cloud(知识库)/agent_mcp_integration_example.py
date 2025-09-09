#!/usr/bin/env python3
"""
Example integration of MCP Patient Database Server with the existing agent system.
This shows how agents can use the MCP server to access patient data during conversations.
"""

import json
import asyncio
from typing import Dict, Any, Optional
from mcp_patient_server import PatientDatabase

class HealthcareAgent:
    """Healthcare agent that can access patient database via MCP"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.patient_db = PatientDatabase()
        self.authorized = True  # In production, implement proper auth
    
    def is_authorized(self) -> bool:
        """Check if agent is authorized to access patient data"""
        return self.authorized
    
    async def handle_patient_query(self, query: str, session_context: Dict[str, Any]) -> str:
        """Handle patient-related queries using MCP tools"""
        
        if not self.is_authorized():
            return "❌ Access denied. Agent not authorized for patient data access."
        
        query_lower = query.lower()
        
        # Pattern matching for different types of queries
        if "patient" in query_lower and any(pid in query for pid in ["p001", "p002", "p003", "p004", "p005"]):
            return await self._get_patient_info(query)
        
        elif "search" in query_lower or "find" in query_lower:
            return await self._search_patients(query)
        
        elif "statistics" in query_lower or "stats" in query_lower or "how many" in query_lower:
            return await self._get_statistics()
        
        elif "diabetes" in query_lower or "hypertension" in query_lower or "cancer" in query_lower:
            return await self._search_by_condition(query)
        
        else:
            return await self._general_patient_help(query)
    
    async def _get_patient_info(self, query: str) -> str:
        """Get specific patient information"""
        # Extract patient ID from query
        patient_id = None
        for pid in ["P001", "P002", "P003", "P004", "P005"]:
            if pid.lower() in query.lower():
                patient_id = pid
                break
        
        if not patient_id:
            return "❓ Please specify a valid patient ID (P001-P005)."
        
        try:
            patient = self.patient_db.get_patient_by_id(patient_id)
            if patient:
                return self._format_patient_info(patient)
            else:
                return f"❌ Patient {patient_id} not found in database."
        except Exception as e:
            return f"❌ Error retrieving patient information: {str(e)}"
    
    async def _search_patients(self, query: str) -> str:
        """Search patients based on query"""
        try:
            # Extract search terms
            search_term = None
            status_filter = None
            
            if "active" in query.lower():
                status_filter = "active"
            elif "discharged" in query.lower():
                status_filter = "discharged"
            
            # Extract condition or name
            conditions = ["diabetes", "hypertension", "cancer", "heart", "pregnancy"]
            for condition in conditions:
                if condition in query.lower():
                    search_term = condition
                    break
            
            patients = self.patient_db.search_patients(query=search_term, status=status_filter)
            
            if patients:
                return self._format_patient_list(patients)
            else:
                return "❌ No patients found matching your criteria."
        
        except Exception as e:
            return f"❌ Error searching patients: {str(e)}"
    
    async def _search_by_condition(self, query: str) -> str:
        """Search patients by medical condition"""
        condition_map = {
            "diabetes": "diabetes",
            "hypertension": "hypertension", 
            "cancer": "cancer",
            "heart": "heart",
            "pregnancy": "pregnancy"
        }
        
        condition = None
        for key, value in condition_map.items():
            if key in query.lower():
                condition = value
                break
        
        if condition:
            try:
                patients = self.patient_db.search_patients(query=condition)
                if patients:
                    return f"📋 **Patients with {condition.title()}:**\n\n" + self._format_patient_list(patients)
                else:
                    return f"❌ No patients found with {condition}."
            except Exception as e:
                return f"❌ Error searching for {condition} patients: {str(e)}"
        else:
            return "❓ Please specify a medical condition (diabetes, hypertension, cancer, heart disease, pregnancy)."
    
    async def _get_statistics(self) -> str:
        """Get database statistics"""
        try:
            stats = self.patient_db.get_patient_statistics()
            return self._format_statistics(stats)
        except Exception as e:
            return f"❌ Error retrieving statistics: {str(e)}"
    
    async def _general_patient_help(self, query: str) -> str:
        """Provide general help for patient queries"""
        return """🏥 **Patient Database Help**

I can help you with:

📋 **Patient Information:**
• "Show me patient P001"
• "Get information about patient P002"

🔍 **Search Patients:**
• "Find patients with diabetes"
• "Show active patients"
• "Search for discharged patients"

📊 **Statistics:**
• "Show patient statistics"
• "How many patients do we have?"

**Available Patient IDs:** P001, P002, P003, P004, P005

What would you like to know?"""
    
    def _format_patient_info(self, patient: Dict[str, Any]) -> str:
        """Format detailed patient information"""
        info = f"""👤 **Patient Information: {patient['name']}**

**Basic Details:**
• Patient ID: {patient['patient_id']}
• Age: {patient['age']} years
• Gender: {patient['gender']}
• Status: {patient['status'].title()}

**Medical Information:**
• Diagnosis: {patient['diagnosis']}
• Treatment: {patient['treatment']}
• Admission Date: {patient['admission_date'] or 'N/A'}
• Discharge Date: {patient['discharge_date'] or 'Still admitted'}

**Notes:** {patient['notes'] or 'No additional notes'}
"""
        
        if patient.get('medical_records'):
            info += "\n📋 **Recent Medical Records:**\n"
            for record in patient['medical_records'][:3]:  # Show last 3 records
                info += f"• {record['date_recorded']}: {record['record_type']} - {record['description']} (Dr. {record['doctor_name']})\n"
            
            if len(patient['medical_records']) > 3:
                info += f"• ... and {len(patient['medical_records']) - 3} more records\n"
        
        return info
    
    def _format_patient_list(self, patients: list) -> str:
        """Format list of patients"""
        if not patients:
            return "❌ No patients found."
        
        result = f"📋 **Found {len(patients)} patient(s):**\n\n"
        
        for patient in patients:
            status_emoji = "🟢" if patient['status'] == 'active' else "🔴"
            result += f"{status_emoji} **{patient['name']}** ({patient['patient_id']})\n"
            result += f"   Age: {patient['age']}, Gender: {patient['gender']}\n"
            result += f"   Diagnosis: {patient['diagnosis']}\n"
            result += f"   Status: {patient['status'].title()}\n\n"
        
        return result
    
    def _format_statistics(self, stats: Dict[str, Any]) -> str:
        """Format database statistics"""
        result = "📊 **Patient Database Statistics**\n\n"
        result += f"👥 **Total Patients:** {stats['total_patients']}\n"
        result += f"🟢 **Active Patients:** {stats['active_patients']}\n"
        result += f"🔴 **Discharged Patients:** {stats['discharged_patients']}\n"
        result += f"📅 **Recent Admissions (30 days):** {stats['recent_admissions_30_days']}\n\n"
        
        if stats.get('gender_distribution'):
            result += "👫 **Gender Distribution:**\n"
            for gender, count in stats['gender_distribution'].items():
                result += f"• {gender}: {count}\n"
        
        return result

# Integration with existing agent system
def integrate_with_agent_system():
    """Example of how to integrate MCP server with existing agent system"""
    
    # This would be added to the existing step6_rag_chatbot.py
    healthcare_agent = HealthcareAgent("Dr. Assistant")
    
    async def enhanced_agent_send_message(agent_id: str, session_id: str, message: str):
        """Enhanced agent message handler with MCP integration"""
        
        # Check if message is patient-related
        patient_keywords = ["patient", "medical", "diagnosis", "treatment", "statistics", 
                          "search", "find", "diabetes", "hypertension", "cancer"]
        
        if any(keyword in message.lower() for keyword in patient_keywords):
            # Use MCP server for patient queries
            session_context = {"agent_id": agent_id, "session_id": session_id}
            response = await healthcare_agent.handle_patient_query(message, session_context)
            return response
        else:
            # Handle as regular agent message
            return f"Agent response: {message}"
    
    return enhanced_agent_send_message

# Example usage
async def demo_agent_queries():
    """Demonstrate agent using MCP server"""
    agent = HealthcareAgent("Dr. Smith")
    
    print("🏥 Healthcare Agent MCP Integration Demo\n")
    
    # Example queries
    queries = [
        "Show me patient P001",
        "Find patients with diabetes", 
        "What are our patient statistics?",
        "Search for active patients",
        "Tell me about patient P003"
    ]
    
    for query in queries:
        print(f"👤 User: {query}")
        response = await agent.handle_patient_query(query, {})
        print(f"🤖 Agent: {response}\n")
        print("-" * 50 + "\n")

if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_agent_queries())