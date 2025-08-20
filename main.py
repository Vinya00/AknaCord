import os
import asyncio
import discord
from discord.ext import commands
from keep_alive import keep_alive
from minesweeper import MinesweeperGame
from image_renderer import render_board

intents = discord.Intents.default()
intents.message_content = True  # szükséges a prefixelt parancsokhoz

bot = commands.Bot(command_prefix="!akna ", intents=intents, help_command=None)

# Csatornánként egy aktív játék és egy nyilvántartott álláskép
games = {}  # channel_id -> MinesweeperGame
last_board_message = {}  # channel_id -> message_id


async def delete_message_safe(message: discord.Message):
    try:
        await message.delete()
    except Exception:
        pass


async def delete_message_by_id_safe(channel: discord.TextChannel, message_id: int):
    try:
        msg = await channel.fetch_message(message_id)
        await msg.delete()
    except Exception:
        pass


async def purge_old_bot_messages(ctx: commands.Context, limit: int = 50):
    """Törli a csatorna legutóbbi bot-üzeneteit (pl. régi állásképek)."""
    try:
        def _is_bot(msg: discord.Message) -> bool:
            return msg.author == bot.user
        await ctx.channel.purge(limit=limit, check=_is_bot)
    except Exception:
        # Ha nincs jogosultság vagy sikertelen, csendben továbblépünk
        pass


async def send_board_and_cleanup(ctx: commands.Context, game: MinesweeperGame, final: bool = False, force_reveal: bool = False):
    # Előző álláskép törlése, ha van és nem végső állás
    if not final and ctx.channel.id in last_board_message:
        await delete_message_by_id_safe(ctx.channel, last_board_message[ctx.channel.id])

    # Ha final vagy game_over, fedjük fel az egészet
    reveal = force_reveal or game.game_over
    path = render_board(game, reveal=reveal)

    sent = await ctx.send(file=discord.File(path))

    # Fájl törlése küldés után
    try:
        os.remove(path)
    except Exception:
        pass

    if final or game.game_over:
        # Végső állás: ezt nem követjük nyomon (maradjon a csatornában)
        if ctx.channel.id in last_board_message:
            del last_board_message[ctx.channel.id]
    else:
        last_board_message[ctx.channel.id] = sent.id


def parse_xy(arg: str):
    """Felhasználói pozíció 'XxY' -> belső 0-alapú (x, y)."""
    s = arg.lower().strip()
    if "x" not in s:
        raise ValueError("Hibás pozíció formátum. Használd így: 3x4")
    xs, ys = s.split("x", 1)
    x = int(xs)
    y = int(ys)
    if x < 1 or y < 1:
        raise ValueError("A koordináták 1-től indulnak.")
    return x - 1, y - 1


def parse_size(arg: str):
    """Méret 'W x H' -> (width, height), 1-alapú bemenet, pozitív egészek."""
    s = arg.lower().strip()
    if "x" not in s:
        raise ValueError("Hibás méret formátum. Használd így: 10x12")
    ws, hs = s.split("x", 1)
    w = int(ws)
    h = int(hs)
    if w < 1 or h < 1:
        raise ValueError("A méretek 1 vagy nagyobb egészek legyenek.")
    return w, h


@bot.event
async def on_ready():
    print(f"Bejelentkezve: {bot.user}")


@bot.command(name="új")
async def uj(ctx: commands.Context, nehezseg: str, meret: str = None, aknak: int = None):
    try:
        nehezseg = nehezseg.strip().lower()
        if nehezseg not in ["könnyű", "normális", "nehéz", "saját"]:
            await delete_message_safe(ctx.message)
            return

        # Csatorna takarítása: régi bot-üzenetek (pl. korábbi végső álláskép) törlése
        await purge_old_bot_messages(ctx, limit=50)

        if nehezseg == "saját":
            if meret is None or aknak is None:
                await delete_message_safe(ctx.message)
                return
            width, height = parse_size(meret)
            game = MinesweeperGame(width, height, int(aknak))
        else:
            game = MinesweeperGame.from_difficulty(nehezseg)

        games[ctx.channel.id] = game

        await send_board_and_cleanup(ctx, game, final=False)

    except ValueError as e:
        # Rövid hibaüzenet, majd automatikus törlés
        msg = await ctx.send(str(e))
        await asyncio.sleep(3)
        await delete_message_safe(msg)
    finally:
        await delete_message_safe(ctx.message)


