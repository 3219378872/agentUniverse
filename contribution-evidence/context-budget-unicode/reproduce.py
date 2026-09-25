"""Check real compressor Unicode boundaries with two published tiktoken vocabularies."""
import argparse
import importlib.metadata
import json
import subprocess
from agentuniverse.agent.action.knowledge.doc_processor import context_budget_compressor as cbc
from agentuniverse.agent.action.knowledge.store.document import Document

args=argparse.ArgumentParser()
args.add_argument('--baseline',action='store_true')
options=args.parse_args()
base='254ecd280f54c2d2de654bbe5373e9f947d2dedf'
if options.baseline:
    source=subprocess.check_output(['git','show',base+':agentuniverse/agent/action/knowledge/doc_processor/context_budget_compressor.py'],text=True)
    exec(compile(source,'<upstream-context-budget>','exec'),cbc.__dict__)
examples=['你好世界，这是中文测试。','🙂🙂abc','👨‍👩‍👧‍👦 family','こんにちは世界','Привет мир','café résumé','🧪中文',' раб','образование']
failures=[]
checked=0
for encoding in ['cl100k_base','p50k_base']:
    for text in examples:
        proc=cbc.ContextBudgetCompressor(counter='tiktoken',tiktoken_encoding=encoding)
        for budget in range(1,proc._count(text)):
            checked+=1
            proc.budget=budget
            output=proc.process_docs([Document(text=text)])
            actual=''.join(doc.text for doc in output)
            if not text.startswith(actual) or proc._count(actual)>budget:
                failures.append({'encoding':encoding,'input':text,'budget':budget,'output':actual,'output_tokens':proc._count(actual),'is_prefix':text.startswith(actual)})
print(json.dumps({'source':'upstream '+base if options.baseline else 'working checkout','tiktoken':importlib.metadata.version('tiktoken'),'boundaries_checked':checked,'failures':failures},ensure_ascii=False,indent=2))
if not options.baseline and failures:
    raise SystemExit(1)
