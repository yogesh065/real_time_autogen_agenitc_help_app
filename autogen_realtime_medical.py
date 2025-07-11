import asyncio
import json
import uuid
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

# AutoGen imports - using available modules
from autogen import Agent, AssistantAgent, UserProxyAgent, config_list_from_json
from autogen.agentchat.contrib.text_analyzer_agent import TextAnalyzerAgent

# WebSocket imports for real-time communication
import websockets
import asyncio

from medical_database import MedicalProductDatabase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MedicalRealtimeAgentSystem:
    def __init__(self, groq_api_key: str, db_path: str = "medical_products.db"):
        logger.info("Initializing MedicalRealtimeAgentSystem...")
        self.db = MedicalProductDatabase(db_path)
        self.session_id = str(uuid.uuid4())
        self.groq_api_key = groq_api_key
        
        logger.info(f"Session ID: {self.session_id}")
        logger.info(f"Groq API Key: {groq_api_key[:10]}...")
        
        # Initialize sample data
        try:
            logger.info("Adding sample medical data...")
            self.db.add_sample_medical_data()
            logger.info("Sample data added successfully")
        except Exception as e:
            logger.warning(f"Sample data might already exist: {e}")
        
        # AutoGen configuration for Groq
        logger.info("Setting up LLM configuration for Groq...")
        self.llm_config = {
            "config_list": [
                {
                    "model": "llama3.1-8b-8192",
                    "api_key": groq_api_key,
                    "base_url": "https://api.groq.com/openai/v1"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1500,
        }
        
        logger.info(f"LLM Config: {self.llm_config}")
        self.setup_medical_agents()
        logger.info("MedicalRealtimeAgentSystem initialization complete!")
    
    def setup_medical_agents(self):
        """Setup specialized medical agents"""
        logger.info("Setting up medical agents...")
        
        # Medical Product Search Agent
        logger.info("Creating MedicalProductSearcher agent...")
        self.product_search_agent = AssistantAgent(
            name="MedicalProductSearcher",
            system_message="""You are a medical product search specialist.
            
            Your responsibilities:
            1. Search medical products database efficiently
            2. Provide comprehensive product information
            3. Filter results based on user needs
            4. Highlight important safety information
            5. Suggest alternatives when appropriate
            
            Always include:
            - Product name and generic name
            - Key indications and uses
            - Important safety warnings
            - Availability and pricing information
            
            Format responses for voice interaction - be clear and organized.""",
            llm_config=self.llm_config
        )
        logger.info("MedicalProductSearcher agent created successfully")
        
        # Dosage Information Agent
        logger.info("Creating DosageSpecialist agent...")
        self.dosage_agent = AssistantAgent(
            name="DosageSpecialist",
            system_message="""You are a dosage and administration specialist.
            
            Your responsibilities:
            1. Provide accurate dosage information
            2. Consider patient age, weight, and conditions
            3. Explain administration instructions clearly
            4. Highlight dosage-related warnings
            5. Recommend professional consultation for complex cases
            
            Always emphasize:
            - Proper dosing schedules
            - Maximum daily limits
            - Age-specific considerations
            - Professional medical supervision requirements
            
            Speak clearly about numbers and measurements.""",
            llm_config=self.llm_config
        )
        logger.info("DosageSpecialist agent created successfully")
        
        # Safety and Interactions Agent
        logger.info("Creating SafetySpecialist agent...")
        self.safety_agent = AssistantAgent(
            name="SafetySpecialist",
            system_message="""You are a medication safety and drug interaction specialist.
            
            Your responsibilities:
            1. Identify potential drug interactions
            2. Highlight contraindications and warnings
            3. Assess patient-specific safety concerns
            4. Provide comprehensive safety guidance
            5. Recommend professional safety evaluations
            
            Always check for:
            - Known drug interactions
            - Contraindications
            - Allergy considerations
            - Special population warnings (pregnancy, elderly, pediatric)
            
            Emphasize safety in all communications.""",
            llm_config=self.llm_config
        )
        logger.info("SafetySpecialist agent created successfully")
        
        # Insurance and Coverage Agent
        logger.info("Creating InsuranceCoverageSpecialist agent...")
        self.insurance_agent = AssistantAgent(
            name="InsuranceCoverageSpecialist",
            system_message="""You are an insurance and medication coverage specialist.
            
            Your responsibilities:
            1. Provide insurance coverage information
            2. Suggest cost-effective alternatives
            3. Explain prior authorization requirements
            4. Recommend patient assistance programs
            5. Guide users on coverage verification
            
            Focus on:
            - Insurance coverage details
            - Generic vs brand options
            - Cost-saving opportunities
            - Patient assistance programs
            
            Help users understand their coverage options clearly.""",
            llm_config=self.llm_config
        )
        logger.info("InsuranceCoverageSpecialist agent created successfully")
        
        # User proxy agent
        logger.info("Creating UserProxyAgent...")
        self.user_proxy = UserProxyAgent(
            name="User",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            llm_config=self.llm_config,
            code_execution_config={"use_docker": False}
        )
        logger.info("UserProxyAgent created successfully")
        logger.info("All medical agents setup complete!")
    
    # Agent function implementations
    def search_medical_products(self, query: str, category: str = None, 
                              prescription_only: bool = None) -> str:
        """Search medical products with advanced filtering"""
        logger.info(f"Searching medical products for query: '{query}'")
        logger.info(f"Category filter: {category}")
        logger.info(f"Prescription only filter: {prescription_only}")
        
        try:
            filters = {}
            if category:
                filters['category'] = category
            if prescription_only is not None:
                filters['prescription_required'] = prescription_only
            
            logger.info(f"Applying filters: {filters}")
            products = self.db.search_products_advanced(query, filters)
            logger.info(f"Found {len(products)} products")
            
            if not products:
                logger.warning(f"No medical products found matching '{query}'")
                return f"No medical products found matching '{query}'. Please try a different search term or ask me to search in a specific category."
            
            result = f"Found {len(products)} medical product(s) for '{query}':\n\n"
            
            for i, product in enumerate(products[:5]):  # Limit to top 5 for voice
                logger.info(f"Processing product {i+1}: {product['name']}")
                result += f"**{product['name']}** ({product['brand_name'] or 'Generic'})\n"
                result += f"Category: {product['category']}\n"
                result += f"Used for: {product['indications']}\n"
                result += f"Prescription required: {'Yes' if product['prescription_required'] else 'No'}\n"
                result += f"Price: ${product['price']}\n"
                result += f"Availability: {product['availability']}\n"
                
                if product['contraindications']:
                    result += f"⚠️ Important: {product['contraindications']}\n"
                
                result += "---\n"
            
            logger.info(f"Generated response with {len(result)} characters")
            return result
            
        except Exception as e:
            logger.error(f"Error searching medical products: {str(e)}")
            return f"Error searching medical products: {str(e)}"
    
    def get_product_details(self, product_name: str) -> str:
        """Get comprehensive details for a specific product"""
        try:
            products = self.db.search_products_advanced(product_name)
            
            if not products:
                return f"Product '{product_name}' not found in our database."
            
            product = products[0]  # Take first match
            
            details = f"**Complete Information for {product['name']}**\n\n"
            details += f"Brand Name: {product['brand_name'] or 'Generic'}\n"
            details += f"Generic Name: {product['generic_name']}\n"
            details += f"Category: {product['category']}\n"
            details += f"Description: {product['description']}\n"
            details += f"Available Forms: {product['dosage_forms']}\n"
            details += f"Strength: {product['strength']}\n"
            details += f"Uses: {product['indications']}\n"
            details += f"Adult Dosage: {product['dosage_adult']}\n"
            details += f"Pediatric Dosage: {product['dosage_pediatric']}\n"
            details += f"Side Effects: {product['side_effects']}\n"
            details += f"Drug Interactions: {product['drug_interactions']}\n"
            details += f"Warnings: {product['warnings']}\n"
            details += f"Storage: {product['storage_conditions']}\n"
            details += f"Manufacturer: {product['manufacturer']}\n"
            details += f"Price: ${product['price']}\n"
            details += f"Insurance Coverage: {product['insurance_coverage']}\n"
            details += f"Prescription Required: {'Yes' if product['prescription_required'] else 'No'}\n"
            
            return details
            
        except Exception as e:
            return f"Error retrieving product details: {str(e)}"
    
    def calculate_dosage(self, product_name: str, patient_age: int, 
                        patient_weight: float, medical_conditions: str = "") -> str:
        """Calculate appropriate dosage based on patient parameters"""
        try:
            products = self.db.search_products_advanced(product_name)
            
            if not products:
                return f"Product '{product_name}' not found for dosage calculation."
            
            product = products[0]
            
            calculation = f"**Dosage Information for {product['name']}**\n\n"
            calculation += f"Patient Age: {patient_age} years\n"
            calculation += f"Patient Weight: {patient_weight} kg\n"
            
            if patient_age < 18:
                calculation += f"Pediatric Dosage: {product['dosage_pediatric']}\n"
                calculation += "⚠️ PEDIATRIC PATIENT: Dosing must be verified by pediatrician\n"
            else:
                calculation += f"Adult Dosage: {product['dosage_adult']}\n"
            
            if medical_conditions:
                calculation += f"Medical Conditions: {medical_conditions}\n"
                calculation += "⚠️ Dosage adjustments may be needed for medical conditions\n"
            
            calculation += f"\n**Important Safety Information:**\n"
            calculation += f"Contraindications: {product['contraindications']}\n"
            calculation += f"Side Effects: {product['side_effects']}\n"
            calculation += f"Warnings: {product['warnings']}\n"
            
            calculation += "\n🏥 **MANDATORY CONSULTATION**: Always consult with healthcare provider for personalized dosing recommendations.\n"
            
            return calculation
            
        except Exception as e:
            return f"Error calculating dosage: {str(e)}"
    
    def check_dosage_safety(self, product_name: str, proposed_dose: str, 
                           patient_age: int, frequency: str) -> str:
        """Check if proposed dosage is within safe limits"""
        try:
            products = self.db.search_products_advanced(product_name)
            
            if not products:
                return f"Product '{product_name}' not found for safety check."
            
            product = products[0]
            
            safety_check = f"**Dosage Safety Check for {product['name']}**\n\n"
            safety_check += f"Proposed Dose: {proposed_dose}\n"
            safety_check += f"Frequency: {frequency}\n"
            safety_check += f"Patient Age: {patient_age} years\n"
            
            if patient_age < 18:
                safety_check += f"Approved Pediatric Dosage: {product['dosage_pediatric']}\n"
            else:
                safety_check += f"Approved Adult Dosage: {product['dosage_adult']}\n"
            
            safety_check += f"\n**Critical Safety Information:**\n"
            safety_check += f"Contraindications: {product['contraindications']}\n"
            safety_check += f"Warnings: {product['warnings']}\n"
            safety_check += f"Maximum Daily Limits: Check product labeling\n"
            
            safety_check += "\n🏥 **PROFESSIONAL VERIFICATION REQUIRED**: Have healthcare provider verify dosage safety before administration.\n"
            
            return safety_check
            
        except Exception as e:
            return f"Error checking dosage safety: {str(e)}"
    
    def check_drug_interactions(self, medications: List[str]) -> str:
        """Check for potential drug interactions"""
        try:
            if len(medications) < 2:
                return "Please provide at least 2 medications to check for interactions."
            
            interaction_report = f"**Drug Interaction Analysis**\n\n"
            interaction_report += f"Medications being checked: {', '.join(medications)}\n\n"
            
            # Get interaction information for each medication
            for med in medications:
                products = self.db.search_products_advanced(med)
                if products:
                    product = products[0]
                    interaction_report += f"**{product['name']}** interactions: {product['drug_interactions']}\n"
            
            interaction_report += "\n**Important Notes:**\n"
            interaction_report += "• This is a basic interaction screening\n"
            interaction_report += "• Some interactions may not be listed\n"
            interaction_report += "• Clinical significance varies by patient\n"
            interaction_report += "• Timing of administration matters\n"
            
            interaction_report += "\n🏥 **PROFESSIONAL CONSULTATION REQUIRED**: Always consult pharmacist or doctor for comprehensive interaction analysis.\n"
            
            return interaction_report
            
        except Exception as e:
            return f"Error checking drug interactions: {str(e)}"
    
    def assess_safety_profile(self, product_name: str, patient_conditions: str = "",
                            allergies: str = "", other_medications: str = "") -> str:
        """Comprehensive safety assessment"""
        try:
            products = self.db.search_products_advanced(product_name)
            
            if not products:
                return f"Product '{product_name}' not found for safety assessment."
            
            product = products[0]
            
            assessment = f"**Comprehensive Safety Assessment for {product['name']}**\n\n"
            
            assessment += f"**Product Safety Profile:**\n"
            assessment += f"Contraindications: {product['contraindications']}\n"
            assessment += f"Side Effects: {product['side_effects']}\n"
            assessment += f"Drug Interactions: {product['drug_interactions']}\n"
            assessment += f"Warnings: {product['warnings']}\n"
            
            if patient_conditions:
                assessment += f"\n**Patient Conditions:** {patient_conditions}\n"
                assessment += "⚠️ Condition-specific precautions may apply\n"
            
            if allergies:
                assessment += f"\n**Patient Allergies:** {allergies}\n"
                assessment += "⚠️ Allergy cross-reactions must be evaluated\n"
            
            if other_medications:
                assessment += f"\n**Other Medications:** {other_medications}\n"
                assessment += "⚠️ Drug interactions must be checked\n"
            
            assessment += "\n**Special Considerations:**\n"
            assessment += f"Prescription Required: {'Yes' if product['prescription_required'] else 'No'}\n"
            assessment += f"Controlled Substance: {'Yes' if product['controlled_substance'] else 'No'}\n"
            
            assessment += "\n🏥 **MANDATORY PROFESSIONAL REVIEW**: Healthcare provider must evaluate all safety factors before use.\n"
            
            return assessment
            
        except Exception as e:
            return f"Error assessing safety profile: {str(e)}"
    
    def check_insurance_coverage(self, product_name: str, insurance_type: str = "") -> str:
        """Check insurance coverage for medication"""
        try:
            products = self.db.search_products_advanced(product_name)
            
            if not products:
                return f"Product '{product_name}' not found for coverage check."
            
            product = products[0]
            
            coverage_info = f"**Insurance Coverage Information for {product['name']}**\n\n"
            coverage_info += f"General Coverage: {product['insurance_coverage']}\n"
            coverage_info += f"Retail Price: ${product['price']}\n"
            coverage_info += f"Prescription Required: {'Yes' if product['prescription_required'] else 'No'}\n"
            
            if insurance_type:
                coverage_info += f"Insurance Type: {insurance_type}\n"
            
            coverage_info += "\n**Coverage Tips:**\n"
            coverage_info += "• Check your specific plan formulary\n"
            coverage_info += "• Ask about generic alternatives\n"
            coverage_info += "• Inquire about prior authorization requirements\n"
            coverage_info += "• Consider patient assistance programs\n"
            
            if product['generic_name'] != product['name']:
                coverage_info += f"• Generic option: {product['generic_name']} (usually better coverage)\n"
            
            coverage_info += "\n💰 **VERIFY COVERAGE**: Contact your insurance provider to confirm coverage details.\n"
            
            return coverage_info
            
        except Exception as e:
            return f"Error checking insurance coverage: {str(e)}"
    
    def find_alternatives(self, product_name: str, reason: str = "cost") -> str:
        """Find alternative medications"""
        try:
            products = self.db.search_products_advanced(product_name)
            
            if not products:
                return f"Product '{product_name}' not found for alternatives search."
            
            original_product = products[0]
            
            # Search for alternatives in same category
            alternatives = self.db.search_products_advanced(
                original_product['indications'], 
                {'category': original_product['category']}
            )
            
            alt_info = f"**Alternative Options for {original_product['name']}**\n\n"
            alt_info += f"Original: {original_product['name']} - ${original_product['price']}\n"
            alt_info += f"Reason for alternatives: {reason}\n\n"
            
            if len(alternatives) > 1:
                alt_info += "**Available Alternatives:**\n"
                
                for alt in alternatives[1:6]:  # Skip original, show 5 alternatives
                    alt_info += f"• {alt['name']} - ${alt['price']}\n"
                    alt_info += f"  Generic: {alt['generic_name']}\n"
                    alt_info += f"  Prescription: {'Yes' if alt['prescription_required'] else 'No'}\n"
                    alt_info += f"  Coverage: {alt['insurance_coverage']}\n\n"
            else:
                alt_info += "No direct alternatives found in our database.\n"
            
            alt_info += "**Important Notes:**\n"
            alt_info += "• Alternatives may have different side effects\n"
            alt_info += "• Dosing may differ between products\n"
            alt_info += "• Effectiveness may vary by individual\n"
            
            alt_info += "\n🏥 **PROFESSIONAL CONSULTATION**: Discuss alternatives with healthcare provider before switching.\n"
            
            return alt_info
            
        except Exception as e:
            return f"Error finding alternatives: {str(e)}"
    
    def log_voice_interaction(self, user_speech: str, agent_response: str, 
                            products_mentioned: str, response_time: int = 0):
        """Log voice interaction for analysis"""
        self.db.log_voice_interaction(
            self.session_id, 
            user_speech, 
            agent_response, 
            products_mentioned, 
            response_time
        ) 