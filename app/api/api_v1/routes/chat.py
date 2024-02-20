from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter, Body
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from sqlalchemy import func
from app import models
from app.config import configs
from app.schemas import chat, message
from app.database import get_db
from app.auth import get_current_user
from app.api.api_v1.dependency.utils import convert_m4a_to_wav, save_wav, concatenate_wav_files, azure_speech_to_text, get_ml_response, check_ml_response, decode_base64
from app.api.api_v1.dependency.utils import VoiceService
from app.api.api_v1.dependency.vad import isSpeaking

router = APIRouter(
    prefix="/chat",
    tags=['Chat']
)


@router.get("/{user_id}",
            summary="Get all chats of an user",
            description="Get all chats of an user by user_id",
            response_model=List[chat.ChatGet])
def get_chats(
    user_id,
    skip: int = 0,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    LatestMessageSubquery = (
        db.query(
            models.Message.chat_id,
            func.max(models.Message.created_at).label('latest_message_time'),
            func.max(models.Message.message_id).label('latest_message_id')  # Assuming you have a sequential ID that can indicate the latest
        )
        .group_by(models.Message.chat_id)
        .subquery('latest_message_subquery')
    )

    # Query to fetch the content of the latest message using the latest_message_id
    MessageContentSubquery = (
        db.query(
            models.Message.message_id,
            models.Message.message.label('latest_message_content')
        )
        .subquery('message_content_subquery')
    )

    # Join Chat, Bot, LatestMessageSubquery, and MessageContentSubquery
    chats_query = (
        db.query(
            models.Chat.chat_id,
            models.Chat.user_id,
            models.Chat.bot_id1,
            models.Bot.bot_name,
            models.Bot.profile_picture,
            LatestMessageSubquery.c.latest_message_time,
            MessageContentSubquery.c.latest_message_content
        )
        .join(models.Bot, models.Bot.bot_id == models.Chat.bot_id1)
        .join(LatestMessageSubquery, LatestMessageSubquery.c.chat_id == models.Chat.chat_id)
        .join(MessageContentSubquery, MessageContentSubquery.c.message_id == LatestMessageSubquery.c.latest_message_id)
        .filter(models.Chat.user_id == user_id)
        .order_by(LatestMessageSubquery.c.latest_message_time.desc())
    )

    chats = chats_query.all()

    chats_list = [
        {
            "chat_id": chat.chat_id,
            "user_id": chat.user_id,
            "bot_id1": chat.bot_id1,
            "bot_id1_name": chat.bot_name,
            "bot_id1_profile_picture": chat.profile_picture,
            "last_message_content": chat.latest_message_content,
            "last_message_time": chat.latest_message_time,
        }
        for chat in chats
    ]

    return chats_list


@router.post("/",
             summary="Create a new chat",
             description="Create a new chat",
             status_code=status.HTTP_201_CREATED)
def create_chat(
    chat: chat.ChatCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):  

    new_chat = models.Chat(**chat.dict())
    num_bots = 5
    for i in range(2, num_bots+1):
        if new_chat.__getattribute__(f"bot_id{i}") == 0:
            new_chat.__setattr__(f"bot_id{i}", None)    

    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    new_message = models.Message(
        chat_id=new_chat.chat_id,
        message = new_chat.bot_id1.greeting,
        created_by_bot = new_chat.bot_id1,
        is_bot = True
    )
    db.add(new_message)
    db.commit()

    return new_chat


@router.delete("/{chat_id}",
               summary="Delete a chat",
               description="Delete a chat by chat_id",
               status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):  
    chat = db.query(models.Chat).filter(models.Chat.chat_id == chat_id).first()
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    db.delete(chat)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{chat_id}/message",
             summary="Create a new message for a chat",
             description="Create a new message",
             response_model=message.MessageGet,
             status_code=status.HTTP_201_CREATED)
async def create_message(
    chat_id: int,
    message_obj: message.MessageCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):  
    
    db_chat = db.query(models.Chat).filter(models.Chat.chat_id == chat_id).first()

    if not db_chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    new_message_data = message_obj.dict()
    new_message_data["chat_id"] = chat_id
    new_message = models.Message(**new_message_data)

    db.add(new_message)
    db.commit()

    bot_id = db_chat.bot_id1
    db_bot = db.query(models.Bot).filter(models.Bot.bot_id == bot_id).first()
    bot_description = db_bot.description
    job_id = get_ml_response(bot_description, new_message.message)
    if job_id:
        ml_response = await check_ml_response(job_id)
    bot_response = models.Message(
        chat_id=chat_id,
        message=ml_response,
        is_bot=True,
        created_by_bot=bot_id
    )
    db.add(bot_response)

    # Update last message in the chat
    db_chat.last_message = bot_response.message_id

    # Update number of interations with bots
    db_bot.num_chats += 1
    db.commit()

    db.refresh(db_chat)
    db.refresh(db_bot)
    
    return message.MessageGet(
        message_id=bot_response.message_id,
        chat_id=bot_response.chat_id,
        user_id=db_chat.user_id,
        bot_id=bot_id,
        message=bot_response.message,
        created_at=bot_response.created_at,
        created_by_user=bot_response.created_by_user,
        created_by_bot=bot_response.created_by_bot,
        is_bot=bot_response.is_bot
    )


