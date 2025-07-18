from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    ingredients = request.form['ingredients']
    dietary = request.form['dietary']
    cuisine = request.form['cuisine']

    prompt = f"""
    You are a professional chef. Create a detailed and original recipe based on the following:

    - Ingredients: {ingredients}
    - Dietary Restrictions: {dietary}
    - Cuisine: {cuisine}

    Include:
    1. A Recipe Title
    2. Total Prep and Cook Time
    3. A full list of ingredients with exact measurements
    4. At least 5 clear step-by-step instructions
    5. Serving suggestions
    6. Tips or substitutions if available

    Format it in plain text with clear section headings.
    """

    try:
        # Get recipe from ChatGPT
        chat_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1200  # Increased token limit
        )
        recipe_text = chat_response.choices[0].message.content

        # Generate image with DALL·E
        image_prompt = f"High quality food photo of {cuisine} cuisine using {ingredients}"
        image_response = client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        image_url = image_response.data[0].url

        return jsonify({"recipe": recipe_text, "image_url": image_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
