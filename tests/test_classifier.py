from code_challenge.classifier import DEFAULT_CATEGORY, classify_transaction


def test_classifica_por_palavras_chave() -> None:
    assert classify_transaction("Starbucks Coffee") == "Food"
    assert classify_transaction("NETFLIX MONTHLY") == "Subscription"
    assert classify_transaction("Compra no Walmart") == "Shopping"


def test_retorna_uncategorized_quando_nao_encontra_regra() -> None:
    assert classify_transaction("Pagamento desconhecido") == DEFAULT_CATEGORY
    assert classify_transaction("   ") == DEFAULT_CATEGORY


def test_respeita_ordem_customizada_de_categorias() -> None:
    # Descricao contem termos de duas categorias; a ordem define prioridade.
    description = "Assinatura Spotify no Amazon Prime"
    assert classify_transaction(description) == "Subscription"
    assert classify_transaction(description, categories_order=("Shopping", "Subscription")) == "Shopping"
