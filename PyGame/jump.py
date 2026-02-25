# import pygame module in this program 
import pygame
 
pygame.init()
 
win = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Jump Game")
 
x = 200
y = 200
 
width = 30
height = 40
 
isjump = False
 
v = 5
m = 1


speed = 5
 
run = True
ctverec = pygame.Rect(x, y, width, height)
cara1_rect = pygame.Rect(100, 200+height, 250, 2)
cara2_rect = pygame.Rect(400, 200+height, 500, 2)
while run:
 
    win.fill((0, 0, 0))
    pygame.draw.rect(win, (255, 0, 0), (x, y, width, height))
     
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()
   
   
    if keys[pygame.K_LEFT] and x > 0:
        x -= speed
        
    if keys[pygame.K_RIGHT] and x < 500 - width:
        x += speed
   

    if isjump == False:
        if keys[pygame.K_SPACE]:
            isjump = True
             
    if isjump:
        F = (1 / 2) * m * (v ** 2)
        y -= F
        v = v - 1
         
        if v < 0:
            m = -1
 

        if cara1_rect.colliderect(ctverec)
            isjump = False
            v = 7 - 1
            m = 1
            ctverec.bottom = cara1_rect


        if v == -6:
            isjump = False
            v = 5
            m = 1
     
    pygame.time.delay(25)
    pygame.display.update()
    
pygame.quit()