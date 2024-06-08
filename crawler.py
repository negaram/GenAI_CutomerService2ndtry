import requests
from bs4 import BeautifulSoup
import pypandoc

url = 'https://www.alibaba.ir/iranout'
response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')

details = soup.find_all('details')

questions = []
answers = []

for detail in details:
    question = detail.find(class_='a-accordion__button')
    answer = detail.find(class_='faq-wrapper__description')

    if question and answer:
        questions.append(question.text.strip())
        answers.append(answer.text.strip())

# Create a Markdown string
markdown_content = "# سوالات پر تکرار\n\n"
for question, answer in zip(questions, answers):
    markdown_content += f"## {question}\n\n{answer}\n\n"

# Convert Markdown to .docx using pypandoc
output = pypandoc.convert_text(markdown_content, 'docx', format='md', outputfile='./data/questions_and_answers.docx')

if not output is None:
    print("questions_and_answers.docx has been created successfully.")
else:
    print("An error occurred while creating the .docx file.")
