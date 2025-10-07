import pygame

pygame.mixer.init()

# --- Load Sounds ---
ambient_sound = pygame.mixer.Sound("assets/sounds/825858__vrymaa__monastery-atmosphere-monk-chant-chimes.wav")
button_sound = pygame.mixer.Sound("assets/sounds/613405__josheb_policarpio__button-6.wav")
orb_sound = pygame.mixer.Sound("assets/sounds/432287__ari_glitch__magic-circle-short-ringing-sfx.mp3")

ambient_volume = 0.3
sfx_volume = 0.2
sound_muted = False

ambient_channel = None  # Keep track of the channel playing ambient

def play_ambient():
    global ambient_channel
    ambient_channel = ambient_sound.play(-1)
    ambient_channel.set_volume(0 if sound_muted else ambient_volume)

def toggle_mute():
    global sound_muted
    sound_muted = not sound_muted
    volume = 0 if sound_muted else 1
    if ambient_channel:
        ambient_channel.set_volume(ambient_volume * volume)
    button_sound.set_volume(sfx_volume * volume)
    orb_sound.set_volume(sfx_volume * volume)

def change_ambient_volume(delta):
    global ambient_volume
    ambient_volume = max(0, min(1, ambient_volume + delta))
    if ambient_channel and not sound_muted:
        ambient_channel.set_volume(ambient_volume)

def change_sfx_volume(delta):
    global sfx_volume
    sfx_volume = max(0, min(1, sfx_volume + delta))
    if not sound_muted:
        button_sound.set_volume(sfx_volume)
        orb_sound.set_volume(sfx_volume)

def play_button_sound():
    if not sound_muted:
        button_sound.play()

def play_orb_sound():
    if not sound_muted:
        orb_sound.play()
