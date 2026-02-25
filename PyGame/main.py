# import pygame module in this program 
import pygame
 
# activate the pygame library . 
# initiate pygame and give permission 
# to use pygame's functionality. 
pygame.init()
 
# create the display surface object 
# of specific dimension..e(500, 500). 
screen = pygame.display.set_mode((500, 500))
 
# set the pygame screendow name 
pygame.display.set_caption("Jump Game")
 
# object current co-ordinates
x = 200
y = 200
 
# dimensions of the object
width = 30
height = 40
 
# Stores if player is jumping or not
isjump = False
 
# Force (v) up and mass m.
v = 7
m = 1
 
# Indicates pygame is running
run = True
ctverec = pygame.Rect(x, y, width, height)
cara1_rect = pygame.Rect(100, 200+height, 250, 2)
cara2_rect = pygame.Rect(400, 200+height*3, 500, 2)
# infinite loop
while run:
 
    # completely fill the surface object 
    # with black colour 
    screen.fill((0, 0, 0))
 
    # drascreeng object on screen which is rectangle here 

    pygame.draw.rect(screen, (255, 0, 0), ctverec)

    # Draw obstacles
    pygame.draw.rect(screen, (255, 255, 255), cara1_rect)
    pygame.draw.rect(screen, (255, 255, 255), cara2_rect)
    # iterate over the list of Event objects 
    # that was returned by pygame.event.get() method. 
    for event in pygame.event.get():
         
        # if event object type is QUIT 
        # then quitting the pygame 
        # and program both. 
        if event.type == pygame.QUIT:
             
            # it will make exit the while loop
            run = False
    # stores keys pressed
    keys = pygame.key.get_pressed() 
    if keys[pygame.K_a]:
        ctverec.x -= 5
    if keys[pygame.K_d]:
        ctverec.x += 5
 
        # if space bar is pressed
    if keys[pygame.K_SPACE]:
            
        # make isjump equal to True
        isjump = True
            
    if isjump :
        # calculate force (F). F = 1 / 2 * mass * velocity ^ 2.
        F =(1 / 2)*m*(v**2)
         
        # change in the y co-ordinate
        ctverec.y -= F
         
        # decreasing velocity while going up and become negative while coming down
        v = v-1
         
        # object reached its maximum height
        if v<0:
             
            # negative sign is added to counter negative velocity
            m =-1
 
            # objected reaches line and stops
            if cara1_rect.colliderect(ctverec):
                isjump = False
                v = 7 - 1
                m = 1
                ctverec.bottom = cara1_rect.top + 1
            if cara2_rect.colliderect(ctverec):
                isjump = False
                v = 7 - 1
                m = 1
                ctverec.bottom = cara2_rect.top + 1

     
    # creates time delay of 10ms
    pygame.time.delay(30)
 
    # it refreshes the screendow
    pygame.display.update() 
# closes the pygame screendow    
pygame.quit()