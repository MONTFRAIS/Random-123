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
import recherche_youtube_titre

api = str(os.environ.get('RIOT_KEY'))
bot = commands.Bot(command_prefix='!')
bot.remove_command('help')
players = {}
queues = {}
queues_titre = {}
fichier_music_att = {}
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
def suppr_apartir(txt, c):
	tmp =""
	for i in txt:
		tmp+=i
		if i == c :
			return tmp
	return tmp

def check_queue(ctx, guild):
	i = guild.id
	if queues[i] != []:

		queues[i].pop(0)
		queues_titre[i].pop(0)
		fichier_music_att[i].pop(0)

		if queues[i] != []:
			url = queues[i][0]
			titre = queues_titre[i][0]
			modif_fichiers_att(i)

			#son suivant
			players[i].play(discord.FFmpegPCMAudio('./music_bot_systeme/suiv.mp3'), after=lambda e: players[i].stop())

			joue_url(ctx, guild, url)

		
def add_queue(ctx, guild, url):
	if guild.id in queues and queues[guild.id] != []:
		queues[guild.id].append(url)
		queues_titre[guild.id].append(recherche_youtube_titre.main(url))
		fichier_music_att[guild.id].append('song'+str(guild.id)+'__'+str(len(queues[guild.id]) - 1)+'__.mp3')

		telecharge_musique(url, guild, len(queues[guild.id]) - 1)
	else:
		queues[guild.id] = [url]
		queues_titre[guild.id] = [recherche_youtube_titre.main(url)]
		fichier_music_att[guild.id] = ['song'+str(guild.id)+'__'+str(len(queues[guild.id]) - 1)+'__.mp3']

		joue_url(ctx, guild, url, "prems")
		
def modif_fichiers_att(id):

	with os.scandir("./") as fichiers:
		for fichier in fichiers:
			if fichier.name == 'song'+str(id)+'__0__.mp3':
				os.remove('song'+str(id)+'__0__.mp3')

	for nb_fichier in range(len(fichier_music_att[id])):

		nv_nom = 'song'+str(id)+'__'+str(nb_fichier - 1)+'__.mp3'

		with os.scandir("./") as fichiers:
			for fichier in fichiers:
				if fichier.name == fichier_music_att[id][nb_fichier]:
					os.rename(fichier, nv_nom)
					fichier_music_att[id][nb_fichier] = nv_nom




def cherche_mot(txt, mot):
	succes = False
	for i in range(len(txt)):
		nb_suite = 0
		if txt[i] == mot[0]:
			nb_suite +=1
			for j in range(len(mot)):
				if i+j < len(txt):
					if txt[i+j] == mot[j] and j != 0:
						nb_suite +=1
		if nb_suite == len(mot):
			succes = True
	return succes

def check_musique_suiv():
	musique_suiv = '__0__.mp3'
	with os.scandir("./") as fichiers:
		for fichier in fichiers:
			succes = cherche_mot(fichier.name, musique_suiv)
			if succes == True:
				return True
	return False

	

def non_playlist(url):
	succes = False
	block_playlist = "list"
	#blocage des playlist par detection de la presence du mot "list" dans l'url
	succes = cherche_mot(url, block_playlist)
	return succes

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

