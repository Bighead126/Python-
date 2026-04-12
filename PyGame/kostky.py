import pygame
import random
import sys
import itertools
import math
import os
from collections import Counter

pygame.init()

try:
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
except pygame.error:
    AUDIO_AVAILABLE = False

# =========================
# NASTAVENÍ OKNA / FULLSCREEN
# =========================
START_FULLSCREEN = False
WINDOWED_SIZE = (1600, 900)

display_info = pygame.display.Info()


def create_screen(fullscreen=False):
    if fullscreen:
        return (
            pygame.display.set_mode(
                (display_info.current_w, display_info.current_h), pygame.FULLSCREEN
            ),
            display_info.current_w,
            display_info.current_h,
        )
    return (
        pygame.display.set_mode(WINDOWED_SIZE, pygame.RESIZABLE),
        WINDOWED_SIZE[0],
        WINDOWED_SIZE[1],
    )


screen, WIDTH, HEIGHT = create_screen(START_FULLSCREEN)
is_fullscreen = START_FULLSCREEN

pygame.display.set_caption("KCD Kostky - Turnaj v Rataji")

# =========================
# FONTY
# =========================
def make_fonts():
    scale = min(WIDTH / 1600, HEIGHT / 900)
    return {
        "font": pygame.font.SysFont("Arial", max(22, int(28 * scale))),
        "big": pygame.font.SysFont("Arial", max(38, int(52 * scale))),
        "ui": pygame.font.SysFont("Arial", max(18, int(22 * scale))),
        "small": pygame.font.SysFont("Arial", max(14, int(17 * scale))),
        "tiny": pygame.font.SysFont("Arial", max(12, int(14 * scale))),
    }


fonts = make_fonts()

# =========================
# BARVY
# =========================
BG = (20, 18, 32)
BG2 = (33, 25, 52)
PANEL = (44, 38, 72)
PANEL2 = (60, 52, 95)
CARD = (48, 42, 80)
CARD2 = (58, 52, 98)

WHITE = (240, 240, 248)
GRAY = (155, 160, 180)
SOFT = (96, 104, 145)

GREEN = (108, 230, 128)
RED = (235, 92, 108)
YELLOW = (255, 214, 92)
BLUE = (86, 176, 255)
PURPLE = (170, 110, 255)
CYAN = (88, 225, 225)
ORANGE = (255, 160, 85)
PINK = (255, 110, 190)

WOOD_DARK = (62, 40, 24)
WOOD_MID = (92, 60, 34)
WOOD_LIGHT = (128, 86, 48)
FELT_GREEN = (48, 102, 70)
FELT_DARK = (34, 74, 52)
FELT_BORDER = (170, 132, 74)

WIN_SCORE = 3000
GROUP_LETTERS = list("ABCDEFGH")
GROUP_RESULTS_SHOW_MS = 10000

# =========================
# AUDIO
# =========================
MUSIC_FILE = "music.ogg"
DICE_ROLL_FILE = "dice_roll.wav"
DICE_RATTLE_FILE = "dice_rattle.wav"

music_loaded = False
snd_dice_roll = None
snd_dice_rattle = None
roll_sound_played = False
rattle_last_tick = 0


def load_audio():
    global music_loaded, snd_dice_roll, snd_dice_rattle

    if not AUDIO_AVAILABLE:
        return

    if os.path.exists(MUSIC_FILE):
        try:
            pygame.mixer.music.load(MUSIC_FILE)
            pygame.mixer.music.set_volume(0.28)
            pygame.mixer.music.play(-1)
            music_loaded = True
        except pygame.error:
            music_loaded = False

    if os.path.exists(DICE_ROLL_FILE):
        try:
            snd_dice_roll = pygame.mixer.Sound(DICE_ROLL_FILE)
            snd_dice_roll.set_volume(0.45)
        except pygame.error:
            snd_dice_roll = None

    if os.path.exists(DICE_RATTLE_FILE):
        try:
            snd_dice_rattle = pygame.mixer.Sound(DICE_RATTLE_FILE)
            snd_dice_rattle.set_volume(0.22)
        except pygame.error:
            snd_dice_rattle = None


def play_sound(sound):
    if AUDIO_AVAILABLE and sound is not None:
        try:
            sound.play()
        except pygame.error:
            pass


# =========================
# POSTAVY
# =========================
KCD_CHARS = [
    ("Jindřich", 450), ("Bořek", 400), ("Ptáček", 650), ("Racek", 350),
    ("Tereza", 420), ("Johanka", 380), ("Štěpánka", 500), ("Adéla", 400),
    ("Diviš", 420), ("Hanuš", 550), ("Ondřej", 300), ("Fritz", 600),
    ("Matěj", 500), ("Kuneš", 700), ("Mlynář", 450), ("Vavřinec", 400),
    ("Radzig", 520), ("Hanekin", 470), ("Janek", 360), ("Hynek", 430),
    ("Zdena", 410), ("Oldřich", 540), ("Marek", 470), ("Pavel", 390),
    ("Viktorín", 560), ("Bohuta", 330), ("Mikuláš", 510), ("Dobromila", 410),
    ("Ambrož", 620), ("Jaroslav", 440), ("Beneš", 480), ("Bedřich", 530),
    ("Linhart", 370), ("Marek z Úžic", 500), ("Havel", 430), ("Blažej", 390),
    ("Ctibor", 460), ("Václav", 480), ("Zikmund", 610), ("Rudlin", 350),
]

# =========================
# GLOBÁLNÍ STAV
# =========================
game_state = "menu"
game_mode = "tournament"
input_text = ""
menu_stage = "mode"
selected_mode_idx = 0

players = []
is_bot = []
bot_risks = []
scores = []
current_p_idx = 0
dice = [1] * 6
active = [True] * 6
selected = [False] * 6
round_score = 0
message = ""
roll_anim = 0
busta_timer = 0
has_loaded_dice = False

tournament_groups = []
group_stage_complete = False
player_group_idx = None
player_eliminated = False
playoff_bracket = []
playoff_pairs = []
playoff_draw_start = 0
current_round_idx = 0
current_match_context = None
tournament_winner = None
current_group_round = 0
third_place_match = None
groups_results_start = 0

bot_phase = "idle"
bot_timer = 0
bot_queue = []

# =========================
# POMOCNÉ FUNKCE
# =========================
def update_fonts():
    global fonts
    fonts = make_fonts()


def toggle_fullscreen():
    global screen, WIDTH, HEIGHT, is_fullscreen
    is_fullscreen = not is_fullscreen
    screen, WIDTH, HEIGHT = create_screen(is_fullscreen)
    update_fonts()


def clamp(v, a, b):
    return max(a, min(b, v))


def ease_out(t):
    t = clamp(t, 0.0, 1.0)
    return 1 - (1 - t) ** 3


def pulse(now, speed=0.008, amount=1.0):
    return 0.5 + 0.5 * math.sin(now * speed) * amount


def lerp(a, b, t):
    return a + (b - a) * t


def shorten_name(name, max_len=12):
    return name if len(name) <= max_len else name[:max_len - 1] + "…"


def draw_text(surface, text, fnt, color, x, y, center=False):
    img = fnt.render(text, True, color)
    rect = img.get_rect(center=(x, y)) if center else img.get_rect(topleft=(x, y))
    surface.blit(img, rect)


def draw_vertical_gradient(surface, top_color, bottom_color):
    for y in range(HEIGHT):
        t = y / max(1, HEIGHT - 1)
        color = (
            int(lerp(top_color[0], bottom_color[0], t)),
            int(lerp(top_color[1], bottom_color[1], t)),
            int(lerp(top_color[2], bottom_color[2], t)),
        )
        pygame.draw.line(surface, color, (0, y), (WIDTH, y))


