import json
import faiss
import numpy as np
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime

# Carrega variáveis de ambiente
load_dotenv()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Função para criar embeddings
def get_embeddings(texts, model="text-embedding-3-small"):
    embeddings = []
    for text in texts:
        response = client.embeddings.create(model=model, input=text)
        embeddings.append(response.data[0].embedding)
    return np.array(embeddings).astype("float32")

# Carrega critérios BDD existentes
with open("criteria_bdd.json", "r", encoding="utf-8") as f:
    criteria = json.load(f)

# Gera embeddings e cria índice FAISS
embeddings = get_embeddings(criteria)
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# Recebe novo critério BDD
novo_criterio = input("Digite o novo critério de aceitação (formato BDD): ")

# Busca critérios semelhantes no índice
novo_embedding = get_embeddings([novo_criterio])
distances, indices = index.search(novo_embedding, k=5)

# Recupera critérios mais próximos
criterios_proximos = [criteria[i] for i in indices[0] if criteria[i] != novo_criterio]

# Monta prompt para análise de conflitos
prompt = f"""
Você é um assistente para análise de critérios de aceitação no formato BDD.
Seu trabalho é comparar um critério novo com critérios existentes e classificá-los em:

- Duplicado: descreve exatamente a mesma funcionalidade ou comportamento, sem diferenças importantes.
- Conflitante: descreve um comportamento oposto ou incompatível com o critério novo.
- Complementar: está relacionado e acrescenta detalhes ou condições, mas não é igual nem conflitante.
- Irrelevante: não está relacionado com o critério novo.

Considere que:

- Critérios duplicados indicam redundância e devem ser evitados.
- Critérios conflitantes indicam problemas que precisam ser resolvidos.
- Critérios complementares enriquecem o entendimento e podem coexistir.
- Critérios irrelevantes não devem ser considerados para duplicação ou conflito.

Dado o critério novo e uma lista de critérios existentes, classifique cada um e explique brevemente o motivo.

Critério novo:
"{novo_criterio}"

Critérios existentes:
{json.dumps(criterios_proximos, indent=2, ensure_ascii=False)}

Explique brevemente o motivo de cada classificação.
"""

# Chama o LLM
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Você é um analista de QA experiente em metodologias ágeis."},
        {"role": "user", "content": prompt}
    ]
)

# Resultado da análise
analise = response.choices[0].message.content

# Mostra resultado no console
print("\n🔍 Análise de conflitos entre critérios BDD:")
print(analise)

# Salva relatório em Markdown
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
nome_arquivo = f"relatorio_analise_{timestamp}.md"

with open(nome_arquivo, "w", encoding="utf-8") as f:
    f.write(f"# Relatório de Análise de Critério BDD\n\n")
    f.write(f"**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
    f.write(f"## Critério analisado:\n")
    f.write(f"> {novo_criterio}\n\n")
    f.write(f"## Critérios semelhantes encontrados:\n")
    for c in criterios_proximos:
        f.write(f"- {c}\n")
    f.write(f"\n## Resultado da análise do LLM:\n")
    f.write(analise)
    f.write("\n")

print(f"\n✅ Relatório salvo em: {nome_arquivo}")
