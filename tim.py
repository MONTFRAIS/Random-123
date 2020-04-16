import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient
import asyncio
import os
from random import randint
import youtube_dl
#Code fait pour l'occasion
import recherche_youtube

api = str(os.environ.get('RIOT_KEY'))
bot = commands.Bot(command_prefix='!')
bot.remove_command('help')
players = {}
queues = {}
player = None

@bot.event
async def on_ready():
	await bot.change_presence(activity=discord.Game(name="!help"))
	print("je suis pret")
	print("Je m'appele " + str(bot.user.name))

@bot.event
async def on_command_error(ctx, error):
	titre = ":x: ERREUR :interrobang:"
	texte = ""
	if isinstance(error, commands.MissingRequiredArgument):
		texte = "il manque un argument lors de ton utilisation de cette commande !!!!\n"
		texte += "tu devrais utiliser la commande help pour savoir comment utiliser cette commande"
	elif isinstance(error, commands.CommandNotFound):
		texte = "Commande Invalide ou Inexistante"
	else:
		print(error)
		texte = "une ERREUR s'est produite"

	'''------embed pour affichage erreur--------'''
	await envoi(ctx, titre, texte)

async def envoi(ctx, titre, texte):
	
	embed = discord.Embed(
		description = texte,
		colour = discord.Colour.blue(),
		title = "**"+titre+"**"
	)
	#embed.set_author(name=titre)
	
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
	msg += "cela a été prouvé"
	await ctx.send(msg)
'''------------------------------------------commandes pour la musique-------------------------------------'''
def check_queue(ctx, guild):
	i = guild.id
	if queues[i] != []:
		url = queues[i].pop(0)
		joue_url(ctx, guild, url)
		
def add_queue(ctx, guild, url):
	if guild.id in queues:
		queues[guild.id].append(url)
	else:
		queues[guild.id] = [url]
		joue_url(ctx, guild, url)


def lien_youtube_valide(url):
	succes = True
	lien_valide = "https://www.youtube.com/watch?v="
	if(len(url)<len(lien_valide)):
		succes = False
	else:
		for i in range(len(lien_valide)):
			if url[i] != lien_valide[i]:
				succes = False
	return succes


def joue_url(ctx, guild, url):

	# join un channel vocal ou pas
	connecter_channel_vo = False
	for x in bot.voice_clients:
		if(x.guild == ctx.message.guild):
			connecter_channel_vo = True
	if connecter_channel_vo == False:
		channel = ctx.message.author.voice.channel
		player = await channel.connect()

		#teste si fichier music deja existant si oui suppression

		with os.scandir("./") as fichiers:
			for fichier in fichiers:
				if fichier.name == 'song'+str(guild.id)+'.mp3':
					os.remove('song'+str(guild.id)+'.mp3')

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

	if connecter_channel_vo == False :
		players[guild.id] = player
		
	players[guild.id].play(discord.FFmpegPCMAudio('song'+str(guild.id)+'.mp3'), after=lambda e: check_queue(ctx, guild))
		
	print('done')

	


@bot.command()
async def joue(ctx, url, *, content=""):
	#variable utile dans tout la def
	guild = ctx.message.guild
	titre = "Music"

	if lien_youtube_valide(str(url)) :

		await envoi(ctx, titre, "Preparation : "+str(url))

		add_queue(ctx, guild, url)

		await ctx.channel.purge(limit=1)

		await envoi(ctx, titre, "Lancement de : \n"+str(url))

	else :
		recherche_music = str(url)+" "+content
		url_trouver, titreMusic = recherche_youtube.main(recherche_music)
		url_trouver = "https://www.youtube.com"+url_trouver

		await envoi(ctx, titre, "Preparation : ["+titreMusic+"]("+url_trouver+")")

		add_queue(ctx, guild, url_trouver)

		await ctx.channel.purge(limit=1)

		await envoi(ctx, titre, "Lancement de : ["+titreMusic+"]("+url_trouver+")")
		

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
async def stop(ctx):
	guild = ctx.message.guild
	if (players[guild.id] != None):
		players[guild.id].stop()

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
	texte += "joue\n"
	texte += "arrete\n"
	texte += "pause\n"
	texte += "resume\n"
	texte += "presentation\n"
	texte += "Version : 6.0\n"
	titre = 'Commande HELP'

	await envoi(ctx, titre, texte)
	
bot.run(str(os.environ.get('TOKEN')))