@router.get("/{chat_id}/message",
            summary="Get all messages of a chat",
            description="Get all messages of a chat by chat_id",
            response_model=List[message.MessageGet])
def get_messages(
    chat_id: int,
    limit: int = 20,
    skip: int = 0,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    messages = (
        db.query(
            models.Message.message_id,
            models.Message.chat_id,
            models.Message.message,
            models.Message.created_at,
            models.Message.created_by_user,
            models.Message.created_by_bot,
            models.Message.is_bot,
            models.Chat.user_id,
            models.Chat.bot_id1.label('bot_id')
        )
        .join(models.Chat, models.Message.chat_id == models.Chat.chat_id)
        .filter(models.Message.chat_id == chat_id)
        .order_by(models.Message.created_at.desc())
        .offset(skip)
        .limit(limit)
        .yield_per(30)
        .all()
    )

    return [
        message.MessageGet(
            message_id=msg.message_id,
            chat_id=msg.chat_id,
            message=msg.message,
            created_at=msg.created_at,
            created_by_user=msg.created_by_user,
            created_by_bot=msg.created_by_bot,
            is_bot=msg.is_bot,
            user_id=msg.user_id,
            bot_id=msg.bot_id
        ) for msg in messages
    ]


@router.get("/{chat_id}/{message_id}",
            summary="Get a specific message in a chat",
            description="Get a specific message in a chat",
            response_model=message.MessageGet)
def get_message(
    chat_id: int,
    message_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    message = (
        db.query(models.Message)
        .filter(models.Message.chat_id == chat_id)
        .filter(models.Message.message_id == message_id)
        .first()
    )

    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")

    return message


@router.get("/{chat_id}/{message_id}",
            summary="Get older messages in a chat",
            description="Get messages older than a specific message in a chat",
            response_model=List[message.MessageGet])
def get_older_messages(
    chat_id: int,
    message_id: int,
    limit: int = 20,
    skip: int = 0,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    messages = (
        db.query(
            models.Message.message_id,
            models.Message.chat_id,
            models.Message.message,
            models.Message.created_at,
            models.Message.created_by_user,
            models.Message.created_by_bot,
            models.Message.is_bot,
            models.Chat.user_id,
            models.Chat.bot_id1.label('bot_id')
        )
        .join(models.Chat, models.Message.chat_id == models.Chat.chat_id)
        .filter(models.Message.chat_id == chat_id, models.Message.message_id < message_id)
        .order_by(models.Message.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        message.MessageGet(
            message_id=msg.message_id,
            chat_id=msg.chat_id,
            message=msg.message,
            created_at=msg.created_at,
            created_by_user=msg.created_by_user,
            created_by_bot=msg.created_by_bot,
            is_bot=msg.is_bot,
            user_id=msg.user_id,
            bot_id=msg.bot_id
        ) for msg in messages
    ]


@router.delete("/{chat_id}/{message_id}",
               summary="Delete a message",
               description="Delete a message by message_id",
               status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
    chat_id: int,
    message_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):  
    message = db.query(models.Message).filter(models.Message.message_id == message_id).first()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    db.delete(message)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


AUDIO_CONCAT_NUM = 0
CONTAIN_AUDIO = False
prefix = "app/api/api_v1/dependency/temp_audio/"

# @router.post("/process_audio/{chat_id}",
#             summary="Process audio",
#             description="Process audio",
#             status_code=status.HTTP_200_OK)
# async def process_audio(
#     voice_chat: chat.VoiceChat = Body(...),
#     db: Session = Depends(get_db),
#     # current_user: str = Depends(get_current_user)
#     ):

#     try:
#         global CONTAIN_AUDIO
#         global AUDIO_CONCAT_NUM
#         need_response = False

#         audio = voice_chat.audio
#         chat_id = voice_chat.chat_id
#         bot_id = voice_chat.bot_id

#         voice = (
#                     db.query(models.Voice)
#                     .join(models.Bot, models.Bot.voice_id == models.Voice.voice_id)
#                     .filter(models.Bot.bot_id == bot_id)
#                     .first()
#                 )


#         temp_file_path = f"{prefix}{chat_id}_temp_audio.m4a"
#         print("Create a temporary path for the m4a file at ", temp_file_path)
#         m4a_file = decode_base64(audio)
#         with open(temp_file_path, "wb+") as file_object:
#             file_object.write(m4a_file)
#         print(f"Audio saved to {temp_file_path} after converting from base64")
#         wav_temp_file_path = f"{prefix}{chat_id}_temp_audio.wav"
#         convert_m4a_to_wav(temp_file_path, wav_temp_file_path)
#         print('Convert m4a to wav in ', wav_temp_file_path)
#         os.remove(temp_file_path)
#         print("Clean up the temporary m4a file")
        
#         vad_results = isSpeaking(wav_temp_file_path)
#         print("VAD result is", vad_results)
#         print(f"There are {AUDIO_CONCAT_NUM} is concatenated, is the audio contain audio before? {CONTAIN_AUDIO}")

#         if vad_results:
#             save_wav(wav_temp_file_path, f"{prefix}concat_audios/{chat_id}{AUDIO_CONCAT_NUM}.wav")
#             AUDIO_CONCAT_NUM += 1
#             CONTAIN_AUDIO = True
#         else:
#             if CONTAIN_AUDIO:
#                 concatlist = []
#                 for i in range(AUDIO_CONCAT_NUM):
#                     concatlist.append(f"{prefix}concat_audios/{chat_id}{i}.wav")
#                 audio_to_translate = concatenate_wav_files(concatlist, chat_id)
#                 for i in range(AUDIO_CONCAT_NUM):
#                     os.remove(f"{prefix}concat_audios/{chat_id}{i}.wav")
#                 need_response = True
                
#             CONTAIN_AUDIO = False
#             AUDIO_CONCAT_NUM = 0
#         os.remove(wav_temp_file_path)

#         if need_response:
#             print(audio_to_translate)
#             text_translation = azure_speech_to_text(audio_to_translate)
#             os.remove(audio_to_translate)
#             bot = db.query(models.Bot).filter(models.Bot.bot_id == bot_id).first()
#             job_id = get_ml_response(bot.description, text_translation)
#             if job_id:
#                 ml_response = await check_ml_response(job_id)
#             if voice.voice_provider == configs.VOICE_PROVIDER_1:
#                 voice_service = VoiceService(ml_response, voice.voice_endpoint)
#                 output_audio = voice_service.get_audio_response_eleventlabs()
#             return {"is_response": True, "response": output_audio, "user_speaking": False}

#         user_speaking = True if AUDIO_CONCAT_NUM > 0 else False
#         return {"is_response": False, "user_speaking": user_speaking}

#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@router.post("/process_audio/{chat_id}",
            summary="Process audio",
            description="Process audio",
            status_code=status.HTTP_200_OK)
async def process_audio(
    voice_chat: chat.VoiceChat = Body(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
    ):

    try:
        audio = voice_chat.audio
        chat_id = voice_chat.chat_id
        bot_id = voice_chat.bot_id
        
        voice = (
            db.query(models.Voice)
            .join(models.Bot, models.Bot.voice_id == models.Voice.voice_id)
            .filter(models.Bot.bot_id == bot_id)
            .first()
        )

        temp_file_path = f"{prefix}{chat_id}_temp_audio.m4a"
        print(temp_file_path)
        m4a_file = decode_base64(audio)
        with open(temp_file_path, "wb+") as file_object:
            file_object.write(m4a_file)
        print(f"Audio saved to {temp_file_path}")
        wav_temp_file_path = f"{prefix}{chat_id}_temp_audio.wav"
        # Convert m4a to wav
        convert_m4a_to_wav(temp_file_path, wav_temp_file_path)
        os.remove(temp_file_path)
        print("wav path in", wav_temp_file_path)
        audio_to_translate = wav_temp_file_path
        text_translation = azure_speech_to_text(audio_to_translate)
        os.remove(audio_to_translate)
        bot = db.query(models.Bot).filter(models.Bot.bot_id == bot_id).first()
        print(bot.description)
        job_id = get_ml_response(bot.description, text_translation)
        if job_id:
            ml_response = await check_ml_response(job_id)
        
        if voice.voice_provider == configs.VOICE_PROVIDER_1:
            voice_service = VoiceService(ml_response, voice.voice_endpoint)
            output_audio = voice_service.get_audio_response_eleventlabs()

        return {"is_response": True, "response": output_audio}


    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))