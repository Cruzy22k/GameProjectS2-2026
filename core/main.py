from core.state import state
from render.window import Window

def main():
    x = state()
    window = Window()
    while x.running:
        if window.poll_quit():
            x.running = False
        eachtick = window.world_tick()
        x.update(eachtick)
        window.clear()
        window.flip()
    window.exit()
if __name__ == "__main__":
    main()