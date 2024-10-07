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


class Artifact(object):
    build_mode = str()
    build_platform = str()
    build_channel = str()
    build_qemu = bool()

    commit_id = str()

    def __str__(self):
        return f'BUILD_MODE: { self.build_mode }\nBUILD_PLATFORM: { self.build_platform }\nBUILD_CHANNEL: { self.build_channel }\nBUILD_QEMU: { 'yes' if self.build_qemu else 'no' }\n\nSHORT_COMMIT_ID: { self.commit_id[:7] }'


def escape_special_chars(text):
    special_chars = r'_[]()~>#+-=|{}.!'  # *`
    for char in special_chars:
        text = text.replace(char, '\\' + char)
    return text


def parse_artifact_name(name: str) -> Artifact | None:
    # PenMods-YDP02X-release-canary-0fd73e42471225f1e2149b8bfc5e55aad7a0d53c

    if not name.startswith('PenMods-'):
        return None

    is_qemu = False
    if name.endswith('-qemu'):
        name = name.removesuffix('-qemu')
        is_qemu = True

    array = name.split('-')
    if len(array) != 5:
        print('unknown path format.')
        return None
    result = Artifact()
    result.build_platform = array[1]
    result.build_mode = array[2]
    result.build_channel = array[3]
    result.build_qemu = is_qemu
    result.commit_id = array[4]

    return result


async def main():
    bot = Bot(token=TOKEN)

    mode = get_env('MODE')

    match mode:
        case 'COMMITMSG':
            branch = get_env('BRANCH')
            repository = get_env('REPOSITORY').split('/')[1]
            commits = json.loads(get_env('COMMITS'))

            msg = f'🔨 *{ len(commits) }* new commit(s) to *{ repository }:{ branch }*\n\n'
            for commit in reversed(commits):
                msg += f'*{ commit['id'][:7] }* { commit['message'] }\n'

            msg = escape_special_chars(msg)

            await bot.send_message(
                chat_id=GROUP_ID,
                text=msg.removesuffix('\n'),
                message_thread_id=THREAD_ID,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        case 'PUBLISH':
            artifact_path = None
            for file in os.listdir():
                if file.startswith('PenMods-'):
                    if artifact_path:
                        print('multi-artifact is unsupported.')
                        return
                    artifact_path = file

            artifact = parse_artifact_name(artifact_path)
            if not artifact:
                print('unable to parse artifact file name.')
                return

            caption = f'```\n{ artifact }\n```\n📦 New *{ artifact.build_channel }* build released!'
            with open(f'{artifact_path}/libPenMods.so', 'rb') as file:
                await bot.send_document(
                    chat_id=GROUP_ID,
                    document=file,
                    caption=caption,
                    message_thread_id=THREAD_ID,
                    parse_mode=ParseMode.MARKDOWN,
                )
        case _:
            print(f'unknown running mode: {mode}')


if __name__ == '__main__':
    asyncio.run(main())