def draw_glow_rect(x, y, w, h, color, layers=3, radius=18):
    for i in range(layers, 0, -1):
        inflate = i * 6
        surf = pygame.Surface((w + inflate * 2, h + inflate * 2), pygame.SRCALPHA)
        alpha = 12 + i * 10
        pygame.draw.rect(
            surf,
            (*color, alpha),
            (0, 0, w + inflate * 2, h + inflate * 2),
            border_radius=radius + i * 2,
        )
        screen.blit(surf, (x - inflate, y - inflate))


def draw_panel(x, y, w, h, fill=PANEL, border=SOFT, radius=18, glow=None):
    if glow:
        draw_glow_rect(x, y, w, h, glow, layers=2, radius=radius)
    pygame.draw.rect(screen, (12, 12, 18), (x + 6, y + 6, w, h), border_radius=radius)
    pygame.draw.rect(screen, fill, (x, y, w, h), border_radius=radius)
    pygame.draw.rect(screen, border, (x, y, w, h), 2, border_radius=radius)


def get_safe_rect(margin_ratio=0.03):
    margin_x = int(WIDTH * margin_ratio)
    margin_y = int(HEIGHT * margin_ratio)
    return pygame.Rect(margin_x, margin_y, WIDTH - margin_x * 2, HEIGHT - margin_y * 2)


# =========================
# LOGIKA KOSTEK
# =========================
def calculate_score(vals):
    if not vals:
        return 0

    c = Counter(vals)

    if sorted(vals) == [1, 2, 3, 4, 5]:
        return 500
    if sorted(vals) == [2, 3, 4, 5, 6]:
        return 750
    if sorted(vals) == [1, 2, 3, 4, 5, 6]:
        return 1500
    if len(vals) == 6 and all(v == 2 for v in c.values()):
        return 1500

    res = 0
    for num, count in c.items():
        if count >= 3:
            base = 1000 if num == 1 else num * 100
            res += base * (2 ** (count - 3))
            count = 0

        if num == 1:
            res += count * 100
        elif num == 5:
            res += count * 50
        elif count > 0:
            return 0

    return res


def get_selected_score():
    vals = [dice[i] for i in range(6) if selected[i]]

    # Na úplně prvním hodu tahu, když padnou dvě trojice na 6 kostkách,
    # dostaneš 2500 bodů.
    is_first_roll = (round_score == 0 and all(active))
    c = Counter(vals)

    if is_first_roll and len(vals) == 6 and sorted(c.values()) == [3, 3]:
        return 2500

    return calculate_score(vals)


def can_score():
    active_dice = [dice[i] for i in range(6) if active[i]]
    if not active_dice:
        return True

    if round_score == 0 and all(active):
        c = Counter(active_dice)
        if len(active_dice) == 6 and sorted(c.values()) == [3, 3]:
            return True

    for r in range(1, len(active_dice) + 1):
        for combo in itertools.combinations(active_dice, r):
            if calculate_score(combo) > 0:
                return True
    return False


# =========================
# TURNAJ LOGIKA
# =========================
def make_team(name, bot=True, risk=400, group=None):
    return {"name": name, "bot": bot, "risk": risk, "group": group, "seed_power": random.randint(0, 9999)}


def build_group(letter, teams):
    for t in teams:
        t["group"] = letter

    fixtures = [
        {"p1": teams[0], "p2": teams[1], "winner": None, "played": False, "score1": 0, "score2": 0, "round": 0},
        {"p1": teams[2], "p2": teams[3], "winner": None, "played": False, "score1": 0, "score2": 0, "round": 0},
        {"p1": teams[0], "p2": teams[2], "winner": None, "played": False, "score1": 0, "score2": 0, "round": 1},
        {"p1": teams[1], "p2": teams[3], "winner": None, "played": False, "score1": 0, "score2": 0, "round": 1},
        {"p1": teams[0], "p2": teams[3], "winner": None, "played": False, "score1": 0, "score2": 0, "round": 2},
        {"p1": teams[1], "p2": teams[2], "winner": None, "played": False, "score1": 0, "score2": 0, "round": 2},
    ]
    rounds = [[0, 1], [2, 3], [4, 5]]

    return {
        "name": letter,
        "teams": teams,
        "fixtures": fixtures,
        "rounds": rounds,
        "standings": {
            t["name"]: {"team": t, "pts": 0, "wins": 0, "played": 0, "pf": 0, "pa": 0, "diff": 0}
            for t in teams
        }
    }


def sort_group_rows(group):
    rows = list(group["standings"].values())
    rows.sort(key=lambda r: (-r["pts"], -r["wins"], -(r["pf"] - r["pa"]), -r["pf"], -r["team"]["risk"], r["team"]["name"]))
    return rows


def register_group_result(group_idx, match_idx, winner_name, score1, score2):
    group = tournament_groups[group_idx]
    match = group["fixtures"][match_idx]
    if match["played"]:
        return

    match["played"] = True
    match["winner"] = match["p1"] if match["p1"]["name"] == winner_name else match["p2"]
    match["score1"] = score1
    match["score2"] = score2

    s1 = group["standings"][match["p1"]["name"]]
    s2 = group["standings"][match["p2"]["name"]]

    s1["played"] += 1
    s2["played"] += 1
    s1["pf"] += score1
    s1["pa"] += score2
    s2["pf"] += score2
    s2["pa"] += score1
    s1["diff"] = s1["pf"] - s1["pa"]
    s2["diff"] = s2["pf"] - s2["pa"]

    if winner_name == match["p1"]["name"]:
        s1["pts"] += 3
        s1["wins"] += 1
    else:
        s2["pts"] += 3
        s2["wins"] += 1


def get_group_top2(group):
    rows = sort_group_rows(group)
    return rows[0]["team"], rows[1]["team"]


def all_groups_done():
    return all(match["played"] for group in tournament_groups for match in group["fixtures"])


def is_group_round_complete(round_idx):
    for group in tournament_groups:
        for match_idx in group["rounds"][round_idx]:
            if not group["fixtures"][match_idx]["played"]:
                return False
    return True


def get_player_match_in_current_group_round():
    if player_group_idx is None:
        return None
    group = tournament_groups[player_group_idx]
    for match_idx in group["rounds"][current_group_round]:
        match = group["fixtures"][match_idx]
        if not match["played"] and (match["p1"]["name"] == input_text or match["p2"]["name"] == input_text):
            return player_group_idx, match_idx, match
    return None


def simulate_group_match(group_idx, match_idx):
    match = tournament_groups[group_idx]["fixtures"][match_idx]
    a, b = match["p1"], match["p2"]
    wa = a["risk"] + random.randint(-160, 160)
    wb = b["risk"] + random.randint(-160, 160)
    if random.random() < 0.08:
        wa, wb = wb, wa

    if wa >= wb:
        register_group_result(group_idx, match_idx, a["name"], WIN_SCORE, random.randint(1600, 2950))
    else:
        register_group_result(group_idx, match_idx, b["name"], random.randint(1600, 2950), WIN_SCORE)


def advance_group_round_or_start_playoff():
    global current_group_round, group_stage_complete, game_state, groups_results_start

    if all_groups_done():
        group_stage_complete = True
        groups_results_start = pygame.time.get_ticks()
        game_state = "groups_results"
        return

    if current_group_round < 2 and is_group_round_complete(current_group_round):
        current_group_round += 1


def simulate_current_group_round():
    player_match = get_player_match_in_current_group_round()

    for g_idx, group in enumerate(tournament_groups):
        for match_idx in group["rounds"][current_group_round]:
            match = group["fixtures"][match_idx]
            if match["played"]:
                continue
            if player_match and g_idx == player_match[0] and match_idx == player_match[1]:
                continue
            simulate_group_match(g_idx, match_idx)

    if player_match:
        _, m_idx, match = player_match
        start_match(match["p1"], match["p2"], {"stage": "groups", "group_idx": player_match[0], "match_idx": m_idx})
    else:
        advance_group_round_or_start_playoff()


