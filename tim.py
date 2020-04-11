import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient
import asyncio
import os
from random import randint
import youtube_dl

api = str(os.environ.get('RIOT_KEY'))
bot = commands.Bot(command_prefix='!')
bot.remove_command('help')

@bot.event
async def on_ready():
	await bot.change_presence(activity=discord.Game(name="!help"))
	print("je suis pret")
	print("Je m'appele " + str(bot.user.name))

@bot.command()
async def insulte(ctx, message):
	table_isultes = []
	nb_alea = randint(0, 4)
	with open("insulte.txt", "r", encoding='utf8') as f:
		for insulte in f.readlines():
			table_isultes.append(insulte)
	msg = str(message)+" = "+str(table_isultes[nb_alea])
	msg += "cela a été prouvé"
	await ctx.send(msg)
'''------------------------------------------commande pour la musique-------------------------------------'''
@bot.command()
async def joue(ctx, url):
	global player
	# join un channel vocal
	co_ch_vo = False
	for x in bot.voice_clients:
		if(x.guild == ctx.message.guild):
			co_ch_vo = True
	if co_ch_vo == False:
		channel = ctx.message.author.voice.channel
		player = await channel.connect()
		os.remove('song.mp3')
	#jouer de la musique
	guild = ctx.message.guild


	ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
	}
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		ydl.download([url])
	for file in os.listdir("./"):
		if file.endswith(".mp3"):
			os.rename(file, 'song.mp3')

	player.play(discord.FFmpegPCMAudio('song.mp3'))
	players[guild.id] = player
	print('done')

@bot.command()
async def arrete(ctx):
	global player
	player = None
	guild = ctx.message.guild.voice_client
	await guild.disconnect()
	os.remove('song.mp3')

'''------------------------------------------commande help-------------------------------------'''
@bot.command()
async def help(ctx):
	texte = "insulte\n"
	texte += "version\n"
	texte += "presentation\n"
	embed = discord.Embed(
		description = texte,
		colour = discord.Colour.blue()
	)
	embed.set_author(name='Commande HELP')

	await ctx.send(embed=embed)
	
bot.run(str(os.environ.get('TOKEN')))
