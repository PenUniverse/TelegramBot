import asyncio
import os
import json

from telegram import Bot
from telegram.constants import ParseMode


def get_env(name: str):
    return os.environ.get(name)


TOKEN = get_env('BOT_TOKEN')

GROUP_ID = get_env('GROUP_ID')
THREAD_ID = get_env('THREAD_ID')


async def main():
    bot = Bot(token=TOKEN)

    mode = get_env('MODE')

    match mode:
        case 'COMMITMSG':
            branch = get_env('BRANCH')
            repository = get_env('REPOSITORY').split('/')[1]
            commits = json.loads(get_env('COMMITS'))

            msg = f'🔨 *{len(commits)}* new commit(s) to *{repository}:{branch}*\n\n'
            for commit in commits:
                msg += f'*{commit['id'][:7]}* {commit['message']}\n'

            await bot.send_message(
                chat_id=GROUP_ID,
                text=msg.removesuffix('\n'),
                message_thread_id=THREAD_ID,
                parse_mode=ParseMode.MARKDOWN,
            )
        case 'PUBLISH':
            path = get_env('FILE_PATH')
            channel = 'unknown'
            if path.find('canary') != -1:
                channel = 'canary'
            elif path.find('beta') != -1:
                channel = 'beta'
            elif path.find('stable') != -1:
                channel = 'stable'
            cap = f'📦 New {channel} build!'
            with open(path, 'rb') as file:
                await bot.send_document(
                    chat_id=GROUP_ID,
                    document=file,
                    caption=cap,
                    message_thread_id=THREAD_ID,
                    parse_mode=ParseMode.MARKDOWN,
                )
        case _:
            print(f'Unknown running mode: {mode}')


if __name__ == '__main__':
    asyncio.run(main())