def generate_playoff_pairs():
    winners, runners = {}, {}
    for group in tournament_groups:
        w, r = get_group_top2(group)
        winners[group["name"]] = w
        runners[group["name"]] = r

    letters = GROUP_LETTERS[:]
    random.shuffle(letters)

    runner_letters = GROUP_LETTERS[:]
    ok = False
    for _ in range(500):
        random.shuffle(runner_letters)
        if all(a != b for a, b in zip(letters, runner_letters)):
            ok = True
            break
    if not ok:
        runner_letters = ["B", "A", "D", "C", "F", "E", "H", "G"]

    pairs = []
    for g_w, g_r in zip(letters, runner_letters):
        pairs.append({"p1": winners[g_w], "p2": runners[g_r], "winner": None, "group_pair": (g_w, g_r)})

    random.shuffle(pairs)
    return pairs


def build_playoff_bracket():
    global playoff_pairs, playoff_bracket, current_round_idx, playoff_draw_start, player_eliminated, third_place_match
    playoff_pairs = generate_playoff_pairs()
    current_round_idx = 0
    playoff_draw_start = pygame.time.get_ticks()
    player_eliminated = True
    third_place_match = None

    for pair in playoff_pairs:
        if pair["p1"]["name"] == input_text or pair["p2"]["name"] == input_text:
            player_eliminated = False

    playoff_bracket = [[{"p1": p["p1"], "p2": p["p2"], "winner": None} for p in playoff_pairs]]


def advance_playoff_round_if_ready():
    global current_round_idx, game_state, tournament_winner, third_place_match

    current_round = playoff_bracket[current_round_idx]
    if not all(m["winner"] is not None for m in current_round):
        return

    if len(current_round) == 2:
        finalists = [current_round[0]["winner"], current_round[1]["winner"]]

        loser1 = current_round[0]["p1"] if current_round[0]["winner"] != current_round[0]["p1"] else current_round[0]["p2"]
        loser2 = current_round[1]["p1"] if current_round[1]["winner"] != current_round[1]["p1"] else current_round[1]["p2"]

        third_place_match = {
            "p1": loser1,
            "p2": loser2,
            "winner": None
        }

        next_round = [{
            "p1": finalists[0],
            "p2": finalists[1],
            "winner": None
        }]
        playoff_bracket.append(next_round)
        current_round_idx += 1
        return

    if len(current_round) == 1:
        final_done = current_round[0]["winner"] is not None
        third_done = third_place_match is None or third_place_match["winner"] is not None

        if not third_done or not final_done:
            return

        tournament_winner = current_round[0]["winner"]
        game_state = "tournament_end"
        return

    next_round = []
    for i in range(0, len(current_round), 2):
        next_round.append({"p1": current_round[i]["winner"], "p2": current_round[i + 1]["winner"], "winner": None})
    playoff_bracket.append(next_round)
    current_round_idx += 1


def get_next_playoff_match():
    if current_round_idx == 3 and third_place_match is not None and third_place_match["winner"] is None:
        match = third_place_match
        if match["p1"]["name"] == input_text or match["p2"]["name"] == input_text:
            return ("third", 0, match)

    round_data = playoff_bracket[current_round_idx]

    for m_idx, match in enumerate(round_data):
        if match["winner"] is None:
            if match["p1"]["name"] == input_text or match["p2"]["name"] == input_text:
                return ("main", m_idx, match)

    if current_round_idx == 3 and third_place_match is not None and third_place_match["winner"] is None:
        return ("third", 0, third_place_match)

    for m_idx, match in enumerate(round_data):
        if match["winner"] is None:
            return ("main", m_idx, match)

    return None


def simulate_playoff_step():
    found = get_next_playoff_match()
    if not found:
        advance_playoff_round_if_ready()
        return

    match_type, m_idx, match = found
    p1, p2 = match["p1"], match["p2"]

    if p1["name"] == input_text or p2["name"] == input_text:
        start_match(p1, p2, {
            "stage": "playoff",
            "round_idx": current_round_idx,
            "match_idx": m_idx,
            "match_type": match_type
        })
        return

    w1 = p1["risk"] + random.randint(-180, 180)
    w2 = p2["risk"] + random.randint(-180, 180)
    winner = p1 if w1 >= w2 else p2

    if match_type == "main":
        playoff_bracket[current_round_idx][m_idx]["winner"] = winner
    else:
        third_place_match["winner"] = winner

    advance_playoff_round_if_ready()


def setup_tournament(p_name):
    global tournament_groups, group_stage_complete, player_group_idx, playoff_bracket, playoff_pairs
    global playoff_draw_start, current_round_idx, player_eliminated, tournament_winner
    global current_group_round, third_place_match, groups_results_start

    group_stage_complete = False
    player_group_idx = None
    playoff_bracket = []
    playoff_pairs = []
    playoff_draw_start = 0
    current_round_idx = 0
    player_eliminated = False
    tournament_winner = None
    current_group_round = 0
    third_place_match = None
    groups_results_start = 0

    sampled = random.sample(KCD_CHARS, 31)
    all_teams = [make_team(p_name, bot=False, risk=400)] + [make_team(n, True, r) for n, r in sampled]
    random.shuffle(all_teams)

    tournament_groups = []
    for gi, letter in enumerate(GROUP_LETTERS):
        teams = all_teams[gi * 4:(gi + 1) * 4]
        group = build_group(letter, teams)
        tournament_groups.append(group)
        for t in teams:
            if t["name"] == p_name:
                player_group_idx = gi


# =========================
# ZÁPASY
# =========================
def start_match(p1, p2, context=None):
    global players, is_bot, bot_risks, scores, current_p_idx, game_state, current_match_context
    players = [p1["name"], p2["name"]]
    is_bot = [p1["bot"], p2["bot"]]
    bot_risks = [p1["risk"], p2["risk"]]
    scores = [0, 0]
    current_p_idx = 0
    current_match_context = context
    game_state = "playing"
    reset_turn()


def reset_turn():
    global round_score, active, selected, roll_anim, busta_timer, message, bot_phase, bot_timer, roll_sound_played
    round_score = 0
    active[:] = [True] * 6
    selected[:] = [False] * 6
    busta_timer = 0
    message = f"Na řadě: {players[current_p_idx]}"
    roll_anim = 35
    roll_sound_played = False
    if is_bot[current_p_idx]:
        bot_phase = "thinking"
        bot_timer = pygame.time.get_ticks() + 1000


def finalize_current_match():
    global game_state, player_eliminated, current_match_context, third_place_match

    winner_name = players[current_p_idx]
    loser_idx = 1 - current_p_idx
    score_w = scores[current_p_idx]
    score_l = scores[loser_idx]

    if current_match_context is None:
        game_state = "menu"
        return

    if current_match_context["stage"] == "groups":
        g_idx = current_match_context["group_idx"]
        m_idx = current_match_context["match_idx"]
        match = tournament_groups[g_idx]["fixtures"][m_idx]

        if match["p1"]["name"] == winner_name:
            register_group_result(g_idx, m_idx, winner_name, score_w, score_l)
        else:
            register_group_result(g_idx, m_idx, winner_name, score_l, score_w)

        current_match_context = None
        advance_group_round_or_start_playoff()
        if game_state not in ("groups_results", "playoff_draw"):
            game_state = "groups"

    elif current_match_context["stage"] == "playoff":
        match_type = current_match_context.get("match_type", "main")
        r_idx = current_match_context["round_idx"]
        m_idx = current_match_context["match_idx"]

        if match_type == "main":
            match = playoff_bracket[r_idx][m_idx]
            match["winner"] = match["p1"] if match["p1"]["name"] == winner_name else match["p2"]

            if winner_name != input_text and (match["p1"]["name"] == input_text or match["p2"]["name"] == input_text):
                player_eliminated = True
        else:
            third_place_match["winner"] = third_place_match["p1"] if third_place_match["p1"]["name"] == winner_name else third_place_match["p2"]

            if winner_name != input_text and (third_place_match["p1"]["name"] == input_text or third_place_match["p2"]["name"] == input_text):
                player_eliminated = True

        current_match_context = None
        advance_playoff_round_if_ready()
        if game_state != "tournament_end":
            game_state = "bracket"


