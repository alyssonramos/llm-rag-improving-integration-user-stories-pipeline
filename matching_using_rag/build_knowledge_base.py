from github import Github
import pandas as pd
import time
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # Use variável de ambiente
if not GITHUB_TOKEN:
    print("⚠️ GITHUB_TOKEN não encontrado. Defina a variável de ambiente ou edite o script.")
    exit(1)

# Repositórios de e-commerce
repos = [
    'magento/magento2',
    'nopSolutions/nopCommerce', 
    'opencart/opencart',
    'PrestaShop/PrestaShop',
    'shopware/platform',
    'shopware/shopware',
    'woocommerce/woocommerce'
]

# Labels relevantes para user stories/features
labels_relevantes = {
    'feature', 'enhancement', 'user story', 'epic', 'story',
    'improvement', 'new feature', 'feature request', 'ui', 'ux',
    'frontend', 'backend', 'api', 'checkout', 'payment', 'cart',
    'login', 'authentication', 'admin', 'customer', 'order'
}

# Labels a excluir
labels_excluir = {
    'cannot reproduce', 'duplicate', 'needs update', 'invalid', 
    'refactoring', 'test', 'wontfix', 'question', 'help wanted',
    'good first issue', 'documentation', 'dependencies'
}

# Conexão com GitHub
g = Github(GITHUB_TOKEN)

# Listas para armazenar os dados
base_conhecimento = []

def adicionar_texto_base(fonte, repositorio, titulo, conteudo, categoria, metadata=None):
    """Adiciona um texto à base de conhecimento"""
    if conteudo and len(conteudo.strip()) > 20:  # Ignora textos muito curtos
        base_conhecimento.append({
            'fonte': fonte,
            'repositorio': repositorio,
            'titulo': titulo,
            'conteudo': conteudo.strip()[:2000],  # Limita tamanho
            'categoria': categoria,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        })

def extrair_issues_relevantes(repo, repo_name, max_issues=20):
    """Extrai issues relevantes para user stories"""
    print(f"📋 Coletando issues de {repo_name}...")
    
    try:
        # Pega issues fechadas recentes (últimos 2 anos)
        since_date = datetime.now() - timedelta(days=730)
        issues = repo.get_issues(
            state='closed', 
            since=since_date,
            sort='updated',
            direction='desc'
        )
        
        count = 0
        for issue in issues:
            if count >= max_issues:
                break
                
            # Ignora pull requests
            if issue.pull_request:
                continue
                
            # Verifica labels
            issue_labels = {label.name.lower() for label in issue.labels}
            
            # Pula se tem labels indesejadas
            if labels_excluir & issue_labels:
                continue
                
            # Prioriza issues com labels relevantes
            tem_label_relevante = bool(labels_relevantes & issue_labels)
            
            # Adiciona à base de conhecimento
            adicionar_texto_base(
                fonte='issue',
                repositorio=repo_name,
                titulo=issue.title,
                conteudo=f"Issue: {issue.title}\n\nDescrição: {issue.body or 'Sem descrição'}",
                categoria='issue_fechada',
                metadata={
                    'labels': list(issue_labels),
                    'numero': issue.number,
                    'relevante': tem_label_relevante,
                    'comentarios': issue.comments
                }
            )
            
            # Se a issue tem muitos comentários, pega alguns
            if issue.comments > 2:
                try:
                    comentarios = issue.get_comments()[:3]  # Primeiros 3 comentários
                    for i, comment in enumerate(comentarios):
                        if len(comment.body) > 50:
                            adicionar_texto_base(
                                fonte='comentario_issue',
                                repositorio=repo_name,
                                titulo=f"Comentário na issue #{issue.number}",
                                conteudo=comment.body,
                                categoria='comentario',
                                metadata={'issue_numero': issue.number}
                            )
                except:
                    pass
            
            count += 1
            
    except Exception as e:
        print(f"❌ Erro ao coletar issues de {repo_name}: {e}")

