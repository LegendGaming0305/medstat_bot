from aiogram import Router, types
from aiogram.filters import Command
from additional_functions import save_to_txt

router = Router()

@router.channel_post(Command('define'))
async def channel_define(channel_post: types.Message):
    chat_id = channel_post.chat.id
    chat_name = channel_post.chat.full_name
    chat_link = channel_post.chat.invite_link
    # channel_post.chat.create_invite_link(name=)
    save_to_txt(saved_chat_ids=f'{chat_name}:{str(chat_id)}:{chat_link}')
    
