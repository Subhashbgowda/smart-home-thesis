from agents.llm_explainer_agent.llm_explainer_agent import LLMExplainerAgent

example_metrics = {
    "rule": {
        "avg_consumption": 0.508,
        "peak_consumption": 3.117,
        "avg_cost": 0.0659,
        "total_cost": 58.86
    },
    "ml": {
        "avg_consumption": 0.533,
        "peak_consumption": 3.016,
        "avg_cost": 0.0203,
        "total_cost": 5.74
    }
}

agent = LLMExplainerAgent()
result = agent.explain_comparison(example_metrics)

print("\n--- LLM EXPLANATION ---\n")
print(result)
