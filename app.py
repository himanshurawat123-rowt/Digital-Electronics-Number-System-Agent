import streamlit as st
import re

# Page Config
st.set_page_config(page_title="AI Number System Agent", page_icon="🔢")
st.title("🔢 AI Number System Conversion Agent")
st.write("Welcome! Ask me any base conversion or validation question in plain English.")

# Radix Map
RADIX_MAP = {
    "binary": 2, "bin": 2, "base 2": 2, "base-2": 2,
    "octal": 8, "oct": 8, "base 8": 8, "base-8": 8,
    "decimal": 10, "dec": 10, "base 10": 10, "base-10": 10,
    "hexadecimal": 16, "hex": 16, "base 16": 16, "base-16": 16
}

DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def is_valid_digit(num_str, base):
    for char in num_str.upper():
        if char not in DIGITS or DIGITS.index(char) >= base:
            return False
    return True

def convert_and_explain(num_str, from_base, to_base):
    num_str = num_str.upper()
    
    # Validation Check
    if not is_valid_digit(num_str, from_base):
        return f"❌ **Validation Error**: The number `{num_str}` is INVALID in Base-{from_base}. Base-{from_base} only allows digits up to `{DIGITS[from_base-1]}`."

    # Step 1: Convert to Decimal
    dec_val = 0
    steps_dec = []
    power = len(num_str) - 1
    for char in num_str:
        digit = DIGITS.index(char)
        dec_val += digit * (from_base ** power)
        steps_dec.append(f"({digit} × {from_base}^{power})")
        power -= 1
        
    explanation = f"### Conversion Process:\n\n"
    explanation += f"**Step 1: Convert `{num_str}` (Base-{from_base}) to Decimal (Base-10)**\n"
    explanation += f"$$\\text{{Decimal}} = " + " + ".join(steps_dec) + f" = {dec_val}$$\n\n"

    if to_base == 10:
        explanation += f"✅ **Final Answer**: `({num_str})_{{{from_base}}} = ({dec_val})_{{10}}`"
        return explanation

    # Step 2: Decimal to Target Base
    temp = dec_val
    remainders = []
    if temp == 0:
        remainders.append("0")
    else:
        while temp > 0:
            rem = temp % to_base
            remainders.append(DIGITS[rem])
            temp //= to_base
            
    res_str = "".join(reversed(remainders))
    
    explanation += f"**Step 2: Convert Decimal `{dec_val}` to Base-{to_base} via Successive Division**\n"
    explanation += f"Divide `{dec_val}` repeatedly by `{to_base}` and collect remainders bottom-to-top.\n\n"
    explanation += f"✅ **Final Answer**: `({num_str})_{{{from_base}}} = ({res_str})_{{{to_base}}}`"
    return explanation

def process_query(user_text):
    text = user_text.lower()
    
    # Validation query check
    valid_match = re.search(r"is\s+([0-9a-f]+)\s+a?\s*valid\s+(binary|octal|decimal|hexadecimal)", text)
    if valid_match:
        num, base_name = valid_match.groups()
        base = RADIX_MAP[base_name]
        valid = is_valid_digit(num, base)
        if valid:
            return f"✅ **Yes!** `{num.upper()}` is a valid {base_name.capitalize()} (Base-{base}) number."
        else:
            return f"❌ **No!** `{num.upper()}` is NOT a valid {base_name.capitalize()} (Base-{base}) number. Base-{base} digits must be strictly less than `{base}`."

    # Natural Language Conversion Check
    num_match = re.search(r"([0-9a-f]+)", text)
    if not num_match:
        return "I couldn't detect a number in your query. Please ask like: *'Convert 101101 to decimal'* or *'Is 10201 a valid binary?'*"
        
    num = num_match.group(1).upper()
    
    # Infer Target Base
    to_base = None
    for key, val in RADIX_MAP.items():
        if f"to {key}" in text or f"in {key}" in text:
            to_base = val
            break
            
    # Infer Source Base
    from_base = None
    for key, val in RADIX_MAP.items():
        if f"from {key}" in text:
            from_base = val
            break
            
    # Auto-detect source base if not specified
    if not from_base:
        if all(c in "01" for c in num):
            from_base = 2
        elif all(c in "01234567" for c in num) and to_base != 8:
            from_base = 10 if to_base == 2 else 8
        elif all(c in "0123456789" for c in num):
            from_base = 10
        else:
            from_base = 16

    if not to_base:
        return f"Please specify the target base! For example: *'Convert {num} to hexadecimal'*."

    return convert_and_explain(num, from_base, to_base)

# Chat Session Management
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your Digital Electronics AI Agent. Ask me to convert numbers or test validity."}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Type your question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    response = process_query(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)