def telecharge_musique(url, guild, nb=0):
	ydl_opts = {
		'audioformat' : "mp3",
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
			os.rename(file, 'song'+str(guild.id)+'__'+str(nb)+'__.mp3')	

def joue_url(ctx, guild, url, num="ok"):
	#suppr ancien fichier
	if num == "prems":
		with os.scandir("./") as fichiers:
			for fichier in fichiers:
				if fichier.name == 'song'+str(guild.id)+'__0__.mp3':
					os.remove('song'+str(guild.id)+'__0__.mp3')

	#jouer de la musique / dl si pas deja dl en avance
	if check_musique_suiv() == False:
		telecharge_musique(url, guild)
	else :
		print('suivant lancer --------------->')

	players[guild.id].stop()
	players[guild.id].play(discord.FFmpegPCMAudio('song'+str(guild.id)+'__0__.mp3'), after=lambda e: check_queue(ctx, guild))
		
	print('done')

async def join(ctx, guild):
		# join un channel vocal ou pas
	connecter_channel_vo = False
	for x in bot.voice_clients:
		if(x.guild == ctx.message.guild):
			connecter_channel_vo = True
	if connecter_channel_vo == False:
		channel = ctx.message.author.voice.channel
		player = await channel.connect()
	#ajout du player si nv
	if connecter_channel_vo == False :
		players[guild.id] = player
		#teste si fichier music deja existant si oui suppression

		'''-------------------------obselete-------------------------------------------'''
		with os.scandir("./") as fichiers:
			for fichier in fichiers:
				if fichier.name == 'song'+str(guild.id)+'.mp3':
					os.remove('song'+str(guild.id)+'.mp3')


@bot.command()
async def joue(ctx, url, *, content=""):
	#variable utile dans tout la def
	guild = ctx.message.guild
	titre = "Music"

	if lien_youtube_valide(str(url)) :

		if non_playlist(url) == True:
			url=suppr_apartir(url, "&")
			await ctx.send("C'est une playliste seul la première a été récuperé")

		await envoi(ctx, titre, "Preparation : "+str(recherche_youtube_titre.main(url)))

		await join(ctx, guild)

		add_queue(ctx, guild, url)

		await ctx.channel.purge(limit=1)

		await envoi(ctx, titre, "Lancement de : \n"+str(recherche_youtube_titre.main(url)))

	else :
		recherche_music = str(url)+" "+content
		url_trouver, titreMusic = recherche_youtube.main(recherche_music)
		url_trouver = "https://www.youtube.com"+url_trouver

		if non_playlist(url_trouver) == True:
			url_trouver=suppr_apartir(url_trouver, "&")
			await ctx.send("C'est une playliste seul la première a été récuperé")

		await envoi(ctx, titre, "Preparation : ["+titreMusic+"]("+url_trouver+")")

		await join(ctx, guild)

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
async def next(ctx):
	guild = ctx.message.guild
	if (players[guild.id] != None):
		players[guild.id].stop()

@bot.command()
async def queue(ctx):
	guild = ctx.message.guild
	texte = ""
	titreM = "Music Queue"
	for titre in queues_titre[guild.id]:
		texte += titre+"\n"
	await envoi(ctx, titreM, texte)

@bot.command()
async def fichier(ctx):
	guild = ctx.message.guild
	texte = ""
	titreM = "Music Queue"
	with os.scandir("./") as fichiers:
			for fichier in fichiers:
				texte += fichier.nom
	await envoi(ctx, titreM, texte)

@bot.command()
async def purgeQueue(ctx):
	guild = ctx.message.guild
	if (players[guild.id] != None):
		players[guild.id].stop()

		queues[guild.id] = []
		queues_titre[guild.id] = []
		fichier_music_att[guild.id] = []

		for fichier in os.listdir("./"):
			if fichier.endswith(".mp3"):
				os.remove(fichier.name)

@bot.command()
async def arrete(ctx):
	guild = ctx.message.guild
	if (players[guild.id] != None):
		players[guild.id].stop()
		guild_voice = ctx.message.guild.voice_client
		await guild_voice.disconnect()

		queues[guild.id] = []
		queues_titre[guild.id] = []
		fichier_music_att[guild.id] = []

		for fichier in os.listdir("./"):
			if fichier.endswith(".mp3"):
				os.remove(fichier.name)

'''------------------------------------------commande help-------------------------------------'''
@bot.command()
async def help(ctx):
	texte = "---------------------\n"
	texte += "insulte\n"
	texte += "joue\n"
	texte += "arrete\n"
	texte += "pause\n"
	texte += "resume\n"
	texte += "next\n"
	texte += "purgeQueue\n"
	texte += "presentation\n"
	texte += "---------------------\n"
	texte += "Version : 8.0\n"
	titre = 'Commande HELP'

	await envoi(ctx, titre, texte)
	
bot.run(str(os.environ.get('TOKEN')))
