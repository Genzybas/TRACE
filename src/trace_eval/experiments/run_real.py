from __future__ import annotations
import argparse
from trace_eval.agents.providers import OpenAIAdapter,AnthropicAdapter,GeminiAdapter,OpenAICompatibleAdapter
from trace_eval.agents.runner import run_study
from trace_eval.agents.tasks import build_tasks
from trace_eval.experiments.io import load_manifest
def adapter(a):
    temp=float(a.generation_parameters.get("temperature",0.0))
    if a.provider=="openai": return OpenAIAdapter(a.agent_id,a.model_version,temp)
    if a.provider=="anthropic": return AnthropicAdapter(a.agent_id,a.model_version,temp)
    if a.provider=="gemini": return GeminiAdapter(a.agent_id,a.model_version,temp)
    if a.provider in ("qwen","deepseek"):
        base=a.base_url or ("https://api.deepseek.com" if a.provider=="deepseek" else "https://dashscope-intl.aliyuncs.com/compatible-mode/v1")
        return OpenAICompatibleAdapter(a.agent_id,a.model_version,a.api_key_env,base,temp)
    raise ValueError(a.provider)
def main():
    p=argparse.ArgumentParser(); p.add_argument("--manifest",required=True); p.add_argument("--runs",required=True); p.add_argument("--seed",type=int,default=42); x=p.parse_args(); m=load_manifest(x.manifest); built={t.task_id:t for t in build_tasks()};
    missing=[t.task_id for t in m.tasks if t.task_id not in built]
    if missing: raise ValueError(f"No executable task/scorer registered: {missing}")
    if any("REPLACE_WITH" in a.model_version for a in m.agents): raise ValueError("Lock every model_version in experiment_manifest.json before running the study.")
    if any("REPLACE_WITH" in (a.base_url or "") for a in m.agents): raise ValueError("Set every provider base_url before running the study.")
    run_study([adapter(a) for a in m.agents],[built[t.task_id] for t in m.tasks],m.repeated_runs_per_condition,x.runs,x.seed)
    print(f"Wrote real execution records to {x.runs}")
if __name__=="__main__": main()
