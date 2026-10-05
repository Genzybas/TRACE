# from __future__ import annotations
# import json, os, time
# from typing import Any, Sequence
# from trace_eval.agents.base import AgentAdapter, AgentReply, ToolSpec
# from trace_eval.experiments.recorder import TraceRecorder
# from trace_eval.domain.primitives import EventCategory
# def schema(t): return {"type":"function","name":t.name,"description":t.description,"parameters":t.parameters}
# def call_tool(t,args,rec):
#     st=time.perf_counter()
#     try:
#         result=t.handler(**args); err=False
#     except Exception as e:
#         result={"error":str(e),"recoverable":True}; err=True
#     rec.record(t.category,t.name,payload={"arguments":args,"result":result},latency_ms=(time.perf_counter()-st)*1000,is_error=err)
#     return result
# class OpenAIAdapter(AgentAdapter):
#     def run(self,*,task_id,prompt,recorder,tools,max_turns=12):
#         from openai import OpenAI
#         client=OpenAI(api_key=os.environ["OPENAI_API_KEY"]); lookup={t.name:t for t in tools}; items=[{"role":"user","content":prompt}]; final=""
#         for _ in range(max_turns):
#             kw={"model":self.model,"input":items,"tools":[schema(t) for t in tools]}
#             r=client.responses.create(**kw); items.extend(r.output); calls=[x for x in r.output if getattr(x,"type",None)=="function_call"]
#             if not calls: final=r.output_text or ""; break
#             for c in calls: items.append({"type":"function_call_output","call_id":c.call_id,"output":json.dumps(call_tool(lookup[c.name],json.loads(c.arguments or "{}"),recorder))})
#         recorder.record(EventCategory.SYSTEM,"agent_call_completed"); self._record_final(recorder,final); return AgentReply(final,{"provider":"openai","model":self.model})
# class AnthropicAdapter(AgentAdapter):
#     def run(self,*,task_id,prompt,recorder,tools,max_turns=12):
#         import anthropic
#         client=anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"]); lookup={t.name:t for t in tools}; msgs=[{"role":"user","content":prompt}]; final=""
#         for _ in range(max_turns):
#             r=client.messages.create(model=self.model,max_tokens=2048,messages=msgs,tools=[{"name":t.name,"description":t.description,"input_schema":t.parameters} for t in tools]); results=[]; has=False
#             for b in r.content:
#                 if getattr(b,"type",None)=="text": final=b.text
#                 elif getattr(b,"type",None)=="tool_use": has=True; results.append({"type":"tool_result","tool_use_id":b.id,"content":json.dumps(call_tool(lookup[b.name],dict(b.input),recorder))})
#             if not has: break
#             msgs += [{"role":"assistant","content":r.content},{"role":"user","content":results}]
#         recorder.record(EventCategory.SYSTEM,"agent_call_completed"); self._record_final(recorder,final); return AgentReply(final,{"provider":"anthropic","model":self.model})
# class OpenAICompatibleAdapter(AgentAdapter):
#     def __init__(self,agent_id,model,api_key_env,base_url,temperature=0.0): super().__init__(agent_id,model,temperature); self.api_key_env=api_key_env; self.base_url=base_url
#     def run(self,*,task_id,prompt,recorder,tools,max_turns=12):
#         from openai import OpenAI
#         client=OpenAI(api_key=os.environ[self.api_key_env],base_url=self.base_url); lookup={t.name:t for t in tools}; msgs=[{"role":"user","content":prompt}]; final=""
#         for _ in range(max_turns):
#             r=client.chat.completions.create(model=self.model,messages=msgs,tools=[schema(t) for t in tools],temperature=self.temperature); m=r.choices[0].message; msgs.append(m.model_dump(exclude_none=True))
#             if not m.tool_calls: final=m.content or ""; break
#             for c in m.tool_calls: msgs.append({"role":"tool","tool_call_id":c.id,"content":json.dumps(call_tool(lookup[c.function.name],json.loads(c.function.arguments or "{}"),recorder))})
#         recorder.record(EventCategory.SYSTEM,"agent_call_completed"); self._record_final(recorder,final); return AgentReply(final,{"provider":self.base_url,"model":self.model})
# class GeminiAdapter(AgentAdapter):
#     def run(self,*,task_id,prompt,recorder,tools,max_turns=12):
#         from google import genai
#         from google.genai import types
#         client=genai.Client(api_key=os.environ["GEMINI_API_KEY"]); lookup={t.name:t for t in tools}; decl=[types.FunctionDeclaration(name=t.name,description=t.description,parameters=t.parameters) for t in tools]; tool=types.Tool(function_declarations=decl); contents=[prompt]; final=""
#         for _ in range(max_turns):
#             r=client.models.generate_content(model=self.model,contents=contents,config=types.GenerateContentConfig(tools=[tool],temperature=self.temperature)); calls=getattr(r,"function_calls",None) or []
#             if not calls: final=r.text or ""; break
#             contents.append(r.candidates[0].content); parts=[]
#             for c in calls: parts.append(types.Part.from_function_response(name=c.name,response=call_tool(lookup[c.name],dict(c.args or {}),recorder)))
#             contents.append(types.Content(role="tool",parts=parts))
#         recorder.record(EventCategory.SYSTEM,"agent_call_completed"); self._record_final(recorder,final); return AgentReply(final,{"provider":"google","model":self.model})



