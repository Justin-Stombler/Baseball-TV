from PIL import Image, ImageDraw, ImageFont
from data.team_colors import get_team_colors
from datetime import datetime
import io
import os

def render(player: dict) -> bytes:

    formatted_date = datetime.now().strftime("%Y-%m-%d")
    
    ###Pulling relevant player data into a saved JPG at 240x240 for output.###
    name = player.get('name')
    team = player.get('team')
    position = player.get('position')
    
    ##eventually would rather make these int based but for now hardcoded values
    if position == 'P':
        stat_one = player['stats'].get('ERA')
        stat_two = player['stats'].get('WHIP')
        stat_three = player['stats'].get('SO')
        percentile_one = player['stats'].get('ERA_pct')
        percentile_two = player['stats'].get('WHIP_pct')
        percentile_three = player['stats'].get('SO_pct')
    else:
        stat_one = player['stats'].get('AVG')
        stat_two = player['stats'].get('OPS')
        stat_three = player['stats'].get('HR')
        percentile_one = player['stats'].get('AVG_pct')
        percentile_two = player['stats'].get('OPS_pct')
        percentile_three = player['stats'].get('HR_pct')

    BG = (13,  13,  13)
    OUTLINE = (240, 240, 240)
    PANEL = (22,  22,  22)
    ACCENT = get_team_colors(team)["primary"]
    POSITION_ACCENT = get_team_colors(team)["secondary"]
    DIM = (90, 90, 90) ##dark gray, diminished, less important text
    TEXT_PRI = (240, 240, 240) ##near white, important text
    TEXT_SEC = (140, 140, 140) ##mid gray, secondary text
    FIRST_PERCENTILE = (0, 255, 0) ##green
    SECOND_PERCENTILE = (255, 255, 0) ##yellow
    THIRD_PERCENTILE = (255, 0, 0) ##red

    W, H = 240, 240

    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    
    ##determining fonts ig
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FONTS    = os.path.join(BASE_DIR, "..", "fonts")

    f_big   = ImageFont.truetype(os.path.join(FONTS, "JetBrainsMono-Bold.ttf"),    20)
    f_med   = ImageFont.truetype(os.path.join(FONTS, "JetBrainsMono-Bold.ttf"),    13)
    f_small = ImageFont.truetype(os.path.join(FONTS, "JetBrainsMono-Regular.ttf"), 10)
    f_tiny  = ImageFont.truetype(os.path.join(FONTS, "JetBrainsMono-Regular.ttf"),  9)

    ##Header
    draw.rectangle([0, 0, W, 44], fill=PANEL)
    draw.rectangle([0, 42, W, 44], fill=ACCENT)

    ##name, team
    draw.text((10, 8), name, font=f_med, fill=TEXT_PRI)
    draw.text((10, 26), team,  font=f_tiny, fill=TEXT_SEC)

    ##trying to auto-detect team length
    name_width = draw.textlength(name, font=f_med)
    team_width = draw.textlength(team, font=f_tiny)

    ##position
    draw.text((16+team_width, 26), position, font=f_tiny, fill=POSITION_ACCENT, outline_width=1, outline_fill=OUTLINE)

    ##stats
    
    ##creating strings
    stat_one_str = f"{stat_one:.3f}" if isinstance(stat_one, float) else str(stat_one)
    stat_two_str = f"{stat_two:.3f}" if isinstance(stat_two, float) else str(stat_two)
    stat_three_str = str(stat_three)

    ##drawing names
    keys = list(player["stats"].keys())

    draw.text((20, 60),  keys[0], font=f_big, fill=TEXT_SEC)
    draw.text((20, 115), keys[1], font=f_big, fill=TEXT_SEC)
    draw.text((20, 170), keys[2], font=f_big, fill=TEXT_SEC)

    ##drawing numbers
    draw.text((160, 60), stat_one_str, font=f_big, fill=TEXT_PRI)
    draw.text((160, 115), stat_two_str, font=f_big, fill=TEXT_PRI)
    draw.text((160, 170), stat_three_str, font=f_big, fill=TEXT_PRI)

    ##tags
    draw.rectangle([0, H - 25, W, H], fill=PANEL)
    draw.text((10, H - 24), f"MLB, {formatted_date}",     font=f_tiny, fill=DIM)
    draw.text((W - 10 - draw.textlength("Justin-Stombler/Baseball-TV", font=f_tiny), H - 24), "Justin-Stombler/Baseball-TV", font=f_tiny, fill=DIM)

    ##5.25 - adding logos
    logo = Image.open(f"data/logos/{player['team']}.png").convert("RGBA")
    logo = logo.resize((25, 25))
    img.paste(logo, (210,10), logo)

    ##5.25 - adding jersey number
    if player.get('number'):
        number_str = f"#{player['number']}"
        draw.text((20+ name_width, 8), number_str, font=f_med, fill=OUTLINE, outline_width=0)
        draw.text((20+name_width, 8), number_str, font=f_med, fill=TEXT_PRI)


    ##percentiles

    percentile_x = 20 ##these are needed for outerbounds
    percentile_y = 220
    diff = percentile_y - percentile_x
    
    adjusted_one = diff * percentile_one/100 ##prorating the length by percentile based on max length
    adjusted_two = diff * percentile_two/100
    adjusted_three = diff * percentile_three/100

    draw.line([(percentile_x, 90), (percentile_x + adjusted_one, 90)], fill=FIRST_PERCENTILE, width=1) ##hell yeah it works
    draw.line([(percentile_x, 145), (percentile_x + adjusted_two, 145)], fill=SECOND_PERCENTILE, width=1)
    draw.line([(percentile_x, 200), (percentile_x + adjusted_three, 200)], fill=THIRD_PERCENTILE, width=1)

    

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    buf.seek(0)
    return buf.read()

if __name__ == "__main__":
    from .main import get_random_player
    player = get_random_player()
    img_bytes = render(player)
    with open("sample_player_card.jpg", "wb") as f:
        f.write(img_bytes)