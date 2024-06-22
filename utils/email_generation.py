import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("sk-proj-EnSbPqFCrq6n5YgmQU0QT3BlbkFJ4ujnLzmBheHlL2GeBtIP"))


def PepperLLM(business_context, customer, prompt):

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": business_context},
            {
                "role": "system",
                "content": "Using the customer data, customize the first paragraph from what you can infer (not directly injecting the data into the paragraph because that would sound like a human did not write it). For instance, what kind of income can you infer from the occupation, living in X City? What about his gender from his name?. Write it in such a way that when someone reads it, it thinks you are just filling in the blanks. For instance, you should never directly mention his job or where he/she lives.",
            },
            {
                "role": "system",
                "content": "You are an email marketer hired to write a drip campaign for a business. The goal of the drip campaign is to convert the customer that recieves the email into a paying customer by giving them information and value. Here is the customer data: "
                + str(customer)
                + "Let’s write an email that is personalized for this specific customer.",
            },
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content.strip()


# Example usage

# customer_data = {
#     "name": "Omar",
#     "email": "modestantonny+omar@gmail.com",
#     "income": 5000,
#     "age": 23,
#     "gender": "male",
#     "occupation": "student and software engineer",
#     "city": "New York City",
#     "hobbies": "video games"
# }

# business_context = DB_Manager.get_business_context(username="jimmy@butternut.com")
# prompt = "The product we are trying to sell is: Start Your First Startup: A Mastery Course to Starting Your First Startup. It is a $2,000 course. Most of the selling language in the emails should happen at the end and not the beginning. Write an email about it"


# email_content = PepperLLM(str(business_context), customer_data, prompt)
# print(email_content)
