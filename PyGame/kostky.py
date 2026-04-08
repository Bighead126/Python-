import pygame
import random
import sys
from collections import Counter

pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kostky (KCD styl)")

font = pygame.font.SysFont(None, 30)
big_font = pygame.font.SysFont(None, 50)

# BARVY
BG = (30, 30, 40)
PANEL = (50, 50, 70)
WHITE = (255,255,255)
GREEN = (120,255,120)
GRAY = (180,180,180)
RED = (255,80,80)
YELLOW = (255,220,120)

# GAME STATE
players = []
scores = []
current_player = 0
dice = [0]*6
active = [True]*6
selected = [False]*6
round_score = 0
message = ""
game_state = "menu"
dice_pos = [(450,300)]*6
dice_target_pos = [(350+i*100,300) for i in range(6)]
WIN_SCORE = 4000

# 🎲 HOD DICE
def roll_dice():
    for i in range(6):
        if active[i]:
            dice[i] = random.randint(1,6)

def animate_roll():
    for _ in range(10):
        for i in range(6):
            if active[i]:
                dice[i] = random.randint(1,6)
                dx = random.randint(-10,10)
                dy = random.randint(-10,10)
                dice_pos[i] = (dice_target_pos[i][0]+dx,dice_target_pos[i][1]+dy)
        draw_game()
        pygame.display.flip()
        pygame.time.delay(50)
    for i in range(6):
        dice_pos[i] = dice_target_pos[i]

# SKÓRE
def calculate_selection_score(selection):
    counts = Counter(selection)
    length = len(selection)

    # postupky
    if sorted(selection) == [1,2,3,4,5]:
        return 500
    if sorted(selection) == [2,3,4,5,6]:
        return 750
    if sorted(selection) == [1,2,3,4,5,6]:
        return 1500

    if length==6 and all(v==2 for v in counts.values()):
        return 1500
    if length==6 and list(counts.values()).count(3)==2:
        return 2500

    score = 0
    for num,count in counts.items():
        if count>=3:
            base = 1000 if num==1 else num*100
            score += base*(2**(count-3))
            count=0
        if num==1:
            score += count*100
        elif num==5:
            score += count*50
        else:
            if count>0:
                return 0
    return score

def any_scoring_possible():
    active_dice = [dice[i] for i in range(6) if active[i]]
    counts = Counter(active_dice)
    if not active_dice: return True
    if any(v in [1,5] for v in active_dice): return True
    if any(c>=3 for c in counts.values()): return True
    sorted_d = sorted(active_dice)
    if sorted_d in ([1,2,3,4,5],[2,3,4,5,6]): return True
    if len(active_dice)==6:
        if sorted_d==[1,2,3,4,5,6]: return True
        if all(v==2 for v in counts.values()): return True
        if list(counts.values()).count(3)==2: return True
    return False

# KRESLENÍ KOSTKY
def draw_die(x,y,val,is_active,is_selected,color_override=None):
    color = GRAY
    if not is_active: color=GREEN
    if is_selected: color=RED
    if color_override: color=color_override
    pygame.draw.rect(screen,color,(x,y,80,80),border_radius=10)
    cx,cy = x+40,y+40
    o=20
    dots = {1:[(0,0)],2:[(-o,-o),(o,o)],3:[(-o,-o),(0,0),(o,o)],
            4:[(-o,-o),(o,-o),(-o,o),(o,o)],
            5:[(-o,-o),(o,-o),(0,0),(-o,o),(o,o)],
            6:[(-o,-o),(o,-o),(-o,0),(o,0),(-o,o),(o,o)]}
    for dx,dy in dots[val]:
        pygame.draw.circle(screen,BG,(cx+dx,cy+dy),6)

# TABULKA SKÓRE
def draw_scoreboard():
    pygame.draw.rect(screen,PANEL,(0,0,300,HEIGHT))
    y=40
    for i,name in enumerate(players):
        text = f"{name}: {scores[i]}"
        color = YELLOW if i==current_player else WHITE
        screen.blit(font.render(text,True,color),(20,y))
        y+=40

def draw_game(color_override=None):
    screen.fill(BG)
    draw_scoreboard()
    for i in range(6):
        draw_die(dice_pos[i][0],dice_pos[i][1],dice[i],active[i],selected[i],color_override=color_override)
    screen.blit(font.render(f"Kolo: {round_score}",True,WHITE),(350,200))
    screen.blit(font.render(message,True,WHITE),(350,600))
    # Tlačítka
    pygame.draw.rect(screen,PANEL,(350,100,180,50),border_radius=10)
    screen.blit(font.render("Hodit",True,WHITE),(390,115))
    pygame.draw.rect(screen,PANEL,(550,100,180,50),border_radius=10)
    screen.blit(font.render("Vzít",True,WHITE),(610,115))
    pygame.draw.rect(screen,PANEL,(750,100,200,50),border_radius=10)
    screen.blit(font.render("Zapsat",True,WHITE),(800,115))
    pygame.display.flip()

