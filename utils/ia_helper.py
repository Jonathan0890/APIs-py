import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def analizar_sentimiento(texto):
    response = openai.ChatCompletion.create(
        model="gpt-4",  # o "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "Eres un analista de sentimiento."},
            {"role": "user", "content": f"Analiza el sentimiento de esta reseña: {texto}"}
        ],
        temperature=0.5,
        max_tokens=100
    )
    return response.choices[0].message["content"].strip()

def analizar_sentimiento_resena(texto):
    prompt = f"Clasifica el siguiente comentario como Positivo, Negativo o Neutral:\n\n\"{texto}\""

    respuesta = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres un asistente que clasifica opiniones."},
            {"role": "user", "content": prompt}
        ]
    )

    contenido = respuesta['choices'][0]['message']['content'].strip()
    return contenido