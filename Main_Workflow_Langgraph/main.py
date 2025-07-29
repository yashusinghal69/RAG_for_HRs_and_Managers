from graph import run_workflow
import json

def main():

    user_id = "HR001"
    query =  "What is the annual budget for the preparation and consulting related to the Affirmative Action Plan (AAP)?"
    
    result = run_workflow(query,user_id)
    
    print("\n✨ Response:")
    print("-" * 50)
    print(json.dumps(result, indent=2))
    print("-" * 50)

if __name__ == "__main__":
    main()  