@bot.command(name="ásás")
async def asas(ctx: commands.Context, pozicio: str):
    try:
        if ctx.channel.id not in games:
            await delete_message_safe(ctx.message)
            return

        game = games[ctx.channel.id]
        x, y = parse_xy(pozicio)
        if not (0 <= x < game.width and 0 <= y < game.height):
            msg = await ctx.send("Pozíció kívül esik a pályán.")
            await asyncio.sleep(3)
            await delete_message_safe(msg)
            return

        game.dig(x, y)

        final = game.game_over
        await send_board_and_cleanup(ctx, game, final=final)

        if final:
            del games[ctx.channel.id]

    except ValueError as e:
        msg = await ctx.send(str(e))
        await asyncio.sleep(3)
        await delete_message_safe(msg)
    finally:
        await delete_message_safe(ctx.message)


@bot.command(name="jelölés")
async def jeloles(ctx: commands.Context, pozicio: str):
    try:
        if ctx.channel.id not in games:
            await delete_message_safe(ctx.message)
            return

        game = games[ctx.channel.id]
        x, y = parse_xy(pozicio)
        if not (0 <= x < game.width and 0 <= y < game.height):
            msg = await ctx.send("Pozíció kívül esik a pályán.")
            await asyncio.sleep(3)
            await delete_message_safe(msg)
            return

        game.toggle_flag(x, y)
        await send_board_and_cleanup(ctx, game, final=False)

    except ValueError as e:
        msg = await ctx.send(str(e))
        await asyncio.sleep(3)
        await delete_message_safe(msg)
    finally:
        await delete_message_safe(ctx.message)


@bot.command(name="befejezés")
async def befejezes(ctx: commands.Context):
    try:
        if ctx.channel.id in games:
            game = games[ctx.channel.id]
            await send_board_and_cleanup(ctx, game, final=True, force_reveal=True)
            del games[ctx.channel.id]
    finally:
        await delete_message_safe(ctx.message)


@bot.command(name="segítség")
async def segitseg(ctx: commands.Context):
    try:
        text = (
            "Aknakereső bot parancsok (minden parancsot !akna előtaggal kezdj):\n"
            "\n"
            "1) új könnyű\n"
            "2) új normális\n"
            "3) új nehéz\n"
            "4) új saját <x>x<y> <aknák>\n"
            "   Példa: !akna új saját 10x12 20\n"
            "\n"
            "5) ásás <x>x<y>\n"
            "   Példa: !akna ásás 3x4\n"
            "\n"
            "6) jelölés <x>x<y>\n"
            "   Példa: !akna jelölés 5x6\n"
            "\n"
            "7) befejezés\n"
            "   Lezárja az aktuális játékot és felfedi a táblát.\n"
            "\n"
            "8) törlés <üzenetID>\n"
            "   Törli a megadott üzenetet a csatornából (ha lehetséges).\n"
            "\n"
            "Megjegyzés:\n"
            "- A koordináták 1-től indulnak, bal felső sarok: 1x1.\n"
            "- A bot a parancsüzeneteket és a korábbi állásképeket törli. A végső állás képe megmarad."
        )
        msg = await ctx.send(text)
        await asyncio.sleep(20)
        await delete_message_safe(msg)
    finally:
        await delete_message_safe(ctx.message)


@bot.command(name="törlés")
async def torles(ctx: commands.Context, uzenet_id: int):
    try:
        await delete_message_by_id_safe(ctx.channel, uzenet_id)
        if ctx.channel.id in last_board_message and last_board_message[ctx.channel.id] == uzenet_id:
            del last_board_message[ctx.channel.id]
    finally:
        await delete_message_safe(ctx.message)


# Replit életben tartása
keep_alive()
# Token környezeti változóból
bot.run(os.getenv("DISCORD_TOKEN"))