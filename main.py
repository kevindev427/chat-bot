import logging
from logging.handlers import RotatingFileHandler
import random
import time
import platform
import datetime
import os
import sys
import xml.etree.ElementTree as ET
from pytz import timezone
from io import UnsupportedOperation
from collections import Counter
import asyncio
import aiohttp
import discord
from discord.ext import commands
import loadconfig

__version__ = '0.8.4'
__cogs__ = [
    'cogs.mod',
    'cogs.fun',
    'cogs.anime'
    ]

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(filename='discordbot.log', maxBytes=1024, encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

description = '''Der-Eddys deutscher Discord Bot, programmiert mit Discord.py'''
bot = commands.Bot(command_prefix=loadconfig.__prefix__, description=description)

def _currenttime():
    return datetime.datetime.now(timezone('Europe/Berlin')).strftime("%H:%M:%S")

def _getRoles(roles):
    string = ''
    for r in roles:
        if not r.is_everyone:
            string += '{}, '.format(r.name)
    if string is '':
        return 'None'
    else:
        return string[:-2]

async def _randomGame():
    #Check games.py to change the list of "games" to be played
    while True:
        await bot.change_presence(game=discord.Game(name=random.choice(loadconfig.__games__)))
        await asyncio.sleep(loadconfig.__gamesTimer__)

@bot.event
async def on_ready():
    print('Logged in as')
    print('Bot-Name: {}'.format(bot.user.name))
    print('Bot-ID: {}'.format(bot.user.id))
    print('------')
    for cog in __cogs__:
        try:
            bot.load_extension(cog)
        except Exception:
            print('Couldn\'t load cog {}'.format(cog))
    bot.commands_used = Counter()
    asyncio.ensure_future(_randomGame())

@bot.event
async def on_command(command, ctx):
    bot.commands_used[command.name] += 1
    msg = ctx.message
    if msg.channel.is_private:
        destination = 'Private Message'
    else:
        destination = '#{0.channel.name} ({0.server.name})'.format(msg)
    logging.info('{0.timestamp}: {0.author.name} in {1}: {0.content}'.format(msg, destination))

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    if member.server.id == loadconfig.__botserverid__:
        memberExtra = '{0} - *{1} ({2})*'.format(member.mention, member, member.id)
        await bot.send_message(bot.get_channel(loadconfig.__botlogchannel__), '`[{0}]` **:white_check_mark:** {1} tritt dem Server {2} bei'.format(_currenttime(), memberExtra, member.server))
        if __greetmsg__ == 'True':
            emojis = [':wave:', ':congratulations:', ':wink:', ':new:', ':cool:', ':white_check_mark:', ':tada:']
            await bot.send_message(member.server.default_channel, '{0} Willkommen {1} auf Der-Eddys Discord Server! Für weitere Informationen, wie unsere nsfw Channel :underage: , besuche unseren <#165973433086115840> Channel.'.format(random.choice(emojis), member.mention))

@bot.event
async def on_member_remove(member):
    if member.server.id == loadconfig.__botserverid__:
        memberExtra = '{0} - *{1} ({2})*'.format(member.mention, member, member.id)
        await bot.send_message(bot.get_channel(loadconfig.__botlogchannel__), '`[{0}]` **:x:** {1} verließ den Server {2}'.format(_currenttime(), memberExtra, member.server))

@bot.event
async def on_server_join(server):
    serverExtra = '{0} - *Besitzer: {1} - Benutzer: {2} ({3})*'.format(server.name, server.owner, server.member_count, server.id)
    await bot.send_message(bot.get_channel(loadconfig.__botlogchannel__), '`[{0}]` **:white_check_mark:** Server {1} hinzugefügt'.format(_currenttime(), serverExtra))

@bot.event
async def on_server_remove(server):
    serverExtra = '{0} - *Besitzer: {1} - Benutzer: {2} ({3})*'.format(server.name, server.owner, server.member_count, server.id)
    await bot.send_message(bot.get_channel(loadconfig.__botlogchannel__), '`[{0}]` **:x:** Server {1} entfernt'.format(_currenttime(), serverExtra))

@bot.event
async def on_message_delete(message):
    member = message.author
    if member.server.id == loadconfig.__botserverid__:
        if not member.bot and not message.content.startswith(loadconfig.__prefix__) and not message.channel is bot.get_channel(loadconfig.__botlogchannel__): #Ignore messages from bots, commands and log channel, my test bot also uses the ; prefix
            memberExtra = '**{0} |** {1} *({2} - {3})*'.format(message.channel.mention, member, member.id, member.server)
            await bot.send_message(bot.get_channel(loadconfig.__botlogchannel__), '`[{0}]` **:warning:** {1} löschte die Nachricht:\n ```{2}```'.format(_currenttime(), memberExtra, message.content))

@bot.event
async def on_message_edit(before, after):
    member = before.author
    if member.server.id == loadconfig.__botserverid__:
        if not member.bot and not before.content.startswith(loadconfig.__prefix__) and not before.content.startswith(';') and not after.edited_timestamp is None and not before.channel is bot.get_channel(loadconfig.__botlogchannel__): #Ignore messages from bots, commands and log channel
            memberExtra = '**{0} |** {1} *({2} - {3})*'.format(before.channel.mention, member, member.id, member.server)
            beforeContent = '**Before** - {0} ({1}):```{2}```'.format(before.author, before.timestamp, before.content)
            afterContent = '**After** - {0} ({1}):```{2}```'.format(after.author, after.edited_timestamp, after.content)
            await bot.send_message(bot.get_channel(loadconfig.__botlogchannel__), '`[{0}]` **:information_source:** {1} änderte die Nachricht:\n {2} \n {3}'.format(_currenttime(), memberExtra, beforeContent, afterContent))

@bot.event
async def on_member_update(before, after):
    if before.server.id == loadconfig.__botserverid__:
        memberExtra = '**{0} |** {1} *({2} - {3})*'.format(before.mention, before, before.id, before.server)
        if len(before.roles) is not len(after.roles):
            await bot.send_message(bot.get_channel(loadconfig.__botlogchannel__), '`[{0}]` **:warning:** {1} Rollen wurden geändert:\n **Before:** `{2}`\n **After:** `{3}`'.format(_currenttime(), memberExtra, _getRoles(before.roles), _getRoles(after.roles)))
        elif before.nick is not after.nick:
            await bot.send_message(bot.get_channel(loadconfig.__botlogchannel__), '`[{0}]` **:information_source:** {1} Nickname wurde geändert:\n **Before:** `{2}`\n **After:** `{3}`'.format(_currenttime(), memberExtra, before.nick, after.nick))
        elif before.avatar_url is not after.avatar_url and False:
            await bot.send_message(bot.get_channel(loadconfig.__botlogchannel__), '`[{0}]` **:information_source:** {1} Avatar wurde geändert:\n **Before:** {2}\n **After:** {3}'.format(_currenttime(), memberExtra, before.avatar_url, after.avatar_url))

@bot.event
async def on_member_ban(member):
    if member.server.id == loadconfig.__botserverid__:
        memberExtra = '{0} - *{1} ({2})*'.format(member.mention, member, member.id)
        await bot.send_message(bot.get_channel(loadconfig.__botlogchannel__), '`[{0}]` **:customs:** {1} wurde gebannt auf Server {2}'.format(_currenttime(), memberExtra, member.server))

@bot.event
async def on_member_unban(member):
    if member.server.id == loadconfig.__botserverid__:
        memberExtra = '{0} - *{1} ({2})*'.format(member.mention, member, member.id)
        await bot.send_message(bot.get_channel(loadconfig.__botlogchannel__), '`[{0}]` **:negative_squared_cross_mark:** {1} wurde entbannt auf Server {2}'.format(_currenttime(), memberExtra, member.server))

@bot.command(aliases=['s', 'uptime', 'up'])
async def status():
    '''Infos über den Bot'''
    timeUp = time.time() - startTime
    hours = timeUp / 3600
    minutes = (timeUp / 60) % 60
    seconds = timeUp % 60

    admin = ''
    users = 0
    channel = 0
    for s in bot.servers:
        users += len(s.members)
        channel += len(s.channels)
        if not admin: admin = s.get_member(loadconfig.__adminid__)

    msg = '**:information_source:** Informationen über diesen Bot:\n'
    msg += '```Admin                : @%s\n' % admin
    msg += 'Uptime               : {0:.0f} Stunden, {1:.0f} Minuten und {2:.0f} Sekunden\n'.format(hours, minutes, seconds)
    msg += 'Benutzer / Server    : %s in %s Server\n' % (users, len(bot.servers))
    msg += 'Beobachtete Channel  : %s Channel\n' % channel
    msg += 'Beobachtete Messages : %s Messages\n' % len(bot.messages)
    msg += 'Ausgeführte Commands : %s Commands\n' % sum(bot.commands_used.values())
    msg += 'Bot Version          : %s\n' % __version__
    msg += 'Discord.py Version   : %s\n' % discord.__version__
    msg += 'Python Version       : %s\n' % platform.python_version()
    msg += 'GitHub               : https://github.com/Der-Eddy/discord_bot```'
    await bot.say(msg)

@bot.command()
async def commands():
    '''Zeigt an wie oft welcher Command benutzt wurde seit dem letzten Startup'''
    msg = ':chart: Liste der ausgeführten Befehle (seit letztem Startup)\n'
    msg += 'Insgesamt: {}\n'.format(sum(bot.commands_used.values()))
    msg += '```js\n'
    msg += '{!s:15s}: {!s:>4s}\n'.format('Name', 'Anzahl')
    chart = sorted(bot.commands_used.items(), key=lambda t: t[1], reverse=True)
    for name, amount in chart:
        msg += '{!s:15s}: {!s:>4s}\n'.format(name, amount)
    msg += '```'
    await bot.say(msg)

@bot.command(pass_context=True, aliases=['p'])
async def ping(ctx):
    '''Misst die Response Time'''
    ping = ctx.message
    pong = await bot.say('**:ping_pong:** Pong!')
    delta = pong.timestamp - ping.timestamp
    delta = int(delta.total_seconds() * 1000)
    await bot.edit_message(pong, '**:ping_pong:** Pong! (%d ms)' % delta)

@bot.command(pass_context=True, aliases=['info', 'github', 'trello'])
async def about(ctx):
    '''Info über mich'''
    msg = '**:information_source: Shinobu Oshino (500 Jahre alt)**\n'
    msg += '```Shinobu Oshino gehört wohl zu den mysteriösesten Charakteren in Bakemonogatari. Sie war bis vorletzten Frühling ein hochangesehener, adeliger, skrupelloser Vampir, der weit über 500 Jahre alt ist. Gnadenlos griff sie Menschen an und massakrierte sie nach Belieben. Auch Koyomi Araragi wurde von ihr attackiert und schwer verwundet. Nur durch das Eingreifen des Exorzisten Meme Oshino konnte Kiss-shot Acerola-orion Heart-under-blade, wie sie damals bekannt war, bezwungen werden. Dabei verlor sie jedoch all ihre Erinnerungen und wurde von einer attraktiven, erwachsenen Frau in einen unschuldigen Mädchenkörper verwandelt.\n\n'
    msg += 'Seitdem lebt sie zusammen mit Meme in einem verlassenen Gebäude und wurde von ihm aufgenommen. Er gab ihr auch ihren Namen Shinobu. Wann immer man Shinobu sehen sollte, sitzt sie nur mit traurigem Gesicht in einer Ecke und träumt vor sich hin. Sie spricht nicht und wirkt auch sonst meistens sehr abwesend. Einzig und allein zu Koyomi scheint sie ein freundschaftliches Verhältnis zu haben. Das Vampirblut in ihr verlangt immer noch nach Opfern und da sich Koyomi in gewisser Art und Weise schuldig fühlt, stellt er sich regelmäßig als Nahrungsquelle für Shinobu zur Verfügung.\n\n'
    msg += 'Quelle: http://www.anisearch.de/character/6598,shinobu-oshino/```\n\n'
    msg += 'Dieser Bot ist außerdem **:free:**, Open-Source, in Python und mit Hilfe von discord.py geschrieben! <https://github.com/Der-Eddy/discord_bot>\n'
    msg += 'Neueste Neuerungen immer zuerst auf unserem Trello Board! <https://trello.com/b/Kh8nfuBE/discord-bot-shinobu-chan>'
    with open('img/ava.png', 'rb') as f:
        await bot.send_file(ctx.message.channel, f, content=msg)

@bot.command(pass_context=True, aliases=['archive'])
async def log(ctx, *limit:int):
    '''Archiviert den Log des derzeitigen Channels und läd diesen auf gist hoch

    Beispiel:
    -----------

    :log 100
    '''
    try:
        limit = int(limit[0])
    except IndexError:
        limit = 1000
    logFile = '{}.log'.format(ctx.message.channel)
    counter = 0
    with open(logFile, 'w', encoding='UTF-8') as f:
        f.write('Archivierte Nachrichten vom Channel: {} am {}\n'.format(ctx.message.channel, ctx.message.timestamp.strftime('%d.%m.%Y %H:%M:%S')))
        async for message in bot.logs_from(ctx.message.channel, limit=limit, before=ctx.message):
            try:
                attachment = '[Angehängte Datei: {}]'.format(message.attachments[0]['url'])
            except IndexError:
                attachment = ''
            f.write('{} {!s:20s}: {} {}\n'.format(message.timestamp.strftime('%d.%m.%Y %H:%M:%S'), message.author, message.clean_content, attachment))
            counter += 1
    msg = ':ok: {} Nachrichten wurden archiviert!'.format(counter)
    with open(logFile, 'rb') as f:
        await bot.send_file(ctx.message.channel, f, content=msg)
    os.remove(logFile)

@bot.command(pass_context=True)
async def echo(ctx, *message):
    '''Gibt ne Nachricht aus'''
    msg = '**:mega:** ' + ' '.join(message)
    await bot.say(msg)
    await bot.delete_message(ctx.message)

@bot.command()
async def invite():
    '''Verschickt einen Invite für den Server des Bot Autors'''
    permInvite = 'https://discord.gg/kPMbPDc'
    msg = '**:cool:** ' + permInvite
    await bot.say(msg)

@bot.command()
async def whois(member: discord.Member = None):
    '''Gibt Informationen über einen Benutzer aus

    Beispiel:
    -----------

    :whois @Der-Eddy#6508
    '''

    if member.top_role.is_everyone:
        topRole = 'everyone aka None' #to prevent @everyone spam
        topRoleColour = '#000000'
    else:
        topRole = member.top_role
        topRoleColour = member.top_role.colour

    if member is not None:
        msg = '**:information_source:** Informationen über %s:\n' % member
        msg += '```General              : %s\n' % member
        msg += 'Name                 : %s\n' % member.name
        msg += 'Server Nickname      : %s\n' % member.display_name
        msg += 'Discriminator        : %s\n' % member.discriminator
        msg += 'ID                   : %s\n' % member.id
        msg += 'Bot Account?         : %s\n' % member.bot
        msg += 'Avatar               : %s\n' % member.avatar_url
        msg += 'Erstellt am          : %s\n' % member.created_at
        msg += 'Server beigetreten am: %s\n' % member.joined_at
        msg += 'Rollenfarbe          : %s (%s)\n' % (topRoleColour, topRole)
        msg += 'Status               : %s\n' % member.status
        msg += 'Rollen               : %s```' % _getRoles(member.roles)
    else:
        msg = '**:no_entry:** Du hast keinen Benutzer angegeben!'
    await bot.say(msg)

@bot.command(aliases=['epvp'])
async def epvpis(*user: str):
    '''Sucht nach einem Benutzernamen auf Elitepvpers

    Beispiel:
    -----------

    :epvpis Der-Eddy
    '''
    user = ' '.join(user)
    url = 'https://www.elitepvpers.com/forum/ajax.php?do=usersearch'
    payload = {
        'do': 'usersearch',
        'fragment': user
    }
    async with aiohttp.post(url, data=payload) as r:
        if r.status == 200:
            root = ET.fromstring(await r.text())
            if len(root) > 0:
                msg = ':ok: Ich konnte {} Accounts finden!\n```'.format(len(root))
                for i in root:
                    userURL = 'https://www.elitepvpers.com/forum/member.php?u=' + i.attrib['userid']
                    msg += '{:15} | {}\n'.format(i.text, userURL)
                msg += '```'
            else:
                msg = ':no_entry: Ich konnte keine Epvp Accounts finden :sweat:'
            await bot.say(msg)

@bot.command(pass_context=True, aliases=['e'])
async def emoji(ctx, emojiname: str):
    '''Gibt eine vergrößerte Version eines angegebenen Emojis zurück

    Beispiel:
    -----------

    :emoji Emilia
    '''
    emoji = discord.utils.get(bot.get_all_emojis(), name=emojiname)
    if emoji:
        tempEmojiFile = 'tempEmoji.png'
        async with aiohttp.get(emoji.url) as img:
            with open(tempEmojiFile, 'wb') as f:
                f.write(await img.read())
        with open(tempEmojiFile, 'rb') as f:
            await bot.send_file(ctx.message.channel, f)
        os.remove(tempEmojiFile)
    else:
        await bot.say(':x: Konnte das angegebene Emoji leider nicht finden :(')

@bot.command(pass_context=True, hidden=True, aliases=['quit_backup'])
async def shutdown_backup(ctx):
    '''Fallback if mod cog couldn't load'''
    if ctx.message.author.id == loadconfig.__adminid__:
        await bot.say('**:ok:** Bye!')
        bot.logout()
        sys.exit(0)
    else:
        await bot.say('**:no_entry:** Du bist nicht mein Bot Besitzer!')

if __name__ == '__main__':
    startTime = time.time()
    bot.run(loadconfig.__token__)
