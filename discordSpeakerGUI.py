import asyncio
import discord
import datetime
import PySimpleGUI as sg
import requests
import io
from PIL import Image, ImageTk

def get_img_data(f, maxsize=(800, 640), first=False):
    """Generate image data using PIL"""
    img = Image.open(f)
    img.thumbnail(maxsize)
    if first:
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)

def get_channels_guild(client, guild):

    connectedGuild = client.get_guild(guild)

    all_Channels = connectedGuild.channels

    clientUser = connectedGuild.get_member(client.user.id)

    text_channels = {}

    for i in all_Channels:
        if isinstance(i, discord.TextChannel):
            if i.permissions_for(clientUser).send_messages:
                text_channels[i.name] = i.id

    return text_channels

def all_channels(client):
    guildchannels = [i.channels for i in client.guilds]
    all_textChannels = {}
    for i in guildchannels:
        for j in i:
            if isinstance(j, discord.TextChannel):
                all_textChannels[j.name] = j.id
    return all_textChannels

async def all_users(client):
    guilds = client.guilds

    total = []

    for i in client.guilds:
        async for j in i.fetch_members():
            if j.id not in total:
                total.append(j.id)

    return len(total)

def get_guilds(client):
    all_guilds = {}
    for i in client.guilds:
        all_guilds[i.name] = i.id
    return all_guilds


