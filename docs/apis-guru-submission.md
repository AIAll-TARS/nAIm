# apis.guru Submission — nAIm API

## Public spec URL
```
https://api.naim.janis7ewski.org/openapi-public.json
```

## Submission method

apis.guru accepts submissions via GitHub PR to their `APIs.guru/openapi-directory` repo.

### Steps

1. Fork `https://github.com/APIs-guru/openapi-directory`
2. Create file: `APIs/naim.janis7ewski.org/1.0.0/openapi.yaml`
3. Content — convert our spec to YAML:
   ```bash
   curl -s https://api.naim.janis7ewski.org/openapi-public.json | python3 -c "
   import json, sys
   try:
       import yaml
   except ImportError:
       import subprocess; subprocess.run(['pip','install','pyyaml'])
       import yaml
   print(yaml.dump(json.load(sys.stdin), allow_unicode=True, sort_keys=False))
   " > openapi.yaml
   ```
4. Submit PR with title: `Add nAIm API — machine-first AI agent service registry`
5. PR body:
   ```
   - Name: nAIm API
   - URL: https://api.naim.janis7ewski.org
   - Category: AI / Machine Learning
   - Description: Machine-first registry of AI agent API services (LLM, TTS, STT, embeddings, search, safety tools)
   - Spec URL: https://api.naim.janis7ewski.org/openapi-public.json
   - License: AGPL-3.0
   ```

## Alternative: web form

https://apis.guru/add-api/

Fill in:
- API name: nAIm
- Spec URL: `https://api.naim.janis7ewski.org/openapi-public.json`
- Category: AI Tools

## Verify spec is valid before submitting

```bash
curl -s https://api.naim.janis7ewski.org/openapi-public.json | python3 -c "
import json, sys
spec = json.load(sys.stdin)
assert spec['openapi'].startswith('3.')
assert 'contact' in spec['info']
assert 'servers' in spec
print('Spec valid ✅')
print('Paths:', list(spec['paths'].keys()))
"
```