from __future__ import annotations
import json, os, time
from typing import Any, Sequence
from trace_eval.agents.base import AgentAdapter, AgentReply, ToolSpec
from trace_eval.experiments.recorder import TraceRecorder
from trace_eval.domain.primitives import EventCategory
def schema(t): return {"type":"function","function":{"name":t.name,"description":t.description,"parameters":t.parameters}}

def responses_schema(t): return {"type":"function","name":t.name,"description":t.description,"parameters":t.parameters}
def call_tool(t,args,rec):
    st=time.perf_counter()
    try:
        result=t.handler(**args); err=False
    except Exception as e:
        result={"error":str(e),"recoverable":True}; err=True
    rec.record(t.category,t.name,payload={"arguments":args,"result":result},latency_ms=(time.perf_counter()-st)*1000,is_error=err)
    return result
class OpenAIAdapter(AgentAdapter):
    def run(self,*,task_id,prompt,recorder,tools,max_turns=12):
        from openai import OpenAI
        client=OpenAI(api_key=os.environ["OPENAI_API_KEY"]); lookup={t.name:t for t in tools}; items=[{"role":"user","content":prompt}]; final=""
        for _ in range(max_turns):
            kw={"model":self.model,"input":items,"tools":[responses_schema(t) for t in tools]}
            r=client.responses.create(**kw); items.extend(r.output); calls=[x for x in r.output if getattr(x,"type",None)=="function_call"]
            if not calls: final=r.output_text or ""; break
            for c in calls: items.append({"type":"function_call_output","call_id":c.call_id,"output":json.dumps(call_tool(lookup[c.name],json.loads(c.arguments or "{}"),recorder))})
        recorder.record(EventCategory.SYSTEM,"agent_call_completed"); self._record_final(recorder,final); return AgentReply(final,{"provider":"openai","model":self.model})
class AnthropicAdapter(AgentAdapter):
    def run(self,*,task_id,prompt,recorder,tools,max_turns=12):
        import anthropic
        client=anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"]); lookup={t.name:t for t in tools}; msgs=[{"role":"user","content":prompt}]; final=""
        for _ in range(max_turns):
            r=client.messages.create(model=self.model,max_tokens=2048,messages=msgs,tools=[{"name":t.name,"description":t.description,"input_schema":t.parameters} for t in tools]); results=[]; has=False
            for b in r.content:
                if getattr(b,"type",None)=="text": final=b.text
                elif getattr(b,"type",None)=="tool_use": has=True; results.append({"type":"tool_result","tool_use_id":b.id,"content":json.dumps(call_tool(lookup[b.name],dict(b.input),recorder))})
            if not has: break
            msgs += [{"role":"assistant","content":r.content},{"role":"user","content":results}]
        recorder.record(EventCategory.SYSTEM,"agent_call_completed"); self._record_final(recorder,final); return AgentReply(final,{"provider":"anthropic","model":self.model})
class OpenAICompatibleAdapter(AgentAdapter):
    def __init__(self,agent_id,model,api_key_env,base_url,temperature=0.0): super().__init__(agent_id,model,temperature); self.api_key_env=api_key_env; self.base_url=base_url
    def run(self,*,task_id,prompt,recorder,tools,max_turns=12):
        from openai import OpenAI
        client=OpenAI(api_key=os.environ[self.api_key_env],base_url=self.base_url); lookup={t.name:t for t in tools}; msgs=[{"role":"user","content":prompt}]; final=""
        for _ in range(max_turns):
            r=client.chat.completions.create(model=self.model,messages=msgs,tools=[schema(t) for t in tools],temperature=self.temperature); m=r.choices[0].message; msgs.append(m.model_dump(exclude_none=True))
            if not m.tool_calls: final=m.content or ""; break
            for c in m.tool_calls: msgs.append({"role":"tool","tool_call_id":c.id,"content":json.dumps(call_tool(lookup[c.function.name],json.loads(c.function.arguments or "{}"),recorder))})
        recorder.record(EventCategory.SYSTEM,"agent_call_completed"); self._record_final(recorder,final); return AgentReply(final,{"provider":self.base_url,"model":self.model})
class GeminiAdapter(AgentAdapter):
    def run(self,*,task_id,prompt,recorder,tools,max_turns=12):
        from google import genai
        from google.genai import types
        client=genai.Client(api_key=os.environ["GEMINI_API_KEY"]); lookup={t.name:t for t in tools}; decl=[types.FunctionDeclaration(name=t.name,description=t.description,parameters=t.parameters) for t in tools]; tool=types.Tool(function_declarations=decl); contents=[prompt]; final=""
        for _ in range(max_turns):
            r=client.models.generate_content(model=self.model,contents=contents,config=types.GenerateContentConfig(tools=[tool],temperature=self.temperature)); calls=getattr(r,"function_calls",None) or []
            if not calls: final=r.text or ""; break
            contents.append(r.candidates[0].content); parts=[]
            for c in calls: parts.append(types.Part.from_function_response(name=c.name,response=call_tool(lookup[c.name],dict(c.args or {}),recorder)))
            contents.append(types.Content(role="tool",parts=parts))
        recorder.record(EventCategory.SYSTEM,"agent_call_completed"); self._record_final(recorder,final); return AgentReply(final,{"provider":"google","model":self.model})
