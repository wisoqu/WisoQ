import g4f




def get_response(chat_history):
    result = g4f.ChatCompletion.create(
        model=g4f.models.gpt_4,
        messages=chat_history,
        provider='Yqcloud'  #Yqcloud
    )
    return result