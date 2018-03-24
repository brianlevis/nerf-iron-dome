import curses
import sys
import nerf_turret
import time

screen = curses.initscr()
curses.noecho()
curses.cbreak()
screen.keypad(True)
screen.nodelay(True)

reflect = sys.argv[1]

def main_loop(rel):
    global last_pressed
    motion = 'n'
    vel = 60
    try:
        while True:

            char = screen.getch()

            if char == ord('q'):
                break
            elif char == ord('u'):
                if vel + 5 < 127:
                    vel += 5
                    print("Velocity at",vel)
                else:
                    vel = 127
                    print("Velocity at max")
            elif char == ord('d'):
                if vel - 5 > 0:
                    vel -= 5
                    print("Velocity at",vel)
                else:
                    vel = 0
                    print("Velocity at min")

            elif char == curses.KEY_RIGHT:
                last_pressed = time.time()
                if motion != 'r':
                    nerf_turret.send_v(rel*vel, 0)
                    motion = 'r'

            elif char == curses.KEY_LEFT:
                last_pressed = time.time()
                if motion != 'l':
                    nerf_turret.send_v(rel*-vel, 0)
                    motion = 'l'

            elif char == curses.KEY_UP:
                last_pressed = time.time()
                if motion != 'u':
                    nerf_turret.send_v(0, max(vel-20,0))
                    motion = 'u'

            elif char == curses.KEY_DOWN:
                last_pressed = time.time()
                if motion != 'd':
                    nerf_turret.send_v(0, min(-vel+20,0))
                    motion = 'd'

            if motion != 'n' and time.time() - last_pressed > 0.5:
                nerf_turret.send_v(0,0)
                motion = 'n'

    finally:
        nerf_turret.send_command('p', 0)
        nerf_turret.send_command('t', 0)
        curses.nocbreak(); screen.keypad(0); curses.echo(); screen.nodelay(0)
        curses.endwin()

main_loop(1 if reflect[0] == "n" else -1)

