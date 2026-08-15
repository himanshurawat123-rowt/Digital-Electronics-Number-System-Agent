from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import re
import io
import uvicorn

app = FastAPI(title="Okay Bot AI Conversion Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# ==========================================
# 1. Conversion Engine with Validation & Steps
# ==========================================
def validate_number(num_str: str, base: int):
    num_str = str(num_str).strip().upper()
    valid_chars = DIGITS[:base]
    for char in num_str:
        if char not in valid_chars:
            return False, char
    return True, None

def base_to_decimal_steps(num_str: str, base: int):
    num_str = str(num_str).strip().upper()
    n = len(num_str)
    total = 0
    parts = []
    
    for i, char in enumerate(num_str):
        power = n - 1 - i
        val = DIGITS.index(char)
        term = val * (base ** power)
        total += term
        parts.append(f"({char} × {base}^{power})")
        
    formula = " + ".join(parts)
    step_desc = f"{num_str}(base {base}) = {formula} = {total}(base 10)"
    return total, step_desc

def decimal_to_base_steps(dec_val: int, target_base: int):
    if dec_val == 0:
        return "0", ["0(base 10) = 0(base " + str(target_base) + ")"]
    
    steps = []
    rem_list = []
    curr = dec_val
    
    while curr > 0:
        q = curr // target_base
        r = curr % target_base
        r_char = DIGITS[r]
        rem_list.append(r_char)
        steps.append(f"{curr} ÷ {target_base} = {q} (Remainder: {r} / '{r_char}')")
        curr = q
        
    res = "".join(reversed(rem_list))
    step_desc = f"{dec_val}(base 10) converted to base {target_base} = {res}(base {target_base})"
    return res, step_desc

def perform_conversion(number: str, from_base: int, to_base: int) -> Dict[str, Any]:
    from_base = int(from_base)
    to_base = int(to_base)
    num_str = str(number).strip().upper()
    
    base_names = {2: "Binary", 8: "Octal", 10: "Decimal", 16: "Hexadecimal"}
    from_name = base_names.get(from_base, f"Base-{from_base}")
    to_name = base_names.get(to_base, f"Base-{to_base}")
    
    # Validation Check
    is_valid, bad_char = validate_number(num_str, from_base)
    if not is_valid:
        allowed_range = f"0 to {DIGITS[from_base-1]}" if from_base <= 10 else f"0-9 and A-{DIGITS[from_base-1]}"
        return {
            "number": num_str,
            "source_base": from_base,
            "target_base": to_base,
            "result": "⚠️ RADIX_RULE_VIOLATION",
            "steps": [
                f"🛑 PROTOCOL_ERROR: Did you forget the fundamental rules of Digital Electronics?",
                f"Character '{bad_char}' is strictly FORBIDDEN in {from_name} (Base-{from_base})!",
                f"Rule Check: {from_name} numbers can ONLY contain digits in the range [{allowed_range}].",
                f"Correction Tip: Please provide a valid {from_name} number and try again, human! 🤖"
            ]
        }
    
    steps_list = []
    
    # Step A: Convert to Decimal
    if from_base != 10:
        dec_val, step_1 = base_to_decimal_steps(num_str, from_base)
        steps_list.append(step_1)
    else:
        dec_val = int(num_str, 10)
        
    # Step B: Convert from Decimal to Target Base
    if to_base != 10:
        final_res, step_2 = decimal_to_base_steps(dec_val, to_base)
        steps_list.append(step_2)
    else:
        final_res = str(dec_val)
        
    if from_base == to_base:
        steps_list.append(f"Number is already in base {from_base}.")

    return {
        "number": num_str,
        "source_base": from_base,
        "target_base": to_base,
        "result": final_res,
        "steps": steps_list
    }

# ==========================================
# 2. Smart NLP & Spoken Command Parser
# ==========================================
def parse_natural_language_command(command_text: str):
    text = command_text.lower().strip()
    
    # Clean wake words: "okay bot", "hey bot", "bot"
    text = re.sub(r"^(?:okay|ok|hey|hi)?\s*bot[,:\s]*", "", text, flags=re.IGNORECASE)
    
    radix_map = {
        "binary": 2, "bin": 2, "2": 2, "base 2": 2, "base-2": 2,
        "octal": 8, "oct": 8, "8": 8, "base 8": 8, "base-8": 8,
        "decimal": 10, "dec": 10, "10": 10, "base 10": 10, "base-10": 10,
        "hexadecimal": 16, "hex": 16, "16": 16, "base 16": 16, "base-16": 16
    }
    
    # Match pattern: convert [number] from [base] to [base]
    match = re.search(r"(?:convert\s+)?([0-9a-zA-Z\s]+?)\s+(?:from\s+)?(binary|octal|decimal|hexadecimal|hex|bin|oct|dec|\d+)\s+(?:to|in|into)\s+(binary|octal|decimal|hexadecimal|hex|bin|oct|dec|\d+)", text)
    if match:
        raw_num = match.group(1).replace(" ", "").upper()
        from_str = match.group(2)
        to_str = match.group(3)
        from_b = radix_map.get(from_str, int(from_str) if from_str.isdigit() else 10)
        to_b = radix_map.get(to_str, int(to_str) if to_str.isdigit() else 16)
        return raw_num, from_b, to_b
    
    # Fallback pattern: convert [number] to [base]
    fallback = re.search(r"convert\s+([0-9a-zA-Z\s]+?)\s+(?:to|in|into)\s+(\w+)", text)
    if fallback:
        raw_num = fallback.group(1).replace(" ", "").upper()
        to_str = fallback.group(2)
        to_b = radix_map.get(to_str, int(to_str) if to_str.isdigit() else 10)
        from_b = 2 if all(c in "01" for c in raw_num) and to_b != 2 else 10
        return raw_num, from_b, to_b
        
    return None, None, None

# ==========================================
# 3. API Endpoints with Soundfile Decoder
# ==========================================
class ConvertRequest(BaseModel):
    number: str
    from_base: int
    to_base: int

class CommandRequest(BaseModel):
    command: str

@app.post("/api/convert")
async def api_convert(req: ConvertRequest):
    return perform_conversion(req.number, req.from_base, req.to_base)

@app.post("/api/command")
async def api_command(req: CommandRequest):
    num, from_b, to_b = parse_natural_language_command(req.command)
    if not num:
        return {
            "transcript": req.command,
            "conversion": {
                "number": "ERROR",
                "source_base": 0,
                "target_base": 0,
                "result": "⚠️ SYNTAX_ERROR",
                "steps": [
                    f"Could not parse command: '{req.command}'",
                    "Try commands like: 'convert 101101 from binary to hexadecimal' or 'convert 255 from decimal to binary'"
                ]
            }
        }
    conversion_data = perform_conversion(num, from_b, to_b)
    return {
        "transcript": req.command,
        "conversion": conversion_data
    }

@app.post("/api/voice")
async def api_voice(audio: UploadFile = File(...)):
    transcript = ""
    audio_bytes = await audio.read()
    
    try:
        import speech_recognition as sr
        
        # Audio decoding using soundfile (converts browser float32/webm to 16-bit PCM WAV)
        try:
            import soundfile as sf
            data, samplerate = sf.read(io.BytesIO(audio_bytes))
            wav_io = io.BytesIO()
            sf.write(wav_io, data, samplerate, format='WAV', subtype='PCM_16')
            audio_pcm = wav_io.getvalue()
        except Exception:
            audio_pcm = audio_bytes
            
        r = sr.Recognizer()
        with sr.AudioFile(io.BytesIO(audio_pcm)) as source:
            audio_data = r.record(source)
            transcript = r.recognize_google(audio_data)
            print(f"🎙️ Recognized Voice Input: '{transcript}'")
            
    except Exception as e:
        print(f"Voice Recognition Error: {e}")
        transcript = ""
        
    if not transcript:
        return {
            "transcript": "Audio could not be recognized. Please speak clearly.",
            "conversion": {
                "number": "VOICE_ERROR",
                "source_base": 0,
                "target_base": 0,
                "result": "🎙️ VOICE_NOT_RECOGNIZED",
                "steps": [
                    "Could not capture voice cleanly from microphone.",
                    "Please speak clearly: 'Convert 101101 from binary to hexadecimal'",
                    "Or type in the text box below and click PROCESS COMMAND."
                ]
            }
        }
        
    num, from_b, to_b = parse_natural_language_command(transcript)
    if not num:
        return {
            "transcript": transcript,
            "conversion": {
                "number": "SYNTAX_ERROR",
                "source_base": 0,
                "target_base": 0,
                "result": "⚠️ COMMAND_NOT_PARSED",
                "steps": [
                    f"Heard: '{transcript}'",
                    "Command format: 'Convert [number] from [source base] to [target base]'"
                ]
            }
        }
        
    conversion_data = perform_conversion(num, from_b, to_b)
    return {
        "transcript": transcript,
        "conversion": conversion_data
    }

@app.get("/")
def home():
    return {"status": "Okay Bot Backend API is running on Port 8000!"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
