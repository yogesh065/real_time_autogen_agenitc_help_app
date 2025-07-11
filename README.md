# Medical AI Assistant with Groq API

A real-time medical product support system powered by AutoGen and Groq's fast LLM API.

## Features

- 🏥 **Medical Product Search**: Find medications, dosages, and alternatives
- 💊 **Dosage Calculations**: Get personalized dosing recommendations
- ⚠️ **Safety & Interactions**: Check drug interactions and contraindications
- 💰 **Insurance Coverage**: Get coverage information and cost-saving tips
- 🤖 **Multi-Agent System**: Specialized medical agents working together
- ⚡ **Fast Responses**: Powered by Groq's ultra-fast LLM API

## Prerequisites

- Python 3.8+
- Groq API key (get one at [console.groq.com](https://console.groq.com/))

## Quick Setup

### 1. Clone and Install Dependencies

```bash
git clone <your-repo-url>
cd real_time_autogen_agenitc_help_app
pip install -r requirements.txt
```

### 2. Set Up Groq API Key

```bash
export GROQ_API_KEY="your-groq-api-key-here"
```

Or add to your shell profile:
```bash
echo 'export GROQ_API_KEY="your-groq-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Test the Setup

```bash
python test_groq_integration.py
```

### 4. Run the Application

```bash
streamlit run streamlit_realtime_medical_app.py
```

## Alternative Setup (Automated)

Run the setup script:

```bash
chmod +x setup_groq.sh
./setup_groq.sh
```

## Usage

### Web Interface

1. Start the Streamlit app: `streamlit run streamlit_realtime_medical_app.py`
2. Open your browser to the provided URL
3. Ask medical questions in the text area
4. Use quick action buttons for common queries

### Sample Queries

- "Find pain relief medications"
- "Acetaminophen dosage for adults"
- "Ibuprofen side effects and warnings"
- "Drug interactions between aspirin and warfarin"
- "Insurance coverage for diabetes medications"

### Programmatic Usage

```python
from autogen_realtime_medical import MedicalRealtimeAgentSystem

# Initialize the system
medical_system = MedicalRealtimeAgentSystem("your-groq-api-key")

# Search for medical products
results = medical_system.search_medical_products("aspirin")

# Get dosage information
dosage_info = medical_system.calculate_dosage("acetaminophen", 30, 70)

# Check drug interactions
interactions = medical_system.check_drug_interactions(["aspirin", "warfarin"])
```

## Architecture

### Multi-Agent System

The application uses AutoGen to coordinate specialized medical agents:

1. **MedicalProductSearcher**: Finds and provides product information
2. **DosageSpecialist**: Calculates and explains dosing
3. **SafetySpecialist**: Checks interactions and safety
4. **InsuranceCoverageSpecialist**: Provides coverage information

### Database

- SQLite database with medical product information
- Includes sample data for testing
- Supports advanced search and filtering

## Configuration

### Environment Variables

- `GROQ_API_KEY`: Your Groq API key (required)

### Model Configuration

The system uses Groq's `llama3.1-8b-8192` model by default. You can modify the model in `autogen_realtime_medical.py`:

```python
"model": "llama3.1-8b-8192",  # Change to other Groq models
```

Available Groq models:
- `llama3.1-8b-8192` (fastest)
- `llama3.1-70b-8192` (most capable)
- `mixtral-8x7b-32768`
- `gemma2-9b-it`

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   - Ensure `GROQ_API_KEY` is set correctly
   - Check with: `echo $GROQ_API_KEY`

2. **Connection Errors**
   - Verify your internet connection
   - Check if Groq API is accessible

3. **Import Errors**
   - Install dependencies: `pip install -r requirements.txt`
   - Check Python version: `python --version`

### Testing

Run the test script to verify everything works:

```bash
python test_groq_integration.py
```

## Security Notes

- Never commit your API key to version control
- Use environment variables for sensitive data
- The system includes safety warnings for medical information

## Medical Disclaimer

⚠️ **Important**: This system provides general medical information only. Always consult with healthcare professionals for medical advice, diagnosis, and treatment.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions:
- Check the troubleshooting section
- Review the test script output
- Ensure all dependencies are installed 