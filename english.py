import os
from dotenv import load_dotenv
from flask import Flask,render_template,request, jsonify
from flask_cors import CORS
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Get API key with fallback
API_KEY = os.environ.get('GEMINI_API_KEY')
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Configure Gemini
genai.configure(api_key=API_KEY)

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('english.html')  
CORS(app, resources={
    r"/chat": {
        "origins": ["*"],
        "methods": ["POST"],
        "allow_headers": ["Content-Type"]
    }
})

# Predefined responses with options and sub-options
PREDEFINED_RESPONSES = {
    "Explore the saris available on the website": {
        "response": """• Wide range of traditional sarees at **Saree Mahal**
• Prices start from ₹999 onwards
• Special festive discounts available""",
        "sub_options": [
            "Special Collection Available",
            "Festive Offers and Deals",
            "Saree Discount (Sale of Clearance)"
        ]
    },
    "Special Collection Available": {
        "response": """• Designer silk sarees starting from ₹15,000
• Exclusive bridal collection with intricate work
• Limited edition festival wear sarees""",
        "sub_options": []
    },
    "Available Saree Types": {
        "response": """• **Saree Mahal** offers various types including:
• Silk, Cotton, Zari, and Polyester sarees
• All sizes and designs available
• Custom stitching options available""",
        "sub_options": [
            "Silk saree (price range is available)",
            "Cotton saree (price range is available)",
            "Zari saree (price range is available)",
            "Polister saree (price range is available)"
        ]
    },
    "Silk saree (price range is available)": {
        "response": """• Price range: ₹5,000 - ₹50,000
• Available colors: Purple, Red, Green, Blue
• Special offer: 20% discount""",
        "sub_options": []
    },
    "Delivery and Return Policy": {
        "response": """• **Saree Mahal** offers free delivery on orders above ₹999
• Easy 7-day return policy
• Fast shipping across India""",
        "sub_options": [
            "Shipping Available Places",
            "Return Policy"
        ]
    },
    "Customer Support": {
        "response": """• Phone: +91 8123040488
• Time: 10 AM - 8 PM
• Email: nithin.vs@ka-naada.com""",
        "sub_options": []
    }
    
}

# Improve error handling in chat route
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        if not data:
            return jsonify({
                "response": "• Invalid request format",
                "sub_options": [],
                "show_main_options": True
            }), 400

        user_input = data.get("message", "").strip()
        if not user_input:
            return jsonify({
                "response": "• Please enter a message",
                "sub_options": [],
                "show_main_options": True
            }), 400
        
        # Check predefined responses first
        if user_input in PREDEFINED_RESPONSES:
            response_data = PREDEFINED_RESPONSES[user_input]
            # Ensure double line breaks between points
            response_data["response"] = response_data["response"].replace("\n", "\n\n")
            return jsonify(response_data)

        # Use Gemini model for non-predefined responses
        model = genai.GenerativeModel('gemini-2.0-flash-lite', 
            generation_config={
                'temperature': 0.7,
                'top_p': 0.8,
                'top_k': 40
            },
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ])

        # Update the context to force English responses
        context = """You are a Saree Mahal store assistant.
IMPORTANT: Always respond in English only.
Provide exactly 3-4 bullet points.
Use '•' for bullet points.
Keep responses short and focused on sarees and store information.
Add line breaks between points.

Question: """ + user_input

        response = model.generate_content(context)
        
        if not response.text:
            return jsonify({
                "response": "• Please ask about our sarees or store services",
                "sub_options": [],
                "show_main_options": True
            })

        # Improved response formatting with double line breaks
        formatted_lines = []
        for line in response.text.split('\n'):
            line = line.strip()
            if line and not line.startswith('Role:') and not line.startswith('Task:'):
                if not line.startswith('•'):
                    line = f"• {line}"
                formatted_lines.append(line)
        
        # Join with double line breaks
        formatted_response = "\n".join(formatted_lines[:4])
        
        return jsonify({
            "response": formatted_response.replace("Saree Mahal", "**Saree Mahal**"),
            "sub_options": [],
            "show_main_options": True
        })

    except Exception as e:
        print(f"Error details: {str(e)}")  # Add detailed error logging
        return jsonify({
            "response": """• Sorry, an error occurred
• Please check your internet connection
• Try refreshing the page""",
            "sub_options": [],
            "show_main_options": True
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


