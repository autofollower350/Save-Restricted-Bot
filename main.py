import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import time
import os
import threading
import json

with open('config.json', 'r') as f: DATA = json.load(f)
def getenv(var): return os.environ.get(var) or DATA.get(var, None)

bot_token = getenv("TOKEN") 
api_hash = getenv("HASH") 
api_id = getenv("ID")
bot = Client("mybot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

ss = getenv("STRING")
if ss is not None:
	acc = Client("myacc" ,api_id=api_id, api_hash=api_hash, session_string=ss)
	acc.start()
else: acc = None

# download status
def downstatus(statusfile,message):
	while True:
		if os.path.exists(statusfile):
			break

	time.sleep(3)      
	while os.path.exists(statusfile):
		with open(statusfile,"r") as downread:
			txt = downread.read()
		try:
			bot.edit_message_text(message.chat.id, message.id, f"__Downloaded__ : **{txt}**")
			time.sleep(10)
		except:
			time.sleep(5)


# upload status
def upstatus(statusfile,message):
	while True:
		if os.path.exists(statusfile):
			break

	time.sleep(3)      
	while os.path.exists(statusfile):
		with open(statusfile,"r") as upread:
			txt = upread.read()
		try:
			bot.edit_message_text(message.chat.id, message.id, f"__Uploaded__ : **{txt}**")
			time.sleep(10)
		except:
			time.sleep(5)


# progress writter
def progress(current, total, message, type):
	with open(f'{message.id}{type}status.txt',"w") as fileup:
		fileup.write(f"{current * 100 / total:.1f}%")


# start command
@bot.on_message(filters.command(["start"]))
def send_start(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
	bot.send_message(message.chat.id, f"__👋 Hi **{message.from_user.mention}**, I am Save Restricted Bot, I can send you restricted content by it's post link__\n\n{USAGE}",
	reply_markup=InlineKeyboardMarkup([[ InlineKeyboardButton("🌐 Source Code", url="https://github.com/bipinkrish/Save-Restricted-Bot")]]), reply_to_message_id=message.id)


@bot.on_message(filters.text)
def save(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
	print(message.text)

	# joining chats
	if "https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text:

		if acc is None:
			bot.send_message(message.chat.id,f"**String Session is not Set**", reply_to_message_id=message.id)
			return

		try:
			try: acc.join_chat(message.text)
			except Exception as e: 
				bot.send_message(message.chat.id,f"**Error** : __{e}__", reply_to_message_id=message.id)
				return
			bot.send_message(message.chat.id,"**Chat Joined**", reply_to_message_id=message.id)
		except UserAlreadyParticipant:
			bot.send_message(message.chat.id,"**Chat alredy Joined**", reply_to_message_id=message.id)
		except InviteHashExpired:
			bot.send_message(message.chat.id,"**Invalid Link**", reply_to_message_id=message.id)

	# getting message
	elif "https://t.me/" in message.text:

		datas = message.text.split("/")
		temp = datas[-1].replace("?single","").split("-")
		fromID = int(temp[0].strip())
		try: toID = int(temp[1].strip())
		except: toID = fromID

		for msgid in range(fromID, toID+1):

			# private
			if "https://t.me/c/" in message.text:
				chatid = int("-100" + datas[4])
				
				if acc is None:
					bot.send_message(message.chat.id,f"**String Session is not Set**", reply_to_message_id=message.id)
					return
				
				handle_private(message,chatid,msgid)
				# try: handle_private(message,chatid,msgid)
				# except Exception as e: bot.send_message(message.chat.id,f"**Error** : __{e}__", reply_to_message_id=message.id)
			
			# bot
			elif "https://t.me/b/" in message.text:
				username = datas[4]
				
				if acc is None:
					bot.send_message(message.chat.id,f"**String Session is not Set**", reply_to_message_id=message.id)
					return
				try: handle_private(message,username,msgid)
				except Exception as e: bot.send_message(message.chat.id,f"**Error** : __{e}__", reply_to_message_id=message.id)

			# public
			else:
				username = datas[3]

				try: msg  = bot.get_messages(username,msgid)
				except UsernameNotOccupied: 
					bot.send_message(message.chat.id,f"**The username is not occupied by anyone**", reply_to_message_id=message.id)
					return
				try:
					if '?single' not in message.text:
						bot.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
					else:
						bot.copy_media_group(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
				except:
					if acc is None:
						bot.send_message(message.chat.id,f"**String Session is not Set**", reply_to_message_id=message.id)
						return
					try: handle_private(message,username,msgid)
					except Exception as e: bot.send_message(message.chat.id,f"**Error** : __{e}__", reply_to_message_id=message.id)

			# wait time
			time.sleep(3)


# handle private
# handle private - Updated Version
def handle_private(message: pyrogram.types.messages_and_media.message.Message, chatid: int, msgid: int):
    try:
        # STEP 1: Pehle chat ko force-resolve karein taaki Pyrogram usse pehchan le
        # Isse "Peer ID Invalid" error khatam ho jayega
        acc.get_chat(chatid)
    except Exception as e:
        print(f"Chat Resolve Error: {e}")
        bot.send_message(message.chat.id, f"**Error**: Could not access chat. Please ensure the String Session account is a member of this chat.\n\nDetails: {e}", reply_to_message_id=message.id)
        return

    try:
        # STEP 2: Ab message fetch karein
        msg: pyrogram.types.messages_and_media.message.Message = acc.get_messages(chatid, msgid)
    except Exception as e:
        bot.send_message(message.chat.id, f"**Error fetching message**: {e}", reply_to_message_id=message.id)
        return

    msg_type = get_message_type(msg)

    if "Text" == msg_type:
        bot.send_message(message.chat.id, msg.text, entities=msg.entities, reply_to_message_id=message.id)
        return

    smsg = bot.send_message(message.chat.id, '__Downloading__', reply_to_message_id=message.id)
    dosta = threading.Thread(target=lambda:downstatus(f'{message.id}downstatus.txt',smsg),daemon=True)
    dosta.start()
    
    # Download logic
    try:
        file = acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        bot.send_message(message.chat.id, f"**Download Error**: {e}", reply_to_message_id=message.id)
        return

    upsta = threading.Thread(target=lambda:upstatus(f'{message.id}upstatus.txt',smsg),daemon=True)
    upsta.start()
    
    # Send media logic
    try:
        if "Document" == msg_type:
            try: thumb = acc.download_media(msg.document.thumbs[0].file_id)
            except: thumb = None
            bot.send_document(message.chat.id, file, thumb=thumb, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])
# Updated handle_private function
def handle_private(message: pyrogram.types.messages_and_media.message.Message, chatid: int, msgid: int):
    try:
        # Step 1: Chat Resolve (Session ko force karo chat dekhne ke liye)
        try:
            acc.get_chat(chatid)
        except Exception:
            # Agar direct ID se nahi khul raha, toh ek baar try/except mein ignore karo
            pass 
        
        # Step 2: Message Fetch
        msg: pyrogram.types.messages_and_media.message.Message = acc.get_messages(chatid, msgid)
    
    except PeerIdInvalid:
        # Yahan Vasusen repo ka logic hai: Agar Peer ID invalid hai, toh retry karo
        print("Peer ID Invalid aaya, retrying...")
        try:
            # Yahan hum ek baar manually chat fetch karke try karte hain
            acc.get_chat(chatid)
            msg = acc.get_messages(chatid, msgid)
        except Exception as e:
            bot.send_message(message.chat.id, f"**Peer ID Invalid Error!**\nIska matlab session ko yeh chat nahi mil rahi. Check karein ki aap us channel ke member hain.\nError: {e}", reply_to_message_id=message.id)
            return

    except Exception as e:
        bot.send_message(message.chat.id, f"**Error**: {e}", reply_to_message_id=message.id)
        return

    # Baaki ka logic waisa hi rahega (Download/Upload)
    msg_type = get_message_type(msg)
    if "Text" == msg_type:
        bot.send_message(message.chat.id, msg.text, entities=msg.entities, reply_to_message_id=message.id)
        return
def handle_private(message, chatid, msgid):
    try:
        # Step 1: Chat Resolve (Session ko force karo chat dekhne ke liye)
        try:
            acc.get_chat(chatid)
        except Exception:
            pass 
        
        # Step 2: Message Fetch
        msg = acc.get_messages(chatid, msgid)
    
    except PeerIdInvalid:
        print("Peer ID Invalid aaya, retrying...")
        try:
            acc.get_chat(chatid)
            msg = acc.get_messages(chatid, msgid)
        except Exception as e:
            bot.send_message(message.chat.id, f"**Peer ID Invalid Error!**\nSession ko chat nahi mili. Check karein ki aap us channel ke member hain.\nError: {e}", reply_to_message_id=message.id)
            return
    except Exception as e:
        bot.send_message(message.chat.id, f"**Error**: {e}", reply_to_message_id=message.id)
        return

    # Download aur Upload Logic
    msg_type = get_message_type(msg)
    if "Text" == msg_type:
        bot.send_message(message.chat.id, msg.text, entities=msg.entities, reply_to_message_id=message.id)
        return

    smsg = bot.send_message(message.chat.id, '__Downloading__', reply_to_message_id=message.id)
    dosta = threading.Thread(target=lambda:downstatus(f'{message.id}downstatus.txt',smsg),daemon=True)
    dosta.start()
    
    try:
        file = acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        bot.send_message(message.chat.id, f"**Download Error**: {e}", reply_to_message_id=message.id)
        return

    upsta = threading.Thread(target=lambda:upstatus(f'{message.id}upstatus.txt',smsg),daemon=True)
    upsta.start()
    
    try:
        if "Document" == msg_type:
            try: thumb = acc.download_media(msg.document.thumbs[0].file_id)
            except: thumb = None
            bot.send_document(message.chat.id, file, thumb=thumb, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])
            if thumb != None: os.remove(thumb)
        elif "Video" == msg_type:
            try: thumb = acc.download_media(msg.video.thumbs[0].file_id)
            except: thumb = None
            bot.send_video(message.chat.id, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=thumb, caption=msg.caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])
            if thumb != None: os.remove(thumb)
    except Exception as e:
        bot.send_message(message.chat.id, f"**Upload Error**: {e}", reply_to_message_id=message.id)

    os.remove(file)
    if os.path.exists(f'{message.id}upstatus.txt'): os.remove(f'{message.id}upstatus.txt')
    bot.delete_messages(message.chat.id,[smsg.id])


# get the type of message
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
	try:
		msg.document.file_id
		return "Document"
	except: pass

	try:
		msg.video.file_id
		return "Video"
	except: pass

	try:
		msg.animation.file_id
		return "Animation"
	except: pass

	try:
		msg.sticker.file_id
		return "Sticker"
	except: pass

	try:
		msg.voice.file_id
		return "Voice"
	except: pass

	try:
		msg.audio.file_id
		return "Audio"
	except: pass

	try:
		msg.photo.file_id
		return "Photo"
	except: pass

	try:
		msg.text
		return "Text"
	except: pass


USAGE = """**FOR PUBLIC CHATS**

__just send post/s link__

**FOR PRIVATE CHATS**

__first send invite link of the chat (unnecessary if the account of string session already member of the chat)
then send post/s link__

**FOR BOT CHATS**

__send link with '/b/', bot's username and message id, you might want to install some unofficial client to get the id like below__

```
https://t.me/b/botusername/4321
```

**MULTI POSTS**

__send public/private posts link as explained above with formate "from - to" to send multiple messages like below__

```
https://t.me/xxxx/1001-1010

https://t.me/c/xxxx/101 - 120
```

__note that space in between doesn't matter__
"""


# infinty polling
bot.run()
