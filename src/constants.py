# constants.py

# Ukuran Jendela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Warna (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE_SKY = (135, 206, 235) # Biru langit (Latar Belakang Level)
GRAY = (200, 200, 200) # Warna tombol
GREEN = (0, 255, 0) # Warna Bob (jika tidak pakai aset)
BROWN = (139, 69, 19) # Warna Tanah (jika tidak pakai aset)

# State Game
STATE_MENU = 0
STATE_LEVEL_SELECT = 1
STATE_PLAYING = 2
# Bisa tambahkan state lain seperti STATE_GAME_OVER, STATE_LEVEL_COMPLETE

# Pengaturan Game
BOB_SPEED = 2
BOB_RADIUS = 15 # Mungkin masih berguna untuk deteksi klik jika aset Bob transparan di pinggir
GRAVITY = 0.5 #GRAVITASI

DOOR_IMAGE_FILE = 'door.png'
# Path Aset
ASSET_DIR = 'assets'
BOB_IMAGE_FILE = 'bob.png'
BLOCK_IMAGE_FILE = 'block.png'
LEVER_UP_IMAGE_FILE = 'lever_up.png'
LEVER_DOWN_IMAGE_FILE = 'lever_down.png'
MOVABLE_WALL_SPEED = 1