import pandas as pd
from sentence_transformers import SentenceTransformer, util

# Carrega o modelo de embeddings (você pode trocar por outro, como all-MiniLM, etc)
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Carrega as issues a partir do CSV
issues_df = pd.read_csv('issues_filtradas.csv')

# Exemplo: lista de user stories (ou carregue de um CSV também)
# user_stories = [
#     "Como cliente, quero poder aplicar cupons de desconto no checkout",
#     "Como administrador, desejo ver um relatório de vendas por mês",
#     "Como usuário, quero poder resetar minha senha por email",
#     "Como cliente, quero adicionar produtos ao carrinho rapidamente",
# ]

user_stories_df = pd.read_csv('userstories.csv', sep=';')
user_stories = user_stories_df['Connextra'].tolist()

# Embeddings das user stories
story_embeddings = model.encode(user_stories, convert_to_tensor=True)

# Processar cada issue
resultados = []

for idx, row in issues_df.iterrows():
    issue_texto = f"{row['título']}. {row['descrição']}"
    issue_embedding = model.encode(issue_texto, convert_to_tensor=True)

    # Calcula a similaridade com todas as user stories
    scores = util.cos_sim(issue_embedding, story_embeddings)[0]

    # Seleciona a melhor user story
    melhor_idx = scores.argmax().item()
    melhor_score = scores[melhor_idx].item()
    melhor_story = user_stories[melhor_idx]

    resultados.append({
        'repositório': row['repositório'],
        'título': row['título'],
        'user_story_match': melhor_story,
        'similaridade': round(melhor_score, 4)
    })

# Salva os resultados em CSV
resultados_df = pd.DataFrame(resultados)
resultados_df.to_csv("match_resultados.csv", index=False, encoding='utf-8-sig')

print("✅ Match concluído. Resultados salvos em 'match_resultados.csv'")
