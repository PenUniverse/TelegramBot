import asyncio
import os
import json
from telegram import Bot

TOKEN       = os.environ.get('BOT_TOKEN')

GROUP_ID    = os.environ.get('GROUP_ID')
THREAD_ID   = os.environ.get('THREAD_ID')

async def main():
    bot = Bot(token=TOKEN)
    branch = os.environ.get('BRANCH')
    repository = os.environ.get('REPOSITORY').split('/')[1]
    commits = json.loads(os.environ.get('COMMITS'))
    msg = f'🔨 **{len(commits)}** new commit(s) to **{repository}:{branch}**\n\n'
    for commit in commits:
        msg += f'*{commit['id'][:7]}*  {commit['message']}\n'
    msg = msg.removesuffix('\n')
    await bot.send_message(chat_id=GROUP_ID, text=msg, message_thread_id=THREAD_ID, parse_mode=ParseMode.MARKDOWN)

if __name__ == "__main__":
    asyncio.run(main())
