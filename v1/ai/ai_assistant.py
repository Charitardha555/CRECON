import os
import json
import requests

class AIAssistant:
    def __init__(self, api_key=None, use_openai=True):
        self.api_key = api_key
        self.use_openai = use_openai
        self.api_key_file = os.path.expanduser("~/.crecon_ai_key.json")
        self.load_api_key()

    def load_api_key(self):
        if os.path.exists(self.api_key_file):
            try:
                with open(self.api_key_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.api_key = data.get("api_key", "")
                    self.use_openai = data.get("use_openai", True)
            except Exception:
                self.api_key = ""
                self.use_openai = True

    def save_api_key(self):
        try:
            with open(self.api_key_file, "w", encoding="utf-8") as f:
                json.dump({"api_key": self.api_key, "use_openai": self.use_openai}, f)
        except Exception:
            pass

    def set_api_key(self, key, use_openai):
        self.api_key = key
        self.use_openai = use_openai
        self.save_api_key()

    def get_ai_response(self, prompt, scan_results=None):
        if not self.api_key:
            return "No API key set. Please enter your OpenAI API key in settings."
        # If scan_results are provided, include them in the prompt
        if scan_results:
            prompt = (
                f"Scan Results:\n{scan_results}\n\n"
                f"User Query: {prompt}\n\n"
                "Instructions:"
                "\n- Only suggest and automate scans using the built-in CRECON scanner."
                "\n- Never mention or recommend nmap tool."
                "\n- If the user asks to scan a target, respond with 'Starting scan...' and trigger the relevant scan in the app."
                "\n- Give only accurate, factual answers."
                "\n- Respond as fast as possible."
                "\n- Format your response as very clear and very concise points one by one in next line.."
                "\n- Do not include unnecessary explanations. And try to give responses in as less points as possible."
                "\n- If suggesting exploits or next steps, do not explain the scanned results again as user can see them in scan window, be direct and actionable."
                "\n- Do not show CVE suggestions for ping scan, only show normal suggestions for ping scan."
                "\n- While suggesting CVEs show the latest exploits only... do not show the old non-working ones."
            )
        else:
            prompt = (
                f"User Query: {prompt}\n\n"
                "Instructions:"
                "\n- If no scan result is provided then you can reply with 'no scan result detected for AI reference'"
                "\n- Only suggest and automate scans using the built-in CRECON scanner."
                "\n- Never mention or recommend nmap tool."
                "\n- If the user asks to scan a target, respond with 'Starting scan...' and trigger the relevant scan in the app."
                "\n- Give only accurate, factual answers."
                "\n- Respond as fast as possible."
                "\n- Format your response as very clear and very concise points one by one in next line.."
                "\n- Do not include unnecessary explanations. And try to give responses in as less points as possible."
                "\n- If suggesting exploits or next steps, do not explain the scanned results again as user can see them in scan window, be direct and actionable."
                "\n- Do not show CVE suggestions for ping scan, only show normal suggestions for ping scan."
                "\n- While suggesting CVEs show the latest exploits only... do not show the old non-working ones."
            )
        # If the API key looks like a URL, treat it as a custom endpoint (e.g., LM Studio)
        if self.api_key.startswith("http://") or self.api_key.startswith("https://"):
            try:
                payload = {
                    "model": "local-model",  # You may need to adjust this for your LM Studio setup
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
                response = requests.post(self.api_key, json=payload, timeout=90)
                response.raise_for_status()
                data = response.json()
                # Try to extract the response from LM Studio compatible API
                if "choices" in data and data["choices"]:
                    return data["choices"][0]["message"]["content"].strip()
                return str(data)
            except Exception as e:
                return f"[AI Error] {e}"
        # Placeholder for actual AI call
        return f"[AI] (Simulated) You asked: {prompt}"

    def get_ai_response_stream(self, prompt, scan_results=None):
        if not self.api_key:
            yield "No API key set. Please enter your OpenAI API key in settings."
            return
        if scan_results:
            prompt = (
                f"Scan Results:\n{scan_results}\n\n"
                f"User Query: {prompt}\n\n"
                "Instructions:"
                "\n- Only suggest and automate scans using the built-in CRECON scanner."
                "\n- Never mention or recommend nmap tool."
                "\n- If the user asks to scan a target, respond with 'Starting scan...' and trigger the relevant scan in the app."
                "\n- Give only accurate, factual answers."
                "\n- Respond as fast as possible."
                "\n- Format your response as very clear and very concise points one by one in next line.."
                "\n- Do not include unnecessary explanations. And try to give responses in as less points as possible."
                "\n- If suggesting exploits or next steps, do not explain the scanned results again as user can see them in scan window, be direct and actionable."
                "\n- Do not show CVE suggestions for ping scan, only show normal suggestions for ping scan."
                "\n- While suggesting CVEs show the latest exploits only... do not show the old non-working ones."
            )
        if self.api_key.startswith("http://") or self.api_key.startswith("https://"):
            try:
                payload = {
                    "model": "local-model",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "stream": True
                }
                with requests.post(self.api_key, json=payload, stream=True, timeout=90) as response:
                    response.raise_for_status()
                    buffer = ""
                    for line in response.iter_lines(decode_unicode=True):
                        if line and line.startswith('data: '):
                            data = line[6:]
                            if data.strip() == '[DONE]':
                                break
                            try:
                                chunk = json.loads(data)
                                if "choices" in chunk and chunk["choices"]:
                                    delta = chunk["choices"][0]["delta"]
                                    if "content" in delta:
                                        buffer += delta["content"]
                                        if "\n" in buffer or len(buffer) > 40:
                                            yield buffer.strip()
                                            buffer = ""
                            except Exception:
                                continue
                    if buffer.strip():
                        yield buffer.strip()

            except Exception as e:
                yield f"[AI Error] {e}"
                return
        else:
            try:
                response = self.get_ai_response(prompt, scan_results).strip()
                # Avoid yielding duplicate responses
                yielded_lines = set()
                for part in response.split('\n'):
                    part = part.strip()
                    if part and part not in yielded_lines:
                        yielded_lines.add(part)
                        yield part
            except Exception as e:
                yield f"[AI Error] {e}"


