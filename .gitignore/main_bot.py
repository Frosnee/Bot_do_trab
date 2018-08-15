import discord
import configparser
from discord.utils import get
import asyncio

# Variáveis Globais

votes = {}
already_voted = {}
punished = {}
user_default_roles = {}
config = configparser.ConfigParser()
config.read("bot_config.txt", "utf-8")
punish_quantity = int(config.get("Main", "punish_votes_quantity"))
punished_timeout = int(config.get("Main", "punish_chat_timeout"))
min_punished_timeout = int(config.get("Main", "min_punished_timeout"))
b_w = config.get("Main", "blocked_words")
blocked_words = b_w.split(", ")

client = discord.Client()


async def cr_role(idd):
    print("Creating Role...")
    perms = discord.Permissions(send_messages=False, read_messages=True, connect=False)
    await client.create_role(idd, name="Punished", colour=discord.Color(0xff0033), permissions=perms, hoist=0)
    return True


async def insertUser(mber):
    user_default_roles[str(mber)] = []
    for i in mber.roles:
        await asyncio.sleep(0.2)
        g = get(mber.server.roles, name="{}".format(str(i)))
        user_default_roles[str(mber)].append(str(i))
        print(user_default_roles)
        await client.remove_roles(mber, g)

    role = get(mber.server.roles, name="Punished")
    await client.add_roles(mber, role)


async def cant_vote(punisher, victim):
    for i in punisher:
        try:
            if already_voted[punisher] == victim:
                return True
            else:
                return False
        except KeyError:
            pass

async def on_timing(obj):
    print("Tick started!")
    await insertUser(obj)
    while True:
        for i in punished.keys():
            if punished[i] >= 0:
                punished[i] -= 1 * len(punished)
                await asyncio.sleep(1)
                print(punished)
            else:
                print("Retirando {}".format(i))
                rm = get(obj.server.roles, name="Punished")
                await client.remove_roles(obj, rm)
                for old_roles in user_default_roles[str(obj)]:
                    await asyncio.sleep(0.2)
                    old_r = get(obj.server.roles, name="{}".format(old_roles))
                    await client.add_roles(obj, old_r)
                punished.pop(i)
                print("Retirado com Sucesso!")


async def punish(user, obj):
    votes[user] = 0
    punished[user] = punished_timeout
    await on_timing(obj)

async def isListed(name):
    if name in votes:
        return True
    if name not in votes:
        return False

@client.event
async def on_ready():
    welcome_message = "\nLogado como: {} | ID: {}\n".format(client.user.name, client.user.id)
    print(str("-" * len(welcome_message)) + welcome_message + "-" * len(welcome_message))
    servers = client.servers


@client.event
async def on_message(message):
    if message.author.server_permissions.administrator and message.content.startswith("!createrole"):
        await cr_role(message.server)
    else:
        author = message.author
        if "Anti Sequela" not in str(author):
            if any(w in message.content.lower() for w in blocked_words):
                await client.send_message(message.channel,
                                          "``` Usuário {} adicionado a lista de punição Reason:(CHAT SHITING)```".format(
                                              str(author)))
                punished[str(author)] = min_punished_timeout
                await on_timing(message.author)
            elif message.content.startswith("!remain"):
                counter = 1
                embed = discord.Embed(title="Membros Punidos:", color=0x00ff00)
                for buser in punished.keys():
                    embed.add_field(name="-----------------------", inline=True,
                                    value="{} {}s restantes.".format(buser, punished[buser]))
                    counter += 1
                await client.send_message(message.channel, embed=embed)

            if message.content.startswith("!punish"):
                print(str(message.mentions[0]))
                words = message.content.split(" ")
                defendant = message.mentions
                nameid = defendant[0]

                if not await cant_vote(str(author), str(nameid)):
                    if await isListed(str(nameid)) and votes[str(nameid)] < punish_quantity - 1:
                        votes[str(nameid)] += 1
                    elif not await isListed(str(nameid)):
                        votes[str(nameid)] = 1

                    else:
                        await client.send_message(message.channel,
                                                  "```python\n {0}/{0} -> Votação encerrada para @{1}. Usuário punido por {2} segundos! ```".format(
                                                      punish_quantity, str(nameid), str(punished_timeout)))
                        await punish(str(nameid), nameid)
                    already_voted[str(author)] = str(nameid)
                    remains_votes_msg = "```pragma\n{}/{} -> Votação de punição para {}```".format(votes[str(nameid)],
                                                                                                   punish_quantity,
                                                                                                   str(nameid))
                    await client.send_message(message.channel, remains_votes_msg)
                else:
                    userid = message.author.id
                    await client.send_message(message.channel,
                                              "<@{}> Você já votou para punição deste usuário".format(
                                                  userid))


client.run('NDc4NzQ0MDk3Njk2MzgyOTk4.DlPIwQ._Azrk63_AK_HrS0QJVgmzAJnd7k')
