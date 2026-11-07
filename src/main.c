/* Projet de test : sprite au joystick (port 2), son sur feu, mesure CPU. */
#include <c64.h>
#include <conio.h>
#include <stdlib.h>
#include <string.h>

extern void __fastcall__ wait_frame(void);
extern unsigned char __fastcall__ read_joy2(void);
extern void __fastcall__ sfx_blip(void);
extern unsigned char idle_count[3];

/* Zone libre $02A7-$02FF : etat lisible depuis le Mac par l'API. */
#define DBG ((volatile unsigned char *)0x02A7)
enum { D_MAGIC = 0, D_FRAME = 3, D_XLO = 4, D_XHI = 5, D_Y = 6,
       D_IDLE = 7, D_INPUT = 10, D_FIRED = 11 };

#define IN_UP 1
#define IN_DOWN 2
#define IN_LEFT 4
#define IN_RIGHT 8
#define IN_FIRE 16

#define SPRITE_BLOCK 13                       /* 13 * 64 = $0340 */
#define SPRITE_DATA ((unsigned char *)0x0340)
#define SPRITE_PTR0 (*(unsigned char *)0x07F8)

/* Au-dessus de ce seuil, la machine ne se comporte pas comme un C64 d'origine. */
#define STOCK_IDLE_MAX 2000UL

static const unsigned char ball[63] = {
    0x00,0xFF,0x00, 0x03,0xFF,0xC0, 0x0F,0xFF,0xF0, 0x1F,0xFF,0xF8,
    0x3F,0xFF,0xFC, 0x3F,0xFF,0xFC, 0x7F,0xFF,0xFE, 0x7F,0xFF,0xFE,
    0xFF,0xFF,0xFF, 0xFF,0xFF,0xFF, 0xFF,0xFF,0xFF, 0xFF,0xFF,0xFF,
    0xFF,0xFF,0xFF, 0x7F,0xFF,0xFE, 0x7F,0xFF,0xFE, 0x3F,0xFF,0xFC,
    0x3F,0xFF,0xFC, 0x1F,0xFF,0xF8, 0x0F,0xFF,0xF0, 0x03,0xFF,0xC0,
    0x00,0xFF,0x00
};

static unsigned int x = 172;
static unsigned char y = 140;
static unsigned char input, last_input, frame, fired;
static unsigned long idle;
static char text[12];

static void show_cpu(void) {
    ultoa(idle, text, 10);
    gotoxy(0, 4);  cclear(40);
    gotoxy(0, 4);  cputs("marge cpu: ");  cputs(text);
    gotoxy(0, 5);  cclear(40);
    gotoxy(0, 5);
    cputs(idle > STOCK_IDLE_MAX ? "TURBO ACTIF: TEST NON REPRESENTATIF"
                                : "VITESSE C64 D'ORIGINE");
}

void main(void) {
    DBG[D_INPUT] = 0;
    DBG[D_FIRED] = 0;

    VIC.bordercolor = COLOR_BLUE;
    VIC.bgcolor0 = COLOR_BLACK;
    textcolor(COLOR_WHITE);
    clrscr();
    cputs("C64-DEV : test de la chaine\r\n");
    cputs("joystick port 2, feu = son\r\n");

    memcpy(SPRITE_DATA, ball, sizeof ball);
    SPRITE_PTR0 = SPRITE_BLOCK;
    VIC.spr0_color = COLOR_YELLOW;
    VIC.spr_ena = 1;

    DBG[D_MAGIC] = 'C';
    DBG[D_MAGIC + 1] = '6';
    DBG[D_MAGIC + 2] = '4';

    for (;;) {
        wait_frame();

        VIC.spr0_x = (unsigned char)x;
        VIC.spr_hi_x = (unsigned char)(x >> 8);
        VIC.spr0_y = y;

        idle = idle_count[0] | ((unsigned int)idle_count[1] << 8)
             | ((unsigned long)idle_count[2] << 16);

        /* D_INPUT non nul remplace le joystick pour les tests a distance. */
        input = DBG[D_INPUT] ? DBG[D_INPUT] : read_joy2();
        if ((input & IN_LEFT)  && x > 24)  x -= 2;
        if ((input & IN_RIGHT) && x < 320) x += 2;
        if ((input & IN_UP)    && y > 50)  y -= 2;
        if ((input & IN_DOWN)  && y < 229) y += 2;
        if ((input & IN_FIRE) && !(last_input & IN_FIRE)) {
            sfx_blip();
            ++fired;
        }
        last_input = input;

        ++frame;
        DBG[D_FRAME] = frame;
        DBG[D_XLO] = (unsigned char)x;
        DBG[D_XHI] = (unsigned char)(x >> 8);
        DBG[D_Y] = y;
        DBG[D_IDLE] = idle_count[0];
        DBG[D_IDLE + 1] = idle_count[1];
        DBG[D_IDLE + 2] = idle_count[2];
        DBG[D_FIRED] = fired;

        if (frame % 50 == 0) show_cpu();
    }
}