def extrair_pull_requests(repo, repo_name, max_prs=15):
    """Extrai Pull Requests com descrições relevantes"""
    print(f"🔀 Coletando PRs de {repo_name}...")
    
    try:
        # PRs fechados recentes
        since_date = datetime.now() - timedelta(days=365)
        prs = repo.get_pulls(
            state='closed',
            sort='updated',
            direction='desc'
        )
        
        count = 0
        for pr in prs:
            if count >= max_prs:
                break
                
            if pr.updated_at < since_date:
                continue
                
            # Só PRs com descrição significativa
            if pr.body and len(pr.body) > 100:
                adicionar_texto_base(
                    fonte='pull_request',
                    repositorio=repo_name,
                    titulo=pr.title,
                    conteudo=f"PR: {pr.title}\n\nDescrição: {pr.body}",
                    categoria='pull_request',
                    metadata={
                        'numero': pr.number,
                        'merged': pr.merged,
                        'additions': pr.additions,
                        'deletions': pr.deletions
                    }
                )
            
            count += 1
            
    except Exception as e:
        print(f"❌ Erro ao coletar PRs de {repo_name}: {e}")

def extrair_documentacao(repo, repo_name):
    """Extrai documentação relevante"""
    print(f"📚 Coletando documentação de {repo_name}...")
    
    arquivos_doc = ['README.md', 'CHANGELOG.md', 'CONTRIBUTING.md', 'docs/README.md']
    
    for arquivo in arquivos_doc:
        try:
            content = repo.get_contents(arquivo)
            if content.size < 50000:  # Evita arquivos muito grandes
                texto = content.decoded_content.decode('utf-8')
                adicionar_texto_base(
                    fonte='documentacao',
                    repositorio=repo_name,
                    titulo=f"Documentação: {arquivo}",
                    conteudo=texto[:2000],  # Primeiros 2000 caracteres
                    categoria='documentacao',
                    metadata={'arquivo': arquivo, 'tamanho': content.size}
                )
        except:
            continue  # Arquivo não existe

def extrair_releases(repo, repo_name, max_releases=5):
    """Extrai notas de release"""
    print(f"🚀 Coletando releases de {repo_name}...")
    
    try:
        releases = repo.get_releases()[:max_releases]
        
        for release in releases:
            if release.body and len(release.body) > 50:
                adicionar_texto_base(
                    fonte='release',
                    repositorio=repo_name,
                    titulo=f"Release {release.tag_name}",
                    conteudo=f"Release: {release.name}\n\nNotas: {release.body}",
                    categoria='release_notes',
                    metadata={
                        'tag': release.tag_name,
                        'data': release.published_at.isoformat() if release.published_at else None
                    }
                )
                
    except Exception as e:
        print(f"❌ Erro ao coletar releases de {repo_name}: {e}")

def main():
    print("🤖 Iniciando extração da base de conhecimento...")
    print(f"📊 Repositórios: {len(repos)}")
    
    for i, repo_name in enumerate(repos, 1):
        print(f"\n[{i}/{len(repos)}] Processando {repo_name}...")
        
        try:
            repo = g.get_repo(repo_name)
            
            # Extrai diferentes tipos de conteúdo
            extrair_issues_relevantes(repo, repo_name)
            extrair_pull_requests(repo, repo_name)
            extrair_documentacao(repo, repo_name)
            extrair_releases(repo, repo_name)
            
            # Pausa para evitar rate limit
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Erro ao processar {repo_name}: {e}")
            continue
    
    # Salva a base de conhecimento
    if base_conhecimento:
        df = pd.DataFrame(base_conhecimento)
        df.to_csv("base_conhecimento.csv", index=False, encoding='utf-8-sig')
        
        # Estatísticas
        print(f"\n✅ Base de conhecimento criada com sucesso!")
        print(f"📈 Total de entradas: {len(base_conhecimento)}")
        print(f"📊 Por categoria:")
        for categoria in df['categoria'].value_counts().items():
            print(f"   - {categoria[0]}: {categoria[1]} entradas")
        print(f"📁 Arquivo salvo: base_conhecimento.csv")
        
        # Cria também um arquivo de texto simples para embeddings
        with open("base_conhecimento.txt", "w", encoding="utf-8") as f:
            for entrada in base_conhecimento:
                f.write(f"{entrada['titulo']}\n{entrada['conteudo']}\n\n---\n\n")
        print(f"📁 Arquivo texto salvo: base_conhecimento.txt")
        
    else:
        print("❌ Nenhum conteúdo foi extraído.")

if __name__ == "__main__":
    main()