from code_challenge.graph import TransactionGraph, execute_classification_graph


def test_grafo_evitar_duplicacao_de_nos_e_arestas() -> None:
    graph = TransactionGraph()
    graph.add_node("input")
    graph.add_node("input")
    graph.add_edge("input", "classify")
    graph.add_edge("input", "classify")

    assert graph.ordered_nodes() == ("input", "classify")
    assert graph.edges() == (("input", "classify"),)


def test_fluxo_principal_de_classificacao_em_grafo() -> None:
    result = execute_classification_graph(
        descriptions=["Starbucks Coffee", "Pagamento sem regra", "Spotify Family"],
    )

    assert result.ordered_nodes == ("input", "classify", "output")
    assert result.edges == (("input", "classify"), ("classify", "output"))
    assert [item.category for item in result.transactions] == ["Food", "Uncategorized", "Subscription"]
    assert [item.description for item in result.transactions] == [
        "Starbucks Coffee",
        "Pagamento sem regra",
        "Spotify Family",
    ]
