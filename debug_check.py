from app.agent.graph import build_graph
from app.agent.nodes.intake import intake
from app.agent.nodes.plan import plan
from app.agent.nodes.permission_check import permission_check
from app.approval.queue import ApprovalQueue
from app.permissions.roles import UserRole
from app.tools.setup import build_default_registry


def fake_llm(prompt):
    return '{"tool": "calculator", "input": {"expression": "2 + 2"}, "reasoning": "test"}'


registry = build_default_registry()
queue = ApprovalQueue()
state = intake("What is 2+2?", UserRole.VIEWER)
state = plan(state, registry, llm_call=fake_llm)
state = permission_check(state)
print("BEFORE INVOKE:", state)

compiled = build_graph(registry, queue)
result = compiled.invoke(state, config={"configurable": {"thread_id": "debug-1"}})
print("AFTER INVOKE:", result)