async def menu(client):
    sg.theme('DarkAmber')

    guilds = get_guilds(client)

    guildNames = [i for i in guilds.keys()]

    channels = all_channels(client)

    userCount = await all_users(client)

    emojis = {}
    for i in client.emojis:
        emojis[i.name] = {"Url" : i.url, "Emoji" : i}

    emojiNames = [i for i in emojis.keys()]

    discordMessageTab = [
        [
            sg.Multiline(size=(70, 15), scrollbar=False, key="-MESSAGECONTENT-"),
            sg.VerticalSeparator(),
            sg.Column([
                [
                    sg.Listbox(emojiNames, size= (20, 8), no_scrollbar=True, enable_events=True, key="-EMOJISELECTED-")
                ],
                [
                    sg.Button("Add Emoji")
                ]
            ]
            ),
            sg.VerticalSeparator(),
            sg.Image(size=(128, 128), key="-EMOJIIMAGE-")
        ],
        [
            sg.Button("Send Message"),
        ]
    ]
    discordEmbedTab = [
        [
            sg.Column(
            [
                [
                    sg.InputText("Title", size=(80, 1), key="-EMBEDTITLE-")
                ],
                [
                    sg.Multiline("Description" ,size=(80, 7), scrollbar=False, key="-EMBEDDESC-"),
                    sg.VerticalSeparator(),
                    sg.Column(
                    [
                        [
                            sg.Text("Red", size=(5, 1)),
                            sg.InputText("0", size=(3, 1), key="-EMBEDRED-")
                        ],
                        [
                            sg.Text("Green", size=(5, 1)),
                            sg.InputText("0", size=(3, 1), key="-EMBEDGREEN-")
                        ],
                        [
                            sg.Text("Blue", size=(5, 1)),
                            sg.InputText("0", size=(3, 1), key="-EMBEDBLUE-")
                        ],
                        [
                            sg.Checkbox("Random Colour", size=(11, 1), key="-EMBEDRANDOMCOLOUR-")
                        ]
                    ]
                    )
                ],
                [
                    sg.InputText("Image Link", size=(80, 1), key="-EMBEDIMAGE-")
                ],
                [
                    sg.InputText("Footer Image Link", size=(80, 1), key="-EMBEDFOOTERIMAGE-")
                ],
                [
                    sg.InputText("Footer", size=(80, 1), key="-EMBEDFOOTER-"),
                    sg.VerticalSeparator(),
                    sg.Checkbox("Default Footer", key="-DEFAULTFOOTER-")
                ],
                [
                    sg.Checkbox("Timestamp", size=(80, 1), key="-EMBEDTIMESTAMP-")
                ]
            ]
            )
        ],
        [
            sg.Button("Send Embed"),
        ]
    ]

    myLayout = [
        [
            sg.TabGroup(
            [
                [
                    sg.Tab("Discord",
                    [
                        [
                            sg.Listbox(guildNames, no_scrollbar = True, enable_events=True, size=(40, 5), key="-GUILDCHOICE-"),
                            sg.VerticalSeparator(),
                            sg.Listbox([], no_scrollbar = True, size=(40, 5), enable_events=True, key="-CHANNELS-"),
                            sg.VerticalSeparator(),
                            sg.Column(
                            [
                                [
                                    sg.Text("Guild Count:"),
                                    sg.Text(len(guilds))
                                ],
                                [
                                    sg.Text("Channel Count:"),
                                    sg.Text(len(channels))
                                ],
                                [
                                    sg.Text("User Count:"),
                                    sg.Text(userCount)
                                ]
                            ]
                            )

                        ],
                        [
                            sg.Multiline(size=(40, 20), write_only=True, key="-CHANNELHISTORY-"),
                            sg.VerticalSeparator(),
                            sg.TabGroup(
                            [
                                [
                                    sg.Tab("Message", discordMessageTab),
                                    sg.Tab("Embed", discordEmbedTab)
                                ]
                            ]
                            )
                        ]
                    ]
                    )
                ]
            ]
            )
        ],
        [
            sg.Button("Close")
        ]
    ]

    myWindow = sg.Window("Discord Bot GUI", myLayout)

    while True:
        event, values = myWindow.read()

        if event == sg.WIN_CLOSED or event == "Close":
            break

        if event == "Add Emoji":
            if len(values["-EMOJISELECTED-"]) < 1:
                continue
            emoji = emojis[values["-EMOJISELECTED-"][0]]["Emoji"]
            message = values["-MESSAGECONTENT-"]
            message += str(emoji)
            myWindow["-MESSAGECONTENT-"].update(message)


        if event == "-EMOJISELECTED-":
            url = emojis[values["-EMOJISELECTED-"][0]]["Url"]
            response = requests.get(url,stream=True)
            image_data = get_img_data(response.raw,first=True)
            myWindow["-EMOJIIMAGE-"].update(data=image_data)

        if event == "Send Message":
            if len(values["-GUILDCHOICE-"]) < 1 or len(values["-CHANNELS-"]) < 1:
                continue
            channel = client.get_channel(channels[values["-CHANNELS-"][0]])
            await channel.send(values["-MESSAGECONTENT-"])

        if event == "Send Embed":
            if len(values["-GUILDCHOICE-"]) < 1 or len(values["-CHANNELS-"]) < 1:
                continue
            embed = discord.Embed(title=values["-EMBEDTITLE-"], description=values["-EMBEDDESC-"])
            embed.set_image(url=values["-EMBEDIMAGE-"])
            if values["-DEFAULTFOOTER-"]:
                embed.set_footer(text=client.user.name, icon_url=client.user.avatar_url)
            else:
                embed.set_footer(text=values["-EMBEDFOOTER-"], icon_url=values["-EMBEDFOOTERIMAGE-"])
            if values["-EMBEDRANDOMCOLOUR-"]:
                embed.colour = discord.Colour.random()
            else:
                try:
                    embed.colour = discord.Colour.from_rgb(int(values["-EMBEDRED-"]), int(values["-EMBEDGREEN-"]), int(values["-EMBEDBLUE-"]))
                except:
                    embed.colour = discord.Colour.from_rgb(0, 0, 0)
            if values["-EMBEDTIMESTAMP-"]:
                embed.timestamp = datetime.datetime.utcnow()
            channel = client.get_channel(channels[values["-CHANNELS-"][0]])
            await channel.send(embed=embed)

        if event == "-GUILDCHOICE-":
            if values["-GUILDCHOICE-"][0] in guilds:
                channels = get_channels_guild(client, guilds[values["-GUILDCHOICE-"][0]])
                myWindow["-CHANNELS-"].update(values=channels)
            else:
                continue

        if event == "-CHANNELS-":
            channel = client.get_channel(channels[values["-CHANNELS-"][0]])
            channelStr = ""
            async for message in channel.history():
                channelStr += "{}: {}\n".format(message.author.name, message.clean_content)
            myWindow["-CHANNELHISTORY-"].update(channelStr)


    myWindow.close()
