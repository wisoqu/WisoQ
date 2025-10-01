import g4f


def get_response(chat_history):
    result = g4f.ChatCompletion.create(
        model=g4f.models.gpt_4,
        messages=chat_history,
        provider='Yqcloud'  #Yqcloud
    )
    return result

def get_chat_name(chat_history):
    chat_title = g4f.ChatCompletion.create(
        model=g4f.models.gpt_4,
        messages=[{'role': 'admin', 'content': f'Get the title of this chat by this message(only 5 words or less): {chat_history[0]['content']}'}],
        provider='Yqcloud'  #Yqcloud
    )
    return chat_title