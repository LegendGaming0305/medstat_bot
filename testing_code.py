import re

class MessageInteraction:
    def __init__(self):
        self.user_id = None
        self.subject = None
        self.form_name = None
        self.question = None
        self.message_id = None
        self.attributes = {
            'user_id': r'<b>Пользователь:</b>\s*([\d]+)',
            'subject': r'<b>Субъект:</b>\s*([^<]+)',
            'form_name': r'<b>Форма:</b>\s*\s*([^<]+)',
            'question': r'<b>Вопрос:</b>\s*([^<]+)',
            'message_id': r'<s>([\d]+)</s>'
        }

    def parse_message(self, message: str):
        message = message.replace('\n', '')
        for attr, pattern in self.attributes.items():
            match = re.search(pattern, message)
            if match:
                setattr(self, attr, match.group(1))

    def create_message(self, user_id: int, subject: str, form_name: str, question: str, message_id: int):
        return f'<b>Пользователь:</b> {user_id}\n<b>Субъект:</b> {subject}\n<b>Форма:</b> {form_name}\n<b>Вопрос:</b> {question}\n<s>{message_id}</s>'

message = '<b>Пользователь:</b> 6469547756\n<b>Субъект:</b> Саратовская область\n<b>Форма:</b> • Ф. № 30 Шелепова Е.А.\n<b>Вопрос:</b> test:\n<s>3175</s>'

parser = MessageInteraction()
parser.parse_message(message)
text = parser.create_message(user_id=6469547756, 
                      subject='Саратовская область', 
                      form_name='• Ф. № 30 Шелепова Е.А.',
                      question='test1',
                      message_id=3185)
parser.parse_message(text)

print("User ID:", parser.user_id)
print("Subject:", parser.subject)
print("Form Name:", parser.form_name)
print("Question:", parser.question)
print("Message ID:", parser.message_id)
print(text)
