import logging
import uuid
from typing import List, Dict, Any, Optional
from medical_database import MedicalProductDatabase
import autogen
from autogen import AssistantAgent, UserProxyAgent
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MedicalToolsAgentSystem:
    """Medical AI system with dynamic tool selection based on user queries"""
    
    def __init__(self, groq_api_key: str, db_path: str = "medical_products.db"):
        logger.info("Initializing MedicalToolsAgentSystem...")
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
                    "model": "llama3-8b-8192",
                    "api_key": groq_api_key,
                    "base_url": "https://api.groq.com/openai/v1"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 10000,
        }
        
        logger.info(f"LLM Config: {self.llm_config}")
        self.setup_tools_and_agents()
        logger.info("MedicalToolsAgentSystem initialization complete!")
    
    def setup_tools_and_agents(self):
        """Setup tools and agents with dynamic tool selection"""
        logger.info("Setting up tools and agents...")
        
        # Define available tools
        self.tools = {
            "search_medical_products": {
                "description": "Search for medical products in the database. Use when user asks about finding medications, drugs, or medical products.",
                "function": self.search_medical_products_tool,
                "parameters": {
                    "query": "string - The search query for medical products",
                    "category": "string (optional) - Filter by category like 'Pain Relief', 'Blood Pressure'",
                    "prescription_only": "boolean (optional) - Filter for prescription-only medications"
                }
            },
            "get_product_details": {
                "description": "Get detailed information about a specific medical product. Use when user asks for detailed info about a specific medication.",
                "function": self.get_product_details_tool,
                "parameters": {
                    "product_name": "string - The name of the medical product"
                }
            },
            "calculate_dosage": {
                "description": "Calculate appropriate dosage for a medication. Use when user asks about dosing, dosage, or how much to take.",
                "function": self.calculate_dosage_tool,
                "parameters": {
                    "product_name": "string - The name of the medication",
                    "patient_age": "integer - Patient age in years",
                    "patient_weight": "float - Patient weight in kg",
                    "medical_conditions": "string (optional) - Any medical conditions"
                }
            },
            "check_safety": {
                "description": "Check safety information for a medication. Use when user asks about side effects, warnings, safety, or drug interactions.",
                "function": self.check_safety_tool,
                "parameters": {
                    "product_name": "string - The name of the medication",
                    "patient_conditions": "string (optional) - Patient medical conditions",
                    "allergies": "string (optional) - Patient allergies",
                    "other_medications": "string (optional) - Other medications being taken"
                }
            },
            "check_insurance_coverage": {
                "description": "Check insurance coverage for medications. Use when user asks about insurance, coverage, cost, or pricing.",
                "function": self.check_insurance_coverage_tool,
                "parameters": {
                    "product_name": "string - The name of the medication",
                    "insurance_type": "string (optional) - Type of insurance"
                }
            },
            "find_alternatives": {
                "description": "Find alternative medications. Use when user asks for alternatives, substitutes, or different options.",
                "function": self.find_alternatives_tool,
                "parameters": {
                    "product_name": "string - The name of the medication",
                    "reason": "string (optional) - Reason for seeking alternatives (cost, side effects, etc.)"
                }
            },
            "general_medical_advice": {
                "description": "Provide general medical information and advice. Use when user asks general health questions not requiring database lookup.",
                "function": self.general_medical_advice_tool,
                "parameters": {
                    "query": "string - The general medical question or topic"
                }
            }
        }
        
        # Create the main medical agent with tool access
        logger.info("Creating MedicalAgent with tools...")
        self.medical_agent = AssistantAgent(
            name="MedicalAgent",
            system_message=f"""You are a comprehensive medical AI assistant with access to a medical products database and various tools.\n\nAvailable Tools:\n{self._format_tools_for_system_message()}\n\nYour responsibilities:\n1. Analyze user queries to determine which tools to use\n2. Use database tools when user asks about specific medications, products, or medical data\n3. Use general advice tool for health questions not requiring database lookup\n4. Provide accurate, helpful, and safe medical information\n5. Always emphasize consulting healthcare professionals for medical decisions\n\nGuidelines:\n- For medication searches, use search_medical_products tool\n- For detailed product info, use get_product_details tool\n- For dosage questions, use calculate_dosage tool\n- For safety concerns, use check_safety tool\n- For insurance/cost questions, use check_insurance_coverage tool\n- For alternatives, use find_alternatives tool\n- For general health advice, use general_medical_advice tool\n\n**When returning results from a database/tool, always present them in clear, natural, conversational language. Summarize and explain the results as if you are talking to a patient or a doctor. Do not use tables or raw data dumps unless the user specifically asks for them.**\n\nAlways format responses clearly and include important safety warnings when discussing medications.always give answer in a conversational mannera nd it should be easy to understand to user """,
            llm_config=self.llm_config
        )
        
        # Create user proxy agent
        logger.info("Creating UserProxyAgent...")
        self.user_proxy = UserProxyAgent(
            name="User",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            llm_config=self.llm_config,
            code_execution_config={"use_docker": False}
        )
        
        logger.info("All tools and agents setup complete!")
    
    def _format_tools_for_system_message(self) -> str:
        """Format tools for system message"""
        tools_text = ""
        for tool_name, tool_info in self.tools.items():
            tools_text += f"- {tool_name}: {tool_info['description']}\n"
        return tools_text
    
    def process_user_query(self, user_query: str) -> str:
        """Process user query using dynamic tool selection"""
        logger.info(f"Processing user query: '{user_query}'")
        
        try:
            # Check if medical agent is available
            if not hasattr(self, 'medical_agent') or self.medical_agent is None:
                logger.warning("Medical agent not available, using fallback")
                return self._fallback_response(user_query)
            
            # Create a conversation to determine which tools to use
            chat_history = [
                {
                    "role": "user",
                    "content": f"""Analyze this user query and determine which tool(s) to use:

User Query: "{user_query}"

Available tools:
{self._format_tools_for_system_message()}

Respond with the tool name and parameters in this format:
TOOL: tool_name
PARAMETERS: {{"param1": "value1", "param2": "value2"}}

If multiple tools are needed, list them in order of priority."""
                }
            ]
            
            # Get tool selection from LLM
            response = self.medical_agent.generate_reply(
                messages=chat_history,
                sender=self.user_proxy
            )
            
            if response is None:
                logger.warning("LLM returned None response, using fallback")
                return self._fallback_response(user_query)
            
            logger.info(f"LLM tool selection response: {response}")
            
            # Parse tool selection and execute
            return self._execute_selected_tools(user_query, str(response))
            
        except Exception as e:
            logger.error(f"Error processing user query: {str(e)}")
            logger.info("Using fallback response due to error")
            return self._fallback_response(user_query)
    
    def _fallback_response(self, user_query: str) -> str:
        """Fallback response when LLM fails"""
        # Simple keyword-based tool selection
        query_lower = user_query.lower()
        
        if any(word in query_lower for word in ['find', 'search', 'look', 'medication', 'drug', 'medicine']):
            return self.search_medical_products_tool(user_query)
        elif any(word in query_lower for word in ['side effect', 'safety', 'warning', 'interaction']):
            # Extract product name from query
            words = query_lower.split()
            for word in words:
                if word in ['ibuprofen', 'acetaminophen', 'tylenol', 'advil']:
                    return self.check_safety_tool(word)
            return self.check_safety_tool("ibuprofen")  # Default example
        elif any(word in query_lower for word in ['dosage', 'dose', 'how much', 'take']):
            return self.calculate_dosage_tool("acetaminophen", 30, 70.0)
        else:
            return self.general_medical_advice_tool(user_query)
    
    def _execute_selected_tools(self, user_query: str, llm_response: str) -> str:
        """Execute tools based on LLM selection"""
        try:
            # Parse tool selections from LLM response
            tool_calls = self._parse_tool_selections(llm_response)
            
            if not tool_calls:
                # Fallback to general advice if no tools selected
                logger.info("No specific tools selected, using general advice")
                return self.general_medical_advice_tool(user_query)
            
            results = []
            for tool_call in tool_calls:
                tool_name = tool_call.get('tool')
                parameters = tool_call.get('parameters', {})
                
                if tool_name in self.tools:
                    logger.info(f"Executing tool: {tool_name} with parameters: {parameters}")
                    result = self.tools[tool_name]['function'](**parameters)
                    results.append(result)
                else:
                    logger.warning(f"Unknown tool: {tool_name}")
            
            # Combine results
            if len(results) == 1:
                return results[0]
            else:
                return "\n\n".join(results)
                
        except Exception as e:
            logger.error(f"Error executing tools: {str(e)}")
            return f"Error processing your request: {str(e)}"
    
    def _parse_tool_selections(self, llm_response: str) -> List[Dict]:
        """Parse tool selections from LLM response"""
        tool_calls = []
        
        # Look for TOOL: and PARAMETERS: patterns
        tool_pattern = r"TOOL:\s*(\w+)"
        param_pattern = r"PARAMETERS:\s*(\{.*?\})"
        
        tools = re.findall(tool_pattern, llm_response)
        params = re.findall(param_pattern, llm_response)
        
        for i, tool in enumerate(tools):
            tool_call = {"tool": tool, "parameters": {}}
            if i < len(params):
                try:
                    import json
                    tool_call["parameters"] = json.loads(params[i])
                except:
                    pass
            tool_calls.append(tool_call)
        
        return tool_calls
    
    # Tool implementations
    def search_medical_products_tool(self, query: str, category: Optional[str] = None, prescription_only: Optional[bool] = None) -> str:
        """Tool for searching medical products (returns list of dicts for LLM to summarize, or summary string for fallback/manual)"""
        logger.info(f"Searching medical products for query: '{query}'")
        try:
            filters = {}
            if category:
                filters['category'] = category
            if prescription_only is not None:
                filters['prescription_required'] = prescription_only
            products = self.db.search_products_advanced(query, filters)
            logger.info(f"Found {len(products)} products")
            if not products:
                return f"No medical products found matching '{query}'."
            # If called from fallback/manual, summarize in natural language
            import inspect
            stack = inspect.stack()
            if any('fallback' in frame.function for frame in stack):
                return self._summarize_products_naturally(products, query)
            # Otherwise, return as stringified list of dicts for LLM
            import json
            return json.dumps(products)
        except Exception as e:
            logger.error(f"Error searching medical products: {str(e)}")
            return f"Error searching medical products: {str(e)}"
    
    def _summarize_products_naturally(self, products, query):
        if not products:
            return "No products found."
        lines = [f"Here are some results for '{query}':"]
        for product in products[:5]:
            name = product.get('name', 'Unknown')
            brand = product.get('brand_name', 'Generic')
            cat = product.get('category', '')
            price = product.get('price', '')
            rx = 'prescription' if product.get('prescription_required') else 'over-the-counter'
            lines.append(f"- {name} ({brand}, {cat}): ${price}, {rx}.")
        if len(products) > 5:
            lines.append(f"...and {len(products)-5} more.")
        return '\n'.join(lines)
    
    def get_product_details_tool(self, product_name: str) -> str:
        """Tool for getting detailed product information"""
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
    
    def calculate_dosage_tool(self, product_name: str, patient_age: int, patient_weight: float, medical_conditions: str = "") -> str:
        """Tool for calculating dosage"""
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
    
    def check_safety_tool(self, product_name: str, patient_conditions: str = "", allergies: str = "", other_medications: str = "") -> str:
        """Tool for checking safety information"""
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
    
    def check_insurance_coverage_tool(self, product_name: str, insurance_type: str = "") -> str:
        """Tool for checking insurance coverage"""
        try:
            products = self.db.search_products_advanced(product_name)
            
            if not products:
                return f"Product '{product_name}' not found for coverage check."
            
            product = products[0]
            
            coverage_info = f"**Insurance Coverage for {product['name']}**\n\n"
            coverage_info += f"Product: {product['name']}\n"
            coverage_info += f"Brand Name: {product['brand_name']}\n"
            coverage_info += f"Generic Name: {product['generic_name']}\n"
            coverage_info += f"Price: ${product['price']}\n"
            coverage_info += f"Insurance Coverage: {product['insurance_coverage']}\n"
            
            if insurance_type:
                coverage_info += f"Insurance Type: {insurance_type}\n"
            
            coverage_info += f"\n**Coverage Notes:**\n"
            if product['prescription_required']:
                coverage_info += "• Prescription medication - may require prior authorization\n"
            else:
                coverage_info += "• Over-the-counter medication - typically not covered by insurance\n"
            
            coverage_info += "• Generic versions may have better coverage\n"
            coverage_info += "• Check with your specific insurance plan for exact coverage\n"
            
            return coverage_info
            
        except Exception as e:
            return f"Error checking insurance coverage: {str(e)}"
    
    def find_alternatives_tool(self, product_name: str, reason: str = "cost") -> str:
        """Tool for finding alternative medications"""
        try:
            products = self.db.search_products_advanced(product_name)
            
            if not products:
                return f"Product '{product_name}' not found for alternative search."
            
            product = products[0]
            
            alternatives = f"**Alternatives for {product['name']}**\n\n"
            alternatives += f"Original Product: {product['name']} ({product['brand_name']})\n"
            alternatives += f"Reason for seeking alternatives: {reason}\n\n"
            
            # Search for similar products
            similar_products = self.db.search_products_advanced(product['generic_name'])
            
            if similar_products:
                alternatives += "**Similar Products:**\n"
                for alt_product in similar_products[:3]:
                    if alt_product['name'] != product['name']:
                        alternatives += f"• {alt_product['name']} ({alt_product['brand_name']})\n"
                        alternatives += f"  Price: ${alt_product['price']}\n"
                        alternatives += f"  Coverage: {alt_product['insurance_coverage']}\n"
                        alternatives += "---\n"
            
            alternatives += "\n**General Alternatives:**\n"
            if "pain" in product['category'].lower():
                alternatives += "• Consider other pain relief options like acetaminophen or ibuprofen\n"
            if "blood pressure" in product['category'].lower():
                alternatives += "• Other blood pressure medications may be available\n"
            
            alternatives += "\n🏥 **CONSULT HEALTHCARE PROVIDER**: Always discuss alternatives with your doctor or pharmacist.\n"
            
            return alternatives
            
        except Exception as e:
            return f"Error finding alternatives: {str(e)}"
    
    def general_medical_advice_tool(self, query: str) -> str:
        """Tool for general medical advice"""
        return f"""I understand you're asking about: {query}

This appears to be a general health question that doesn't require specific medication database lookup. 

Here are some general guidelines:
• Always consult with healthcare professionals for medical advice
• Don't self-diagnose or self-treat serious conditions
• Keep track of your symptoms and medical history
• Follow prescribed treatment plans
• Maintain regular check-ups with your doctor

For specific medication information, drug interactions, or dosage questions, I can search our medical database. Would you like me to look up any specific medications or medical products?

🏥 **IMPORTANT**: This is general information only. Always consult with qualified healthcare professionals for medical advice and treatment.""" 