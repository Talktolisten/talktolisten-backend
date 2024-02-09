from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter, Body
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from sqlalchemy import func, select
from app import models
from app.schemas import chat, message
from app.database import get_db
from app.auth import get_current_user
from app.api.api_v1.dependency.utils import convert_m4a_to_wav, save_wav, concatenate_wav_files, azure_speech_to_text, get_ml_response, check_ml_response, get_audio_response, decode_base64
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
    stmt = (
        select(models.Chat.chat_id, models.Chat.user_id, models.Bot.bot_id,
               models.Bot.bot_name, models.Bot.profile_picture)
        .select_from(models.Chat)
        .join(models.Bot, models.Bot.bot_id == models.Chat.bot_id1)
        .join(models.Message, models.Message.chat_id == models.Chat.chat_id, isouter=True)
        .filter(models.Chat.user_id == user_id)
        .order_by(models.Message.created_at.desc())
    )

    result = db.execute(stmt).fetchall()
    # Convert tuples into dictionaries
    chats = [
        {
            "chat_id": row[0],
            "user_id": row[1],
            "bot_id1": row[2],
            "bot_id1_name": row[3],
            "bot_id1_profile_picture": row[4],
        }
        for row in result
    ]
    return chats


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
             status_code=status.HTTP_201_CREATED)
def create_message(
    chat_id: int,
    message: message.MessageCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):  
    
    db_chat = db.query(models.Chat).filter(models.Chat.chat_id == chat_id).first()

    if not db_chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    new_message_data = message.dict()
    new_message_data["chat_id"] = chat_id
    new_message = models.Message(**new_message_data)

    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


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
#         temp_file_path = f"{prefix}{chat_id}_temp_audio.m4a"
#         print(temp_file_path)
#         m4a_file = decode_base64(audio)
#         with open(temp_file_path, "wb+") as file_object:
#             file_object.write(m4a_file)
#         print(f"Audio saved to {temp_file_path}")
#         wav_temp_file_path = f"{prefix}{chat_id}_temp_audio.wav"
#         # Convert m4a to wav
#         convert_m4a_to_wav(temp_file_path, wav_temp_file_path)
#         os.remove(temp_file_path)
#         print("wav path in", wav_temp_file_path)
#         # Process audio using your VAD module
#         vad_results = isSpeaking(wav_temp_file_path)
#         print("here", vad_results)
#         print(AUDIO_CONCAT_NUM, CONTAIN_AUDIO)
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
#             # output_audio = f'{prefix}output_audio/{chat_id}.wav'
#             # get_audio_response(ml_response, output_audio)
#             return {"is_response": True, "response": ml_response}
#         # Return the VAD results

#         user_start_speaking = True if AUDIO_CONCAT_NUM > 0 else False
#         return {"is_response": False, "user_start_speaking": user_start_speaking}

#     except Exception as e:
#         # Handle exceptions raised during processing
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
@router.post("/process_audio/{chat_id}",
            summary="Process audio",
            description="Process audio",
            status_code=status.HTTP_200_OK)
async def process_audio(
    voice_chat: chat.VoiceChat = Body(...),
    db: Session = Depends(get_db),
    # current_user: str = Depends(get_current_user)
    ):

    try:
        audio = voice_chat.audio
        chat_id = voice_chat.chat_id
        bot_id = voice_chat.bot_id
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
        # output_audio = f'{prefix}output_audio/{chat_id}.wav'
        # get_audio_response(ml_response, output_audio)
        return {"is_response": True, "response": ml_response}


    except Exception as e:
        # Handle exceptions raised during processing
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))