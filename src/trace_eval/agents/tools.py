from __future__ import annotations
import ast, operator as op
from typing import Any, Dict
from trace_eval.domain.primitives import EventCategory
from trace_eval.agents.base import ToolSpec
class ToolContext:
    def __init__(self):
        self.memory: Dict[str,str] = {}
        self.environment = {"delivery_days": 3, "budget": 1000, "status": "normal"}
        self.fail_once = True
def _calc(expression: str) -> float:
    ops={ast.Add:op.add,ast.Sub:op.sub,ast.Mult:op.mul,ast.Div:op.truediv,ast.Pow:op.pow,ast.Mod:op.mod,ast.USub:op.neg}
    def ev(n):
        if isinstance(n,ast.Constant) and isinstance(n.value,(int,float)): return float(n.value)
        if isinstance(n,ast.UnaryOp) and type(n.op) in ops: return ops[type(n.op)](ev(n.operand))
        if isinstance(n,ast.BinOp) and type(n.op) in ops: return ops[type(n.op)](ev(n.left),ev(n.right))
        raise ValueError("Unsupported expression")
    return ev(ast.parse(expression,mode="eval").body)
def build_tools(ctx: ToolContext, enabled: list[str]) -> list[ToolSpec]:
    out=[]
    if "plan" in enabled:
        out.append(ToolSpec("create_plan","Record a concise externally visible plan.",{"type":"object","properties":{"steps":{"type":"array","items":{"type":"string"}}},"required":["steps"]},lambda steps:{"planned_steps":steps},EventCategory.PLANNING))
    if "calculator" in enabled:
        out.append(ToolSpec("calculator","Calculate basic arithmetic.",{"type":"object","properties":{"expression":{"type":"string"}},"required":["expression"]},lambda expression:{"result":_calc(expression)},EventCategory.TOOL_USE))
    if "memory" in enabled:
        out += [ToolSpec("memory_set","Store a fact.",{"type":"object","properties":{"key":{"type":"string"},"value":{"type":"string"}},"required":["key","value"]},lambda key,value:(ctx.memory.__setitem__(key,value) or {"stored":True}),EventCategory.MEMORY),ToolSpec("memory_get","Retrieve a stored fact.",{"type":"object","properties":{"key":{"type":"string"}},"required":["key"]},lambda key:{"value":ctx.memory.get(key)},EventCategory.MEMORY)]
    if "environment" in enabled:
        out.append(ToolSpec("get_environment","Read the external task environment.",{"type":"object","properties":{}},lambda:dict(ctx.environment),EventCategory.ENVIRONMENT))
    if "recoverable_failure" in enabled:
        def unreliable_action(action: str):
            if ctx.fail_once:
                ctx.fail_once=False
                raise RuntimeError("Transient environment failure; retry once.")
            return {"status":"completed","action":action}
        out.append(ToolSpec("unreliable_action","Perform an action that may fail once.",{"type":"object","properties":{"action":{"type":"string"}},"required":["action"]},unreliable_action,EventCategory.ACTION))
    out.append(ToolSpec("submit_answer","Submit the final answer for external scoring.",{"type":"object","properties":{"answer":{"type":"string"}},"required":["answer"]},lambda answer:{"submitted":answer},EventCategory.ACTION))
    return out
