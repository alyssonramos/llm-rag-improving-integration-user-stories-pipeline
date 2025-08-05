import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Exemplo de avaliação simples de um critério de aceitação
def avaliar_criterio(criterio, descricao_user_story):
    prompt = f"""
    A seguir está uma user story e um critério de aceitação.
    Avalie se o critério está de acordo com a user story.
    
    User Story:
    {descricao_user_story}

    Critério de Aceitação:
    {criterio}

    Responda apenas com 'Sim' ou 'Não' e uma justificativa de no máximo 2 frases.
    """
    resposta = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return resposta.choices[0].message["content"]

# Exemplo de uso:
descricao = "Como comprador, eu quero receber um e-mail de confirmação após a compra, para saber que foi finalizada com sucesso."
criterio = "O sistema não deve sinalizar para o usuario que a compra foi finalizada."

resultado = avaliar_criterio(criterio, descricao)
print("Avaliação:", resultado)
