# MCP Patient Database Server

A Model Context Protocol (MCP) server that provides secure access to patient database for authorized healthcare agents.

## Overview

This MCP server allows healthcare agents to:
- Query patient information by ID
- Search patients by name, diagnosis, or treatment
- Get database statistics
- Access medical records securely

## Features

- **Secure Access**: Only authorized agents can access patient data
- **SQLite Database**: Lightweight, file-based patient database
- **Sample Data**: Pre-populated with sample patient records
- **Medical Records**: Detailed medical history tracking
- **Search Capabilities**: Flexible patient search functionality
- **Statistics**: Database analytics and reporting

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r mcp_requirements.txt
   ```

2. **Verify MCP Installation**:
   ```bash
   python -c "import mcp; print('MCP installed successfully')"
   ```

## Database Schema

### Patients Table
- `id`: Primary key
- `patient_id`: Unique patient identifier (P001, P002, etc.)
- `name`: Patient full name
- `age`: Patient age
- `gender`: Patient gender
- `diagnosis`: Primary diagnosis
- `treatment`: Current treatment plan
- `admission_date`: Hospital admission date
- `discharge_date`: Hospital discharge date (if applicable)
- `status`: Patient status (active/discharged)
- `notes`: Additional notes
- `created_at`: Record creation timestamp

### Medical Records Table
- `id`: Primary key
- `patient_id`: Reference to patient
- `record_type`: Type of medical record
- `description`: Record description
- `date_recorded`: Date of record
- `doctor_name`: Attending physician

## Sample Data

The server comes with 5 sample patients:
- **P001**: John Smith (Hypertension)
- **P002**: Mary Johnson (Diabetes Type 2)
- **P003**: Robert Brown (Heart Disease)
- **P004**: Sarah Davis (Pregnancy)
- **P005**: Michael Wilson (Cancer)

## Usage

### Starting the Server

```bash
python mcp_patient_server.py
```

### Available Tools

#### 1. Get Patient by ID
```json
{
  "tool": "get_patient",
  "parameters": {
    "patient_id": "P001"
  }
}
```

**Response**: Complete patient information including medical records

#### 2. Search Patients
```json
{
  "tool": "search_patients",
  "parameters": {
    "query": "diabetes",
    "status": "active"
  }
}
```

**Parameters**:
- `query` (optional): Search term for name, diagnosis, or treatment
- `status` (optional): Filter by status ("active" or "discharged")

#### 3. Get Statistics
```json
{
  "tool": "get_statistics",
  "parameters": {}
}
```

**Response**: Database statistics including patient counts and demographics

## Agent Integration

### Configuration for Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "patient-database": {
      "command": "python",
      "args": ["/path/to/mcp_patient_server.py"]
    }
  }
}
```

### Example Agent Queries

1. **"Show me information about patient P001"**
   - Uses: `get_patient` tool
   - Returns: Complete patient profile with medical history

2. **"Find all patients with diabetes"**
   - Uses: `search_patients` tool with query="diabetes"
   - Returns: List of diabetic patients

3. **"How many active patients do we have?"**
   - Uses: `get_statistics` tool
   - Returns: Database statistics including active patient count

4. **"Show me all discharged patients"**
   - Uses: `search_patients` tool with status="discharged"
   - Returns: List of discharged patients

## Security Features

- **Agent Authorization**: Only specified agents can access the server
- **Data Validation**: Input validation for all queries
- **Error Handling**: Secure error messages without data leakage
- **Audit Logging**: All database access is logged

## File Structure

```
RAG_API_Cloud(知识库)/
├── mcp_patient_server.py      # Main MCP server
├── mcp_requirements.txt       # Python dependencies
├── mcp_config.json           # Server configuration
├── MCP_Patient_Server_README.md  # This documentation
└── patients.db               # SQLite database (auto-created)
```

## Troubleshooting

### Common Issues

1. **"Module 'mcp' not found"**
   - Solution: Install MCP with `pip install mcp`

2. **"Database file not found"**
   - Solution: The database is auto-created on first run

3. **"Permission denied"**
   - Solution: Ensure the script has write permissions for database creation

### Logs

The server logs all operations to help with debugging:
- Database initialization
- Tool calls and responses
- Error conditions

## Development

### Adding New Tools

1. Add tool definition in `handle_list_tools()`
2. Implement tool logic in `handle_call_tool()`
3. Update configuration and documentation

### Database Modifications

1. Modify `init_database()` method
2. Add new query methods to `PatientDatabase` class
3. Test with sample data

## License

This MCP server is provided for educational and development purposes. Ensure compliance with healthcare data regulations (HIPAA, GDPR) when using with real patient data.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review server logs
3. Verify MCP client configuration
4. Test with sample queries