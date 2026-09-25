from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
def generate_figures(study_json,output_dir):
    d=json.loads(Path(study_json).read_text(encoding="utf-8")); o=Path(output_dir); o.mkdir(parents=True,exist_ok=True); agents=[a["agent_id"] for a in d["agents"]]
    angles=np.linspace(0,2*np.pi,3,endpoint=False).tolist()+[0]; fig=plt.figure(figsize=(9,7)); ax=fig.add_subplot(111,polar=True)
    for a in d["agents"]:
        vals=[a["cognitive_mean"],a["operational_mean"],a["reliability_mean"]]; vals += vals[:1]; ax.plot(angles,vals,label=a["agent_id"]); ax.fill(angles,vals,alpha=.08)
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(["Cognitive","Operational","Reliability"]); ax.set_ylim(0,1); ax.set_title("TRACE Behavioural Signature Comparison"); ax.legend(loc="upper right",bbox_to_anchor=(1.35,1.15)); fig.tight_layout(); fig.savefig(o/"figure_4_behavioural_signatures.png",dpi=300,bbox_inches="tight"); plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,6)); x=[a["success_mean"] for a in d["agents"]]; y=[a["confidence_mean"] for a in d["agents"]]; ax.scatter(x,y,s=60)
    for n,xi,yi in zip(agents,x,y): ax.annotate(n,(xi,yi),xytext=(5,5),textcoords="offset points")
    ax.set_xlabel("Task Success Rate"); ax.set_ylabel("Behavioural Confidence ($\\kappa$)"); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.set_title("Behavioural Confidence versus Task Success"); fig.tight_layout(); fig.savefig(o/"figure_5_confidence_vs_success.png",dpi=300,bbox_inches="tight"); plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,6)); ax.bar(agents,[a["final_score_mean"] for a in d["agents"]]); ax.set_ylabel("Mean TRACE Final Score"); ax.set_title("TRACE Final Scores Across Evaluated Agents"); ax.set_ylim(0,1); ax.tick_params(axis="x",rotation=20); fig.tight_layout(); fig.savefig(o/"figure_6_trace_scores.png",dpi=300,bbox_inches="tight"); plt.close(fig)
