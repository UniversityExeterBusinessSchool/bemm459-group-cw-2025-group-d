class ChatBox:
    def __init__(self, chat_id, buyer, shop, last_update, messages):
        self.chat_id = chat_id
        self.buyer = buyer
        self.shop = shop
        self.last_update = last_update
        self.messages = messages

    def __str__(self):
        return f"ChatBox(chat_id={self.chat_id}, buyer={self.buyer}, shop={self.shop}, last_update={self.last_update})"
