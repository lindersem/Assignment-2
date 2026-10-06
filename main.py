import json
import os
import ast

def display_menu():
    console_name = "HARBORFLOW PORT INTELLIGENCE"
    console_menu = '''1. List registered vessels
2. Inspect a vessel manifest
3. Identify priority cargo
4. Export a customer operations profile 
5. Find port calls by month
6. Sanitize an incident report
7. Analyze the longest stable event sequence 
8. Assess weather risk for upcoming calls 
9. Search incident reports
10. Close console'''
    print(f'''{console_name}\n{console_menu}''')

path = "dataset/vessels/"

#def list_files():
#    return os.listdir()


def main():
    """Run the HarborFlow Port Intelligence Console."""
    # TODO: implement the persistent menu and orchestrate the services.
#    print(list_files(path))

    for file in os.listdir(path):
        content = open(path + file, "r").read()
        try:
            print(ast.literal_eval(content)["name"])
        except:
            print("Damaged Record")
    
    running = True

    while running:
        display_menu()

        try:
            selected_service = int(input("Select service: "))
        except ValueError:
            print("Error - Select a service from 1 to 10.")
            continue

        if selected_service == 1:

            #List registered vessels
            pass
        
        elif selected_service == 2:
            #Inspect a vessel manifest
            pass
        
        elif selected_service == 3:
            #Identify priority cargo
            pass
        
        elif selected_service == 4:

            #Export a customer operations profile
            pass
        
        elif selected_service == 5:
            #Find port calls by month
            pass
        
        elif selected_service == 6:
            #Sanitize an incident report
            pass
        
        elif selected_service == 7:
            #Analyze the longest stable event sequence
            pass
        
        elif selected_service == 8:
            #Assess weather risk for upcoming calls
            pass
        
        elif selected_service == 9:
            #Search incident reports
            pass
        
        elif selected_service == 10:
            #Close console
            running = False
            print("Console closed. HarborFlow operational data remains safe.")
        
        else:
            print("Error - Select a service from 1 to 10.")
    
    pass


if __name__ == "__main__":
    main()
