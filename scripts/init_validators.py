import sys
import os
import json

# Ensure project root is on PYTHONPATH so we can import rpc_tools
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from rpc_tools.genlayer_rpc import rpc

def recreate_validators():
    print("Fetching existing validators...")
    try:
        response = rpc("sim_getAllValidators", [])
        validators = response.get('result', [])
        print(f"Found {len(validators)} validators.")
        
        for v in validators:
            print(f"Validator item: {v}")
            if isinstance(v, dict):
                v_addr = v.get('address')
            else:
                print("Unexpected validator structure")
                continue
                
            if v_addr is None:
                print("Validator address not found")
                continue

            print(f"Deleting validator {v_addr}...")
            try:
                rpc("sim_deleteValidator", [v_addr])
                print(f"Deleted validator {v_addr}.")
            except Exception as e:
                print(f"Failed to delete validator {v_addr}: {e}")
                
    except Exception as e:
        print(f"Error fetching validators: {e}")
        return

    print("Creating new validators with corrected configuration...")
    
    validator_params = {
        "stake": 10000,
        "provider": "heuristai",
        "model": "deepseek/deepseek-v3",
        "config": {"max_tokens": 4000, "temperature": 0.1},
    }

    num_validators = 3
    print(f"Using params: {validator_params}")
    for i in range(num_validators):
        print(f"Creating validator {i+1}/{num_validators}...")
        try:
            args_list = [
                validator_params["stake"],
                validator_params["provider"],
                validator_params["model"],
                validator_params["config"],
            ]
            
            result = rpc("sim_createValidator", args_list)
            print(f"Success! Validator {i+1} created.")
        except Exception as e:
            print(f"Failed to create validator {i+1}: {e}")

if __name__ == "__main__":
    recreate_validators()
