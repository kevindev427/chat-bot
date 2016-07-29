import discord
from discord.ext import commands
import asyncio
import aiohttp
import random

class fun():
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def cookie(self):
        '''Keks'''
        await self.bot.say(':cookie:')

    @commands.command()
    async def praise(self):
        '''Praise the Sun'''
        await self.bot.say('https://i.imgur.com/K8ySn3e.gif')

    @commands.command()
    async def java(self):
        '''Weil Java != Javscript'''
        await self.bot.say(':interrobang: Meintest du jQuery, Javascript oder Node.js? https://abload.de/img/2016-05-102130191kzpu.png')

    @commands.command()
    async def praise(self):
        '''Praise the Sun'''
        await self.bot.say('https://i.imgur.com/K8ySn3e.gif')

    @commands.command()
    async def css(self):
        '''Counter Strike: Source'''
        await self.bot.say('http://i.imgur.com/TgPKFTz.gif')

    @commands.command()
    async def countdown(self):
        '''It's the final countdown'''
        countdown = ['five', 'four', 'three', 'two', 'one']
        for num in countdown:
            await self.bot.say(':{0}:'.format(num))
            await asyncio.sleep(1)
        await self.bot.say(':ok: DING DING DING')

    @commands.command()
    async def neko(self):
        '''Zufällige Katzen Bilder nyan~'''
        #http://discordpy.readthedocs.io/en/latest/faq.html#what-does-blocking-mean
        async with aiohttp.get('http://random.cat/meow') as r:
            if r.status == 200:
                js = await r.json()
                emojis = [':cat2: ', ':cat: ', ':heart_eyes_cat: ']
                msg = random.choice(emojis) + js['file']
                await self.bot.say(msg)


    @commands.command(pass_context=True)
    async def random(self, ctx, *arg):
        '''Gibt eine zufällige Zahl aus'''
        if not arg:
            start = 0
            end = 100
        elif len(arg) == 1:
            start = 0
            end = int(arg[0])
        elif len(arg) > 1:
            start = int(arg[0])
            end = int(arg[1])
        await self.bot.say(':arrows_counterclockwise: Zufällige Zahl ({0} - {1}): {2}'.format(start, end, random.randint(start, end)))

    @commands.command(pass_context=True)
    async def steinigt(self, ctx, *member:str):
        '''Monty Python'''
        await self.bot.say(member + '\nhttps://media.giphy.com/media/l41lGAcThnMc29u2Q/giphy.gif')

def setup(bot):
    bot.add_cog(fun(bot))
