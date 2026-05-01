from agents.llm_explainer_agent.skills.llm_explainer_skill import LLMExplainerSkill


class LLMExplainerAgent:
    """
    Agent wrapper for LLM-based explanations.
    """

    def __init__(self):
        self.skill = LLMExplainerSkill()

    def explain_comparison(self, comparison_metrics):
        return self.skill.explain_comparison(comparison_metrics)
