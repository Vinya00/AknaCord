from PIL import Image, ImageDraw, ImageFont
import uuid

CELL = 32
GRID = (200, 200, 200)
HIDDEN = (180, 180, 180)
REVEALED = (235, 235, 235)
FLAG = (30, 100, 220)
MINE = (220, 30, 30)
EXPLODED = (255, 120, 120)
WRONG = (120, 120, 120)
TEXT = (20, 20, 20)

NUM_COLORS = {
    1: (25, 118, 210),
    2: (56, 142, 60),
    3: (211, 47, 47),
    4: (123, 31, 162),
    5: (191, 54, 12),
    6: (0, 151, 167),
    7: (66, 66, 66),
    8: (0, 0, 0),
}

def _font(size=18):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()

def render_board(game, reveal=False):
    w = game.width * CELL
    h = game.height * CELL
    img = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(img)
    font = _font(18)

    for y in range(game.height):
        for x in range(game.width):
            left = x * CELL
            top = y * CELL
            rect = [left, top, left + CELL, top + CELL]

            is_revealed = game.revealed[y][x] or reveal
            exploded = (game.exploded_at == (x, y))
            fill = REVEALED if is_revealed else HIDDEN
            if (reveal or game.game_over) and exploded:
                fill = EXPLODED

            draw.rectangle(rect, fill=fill, outline=GRID)

            if is_revealed:
                if (x, y) in game.mines_pos:
                    # Akna kirajzolása
                    r = CELL // 2 - 6
                    cx, cy = left + CELL // 2, top + CELL // 2
                    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=MINE)
                else:
                    n = game.board[y][x]
                    if n > 0:
                        txt = str(n)
                        color = NUM_COLORS.get(n, TEXT)
                        tw, th = draw.textsize(txt, font=font)
                        draw.text((left + (CELL - tw) / 2, top + (CELL - th) / 2), txt, fill=color, font=font)
            else:
                # Rejtett mező: zászló
                if game.flags[y][x]:
                    pole_x = left + CELL // 3
                    draw.line([(pole_x, top + 6), (pole_x, top + CELL - 6)], fill=FLAG, width=2)
                    draw.polygon(
                        [(pole_x + 2, top + 6), (pole_x + 14, top + 12), (pole_x + 2, top + 18)],
                        fill=FLAG
                    )

    # Vereségnél rossz zászlók megjelölése
    if (reveal or game.game_over) and not game.victory:
        for y in range(game.height):
            for x in range(game.width):
                if game.flags[y][x] and (x, y) not in game.mines_pos:
                    left = x * CELL
                    top = y * CELL
                    draw.line([(left + 6, top + 6), (left + CELL - 6, top + CELL - 6)], fill=WRONG, width=3)
                    draw.line([(left + CELL - 6, top + 6), (left + 6, top + CELL - 6)], fill=WRONG, width=3)

    path = f"board_{uuid.uuid4().hex}.png"
    img.save(path)
    return path