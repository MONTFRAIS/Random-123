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
players = {}

@bot.event
async def on_ready():
	await bot.change_presence(activity=discord.Game(name="!help"))
	print("je suis pret")
	print("Je m'appele " + str(bot.user.name))

@bot.event
async def on_command_error(ctx, error):
	texte = ""
	if isinstance(error, commands.MissingRequiredArgument):
		texte = "il manque un argument lors de ton utilisation de cette commande !!!!\n"
		texte += "tu devrais utiliser la commande help pour savoir comment utiliser cette commande"
	elif isinstance(error, commands.CommandNotFound):
		texte = "Commande Invalide ou Inexistante"
	else:
		texte = "une ERREUR s'est produite"

	'''------embed pour affichage erreur--------'''
	embed = discord.Embed(
		description = texte,
		colour = discord.Colour.blue()
	)
	embed.set_author(name=':x: ERREUR :interrobang:')

	await ctx.send(embed=embed)

'''------------------------------------------commandes normales-------------------------------------'''
@bot.command()
async def insulte(ctx, message):
	table_isultes = []
	nb_alea = randint(0, 310)
	with open("insulte.txt", "r") as f:
		for insulte in f.readlines():
			table_isultes.append(insulte)
	msg = str(message)+"  ->  " + str(table_isultes[nb_alea])
	msg += "cela a ete prouve"
	await ctx.send(msg)
'''------------------------------------------commandes pour la musique-------------------------------------'''
def check_queue(ctx):
	pass

@bot.command()
async def joue(ctx, url):
	#variable utile dans tout la def
	guild = ctx.message.guild

	# join un channel vocal
	co_ch_vo = False
	for x in bot.voice_clients:
		if(x.guild == ctx.message.guild):
			co_ch_vo = True
	if co_ch_vo == False:
		channel = ctx.message.author.voice.channel
		player = await channel.connect()

		#teste si fichier music deja existant si oui suppression

		with os.scandir("./") as fichiers:
			for fichier in fichiers:
				if fichier.name == 'song'+str(guild.id)+'.mp3':
					os.remove('song.mp3')
	
	
	#jouer de la musique


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
			os.rename(file, 'song'+str(guild.id)+'.mp3')

	player.play(discord.FFmpegPCMAudio('song'+str(guild.id)+'.mp3'))
	players[guild.id] = player
	print('done')

@bot.command()
async def pause(ctx):
	guild = ctx.message.guild
	if (players[guild.id] != None):
		players[guild.id].pause()
@bot.command()
async def resume(ctx):
	guild = ctx.message.guild
	if (players[guild.id] != None):
		players[guild.id].resume()

@bot.command()
async def arrete(ctx):
	guild = ctx.message.guild
	if (players[guild.id] != None):
		players[guild.id].stop()
		guild_voice = ctx.message.guild.voice_client
		await guild_voice.disconnect()
		os.remove('song'+str(guild.id)+'.mp3')

'''------------------------------------------commande help-------------------------------------'''
@bot.command()
async def help(ctx):
	texte = "insulte\n"
	texte += "presentation\n"
	texte += "Version : 2.0\n"
	embed = discord.Embed(
		description = texte,
		colour = discord.Colour.blue()
	)
	embed.set_author(name='Commande HELP')

	await ctx.send(embed=embed)
	
bot.run(str(os.environ.get('TOKEN')))
