from github import Github
import pandas as pd

# Seu token pessoal

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

# Labels a excluir
labels_excluir = set([
    'cannot reproduce', 'duplicate', 'needs update',
    'invalid', 'refactoring', 'test'
])

# Conexão com GitHub
g = Github(GITHUB_TOKEN)

# Lista para armazenar os dados
dados_issues = []

for repo_full_name in repos:
    repo = g.get_repo(repo_full_name)
    issues = repo.get_issues(state='closed')  # apenas fechadas

    count_total = 0
    count_filtradas = 0

    for issue in issues:
        # Ignorar pull requests
        if issue.pull_request:
            continue

        count_total += 1

        # Verifica se a issue possui labels indesejadas
        issue_labels = set(label.name.lower() for label in issue.labels)
        if labels_excluir & issue_labels:
            continue

        count_filtradas += 1

        # Adiciona os dados
        dados_issues.append({
            'repositório': repo_full_name,
            'título': issue.title,
            'descrição': issue.body or "",
            'labels': ', '.join(label.name for label in issue.labels)
        })

        # Pega no máximo 6 issues válidas por repositório
        if count_filtradas >= 6:
            break

    print(f'✅ {repo_full_name}: {count_filtradas} issues coletadas (de {count_total} analisadas)')

# Salvar em CSV
df = pd.DataFrame(dados_issues)
df.to_csv("issues_filtradas.csv", index=False, encoding='utf-8-sig')
print("\n📁 Arquivo 'issues_filtradas.csv' salvo com sucesso.")
