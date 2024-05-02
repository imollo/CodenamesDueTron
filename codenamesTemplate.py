from PIL import Image,ImageDraw,ImageFont
import random

def listaAMatriz(L,n):
    """Divide la lista L en sublistas de tamaño n. Requiere que la longitud de L sea divisible por n."""
    N = len(L)//n
    M = [ L[i*(len(L)//N):(i+1)*(len(L)//N)] for i in range(N)]
    return M

def pegarCeldas(fondo, M, P, WS, CAR, SEP):
    # Los colores para el fondo de las pistas y las pistas 
    ASE_COLOR = (35,35,35)
    CLUE_ASE_COLOR = (97,76,76)
    CIV_COLOR = (228,210,165)
    CLUE_CIV_COLOR = (122,111,84)
    ESP_COLOR = (3,159,67)
    CLUE_ESP_COLOR = (1,92,37)
    NAD_COLOR = (150,150,150)
    CLUE_NAD_COLOR = (70,70,70)

    # Las imágenes para usar de base
    ASE_IMAGE = Image.new('RGB',WS,ASE_COLOR)
    CIV_IMAGE = Image.new('RGB',WS,CIV_COLOR)    
    ESP_IMAGE = Image.new('RGB',WS,ESP_COLOR)
    NAD_IMAGE = Image.new('RGB',WS,NAD_COLOR)
    

    # La fuente para las pistas
    CLUE_FONT = ImageFont.truetype(r'/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',18)
    
    # Aquí pego las celdas en fondo
    for i in range(len(P[0])):
        for j in range(len(P)):
            ch = M[j][i]
            pa = P[j][i]            
            box = (SEP+i*(WS[0]+SEP),CAR+SEP+j*(WS[1]+SEP), SEP+i*(WS[0]+SEP)+WS[0],CAR+SEP+j*(WS[1]+SEP)+WS[1])
            (cajita,clue_col) = (ESP_IMAGE.copy(),CLUE_ESP_COLOR) if ch=='e' else ((CIV_IMAGE.copy(),CLUE_CIV_COLOR) if ch=='c' else ((ASE_IMAGE.copy(),CLUE_ASE_COLOR) if ch=='a' else (NAD_IMAGE.copy(),CLUE_NAD_COLOR)))
            daux = ImageDraw.Draw(cajita)
            daux_w,daux_h = daux.textsize(pa,font=CLUE_FONT)
            daux.text( ((WS[0]-daux_w)//2,(WS[1]-daux_h)//2), pa, font=CLUE_FONT, fill=clue_col)
            fondo.paste(cajita,box)

def pegarCaratula(fondo,CAR_W,CAR_H,CAR_SEP):
    #CODE_FONT = ImageFont.truetype('SkyFallDone.ttf',50)
    #VLAA_FONT = ImageFont.truetype('SkyFallDone.ttf',18)
    CODE_FONT = ImageFont.truetype('Skyfall.ttf',50)
    VLAA_FONT = ImageFont.truetype('Skyfall.ttf',18)
    CODE_msg = "CODENAMES DUET"
    VLAA_msg = "VLAADA CHVATIL & SCOT EATON"
    
    d = ImageDraw.Draw(fondo)
    V_w,V_h = d.textsize(VLAA_msg,font=VLAA_FONT)
    C_w,C_h = d.textsize(CODE_msg,font=CODE_FONT)
    d.text( ((CAR_W-V_w)//2,(CAR_H-C_h-V_h-CAR_SEP)//2), VLAA_msg, font=VLAA_FONT, fill='white')
    d.text( ((CAR_W-C_w)//2,((CAR_H-C_h-V_h-CAR_SEP)//2)+V_h+CAR_SEP), CODE_msg, font=CODE_FONT,fill='white')
    

def crearImagenDeClaves(L,palabras,n=5,m=5):    
    SEP = 5       # La separación H y V entre dos celdas 
    WS = (150,45) # Word Size: el tamaño de las celdas
    CAR = 125     # La altura de la carátula

    FON_COLOR = (0,0,0) #(10,22,3)
    fondo = Image.new('RGB',(SEP+(WS[0]+SEP)*m,CAR+SEP+(WS[1]+SEP)*n),FON_COLOR)
    
    #Aquí pego las celdas
    M = listaAMatriz(L,n)
    P = listaAMatriz(palabras,n)
    pegarCeldas(fondo, M, P, WS, CAR, SEP)

    #Aquí escribo la carátula de la imagen    
    CAR_W = SEP+(WS[0]+SEP)*m
    CAR_H = CAR
    CAR_SEP = 10
    pegarCaratula(fondo,CAR_W,CAR_H,CAR_SEP)
    
    return fondo


###################################################################  
