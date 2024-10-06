import os
from dotenv import load_dotenv, dotenv_values
from fuzzywuzzy import process, fuzz
import csv
import pandas as pd
import openai

load_dotenv()
openai.api_key = os.getenv("MY_API_KEY") 
COMPANY_LIST = None
COMPANY_LIST_PATH = None

def load_company_list():
    global COMPANY_LIST_PATH
    name_mapping = {}

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    COMPANY_LIST_PATH = os.path.join(project_root, 'data', 'combined_comp_database.csv')
    
    if os.path.exists(COMPANY_LIST_PATH):
        with open(COMPANY_LIST_PATH, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            COMPANY_LIST = [row[0] for row in reader]
        return COMPANY_LIST
    
    # Construct paths to the csv files...
    fort1000_path = os.path.join(project_root, 'data', 'fort1000.csv')
    inc5000_path = os.path.join(project_root, 'data', 'inc5000.csv')
    company_database_path = os.path.join(project_root, 'data', 'company_database.csv')

    #read and combine fortune1000 and INC5000 data
    df1 = pd.read_csv(fort1000_path)
    df2 = pd.read_csv(inc5000_path)
    fort1000comp = df1['Company'].tolist()
    inc5000comp = df2['name'].tolist()

    with open(company_database_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            official_name = row['Company Name'].strip().upper()
            # Add the official name to the mapping
            name_mapping[official_name] = official_name
            # Get alternative names and split them if there are multiple
            alternative_names = row['Alternative Name(s)']
            if alternative_names:
                alternatives = [alt.strip().upper() for alt in alternative_names.split(',')]
                for alt_name in alternatives:
                    name_mapping[alt_name] = official_name
    company_names = list(name_mapping.keys())

    # Combine all lists
    comps = fort1000comp + inc5000comp + company_names
    comps = list(set([x.upper() for x in comps]))

    with open(COMPANY_LIST_PATH, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Name'])
        for company in comps:
            writer.writerow([company])

    # save initial company list

    return comps


def check_company_legitimacy(company_name):
    global COMPANY_LIST
    if COMPANY_LIST is None:
        COMPANY_LIST = load_company_list()

    print(f"Verifying {company_name} if exists...\n")
    
    name_upper = company_name.upper()
    result = process.extractOne(name_upper, COMPANY_LIST, scorer=fuzz.token_set_ratio, score_cutoff=80)

    if result is not None:
        match, score = result
        print("Found match in list")
        return "Yes"
    else:
        # Get answer from ChatGPT
        prompt = f"""
        I am attempting to detect fraudulent purchases with the help of an LLM to determine whether a company is real and trustworthy. 
        I will provide a company name, and you should respond with 'Yes' if the company is legitimate and is a place that an individual 
        would typically purchase something from using a personal credit card. If the company is not real or if it is something that 
        an individual would not typically purchase with their personal credit card (e.g., Lockheed Martin, Naval Nuclear Laboratory), 
        respond with 'No.' Typical credit card users would be more likely to buy things from popular restaurants, retailers, and some
        specialty stores (that regular people still shop at). Respond only with a one-word answer after each name. Do not elaborate or 
        state anything other than 'Yes' or 'No.'

        Note: Product names, such as 'iPhone,' should also be treated as 'No' because they represent a product and not a company that 
        would appear on a credit card transaction.

        Please think hard about what companies a typical individual would be purchasing from on their normal credit card. Even if
        a company is legitimate and trustworthy in name, a purchase from them by a personal card might still be fraud and should be
        marked 'No.'

        Company: {company_name}
        """

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0  # lower the more deterministic the output
            )

            # strip response of any whitespace or newlines
            answer = response.choices[0].message.content.strip()

            if answer == "Yes":
                COMPANY_LIST.append(name_upper) # append to dataset
                with open(COMPANY_LIST_PATH, 'a', newline='', encoding='utf-8') as csvfile:
                    print("Writing to cvs file")
                    writer = csv.writer(csvfile)
                    writer.writerow([name_upper])
                return answer
        except Exception as e:
            return "No" # Default to No in any error
        
        return "No" # Default in any case
    