# WIN SCREEN
def draw_win(winner):
    screen.fill(BG)
    screen.blit(big_font.render(f"{winner} vyhrál!", True, GREEN),(250,200))
    # Celkové skóre všech hráčů
    y=300
    for i,name in enumerate(players):
        text=f"{name}: {scores[i]}"
        screen.blit(font.render(text,True,WHITE),(350,y))
        y+=40
    # Možnost restartu
    pygame.draw.rect(screen,PANEL,(350,500,180,50),border_radius=10)
    screen.blit(font.render("Nová hra",True,WHITE),(390,515))
    pygame.draw.rect(screen,PANEL,(550,500,180,50),border_radius=10)
    screen.blit(font.render("Menu",True,WHITE),(610,515))
    pygame.display.flip()

def next_player():
    global current_player,round_score,active,selected
    current_player = (current_player+1)%len(players)
    round_score=0
    active=[True]*6
    selected=[False]*6
    dice_pos[:] = [(450,300)]*6
    roll_dice()

# Hlavní smyčka
def main():
    global players,scores,game_state,message,round_score,active,selected,dice,WIN_SCORE
    clock = pygame.time.Clock()
    input_text = ""
    stage = "names"  # menu stage: names / target_score

    target_options = [4000,5000,10000,15000,20000]
    selected_target = 4000

    while True:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit(); sys.exit()

            if game_state=="menu":
                screen.fill(BG)
                if stage=="names":
                    screen.blit(big_font.render("Zadej jména hráčů (oddělit čárkou)",True,WHITE),(50,150))
                    screen.blit(font.render(input_text,True,WHITE),(50,250))
                elif stage=="target":
                    screen.blit(big_font.render("Vyber cílové skóre",True,WHITE),(50,150))
                    for i,opt in enumerate(target_options):
                        color=YELLOW if opt==selected_target else WHITE
                        screen.blit(font.render(str(opt),True,color),(50,250+i*50))
                pygame.display.flip()

                if event.type==pygame.KEYDOWN:
                    if stage=="names":
                        if event.key==pygame.K_RETURN and input_text:
                            players=input_text.split(",")
                            scores=[0]*len(players)
                            stage="target"
                        elif event.key==pygame.K_BACKSPACE:
                            input_text=input_text[:-1]
                        else:
                            input_text+=event.unicode
                    elif stage=="target":
                        if event.key==pygame.K_DOWN:
                            idx=target_options.index(selected_target)
                            if idx<len(target_options)-1: selected_target=target_options[idx+1]
                        if event.key==pygame.K_UP:
                            idx=target_options.index(selected_target)
                            if idx>0: selected_target=target_options[idx-1]
                        if event.key==pygame.K_RETURN:
                            WIN_SCORE=selected_target
                            game_state="game"
                            dice_pos[:] = [(450,300)]*6
                            roll_dice()

            elif game_state=="game":
                draw_game()
                if event.type==pygame.MOUSEBUTTONDOWN:
                    mx,my=pygame.mouse.get_pos()
                    # kostky
                    for i in range(6):
                        x=dice_pos[i][0]
                        y=dice_pos[i][1]
                        if x<mx<x+80 and y<my<y+80 and active[i]:
                            selected[i]=not selected[i]
                    # Hodit
                    if 350<mx<530 and 100<my<150:
                        animate_roll()
                        if not any_scoring_possible():
                            draw_game(color_override=RED)
                            pygame.display.flip()
                            pygame.time.delay(5000)
                            next_player()
                            message=""
                    # Vzít
                    if 550<mx<730 and 100<my<150:
                        chosen=[dice[i] for i in range(6) if selected[i] and active[i]]
                        pts=calculate_selection_score(chosen)
                        if pts>0:
                            round_score+=pts
                            for i in range(6):
                                if selected[i]: active[i]=False; selected[i]=False
                            if all(not a for a in active):
                                active=[True]*6
                                dice_pos[:] = [(450,300)]*6
                                animate_roll()
                        else: message="❌ Neplatné"
                    # Zapsat
                    if 750<mx<950 and 100<my<150:
                        scores[current_player]+=round_score
                        if scores[current_player]>=WIN_SCORE:
                            game_state="win"
                        else:
                            next_player()

            elif game_state=="win":
                draw_win(players[current_player])
                if event.type==pygame.MOUSEBUTTONDOWN:
                    mx,my=pygame.mouse.get_pos()
                    if 350<mx<530 and 500<my<550:  # Nová hra
                        game_state="menu"
                        stage="names"
                        input_text=""
                    if 550<mx<730 and 500<my<550:  # Menu
                        game_state="menu"
                        stage="names"
                        input_text=""
        clock.tick(60)

if __name__=="__main__":
    main()