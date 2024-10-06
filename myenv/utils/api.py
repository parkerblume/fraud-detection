import os
from dotenv import load_dotenv, dotenv_values
import openai

load_dotenv()
openai.api_key = os.getenv("MY_API_KEY") 

def check_company_legitimacy(company_name):
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

    print(company_name)

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # Use chat model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=10,
        temperature=0  # Keep temperature low for deterministic output
    )

    # strip response of any whitespace or newlines
    answer = response.choices[0].message.content.strip()
    print(answer)
    return answer