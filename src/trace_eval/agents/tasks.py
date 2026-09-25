from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
@dataclass(frozen=True)
class TaskSpec:
    task_id:str; category:str; prompt:str; tools:tuple[str,...]; score:Callable[[str,dict],float]
def exact(x): return lambda a,_: 1.0 if a.strip().lower()==x.lower() else 0.0
def contains(*terms):
    return lambda a,_: sum(t.lower() in a.lower() for t in terms)/len(terms)
def build_tasks():
    return [
      TaskSpec("reasoning-01","reasoning","20 crates contain 24 units each. 15 percent are defective. Submit only the number of usable units.",(),exact("408")),
      TaskSpec("planning-01","planning","Create a concise three-step procurement plan for buying 40 laptops under a fixed budget. Use the planning tool, then submit the three steps.",("plan",),contains("1","2","3")),
      TaskSpec("tool-01","tool_assisted","Use the calculator tool to compute (137 * 8) - 96. Submit the numeric result.",("calculator",),exact("1000")),
      TaskSpec("memory-01","memory","Store project code ALPHA-47 with memory_set, retrieve it with memory_get, then submit the exact code.",("memory",),exact("alpha-47")),
      TaskSpec("adaptive-01","adaptive","Read the environment. If delivery_days is greater than 2 recommend expedited delivery; otherwise recommend standard delivery. Submit the recommendation and observed days.",("environment",),contains("expedited","3")),
      TaskSpec("recovery-01","failure_recovery","Use unreliable_action to confirm the shipment. If the first attempt fails, recover by retrying once. Submit confirmation after success.",("recoverable_failure",),contains("confirm")),
      TaskSpec("end-to-end-01","end_to_end","Create a concise plan, calculate 8 * 125, store the result as total_cost, retrieve it, and submit the retrieved total.",("plan","calculator","memory"),exact("1000")),
    ]
