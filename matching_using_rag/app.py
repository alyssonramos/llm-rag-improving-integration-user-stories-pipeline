import openai
from dotenv import load_dotenv
import os
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import torch
import pickle

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do modelo e OpenAI
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    print("⚠️ OPENAI_API_KEY não encontrada. Defina a variável de ambiente.")
    exit(1)

def busca_na_base(textos_para_busca, base_conhecimento, base_embeddings, top_k=3):
    # Junta os textos de busca (issue + user story)
    consulta = " ".join(textos_para_busca)
    consulta_embedding = model.encode(consulta, convert_to_tensor=True)
    # Calcula similaridade com todos os textos da base
    scores = util.cos_sim(consulta_embedding, base_embeddings)[0]
    # Pega os índices dos top_k mais similares
    top_indices = scores.argsort(descending=True)[:top_k]
    # Retorna os textos mais relevantes
    return [base_conhecimento[i] for i in top_indices]

def recuperar_contexto(issue, user_story, base_conhecimento, base_embeddings, top_k=3):
    """Recupera contexto relevante da base de conhecimento usando RAG"""
    textos_para_busca = [issue, user_story]
    trechos_relevantes = busca_na_base(textos_para_busca, base_conhecimento, base_embeddings, top_k)
    return "\n".join(trechos_relevantes)

def julgar_match_rag(issue, user_story, base_conhecimento, base_embeddings):
    """Julga se há match entre issue e user story usando RAG"""
    contexto = recuperar_contexto(issue, user_story, base_conhecimento, base_embeddings)
    
    prompt = f"""
    Contexto:
    {contexto}

    Issue:
    {issue}

    User Story:
    {user_story}

    Pergunta: Baseado no contexto fornecido, a issue afeta a funcionalidade e o papel cobertos pela user story? 
    Considere se elas tratam do mesmo domínio, funcionalidade ou componente do sistema.
    Responda apenas "yes" ou "no".
    """
    
    try:
        # Usando a nova API do OpenAI
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=10
        )
        resultado = resposta.choices[0].message.content.strip().lower()
        return resultado == "yes"
    except Exception as e:
        print(f"❌ Erro na chamada da API: {e}")
        return False

def carregar_base_conhecimento():
    """Carrega a base de conhecimento e cria embeddings"""
    print("📚 Carregando base de conhecimento...")
    
    # Verifica se o arquivo existe
    if not os.path.exists('base_conhecimento.csv'):
        print("❌ Arquivo base_conhecimento.csv não encontrado.")
        print("   Execute primeiro o build_knowledge_base.py para criar a base.")
        exit(1)
    
    # Carrega a base
    df_base = pd.read_csv('base_conhecimento.csv')
    print(f"✅ Base carregada: {len(df_base)} entradas")
    
    # Prepara textos para embeddings
    textos_base = []
    for _, row in df_base.iterrows():
        texto = f"{row['titulo']} {row['conteudo']}"
        textos_base.append(texto)
    
    # Verifica se já existem embeddings salvos
    embeddings_file = 'base_embeddings.pkl'
    if os.path.exists(embeddings_file):
        print("📥 Carregando embeddings salvos...")
        with open(embeddings_file, 'rb') as f:
            base_embeddings = pickle.load(f)
    else:
        print("🔄 Criando embeddings da base de conhecimento...")
        base_embeddings = model.encode(textos_base, convert_to_tensor=True)
        
        # Salva os embeddings
        with open(embeddings_file, 'wb') as f:
            pickle.dump(base_embeddings, f)
        print("💾 Embeddings salvos para uso futuro")
    
    return textos_base, base_embeddings

def main():
    print("🚀 Iniciando matching com RAG...")
    
    # Carrega a base de conhecimento
    base_conhecimento, base_embeddings = carregar_base_conhecimento()
    
    # Carrega issues e user stories
    print("📋 Carregando issues e user stories...")
    issues_df = pd.read_csv('issues_filtradas.csv')
    user_stories_df = pd.read_csv('userstories.csv', sep=';')
    user_stories = user_stories_df['Connextra'].tolist()
    
    print(f"📊 {len(issues_df)} issues e {len(user_stories)} user stories para processar")
    
    # Lista para armazenar resultados
    resultados = []
    total_comparacoes = len(issues_df) * len(user_stories)
    
    # Processa cada combinação
    for i, user_story in enumerate(user_stories):
        print(f"\n📝 Processando User Story {i+1}/{len(user_stories)}")
        
        for j, (_, issue_row) in enumerate(issues_df.iterrows()):
            # comparacao_atual += 1
            issue_texto = f"{issue_row['título']}. {issue_row['descrição']}"
            
            # Faz o julgamento usando RAG
            resultado = julgar_match_rag(issue_texto, user_story, base_conhecimento, base_embeddings)
            
            # Armazena resultado
            resultados.append({
                'issue_id': j,
                'user_story_id': i,
                'issue_titulo': issue_row['título'],
                'user_story': user_story,
                'match': resultado
            })
            
            
    # Salva resultados
    df_resultados = pd.DataFrame(resultados)
    df_resultados.to_csv('match_resultados_rag.csv', index=False)
    
    # Estatísticas
    matches_encontrados = df_resultados['match'].sum()
    print(f"\n✅ Processamento concluído!")
    print(f"📊 Total de comparações: {total_comparacoes}")
    print(f"🎯 Matches encontrados: {matches_encontrados}")
    print(f"📈 Taxa de match: {matches_encontrados/total_comparacoes*100:.2f}%")
    print(f"💾 Resultados salvos em: match_resultados_rag.csv")

if __name__ == "__main__":
    main()