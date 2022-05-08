import discord
from discord.ext import commands
from config import *
import youtube_dl
import asyncio
import os
import time
import uuid


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'executable':"bin/ffmpeg.exe",
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

nowPlay = {}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

players = {}
queues = {}

bot = commands.Bot(command_prefix="ks.")
bot.remove_command("help")

def check(id):
    global queues
    if id in queues:
        pass
    else:
        queues[id] = []
    if queues[id] != []:
        try:
            vc = queues[id][0]['vc']
            vc.play(discord.FFmpegPCMAudio(executable="bin/ffmpeg.exe", source=queues[id][0]['source']), after=lambda e : check(id))
        except:
            pass
        del queues[id][0]

@bot.command(name="join")
async def join(ctx):
    voice = ctx.author.voice
    server = ctx.message.guild
    if voice is not None:
        try:
            await voice.channel.connect()
            embed = discord.Embed(color=0xd501c0)
            embed.add_field(name="Koper sounds", value="The bot is connected", inline=False)
            await ctx.send(embed=embed)
        except:
            embed = discord.Embed(color=0xd501c0)
            embed.add_field(name="Koper sounds", value="The bot is already connected", inline=False)
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(color=0xd501c0)
        embed.add_field(name="Koper sounds", value="You are not in voice chat", inline=False)
        await ctx.send(embed=embed)

@bot.command(name="disconnect")
async def disconnect(ctx):
    server = ctx.message.guild
    try:
        voice_channel = ctx.guild.voice_client
        await voice_channel.disconnect()
        embed = discord.Embed(color=0xd501c0)
        embed.add_field(name="Koper sounds", value="The bot has disconnected", inline=False)
        await ctx.send(embed=embed)
    except:
        embed = discord.Embed(color=0xd501c0)
        embed.add_field(name="Koper sounds", value="Error", inline=False)
        await ctx.send(embed=embed)


@bot.command(name="play")
async def play(ctx, url):
    global nowPlay
    global queues
    voice = ctx.author.voice
    server = ctx.message.guild
    voice_channel = ctx.guild.voice_client
    # player.play(discord.FFmpegPCMAudio(executable="bin/ffmpeg.exe", source="123.mp3"))
    ytdl_format_options['outtmpl'] = str(server.id)+".mp3"
    if voice is not None:
        try:
            voice_channel = await voice.channel.connect()
        except:
            pass
    else:
        embed = discord.Embed(color=0xd501c0)
        embed.add_field(name="Koper sounds", value="You are not in voice chat", inline=False)
        await ctx.send(embed=embed)
    with youtube_dl.YoutubeDL(ytdl_format_options) as dl:
        video = dl.extract_info(url, download=False)
        if "entries" in video:
            plrUrl = video["entries"][0]['formats'][0]['url']
            url = video["entries"][0]['webpage_url']
        else:
            url = video['webpage_url']
            plrUrl = video['formats'][0]['url']
        try:
            players[server.id] = voice_channel.play(discord.FFmpegPCMAudio(executable="bin/ffmpeg.exe", source=plrUrl), after=lambda e : check(server.id))
            embed = discord.Embed(color=0xd501c0)
            embed.add_field(name="Koper sounds", value="The track is being played: "+url, inline=False)
            await ctx.send(embed=embed)
        except:
            if server.id in queues:
                pass
            else:
                queues[server.id] = []
            queues[server.id].append({
                'vc': voice_channel,
                'source': plrUrl,
                'url': url
            })
            embed = discord.Embed(color=0xd501c0)
            embed.add_field(name="Koper sounds", value="Track added to queue: " + url, inline=False)
            await ctx.send(embed=embed)

@bot.command(name="queue")
async def queue(ctx):
    global queues
    global nowPlay
    server = ctx.message.guild
    embed = discord.Embed(color=0xd501c0)
    text = ""
    if server.id in queues:
        pass
    else:
        queues[server.id] = []
    if queues[server.id] != []:
        for i in queues[server.id]:
            text += f"""{i['url']}
"""
        embed.add_field(name="Koper sounds", value="Queue: ```" + text + "```")
    else:
        embed.add_field(name="Koper sounds", value="Queue is empty")

    await ctx.send(embed=embed)

@bot.command(name="stop")
async def stop(ctx):
    voice = ctx.author.voice
    server = ctx.message.guild
    voice_channel = ctx.guild.voice_client
    voice_channel.stop()
    embed = discord.Embed(color=0xd501c0)
    embed.add_field(name="Koper sounds", value="Track on stopped", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="pause")
async def pause(ctx):
    voice = ctx.author.voice
    server = ctx.message.guild
    voice_channel = ctx.guild.voice_client
    voice_channel.pause()
    embed = discord.Embed(color=0xd501c0)
    embed.add_field(name="Koper sounds", value="Track on paused", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="resume")
async def resume(ctx):
    voice = ctx.author.voice
    server = ctx.message.guild
    voice_channel = ctx.guild.voice_client
    voice_channel.resume()
    embed = discord.Embed(color=0xd501c0)
    embed.add_field(name="Koper sounds", value="Track on is being played again", inline=False)
    await ctx.send(embed=embed)


bot.run(TOKEN)
