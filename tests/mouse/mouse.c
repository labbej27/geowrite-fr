/* Diagnostic : ce que le C64 recoit d'une souris 1351 sur chaque port. */
#include <c64.h>
#include <conio.h>
#include <stdio.h>

#define POTX (*(volatile unsigned char *)0xD419)
#define POTY (*(volatile unsigned char *)0xD41A)
#define PRA  (*(volatile unsigned char *)0xDC00)
#define PRB  (*(volatile unsigned char *)0xDC01)
#define DDRA (*(volatile unsigned char *)0xDC02)
/* $02A7 : 'M', compteur, puis pour chaque port x, y, boutons, nb de changements. */
#define DBG  ((volatile unsigned char *)0x02A7)

static unsigned char last_x[2], last_y[2], moves[2];

static void settle(void) {               /* la lecture POT prend 512 cycles */
    unsigned int i;
    for (i = 0; i < 400; ++i) { }
}

void main(void) {
    unsigned char port, x, y, buttons, n = 0;
    asm("sei");                          /* le scan clavier perturbe $DC00 */
    clrscr();
    cputs("test souris 1351\r\nbouge la souris et clique\r\n");
    DBG[0] = 'M';
    for (;;) {
        for (port = 0; port < 2; ++port) {
            DDRA = 0xC0;
            PRA = port ? 0x80 : 0x40;    /* choisit le port lu par le SID */
            settle();
            x = POTX;
            y = POTY;
            buttons = (port ? PRA : PRB) & 0x1F;
            if (n && (x != last_x[port] || y != last_y[port])) ++moves[port];
            last_x[port] = x;
            last_y[port] = y;
            DBG[2 + port * 4] = x;
            DBG[3 + port * 4] = y;
            DBG[4 + port * 4] = buttons;
            DBG[5 + port * 4] = moves[port];
            gotoxy(0, 4 + port);
            cprintf("port %u  x=%3u y=%3u btn=%02x chg=%3u", port + 1, x, y, buttons, moves[port]);
        }
        DBG[1] = ++n;
    }
}
