import pandas as pd
import openai
import os
from dotenv import load_dotenv
from tqdm import tqdm

# Carrega API Key do .env
load_dotenv()

openai.api_key = ""

# === PARTE 1: GERAÇÃO DE CRITÉRIOS ===

matches_df = pd.read_csv("match_resultados_rag.csv")
user_stories = matches_df[['user_story_id', 'user_story']].drop_duplicates()
criterios_gerados = []

for _, row in tqdm(user_stories.iterrows(), total=len(user_stories)):
    us_id = row['user_story_id']
    us_texto = row['user_story']

    issues_relacionadas = matches_df[(matches_df['user_story_id'] == us_id) & (matches_df['match'] == True)]
    contexto_issues = "\n".join(issues_relacionadas['issue_titulo'].tolist())

    prompt = f"""
Você é um analista de requisitos. Dada a user story e as issues relacionadas, gere critérios de aceitação claros e testáveis.

User Story:
{us_texto}

Issues relacionadas:
{contexto_issues if contexto_issues else 'Nenhuma'}

Gere os critérios de aceitação em bullets:
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        criterios = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        criterios = f"[Erro ao gerar critérios: {str(e)}]"

    criterios_gerados.append({
        "user_story_id": us_id,
        "user_story": us_texto,
        "criterios_gerados": criterios
    })

criterios_df = pd.DataFrame(criterios_gerados)
criterios_df.to_csv("criterios_gerados.csv", index=False)
print("✅ Critérios gerados salvos em criterios_gerados.csv")

# === PARTE 2: COMPARAÇÃO COM CRITÉRIOS ORIGINAIS ===

# Carrega base original com critérios existentes
original_df = pd.read_csv("User-storiese--commerce.csv")

# Junta com os critérios gerados com base no ID da user story
comparacao_df = criterios_df.merge(
    original_df,
    left_on="user_story_id",
    right_on="ID",
    how="left"
)

resultados = []

for _, row in tqdm(comparacao_df.iterrows(), total=len(comparacao_df)):
    criterios_gerados = row['criterios_gerados']
    criterios_originais = row['Acceptance Criteria']

    # Se não há critério original, pula
    if pd.isna(criterios_originais) or not criterios_originais.strip():
        comparacao = "Sem critério original para comparar"
    else:
        # Prompt para comparar os critérios
        prompt_comp = f"""
Compare os critérios gerados com os critérios originais abaixo. Avalie se os gerados cobrem os originais.

Critérios gerados:
{criterios_gerados}

Critérios originais:
{criterios_originais}

Responda apenas com: 'Sim', 'Parcialmente' ou 'Não'.
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt_comp}],
                temperature=0
            )
            comparacao = response['choices'][0]['message']['content'].strip().split('\n')[0]
        except Exception as e:
            comparacao = f"Erro na comparação: {str(e)}"

    resultados.append({
        "user_story_id": row["user_story_id"],
        "user_story": row["user_story"],
        "criterios_gerados": criterios_gerados,
        "criterios_originais": criterios_originais,
        "comparacao": comparacao
    })

pd.DataFrame(resultados).to_csv("comparacao_criterios.csv", index=False)
print("✅ Comparações salvas em comparacao_criterios.csv")
