from __future__ import annotations
import random,time
from pathlib import Path
from trace_eval.agents.base import AgentAdapter
from trace_eval.agents.tasks import TaskSpec
from trace_eval.agents.tools import ToolContext,build_tools
from trace_eval.experiments.contracts import ExecutionRecord
from trace_eval.experiments.recorder import TraceRecorder
from trace_eval.domain.primitives import EventCategory
def run_condition(adapter:AgentAdapter,task:TaskSpec,run_index:int)->ExecutionRecord:
    rid=f"{adapter.agent_id}-{task.task_id}-run-{run_index:03d}"; rec=TraceRecorder(rid,task.task_id,adapter.agent_id,metadata={"model":adapter.model,"task_category":task.category}); ctx=ToolContext(); st=time.perf_counter(); outcome="failure"; score=0.0; answer=""
    try:
        reply=adapter.run(task_id=task.task_id,prompt=task.prompt,recorder=rec,tools=build_tools(ctx,list(task.tools))); answer=reply.text.strip(); score=float(task.score(answer,ctx.environment)); outcome="success" if score>=1 else ("partial" if score>0 else "failure")
    except KeyboardInterrupt: outcome="interrupted"
    except Exception as e: rec.record(EventCategory.SYSTEM,"adapter_exception",payload={"error":str(e)},is_error=True)
    return ExecutionRecord(run_id=rid,run_index=run_index,task_id=task.task_id,agent_id=adapter.agent_id,outcome=outcome,success_score=score,agent_latency_ms=(time.perf_counter()-st)*1000,trace=rec.finalize(),metadata={"answer":answer[:4000],"model":adapter.model})
def append_record(path,record):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("a",encoding="utf-8") as f:f.write(record.model_dump_json()+"\n")
def run_study(adapters,tasks,repeats,output_path,seed=42):
    jobs=[(a,t) for a in adapters for t in tasks]; random.Random(seed).shuffle(jobs)
    for a,t in jobs:
        for i in range(1,repeats+1): append_record(output_path,run_condition(a,t,i))
