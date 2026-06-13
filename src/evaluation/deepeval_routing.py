import os

from evaluation.routing_cases import build_routing_cases


def build_deepeval_cases():
    from deepeval.test_case import LLMTestCase, ToolCall

    cases = []
    for case in build_routing_cases():
        cases.append(
            LLMTestCase(
                name=case.name,
                input=case.question,
                actual_output=case.expected_answer_hint,
                tools_called=[ToolCall(name=name) for name in case.expected_tools],
                expected_tools=[ToolCall(name=name) for name in case.expected_tools],
            )
        )
    return cases


def run_routing_evaluation() -> None:
    from deepeval import evaluate
    from deepeval.metrics import ToolCorrectnessMetric
    from deepeval.models import AnthropicModel

    model_id = os.getenv("SHOPAGENT_EVAL_MODEL", os.getenv("SHOPAGENT_MODEL", "claude-sonnet-4-6"))
    metric = ToolCorrectnessMetric(threshold=1.0, model=AnthropicModel(model=model_id))
    evaluate(test_cases=build_deepeval_cases(), metrics=[metric])


if __name__ == "__main__":
    run_routing_evaluation()
