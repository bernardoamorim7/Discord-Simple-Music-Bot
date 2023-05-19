# Import Libraries
import discord
import asyncio
from yt_dlp import YoutubeDL
from random import shuffle


# Discord bot initialization
TOKEN = "INSERT_YOUR_TOKEN_HERE"  # Insert your Token here

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = discord.Client(intents=intents)

voice_clients = {}

YT_DL_OPTIONS = {"format": "bestaudio/best"}
YT_DL = YoutubeDL(YT_DL_OPTIONS)

FFMPEG_OPTIONS = {"options": "-vn"}

queue = []

current_song = None

playing = False


# Event that happens when the bot gets run
@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")
    print("-------------------------------")


# Event that happens when a message gets sent
@bot.event
async def on_message(message):
    global queue, playing, current_song

    async def play_next():
        global queue, playing, current_song

        if not playing:
            try:
                current_song = queue[0]

                player = discord.FFmpegPCMAudio(
                    current_song["url"], **FFMPEG_OPTIONS
                )

                voice_clients[message.guild.id].play(
                    player, after=lambda e: asyncio.run(play_next())
                )

                await message.channel.send(
                    f'Now playing: **{current_song["title"]}**\n{current_song["webpage_url"]}'
                )

                playing = True

                return True

            except Exception as e:
                print(e)
                print("There is no song left in the queue")

        if len(queue) > 0:
            playing = True

            try:
                current_song = queue.pop(0)

                player = discord.FFmpegPCMAudio(
                    current_song["url"], **FFMPEG_OPTIONS
                )

                voice_clients[message.guild.id].play(
                    player, after=lambda e: asyncio.run(play_next())
                )

                await message.channel.send(
                    f'Now playing: **{current_song["title"]}**\n{current_song["webpage_url"]}'
                )

                playing = True

            except Exception as e:
                print(e)
                print("There is no song left in the queue")

        else:
            playing = False
            current_song = None

            return False

    if message.content.startswith("?join"):
        try:
            voice_client = await message.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client

        except Exception as e:
            print(e)
            await message.channel.send("Error joining voice channel")

    if message.content.startswith("?leave"):
        try:
            voice_client = voice_clients[message.guild.id]
            await voice_client.disconnect()

        except Exception as e:
            print(e)
            await message.channel.send("Bot is not in a voice channel")

    if message.content.startswith("?play"):
        try:
            voice_client = await message.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client

        except Exception as e:
            print(e)

        try:
            url = message.content.split()[1]

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None, lambda: YT_DL.extract_info(url, download=False)
            )

            queue.append(data)

            await message.channel.send("Song added to queue")

        except Exception as e:
            print(e)
            await message.channel.send("Error playing song")

        try:
            await play_next()

        except Exception:
            playing = False

    if message.content.startswith("?search"):
        try:
            voice_client = await message.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client

        except Exception as e:
            print(e)

        try:
            info = YT_DL.extract_info(
                "ytsearch:%s" % message.content.split("?search ")[1:],
                download=False,
            )["entries"][0]

            queue.append(info)

            await message.channel.send("Song added to queue")

        except Exception as e:
            print(e)
            await message.channel.send("Error searching song")

        try:
            await play_next()

        except Exception:
            playing = False

    if message.content.startswith("?stop"):
        try:
            voice_client = voice_clients[message.guild.id]
            voice_client.stop()

            playing = False

        except Exception as e:
            print(e)
            await message.channel.send("There is no song to stop")

    if message.content.startswith("?pause"):
        try:
            voice_client = voice_clients[message.guild.id]
            voice_client.pause()

        except Exception as e:
            print(e)
            await message.channel.send("There is no song to pause")

    if message.content.startswith("?resume"):
        try:
            voice_client = voice_clients[message.guild.id]
            voice_client.resume()

        except Exception as e:
            print(e)
            await message.channel.send("There is no song to resume")

    if message.content.startswith("?skip"):
        try:
            if len(queue) > 0:
                voice_client = voice_clients[message.guild.id]
                voice_client.stop()

                try:
                    if await play_next():
                        await message.channel.send("Song skipped")

                except Exception:
                    playing = False
                    await message.channel.send(
                        "There is no song left in the queue"
                    )

        except Exception as e:
            print(e)
            await message.channel.send("There is no song to skip")

    if message.content.startswith("?queue"):
        try:
            retval = ""

            for i, m in enumerate(queue):
                retval = retval + f'\t{i+1}.  {m["title"]}\n'

            if retval != "":
                await message.channel.send(
                    f"**-------  Queue  -------**\n{retval}**-----------------------**"
                )

            else:
                await message.channel.send("There is no song in the queue")

        except Exception as e:
            print(e)
            await message.channel.send("There is no song in the queue")

    if message.content.startswith("?clear"):
        try:
            queue = []

            await message.channel.send("Queue cleared")

        except Exception as e:
            print(e)
            await message.channel.send("There is no song in the queue")

    if message.content.startswith("?shuffle"):
        try:
            shuffle(queue)

            await message.channel.send("Queue shuffled")

        except Exception as e:
            print(e)
            await message.channel.send("There is no song in the queue")

    # Help
    if message.content.startswith("?help"):
        await message.channel.send(
            "Commands: \n\n"
            "?join - Joins voice channel \n"
            "?leave - Leaves voice channel\n"
            "?play [url] - Plays song from url\n"
            "?search [song] - Searches song and plays it\n"
            "?stop - Stops playing song \n"
            "?pause - Pauses song\n"
            "?resume - Resumes song\n"
            "?skip - Skips song\n"
            "?queue - Shows queue\n"
            "?clear - Clears queue\n"
            "?shuffle - Shuffles queue\n"
            "?help - Shows this message\n\n"
            "If you need more help, contact me through GitHub @bernardoamorim7"
        )

    # Random Answers
    # Check if the message was sent by the bot
    if message.author == bot.user:
        return

    # You can write bot answer this way
    # elif "hi" in message.content.lower():
    #    await message.channel.send("Hi!")


# Run the bot
def main():
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
