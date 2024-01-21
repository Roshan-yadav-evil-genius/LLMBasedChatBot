from DBPipeline import DBInstance
from rich import print
import time
from datetime import datetime
from dotenv import load_dotenv
from telepot import Bot
from FollowUp import FollowUp
from LLM import LLMMODEL
from SettingLoder import WAIT_FOR_RESPONSE,parseFollowUpSetting,SETTING_FILE_STREAM
load_dotenv()

llmmodel = LLMMODEL()

def organize_conversation(messages):
    conversation = []
    current_role = None
    current_message = ""
    last_id = None

    for message in messages:
        role = message['role']
        content = message['content']
        message_id = message['id']
        created_on = message['createdon']
        tag = message['tag']

        if role == current_role:
            current_message += " " + content
            last_id = message_id
        else:
            if current_message:
                conversation.append({'id': last_id, 'role': current_role, 'content': current_message.strip(),'createdon': created_on, 'tag': tag})
            current_role = role
            current_message = content
            last_id = message_id

    if current_message:
        conversation.append({'id': last_id, 'role': current_role, 'content': current_message.strip(),
                             'createdon': created_on, 'tag': tag})

    return conversation


def compare_conversations(before, after):
    missing_ids = []
    updated_ids = []

    before_dict = {message['id']: message['content'] for message in before}
    after_dict = {message['id']: message['content'] for message in after}

    for message_id, content_before in before_dict.items():
        if message_id in after_dict:
            content_after = after_dict[message_id]
            if content_before.strip() != content_after.strip():
                updated_ids.append(message_id)
        else:
            missing_ids.append(message_id)

    return missing_ids, updated_ids


def get_content_by_id(messages, target_id):
    for message in messages:
        if message['id'] == target_id:
            return message['content']
    return None


def last_reply_timing(datetime_string):
    date_time_obj = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S')
    current_time = datetime.now()
    time_difference_seconds = (current_time - date_time_obj).total_seconds()

    if time_difference_seconds < 86400:
        return int(time_difference_seconds), 0
    else:
        days = int(time_difference_seconds / 86400)
        seconds_remaining = int(time_difference_seconds % 86400)
        return days, seconds_remaining


def respond_for_query(userid, organized_chat_history):
    DataBase=DBInstance()
    print("[+] Responding")
    username = DataBase.get_username_by_userid(userid)
    response=llmmodel.getResponseFromLLM(userid,organized_chat_history)
    DataBase.insertChatHistory(userid, username, 'assistant', response)


def take_follow_up(userid, organized_chat_history, prompt):
    DataBase=DBInstance()
    username = DataBase.get_username_by_userid(userid)
    response=llmmodel.getFollowUpFromLLM(userid,organized_chat_history,prompt)
    DataBase.insertChatHistory(userid, username, 'assistant', response, tag='followup')


def StartResponder():
    time.sleep(30)
    DataBase=DBInstance()
    while True:
        for userid in DataBase.getUserIds():
            user_chat_history = DataBase.getChatHistoryByUserID(userid)
            organized_chat_history = organize_conversation(user_chat_history)
            to_delete, to_update = compare_conversations(user_chat_history, organized_chat_history)

            for id in to_delete:
                DataBase.deleteChatHistoryById(id)
            for id in to_update:
                DataBase.updateChatHistoryContentById(id, get_content_by_id(organized_chat_history, id))

            final_response = organized_chat_history[-1]

            seconds, _ = last_reply_timing(final_response['createdon'])
            # print(final_response)
            if final_response['role'] == 'user':
                print(f"[+] Waiting for More Msgs : {WAIT_FOR_RESPONSE - seconds}")
                if seconds > WAIT_FOR_RESPONSE:
                    print(final_response)
                    respond_for_query(userid, organized_chat_history)
            elif final_response['role'] == 'assistant':
                followup = FollowUp(userid) # if want followup update data in db
                
                requiredfollowup = followup.wantFollowUp(final_response['createdon'])
                if requiredfollowup:
                    prompt= f"In the last {requiredfollowup}, I haven't been responsive or shown interest. Please send a message to persuade me. also add some exiciting offer to convence on the basis of durationi not responded"
                    take_follow_up(userid, organized_chat_history, prompt)

        time.sleep(1)


if __name__ == "__main__":
    StartResponder()