# =========================
# VZHLED STOLU
# =========================
def draw_pixel_noise(rect, count, base_colors):
    for _ in range(count):
        x = random.randint(rect.x, rect.right - 2)
        y = random.randint(rect.y, rect.bottom - 2)
        c = random.choice(base_colors)
        pygame.draw.rect(screen, c, (x, y, 2, 2))


def draw_table():
    draw_vertical_gradient(screen, (18, 14, 24), (8, 8, 12))
    safe = get_safe_rect(0.03)

    # dřevěná stěna / pozadí
    plank_h = max(26, HEIGHT // 18)
    for i, y in enumerate(range(0, HEIGHT, plank_h)):
        c = WOOD_DARK if i % 2 == 0 else WOOD_MID
        pygame.draw.rect(screen, c, (0, y, WIDTH, plank_h))
        pygame.draw.line(screen, WOOD_LIGHT, (0, y), (WIDTH, y), 1)
        for j in range(6):
            xx = int((j + 0.5) * WIDTH / 6)
            pygame.draw.line(screen, (70, 46, 28), (xx, y), (xx, y + plank_h), 2)

    # tmavé rohy
    vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for i in range(7):
        alpha = 25 - i * 3
        pygame.draw.rect(vignette, (0, 0, 0, alpha), (i * 14, i * 14, WIDTH - i * 28, HEIGHT - i * 28), width=18)
    screen.blit(vignette, (0, 0))

    # stůl
    table_w = int(safe.w * 0.82)
    table_h = int(safe.h * 0.62)
    table_x = safe.centerx - table_w // 2
    table_y = safe.centery - table_h // 2 + 40

    # dřevěný rám
    pygame.draw.rect(screen, (18, 12, 8), (table_x + 10, table_y + 12, table_w, table_h), border_radius=26)
    pygame.draw.rect(screen, WOOD_DARK, (table_x, table_y, table_w, table_h), border_radius=26)
    pygame.draw.rect(screen, WOOD_LIGHT, (table_x, table_y, table_w, table_h), 3, border_radius=26)

    # plátno
    inner = pygame.Rect(table_x + 36, table_y + 34, table_w - 72, table_h - 68)
    pygame.draw.rect(screen, FELT_DARK, inner, border_radius=22)
    pygame.draw.rect(screen, FELT_GREEN, (inner.x + 6, inner.y + 6, inner.w - 12, inner.h - 12), border_radius=20)
    pygame.draw.rect(screen, FELT_BORDER, inner, 2, border_radius=22)

    # pixel/texture šum
    draw_pixel_noise(inner, max(220, inner.w * inner.h // 6000), [
        (42, 92, 62),
        (52, 108, 76),
        (36, 82, 56),
        (62, 116, 82),
    ])

    # lehké škrábance / used look
    for i in range(12):
        x1 = inner.x + 20 + i * max(20, inner.w // 14)
        y1 = inner.y + random.randint(25, inner.h - 25)
        x2 = x1 + random.randint(18, 50)
        pygame.draw.line(screen, (76, 132, 96), (x1, y1), (x2, y1 + random.randint(-4, 4)), 1)

    # ornament rohů
    corner_color = (196, 160, 92)
    s = 20
    pygame.draw.line(screen, corner_color, (inner.x + 18, inner.y + 18), (inner.x + 18 + s, inner.y + 18), 2)
    pygame.draw.line(screen, corner_color, (inner.x + 18, inner.y + 18), (inner.x + 18, inner.y + 18 + s), 2)

    pygame.draw.line(screen, corner_color, (inner.right - 18, inner.y + 18), (inner.right - 18 - s, inner.y + 18), 2)
    pygame.draw.line(screen, corner_color, (inner.right - 18, inner.y + 18), (inner.right - 18, inner.y + 18 + s), 2)

    pygame.draw.line(screen, corner_color, (inner.x + 18, inner.bottom - 18), (inner.x + 18 + s, inner.bottom - 18), 2)
    pygame.draw.line(screen, corner_color, (inner.x + 18, inner.bottom - 18), (inner.x + 18, inner.bottom - 18 - s), 2)

    pygame.draw.line(screen, corner_color, (inner.right - 18, inner.bottom - 18), (inner.right - 18 - s, inner.bottom - 18), 2)
    pygame.draw.line(screen, corner_color, (inner.right - 18, inner.bottom - 18), (inner.right - 18, inner.bottom - 18 - s), 2)


# =========================
# DRAW - SKUPINY
# =========================
def draw_group_card(group, rect, is_player_group, now, show_round_info=True):
    player_glow = BLUE
    header_color = PURPLE if not is_player_group else CYAN

    draw_panel(
        rect.x,
        rect.y,
        rect.w,
        rect.h,
        fill=CARD,
        border=header_color if is_player_group else SOFT,
        radius=22,
        glow=player_glow if is_player_group else None,
    )

    header_h = int(rect.h * 0.14)
    pygame.draw.rect(screen, header_color if is_player_group else PANEL2, (rect.x, rect.y, rect.w, header_h), border_radius=22)
    pygame.draw.rect(screen, CARD, (rect.x, rect.y + header_h // 2, rect.w, header_h), border_radius=0)

    draw_text(screen, f"Skupina {group['name']}", fonts["ui"], YELLOW if is_player_group else WHITE, rect.x + 16, rect.y + 10)

    rows = sort_group_rows(group)

    col_x = [rect.x + 16, rect.x + int(rect.w * 0.56), rect.x + int(rect.w * 0.66), rect.x + int(rect.w * 0.76)]
    head_y = rect.y + header_h + 8
    draw_text(screen, "Jméno", fonts["small"], GRAY, col_x[0], head_y)
    draw_text(screen, "B", fonts["small"], GRAY, col_x[1], head_y)
    draw_text(screen, "V", fonts["small"], GRAY, col_x[2], head_y)
    draw_text(screen, "Skóre", fonts["small"], GRAY, col_x[3], head_y)

    row_h = int((rect.h * 0.48) / 4)
    base_y = head_y + 24

    for i, row in enumerate(rows):
        ry = base_y + i * row_h
        team_name = row["team"]["name"]
        is_player = team_name == input_text
        is_top2 = i < 2

        row_color = WHITE
        accent = SOFT
        if is_top2:
            row_color = GREEN
            accent = GREEN
        if is_player:
            row_color = BLUE
            accent = BLUE

        if is_top2 or is_player:
            draw_glow_rect(rect.x + 10, ry - 2, rect.w - 20, row_h - 6, accent, layers=1, radius=12)

        pygame.draw.rect(screen, (58, 52, 88), (rect.x + 8, ry, rect.w - 16, row_h - 8), border_radius=12)
        if is_player:
            pygame.draw.rect(screen, BLUE, (rect.x + 8, ry, rect.w - 16, row_h - 8), 2, border_radius=12)

        draw_text(screen, shorten_name(team_name, 18), fonts["small"], row_color, col_x[0], ry + 6)
        draw_text(screen, str(row["pts"]), fonts["small"], row_color, col_x[1], ry + 6)
        draw_text(screen, str(row["wins"]), fonts["small"], row_color, col_x[2], ry + 6)
        draw_text(screen, f"{row['pf']}:{row['pa']}", fonts["small"], row_color, col_x[3], ry + 6)

    footer_y = rect.bottom - 52
    played = sum(1 for m in group["fixtures"] if m["played"])
    total = len(group["fixtures"])
    draw_text(screen, f"Zápasy: {played}/{total}", fonts["tiny"], GRAY, rect.x + 14, footer_y)

    if show_round_info:
        draw_text(screen, f"Kolo {current_group_round + 1}:", fonts["tiny"], YELLOW, rect.x + 14, footer_y + 20)
        fixture_parts = []
        for match_idx in group["rounds"][current_group_round]:
            m = group["fixtures"][match_idx]
            fixture_parts.append(f"{shorten_name(m['p1']['name'], 8)}-{shorten_name(m['p2']['name'], 8)}")
        draw_text(screen, " | ".join(fixture_parts), fonts["tiny"], WHITE, rect.x + 86, footer_y + 20)
    else:
        draw_text(screen, "POSTUPUJÍ 1. A 2. MÍSTO", fonts["tiny"], YELLOW, rect.x + 14, footer_y + 20)


def draw_groups():
    draw_vertical_gradient(screen, BG2, BG)

    safe = get_safe_rect(0.025)

    draw_text(screen, "Skupinová fáze", fonts["big"], YELLOW, safe.centerx, safe.y + 18, center=True)
    draw_text(screen, "Všech 8 skupin hraje současně po kolech • postupují první 2 • modrá = hráč", fonts["ui"], WHITE, safe.centerx, safe.y + 72, center=True)
    draw_text(screen, f"Aktuální kolo: {current_group_round + 1}/3", fonts["ui"], CYAN, safe.right - 10, safe.y + 24)

    top_area_h = 105
    bottom_bar_h = 64
    content_y = safe.y + top_area_h
    content_h = safe.h - top_area_h - bottom_bar_h - 18

    cols = 4
    rows = 2
    gap_x = int(safe.w * 0.014)
    gap_y = int(safe.h * 0.02)
    card_w = (safe.w - gap_x * (cols - 1)) // cols
    card_h = (content_h - gap_y * (rows - 1)) // rows

    for idx, group in enumerate(tournament_groups):
        c = idx % cols
        r = idx // cols
        rect = pygame.Rect(
            safe.x + c * (card_w + gap_x),
            content_y + r * (card_h + gap_y),
            card_w,
            card_h
        )
        draw_group_card(group, rect, idx == player_group_idx, pygame.time.get_ticks(), show_round_info=True)

    bottom_rect = pygame.Rect(safe.x, safe.bottom - bottom_bar_h, safe.w, bottom_bar_h)
    draw_panel(bottom_rect.x, bottom_rect.y, bottom_rect.w, bottom_rect.h, fill=PANEL, border=PURPLE, radius=18)

    player_match = get_player_match_in_current_group_round()
    if player_match:
        _, _, match = player_match
        info = f"V tomto kole hrají všichni najednou • tvůj zápas: {match['p1']['name']} vs {match['p2']['name']}"
        draw_text(screen, info, fonts["ui"], YELLOW, bottom_rect.x + 20, bottom_rect.y + 10)
        draw_text(screen, "MEZERNÍK: spustit celé kolo", fonts["ui"], WHITE, bottom_rect.x + 20, bottom_rect.y + 34)
    else:
        draw_text(screen, "MEZERNÍK: dopočítat celé aktuální kolo ve všech skupinách", fonts["ui"], WHITE, bottom_rect.x + 20, bottom_rect.y + 22)


def draw_groups_results():
    draw_vertical_gradient(screen, (28, 26, 50), (12, 12, 20))
    safe = get_safe_rect(0.025)
    elapsed = pygame.time.get_ticks() - groups_results_start
    remaining = max(0, (GROUP_RESULTS_SHOW_MS - elapsed + 999) // 1000)

    draw_text(screen, "Konečné tabulky skupin", fonts["big"], YELLOW, safe.centerx, safe.y + 18, center=True)
    draw_text(screen, "Do play-off postupují první 2 týmy z každé skupiny", fonts["ui"], WHITE, safe.centerx, safe.y + 72, center=True)
    draw_text(screen, f"Za {remaining}s se otevře play-off", fonts["ui"], ORANGE, safe.right - 10, safe.y + 24)

    top_area_h = 105
    bottom_bar_h = 64
    content_y = safe.y + top_area_h
    content_h = safe.h - top_area_h - bottom_bar_h - 18

    cols = 4
    rows = 2
    gap_x = int(safe.w * 0.014)
    gap_y = int(safe.h * 0.02)
    card_w = (safe.w - gap_x * (cols - 1)) // cols
    card_h = (content_h - gap_y * (rows - 1)) // rows

    for idx, group in enumerate(tournament_groups):
        c = idx % cols
        r = idx // cols
        rect = pygame.Rect(
            safe.x + c * (card_w + gap_x),
            content_y + r * (card_h + gap_y),
            card_w,
            card_h
        )
        draw_group_card(group, rect, idx == player_group_idx, pygame.time.get_ticks(), show_round_info=False)

    bottom_rect = pygame.Rect(safe.x, safe.bottom - bottom_bar_h, safe.w, bottom_bar_h)
    draw_panel(bottom_rect.x, bottom_rect.y, bottom_rect.w, bottom_rect.h, fill=PANEL, border=GREEN, radius=18)
    draw_text(screen, "Zeleně zvýrazněné týmy opravdu postupují do play-off.", fonts["ui"], GREEN, bottom_rect.x + 20, bottom_rect.y + 10)
    draw_text(screen, "Po 10 sekundách se automaticky spustí los vyřazovací části.", fonts["ui"], WHITE, bottom_rect.x + 20, bottom_rect.y + 34)


# =========================
# DRAW - LOS PLAYOFF
# =========================
def draw_playoff_draw():
    draw_vertical_gradient(screen, (24, 26, 50), (12, 12, 22))
    safe = get_safe_rect(0.04)
    elapsed = pygame.time.get_ticks() - playoff_draw_start

    draw_text(screen, "Los play-off", fonts["big"], YELLOW, safe.centerx, safe.y + 16, center=True)
    draw_text(screen, "Náhodné rozdělení bez souboje týmů ze stejné skupiny v osmifinále", fonts["ui"], WHITE, safe.centerx, safe.y + 68, center=True)

    area_w = int(safe.w * 0.68)
    area_x = safe.centerx - area_w // 2
    start_y = safe.y + 120
    slot_h = int((safe.h - 220) / 8) - 6
    gap = 10

    top_names = [p["p1"]["name"] for p in playoff_pairs]
    low_names = [p["p2"]["name"] for p in playoff_pairs]

    for i in range(8):
        y = start_y + i * (slot_h + gap)
        rect = pygame.Rect(area_x, y, area_w, slot_h)
        draw_panel(rect.x, rect.y, rect.w, rect.h, fill=CARD2, border=ORANGE, radius=18, glow=ORANGE)

        pair = playoff_pairs[i]
        fixed = elapsed > 260 + i * 140
        p1 = pair["p1"]["name"] if fixed else random.choice(top_names)
        p2 = pair["p2"]["name"] if fixed else random.choice(low_names)

        draw_text(screen, f"Osmifinále {i + 1}", fonts["small"], GRAY, rect.x + 14, rect.y + 8)
        draw_text(screen, shorten_name(p1, 28), fonts["ui"], BLUE if p1 == input_text else WHITE, rect.x + 22, rect.centery)
        draw_text(screen, "vs", fonts["ui"], YELLOW, rect.centerx, rect.centery, center=True)
        draw_text(screen, shorten_name(p2, 28), fonts["ui"], BLUE if p2 == input_text else WHITE, rect.right - 22, rect.centery, center=True)

    draw_text(screen, "Po losu se otevře pavouk", fonts["ui"], WHITE, safe.centerx, safe.bottom - 18, center=True)


# =========================
# DRAW - PAVOUK
# =========================
def get_bracket_positions():
    safe = get_safe_rect(0.03)
    top = safe.y + 130
    bottom = safe.bottom - 110
    mid_y = (top + bottom) // 2

    r16_h = int(safe.h * 0.07)
    qf_h = int(safe.h * 0.075)
    sf_h = int(safe.h * 0.08)
    final_h = int(safe.h * 0.09)
    third_h = int(safe.h * 0.08)

    r16_w = int(safe.w * 0.12)
    qf_w = int(safe.w * 0.125)
    sf_w = int(safe.w * 0.13)
    final_w = int(safe.w * 0.145)
    third_w = int(safe.w * 0.135)

    left_x = safe.x + 10
    qf_left_x = safe.x + int(safe.w * 0.18)
    sf_left_x = safe.x + int(safe.w * 0.38)

    final_x = safe.centerx - final_w // 2
    third_x = safe.centerx - third_w // 2

    sf_right_x = safe.right - int(safe.w * 0.38) - sf_w
    qf_right_x = safe.right - int(safe.w * 0.18) - qf_w
    right_x = safe.right - r16_w - 10

    lane_h = bottom - top
    r16_y = [top + int(lane_h * v) for v in (0.02, 0.28, 0.54, 0.80)]
    qf_y = [top + int(lane_h * v) for v in (0.15, 0.67)]
    sf_y = [mid_y - sf_h // 2]

    final_y = top + int(lane_h * 0.22)
    third_y = top + int(lane_h * 0.68)

    return {
        (0, 0): (left_x, r16_y[0], r16_w, r16_h),
        (0, 1): (left_x, r16_y[1], r16_w, r16_h),
        (0, 2): (left_x, r16_y[2], r16_w, r16_h),
        (0, 3): (left_x, r16_y[3], r16_w, r16_h),

        (0, 4): (right_x, r16_y[0], r16_w, r16_h),
        (0, 5): (right_x, r16_y[1], r16_w, r16_h),
        (0, 6): (right_x, r16_y[2], r16_w, r16_h),
        (0, 7): (right_x, r16_y[3], r16_w, r16_h),

        (1, 0): (qf_left_x, qf_y[0], qf_w, qf_h),
        (1, 1): (qf_left_x, qf_y[1], qf_w, qf_h),

        (1, 2): (qf_right_x, qf_y[0], qf_w, qf_h),
        (1, 3): (qf_right_x, qf_y[1], qf_w, qf_h),

        (2, 0): (sf_left_x, sf_y[0], sf_w, sf_h),
        (2, 1): (sf_right_x, sf_y[0], sf_w, sf_h),

        (3, 0): (final_x, final_y, final_w, final_h),
        ("third", 0): (third_x, third_y, third_w, third_h),
    }


def draw_connector(from_box, to_box, color, width):
    x1, y1, w1, h1 = from_box
    x2, y2, w2, h2 = to_box

    if x1 < x2:
        start = (x1 + w1, y1 + h1 // 2)
        end = (x2, y2 + h2 // 2)
        xm = start[0] + (end[0] - start[0]) * 0.42
    else:
        start = (x1, y1 + h1 // 2)
        end = (x2 + w2, y2 + h2 // 2)
        xm = start[0] + (end[0] - start[0]) * 0.42

    pygame.draw.line(screen, color, start, (xm, start[1]), width)
    pygame.draw.line(screen, color, (xm, start[1]), (xm, end[1]), width)
    pygame.draw.line(screen, color, (xm, end[1]), end, width)


def draw_bracket_box(x, y, w, h, match, round_idx, match_idx, now):
    p1 = match["p1"]["name"] if match["p1"] else "?"
    p2 = match["p2"]["name"] if match["p2"] else "?"
    p1_won = match["winner"] == match["p1"]
    p2_won = match["winner"] == match["p2"]

    is_player_match = p1 == input_text or p2 == input_text
    is_final = (round_idx == 3 and match_idx == 0)
    is_third = (match_idx == 99)

    is_active_round = round_idx == current_round_idx and match["winner"] is None
    has_player_open_match = any(
        m["winner"] is None and (m["p1"]["name"] == input_text or m["p2"]["name"] == input_text)
        for m in playoff_bracket[current_round_idx]
    )
    if round_idx == 3 and third_place_match is not None and third_place_match["winner"] is None:
        has_player_open_match = has_player_open_match or third_place_match["p1"]["name"] == input_text or third_place_match["p2"]["name"] == input_text

    is_active_match = is_active_round and (is_player_match or not has_player_open_match)
    if is_third and match["winner"] is None:
        if third_place_match is not None:
            is_active_match = (match["p1"]["name"] == input_text or match["p2"]["name"] == input_text) or not any(
                m["winner"] is None and (m["p1"]["name"] == input_text or m["p2"]["name"] == input_text)
                for m in playoff_bracket[current_round_idx]
            )

    fill = CARD2
    border = ORANGE if is_final else SOFT
    glow = None

    if is_third:
        border = ORANGE
        fill = (94, 64, 48)

    if is_player_match:
        border = BLUE
        fill = (56, 72, 108)
        glow = BLUE
    if is_active_match:
        border = YELLOW
        fill = (110, 78, 48) if (is_final or is_third) else (88, 64, 98)
        glow = YELLOW

    draw_panel(x, y, w, h, fill=fill, border=border, radius=18, glow=glow)
    pygame.draw.line(screen, border, (x + 12, y + h // 2), (x + w - 12, y + h // 2), 1)

    name_font = fonts["small"] if w < 180 else fonts["ui"]
    draw_text(screen, shorten_name(p1, 18 if w > 200 else 14), name_font, GREEN if p1_won else (BLUE if p1 == input_text else WHITE), x + 12, y + 8)
    draw_text(screen, shorten_name(p2, 18 if w > 200 else 14), name_font, GREEN if p2_won else (BLUE if p2 == input_text else WHITE), x + 12, y + h // 2 + 4)

    if match["winner"] is not None:
        pygame.draw.circle(screen, GREEN, (x + w - 16, y + h // 2), 6)
        pygame.draw.circle(screen, BG, (x + w - 16, y + h // 2), 2)


def draw_bracket():
    draw_vertical_gradient(screen, (20, 22, 44), (10, 10, 18))
    safe = get_safe_rect(0.03)
    now = pygame.time.get_ticks()

    draw_text(screen, "Play-off", fonts["big"], YELLOW, safe.centerx, safe.y + 10, center=True)
    draw_text(screen, "Levá a pravá strana pavouka • modrá = hráč • zelená = postup", fonts["ui"], WHITE, safe.centerx, safe.y + 62, center=True)

    labels = {0: "Osmifinále", 1: "Čtvrtfinále", 2: "Semifinále", 3: "Finále + o 3. místo"}
    draw_text(screen, labels.get(current_round_idx, ""), fonts["ui"], CYAN, safe.centerx, safe.y + 98, center=True)

    pos = get_bracket_positions()

    line_soft = PURPLE
    line_win = GREEN
    bronze_col = ORANGE

    for r_idx in range(1, len(playoff_bracket)):
        prev_round = playoff_bracket[r_idx - 1]
        curr_round = playoff_bracket[r_idx]

        for m_idx, _ in enumerate(curr_round):
            if r_idx == 3:
                box_a = pos[(2, 0)]
                box_b = pos[(2, 1)]
                dst = pos[(3, 0)]
                draw_connector(box_a, dst, line_win if playoff_bracket[2][0]["winner"] else line_soft, 4)
                draw_connector(box_b, dst, line_win if playoff_bracket[2][1]["winner"] else line_soft, 4)
                break

            src_a = m_idx * 2
            src_b = m_idx * 2 + 1
            dst = pos[(r_idx, m_idx)]
            box_a = pos[(r_idx - 1, src_a)]
            box_b = pos[(r_idx - 1, src_b)]
            draw_connector(box_a, dst, line_win if prev_round[src_a]["winner"] else line_soft, 4)
            draw_connector(box_b, dst, line_win if prev_round[src_b]["winner"] else line_soft, 4)

    if third_place_match is not None:
        third_box = pos[("third", 0)]
        draw_connector(pos[(2, 0)], third_box, bronze_col, 4)
        draw_connector(pos[(2, 1)], third_box, bronze_col, 4)

    for r_idx, round_data in enumerate(playoff_bracket):
        for m_idx, match in enumerate(round_data):
            draw_bracket_box(*pos[(r_idx, m_idx)], match, r_idx, m_idx, now)

    if third_place_match is not None:
        draw_bracket_box(*pos[("third", 0)], third_place_match, 3, 99, now)

    draw_text(screen, "LEVÁ STRANA", fonts["small"], GRAY, safe.x + 40, safe.y + 132)
    draw_text(screen, "PRAVÁ STRANA", fonts["small"], GRAY, safe.right - 180, safe.y + 132)

    fx, fy, fw, fh = pos[(3, 0)]
    draw_text(screen, "FINÁLE", fonts["ui"], YELLOW, fx + fw // 2, fy - 28, center=True)

    if third_place_match is not None:
        tx, ty, tw, th = pos[("third", 0)]
        draw_text(screen, "O 3. MÍSTO", fonts["ui"], ORANGE, tx + tw // 2, ty + th + 14, center=True)

    bottom_rect = pygame.Rect(safe.x, safe.bottom - 62, safe.w, 62)
    draw_panel(bottom_rect.x, bottom_rect.y, bottom_rect.w, bottom_rect.h, fill=PANEL, border=PINK, radius=18)

    found = get_next_playoff_match()
    if found:
        match_type, _, match = found
        title = "Další zápas"
        if match_type == "third":
            title = "Zápas o 3. místo"
        draw_text(screen, f"{title}: {match['p1']['name']} vs {match['p2']['name']}", fonts["ui"], YELLOW, bottom_rect.x + 18, bottom_rect.y + 10)
        draw_text(screen, "MEZERNÍK: odehrát / simulovat další zápas", fonts["ui"], WHITE, bottom_rect.x + 18, bottom_rect.y + 34)
    else:
        draw_text(screen, "Čeká se na vytvoření dalšího kola...", fonts["ui"], WHITE, bottom_rect.x + 18, bottom_rect.y + 20)


# =========================
# DRAW - MENU / MATCH / END
# =========================
def draw_menu():
    draw_vertical_gradient(screen, (30, 24, 52), (12, 12, 20))
    safe = get_safe_rect(0.05)

    draw_text(screen, "KOSTKY Z KCD", fonts["big"], YELLOW, safe.centerx, safe.y + 80, center=True)
    draw_text(screen, "F11 přepíná fullscreen • layout se přizpůsobí automaticky", fonts["ui"], CYAN, safe.centerx, safe.y + 135, center=True)

    if AUDIO_AVAILABLE:
        audio_txt = "Hudba a zvuky se načtou automaticky, pokud jsou ve složce music.ogg / dice_roll.wav / dice_rattle.wav"
    else:
        audio_txt = "Audio není dostupné v mixeru, hra poběží bez zvuku"
    draw_text(screen, audio_txt, fonts["tiny"], GRAY, safe.centerx, safe.y + 170, center=True)

    if menu_stage == "mode":
        panel_w = int(safe.w * 0.38)
        panel_h = int(safe.h * 0.34)
        px = safe.centerx - panel_w // 2
        py = safe.centery - panel_h // 2
        draw_panel(px, py, panel_w, panel_h, fill=CARD, border=PURPLE, radius=24, glow=PURPLE)

        options = ["Hráč vs Hráč", "Vyzvat postavu", "Turnaj (skupiny + play-off)"]
        for i, m in enumerate(options):
            yy = py + 60 + i * 72
            selected_color = YELLOW if i == selected_mode_idx else WHITE
            if i == selected_mode_idx:
                draw_glow_rect(px + 24, yy - 8, panel_w - 48, 48, YELLOW, layers=1, radius=14)
                pygame.draw.rect(screen, (88, 68, 46), (px + 24, yy - 6, panel_w - 48, 44), border_radius=14)
            draw_text(screen, m, fonts["font"], selected_color, safe.centerx, yy + 6, center=True)

    else:
        panel_w = int(safe.w * 0.42)
        panel_h = int(safe.h * 0.24)
        px = safe.centerx - panel_w // 2
        py = safe.centery - panel_h // 2
        draw_panel(px, py, panel_w, panel_h, fill=CARD, border=CYAN, radius=24, glow=CYAN)
        draw_text(screen, "Zadej své jméno:", fonts["font"], WHITE, safe.centerx, py + 55, center=True)
        draw_text(screen, input_text + "_", fonts["big"], YELLOW, safe.centerx, py + 130, center=True)


def draw_playing():
    draw_table()
    layout = get_playing_layout()

    draw_panel(layout["score_panel"].x, layout["score_panel"].y, layout["score_panel"].w, layout["score_panel"].h, fill=CARD, border=CYAN, radius=18)
    for i in range(2):
        c = YELLOW if i == current_p_idx else WHITE
        draw_text(screen, f"{players[i]}: {scores[i]}", fonts["font"], c, layout["score_panel"].x + 24, layout["score_panel"].y + 26 + i * 54)

    draw_text(screen, f"Kolo: {round_score}", fonts["big"], WHITE, layout["info_area"].x, layout["info_area"].y + 4)
    draw_text(screen, message, fonts["font"], RED if "❌" in message else CYAN, layout["info_area"].x, layout["info_area"].y + 70)

    draw_dice()

    if not is_bot[current_p_idx] and roll_anim == 0 and busta_timer == 0:
        rb = layout["roll_btn"]
        bb = layout["bank_btn"]

        draw_panel(rb.x, rb.y, rb.w, rb.h, fill=(54, 110, 74), border=GREEN, radius=16, glow=GREEN)
        draw_panel(bb.x, bb.y, bb.w, bb.h, fill=(118, 90, 36), border=YELLOW, radius=16, glow=YELLOW)

        draw_text(screen, "HODIT", fonts["font"], BG, rb.centerx, rb.centery, center=True)
        draw_text(screen, "ZAPSAT", fonts["font"], BG, bb.centerx, bb.centery, center=True)


def draw_match_win():
    draw_vertical_gradient(screen, (28, 24, 40), (12, 12, 18))
    safe = get_safe_rect(0.08)
    draw_text(screen, f"Vítěz: {players[current_p_idx]}!", fonts["big"], GREEN, safe.centerx, safe.centery - 40, center=True)
    draw_text(screen, "Stiskni MEZERNÍK", fonts["font"], WHITE, safe.centerx, safe.centery + 35, center=True)


def draw_tournament_end():
    draw_vertical_gradient(screen, (28, 22, 36), (12, 12, 18))
    safe = get_safe_rect(0.08)
    champ = tournament_winner["name"] if tournament_winner else "?"
    draw_text(screen, f"ŠAMPION: {champ.upper()}", fonts["big"], YELLOW, safe.centerx, safe.centery - 70, center=True)

    if champ == input_text:
        draw_text(screen, "Vyhrál jsi celý turnaj!", fonts["font"], GREEN, safe.centerx, safe.centery + 5, center=True)
    else:
        draw_text(screen, f"Turnaj vyhrál {champ}.", fonts["font"], WHITE, safe.centerx, safe.centery + 5, center=True)

    if third_place_match and third_place_match["winner"] is not None:
        bronze_name = third_place_match["winner"]["name"]
        draw_text(screen, f"3. místo: {bronze_name}", fonts["ui"], ORANGE, safe.centerx, safe.centery + 48, center=True)

    draw_text(screen, "Stiskni R pro návrat", fonts["font"], CYAN, safe.centerx, safe.centery + 110, center=True)


# =========================
# HLAVNÍ SMYČKA
# =========================
def main():
    global game_state, input_text, menu_stage, selected_mode_idx, game_mode
    global roll_anim, busta_timer, current_p_idx, round_score, message
    global bot_phase, bot_timer, player_eliminated, has_loaded_dice
    global players, is_bot, scores, bot_risks, bot_queue
    global screen, WIDTH, HEIGHT, roll_sound_played, rattle_last_tick

    load_audio()
    clock = pygame.time.Clock()

    while True:
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                toggle_fullscreen()

            if event.type == pygame.VIDEORESIZE and not is_fullscreen:
                WIDTH, HEIGHT = max(1100, event.w), max(700, event.h)
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                update_fonts()

            if game_state == "menu":
                if event.type == pygame.KEYDOWN:
                    if menu_stage == "mode":
                        if event.key == pygame.K_UP:
                            selected_mode_idx = (selected_mode_idx - 1) % 3
                        elif event.key == pygame.K_DOWN:
                            selected_mode_idx = (selected_mode_idx + 1) % 3
                        elif event.key == pygame.K_RETURN:
                            game_mode = ["pvp", "bot", "tournament"][selected_mode_idx]
                            menu_stage = "name"

                    elif menu_stage == "name":
                        if event.key == pygame.K_RETURN and input_text:
                            if game_mode == "pvp":
                                players = [input_text, "Hráč 2"]
                                is_bot = [False, False]
                                scores = [0, 0]
                                game_state = "playing"
                                reset_turn()
                            elif game_mode == "bot":
                                bot_char = random.choice(KCD_CHARS)
                                players = [input_text, bot_char[0]]
                                is_bot = [False, True]
                                bot_risks = [0, bot_char[1]]
                                scores = [0, 0]
                                game_state = "playing"
                                reset_turn()
                            else:
                                setup_tournament(input_text)
                                game_state = "groups"
                        elif event.key == pygame.K_BACKSPACE:
                            input_text = input_text[:-1]
                        else:
                            if len(input_text) < 18 and event.unicode.isprintable():
                                input_text += event.unicode

            elif game_state == "groups":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    simulate_current_group_round()

            elif game_state == "bracket":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    simulate_playoff_step()

            elif game_state == "playing" and not is_bot[current_p_idx] and roll_anim == 0 and busta_timer == 0:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    layout = get_playing_layout()
                    mx, my = pygame.mouse.get_pos()
                    ds = layout["dice_size"]
                    gap = layout["gap"]
                    start_x = layout["dice_x"]
                    y = layout["dice_y"]

                    for i in range(6):
                        x = start_x + i * (ds + gap)
                        if x < mx < x + ds and y < my < y + ds and active[i]:
                            selected[i] = not selected[i]

                    if layout["roll_btn"].collidepoint(mx, my):
                        pts = get_selected_score()
                        if pts > 0:
                            round_score += pts
                            for i in range(6):
                                if selected[i]:
                                    active[i] = False
                                    selected[i] = False
                            if sum(active) == 0:
                                active[:] = [True] * 6
                            roll_anim = 35
                            roll_sound_played = False

                    elif layout["bank_btn"].collidepoint(mx, my):
                        pts = get_selected_score()
                        if pts > 0 or round_score > 0:
                            scores[current_p_idx] += (round_score + pts)
                            if scores[current_p_idx] >= WIN_SCORE:
                                game_state = "match_win"
                            else:
                                current_p_idx = 1 - current_p_idx
                                reset_turn()

            elif game_state == "tournament_end":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    game_state = "menu"
                    menu_stage = "mode"
                    input_text = ""

        if game_state == "groups_results" and now - groups_results_start > GROUP_RESULTS_SHOW_MS:
            build_playoff_bracket()
            game_state = "playoff_draw"

        if game_state == "playoff_draw" and now - playoff_draw_start > 2200:
            game_state = "bracket"

        if game_state == "playing" and is_bot[current_p_idx] and roll_anim == 0 and busta_timer == 0:
            if now > bot_timer:
                if bot_phase == "thinking":
                    valid = [i for i in range(6) if active[i]]
                    best_c = []

                    if round_score == 0 and all(active):
                        all_vals = [dice[i] for i in valid]
                        c = Counter(all_vals)
                        if len(all_vals) == 6 and sorted(c.values()) == [3, 3]:
                            best_c = valid[:]

                    if not best_c:
                        for r in range(1, len(valid) + 1):
                            for combo in itertools.combinations(valid, r):
                                if calculate_score([dice[idx] for idx in combo]) > 0:
                                    best_c = list(combo)

                    if best_c:
                        bot_queue = best_c
                        bot_phase = "picking"
                    bot_timer = now + 800

                elif bot_phase == "picking":
                    if bot_queue:
                        idx = bot_queue.pop(0)
                        selected[idx] = True
                        bot_timer = now + 550
                    else:
                        pts = get_selected_score()
                        round_score += pts
                        for i in range(6):
                            if selected[i]:
                                active[i] = False
                                selected[i] = False
                        if sum(active) == 0:
                            active[:] = [True] * 6
                        bot_phase = "deciding"
                        bot_timer = now + 1000
                        roll_sound_played = False

                elif bot_phase == "deciding":
                    if sum(active) >= 3 or round_score < bot_risks[current_p_idx]:
                        roll_anim = 35
                        bot_phase = "thinking"
                        roll_sound_played = False
                    else:
                        scores[current_p_idx] += round_score
                        if scores[current_p_idx] >= WIN_SCORE:
                            game_state = "match_win"
                        else:
                            current_p_idx = 1 - current_p_idx
                            reset_turn()
                    bot_timer = now + 500

        if game_state == "playing" and roll_anim > 0:
            if not roll_sound_played:
                play_sound(snd_dice_roll)
                roll_sound_played = True
                rattle_last_tick = now

            if snd_dice_rattle is not None and now - rattle_last_tick > 120 and roll_anim > 6:
                play_sound(snd_dice_rattle)
                rattle_last_tick = now

            roll_anim -= 1
            for i in range(6):
                if active[i]:
                    if i == 0 and has_loaded_dice:
                        dice[i] = random.choice([1, 3, 5])
                    else:
                        dice[i] = random.randint(1, 6)

            if roll_anim == 0:
                if not can_score():
                    message = "❌ NIC NEPADLO (Busta)!"
                    busta_timer = now + 2500
                elif is_bot[current_p_idx]:
                    bot_phase = "thinking"
                    bot_timer = now + 900

        if busta_timer > 0 and now > busta_timer:
            current_p_idx = 1 - current_p_idx
            reset_turn()

        if game_state == "menu":
            draw_menu()
        elif game_state == "groups":
            draw_groups()
        elif game_state == "groups_results":
            draw_groups_results()
        elif game_state == "playoff_draw":
            draw_playoff_draw()
        elif game_state == "bracket":
            draw_bracket()
        elif game_state == "playing":
            draw_playing()
        elif game_state == "match_win":
            draw_match_win()
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                finalize_current_match()
        elif game_state == "tournament_end":
            if tournament_winner and tournament_winner["name"] == input_text:
                has_loaded_dice = True
            draw_tournament_end()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
