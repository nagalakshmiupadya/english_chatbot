from flask import Flask, request, jsonify
from google import generativeai as genai
from dotenv import load_dotenv
from flask_cors import CORS
import os

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)
app = Flask(__name__)
CORS(app)

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

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_input = data.get("message", "").strip()
        
        # Check predefined responses first
        if user_input in PREDEFINED_RESPONSES:
            response_data = PREDEFINED_RESPONSES[user_input]
            # Ensure double line breaks between points
            response_data["response"] = response_data["response"].replace("\n", "\n\n")
            return jsonify(response_data)

        # Use Gemini model for non-predefined responses
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        
        context = """You are a Saree Mahal store assistant.
        Provide only 3-4 bullet points.
        Use '•' for bullet points.
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
        print(f"Error: {str(e)}")
        return jsonify({
            "response": "• Sorry, an error occurred\n\n• Please try again",
            "sub_options": [],
            "show_main_options": True
        })

if __name__ == "__main__":
    app.run(debug=True)