import threading
from neopixel import *
import RPi.GPIO as GPIO
import time

SENSECOVER = 12

# LED animations


def fastColorWipe(strip, update, ledsettings):
    brightness = ledsettings.backlight_brightness_percent / 100
    red = int(ledsettings.get_backlight_color("Red") * brightness)
    green = int(ledsettings.get_backlight_color("Green") * brightness)
    blue = int(ledsettings.get_backlight_color("Blue") * brightness)
    color = Color(green, red, blue)
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    if update:
        strip.show()


def theaterChase(strip, color, ledsettings, menu, wait_ms=25):
    """Movie theater light style chaser animation."""
    menu.screensaver_is_running = False
    time.sleep(0.5)
    if menu.screensaver_is_running:
        return
    menu.t = threading.currentThread()
    j = 0
    menu.screensaver_is_running = True

    while menu.screensaver_is_running:
        last_state = 1
        cover_opened = GPIO.input(SENSECOVER)
        while not cover_opened:
            if last_state != cover_opened:
                # clear if changed
                fastColorWipe(strip, True, ledsettings)
            time.sleep(.1)
            last_state = cover_opened
            cover_opened = GPIO.input(SENSECOVER)

        red = int(ledsettings.get_color("Red"))
        green = int(ledsettings.get_color("Green"))
        blue = int(ledsettings.get_color("Blue"))

        for q in range(5):
            for i in range(0, strip.numPixels(), 5):
                strip.setPixelColor(i + q, Color(green, red, blue))
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 5):
                strip.setPixelColor(i + q, 0)
        j += 1
        if j > 256:
            j = 0
    menu.screensaver_is_running = False
    fastColorWipe(strip, True, ledsettings)


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


def rainbow(strip, ledsettings, menu, wait_ms=20):
    """Draw rainbow that fades across all pixels at once."""
    menu.screensaver_is_running = False
    time.sleep(0.2)
    if menu.screensaver_is_running:
        return
    fastColorWipe(strip, True, ledsettings)
    menu.t = threading.currentThread()
    j = 0
    menu.screensaver_is_running = True
    while menu.screensaver_is_running:
        last_state = 1
        cover_opened = GPIO.input(SENSECOVER)
        while not cover_opened:
            if last_state != cover_opened:
                # clear if changed
                fastColorWipe(strip, True, ledsettings)
            time.sleep(.1)
            last_state = cover_opened
            cover_opened = GPIO.input(SENSECOVER)

        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel(j & 255))
        j += 1
        if j >= 256:
            j = 0
        strip.show()
        time.sleep(wait_ms / 1000.0)
    menu.screensaver_is_running = False
    fastColorWipe(strip, True, ledsettings)


def rainbowCycle(strip, ledsettings, menu, wait_ms=20):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    menu.screensaver_is_running = False
    time.sleep(0.2)
    if menu.screensaver_is_running:
        return
    fastColorWipe(strip, True, ledsettings)
    menu.t = threading.currentThread()
    j = 0
    menu.screensaver_is_running = True
    while menu.screensaver_is_running:
        last_state = 1
        cover_opened = GPIO.input(SENSECOVER)
        while not cover_opened:
            if last_state != cover_opened:
                # clear if changed
                fastColorWipe(strip, True, ledsettings)
            time.sleep(.1)
            last_state = cover_opened
            cover_opened = GPIO.input(SENSECOVER)

        for i in range(strip.numPixels()):
            strip.setPixelColor(
                i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        j += 1
        if j >= 256:
            j = 0
        strip.show()
        time.sleep(wait_ms / 1000.0)
    menu.screensaver_is_running = False
    fastColorWipe(strip, True, ledsettings)


def theaterChaseRainbow(strip, ledsettings, menu, wait_ms=25):
    """Rainbow movie theater light style chaser animation."""
    menu.screensaver_is_running = False
    time.sleep(0.5)
    if menu.screensaver_is_running:
        return
    fastColorWipe(strip, True, ledsettings)
    menu.t = threading.currentThread()
    j = 0
    menu.screensaver_is_running = True
    while menu.screensaver_is_running:
        last_state = 1
        cover_opened = GPIO.input(SENSECOVER)
        while not cover_opened:
            if last_state != cover_opened:
                # clear if changed
                fastColorWipe(strip, True, ledsettings)
            time.sleep(.1)
            last_state = cover_opened
            cover_opened = GPIO.input(SENSECOVER)

        for q in range(5):
            for i in range(0, strip.numPixels(), 5):
                strip.setPixelColor(i + q, wheel((i + j) % 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 5):
                strip.setPixelColor(i + q, 0)
        j += 1

        if j > 256:
            j = 0
    menu.screensaver_is_running = False
    fastColorWipe(strip, True, ledsettings)


def breathing(strip, ledsettings, menu, wait_ms=2):
    menu.screensaver_is_running = False
    time.sleep(0.1)
    if menu.screensaver_is_running:
        return
    fastColorWipe(strip, True, ledsettings)
    menu.t = threading.currentThread()
    menu.screensaver_is_running = True

    multiplier = 24
    direction = 2
    while menu.screensaver_is_running:
        last_state = 1
        cover_opened = GPIO.input(SENSECOVER)
        while not cover_opened:
            if last_state != cover_opened:
                # clear if changed
                fastColorWipe(strip, True, ledsettings)
            time.sleep(.1)
            last_state = cover_opened
            cover_opened = GPIO.input(SENSECOVER)

        if multiplier >= 98 or multiplier < 24:
            direction *= -1
        multiplier += direction
        divide = multiplier / float(100)
        red = int(round(float(ledsettings.get_color("Red")) * float(divide)))
        green = int(
            round(float(ledsettings.get_color("Green")) * float(divide)))
        blue = int(round(float(ledsettings.get_color("Blue")) * float(divide)))

        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(green, red, blue))
        strip.show()
        if wait_ms > 0:
            time.sleep(wait_ms / 1000.0)
    menu.screensaver_is_running = False
    fastColorWipe(strip, True, ledsettings)


def sound_of_da_police(strip, ledsettings, menu, wait_ms=5):
    menu.screensaver_is_running = False
    time.sleep(0.1)
    if menu.screensaver_is_running:
        return
    fastColorWipe(strip, True, ledsettings)
    menu.t = threading.currentThread()
    menu.screensaver_is_running = True
    middle = strip.numPixels() / 2
    r_start = 0
    l_start = 196
    while menu.screensaver_is_running:
        last_state = 1
        cover_opened = GPIO.input(SENSECOVER)
        while not cover_opened:
            if last_state != cover_opened:
                # clear if changed
                fastColorWipe(strip, True, ledsettings)
            time.sleep(.1)
            last_state = cover_opened
            cover_opened = GPIO.input(SENSECOVER)

        r_start += 14
        l_start -= 14
        for i in range(strip.numPixels()):
            if (i > middle) and i > r_start and i < (r_start + 40):
                strip.setPixelColor(i, Color(0, 255, 0))
            elif (i < middle) and i < l_start and i > (l_start - 40):
                strip.setPixelColor(i, Color(0, 0, 255))
            else:
                strip.setPixelColor(i, Color(0, 0, 0))
        if r_start > 150:
            r_start = 0
            l_start = 175
        strip.show()
        time.sleep(wait_ms / 1000.0)
    menu.screensaver_is_running = False
    fastColorWipe(strip, True, ledsettings)


def scanner(strip, ledsettings, menu, wait_ms=1):
    menu.screensaver_is_running = False
    time.sleep(0.1)
    if menu.screensaver_is_running:
        return
    fastColorWipe(strip, True, ledsettings)
    menu.t = threading.currentThread()
    menu.screensaver_is_running = True

    position = 0
    direction = 3
    scanner_length = 20

    red_fixed = ledsettings.get_color("Red")
    green_fixed = ledsettings.get_color("Green")
    blue_fixed = ledsettings.get_color("Blue")
    while menu.screensaver_is_running:
        last_state = 1
        cover_opened = GPIO.input(SENSECOVER)
        while not cover_opened:
            if last_state != cover_opened:
                # clear if changed
                fastColorWipe(strip, True, ledsettings)
            time.sleep(.1)
            last_state = cover_opened
            cover_opened = GPIO.input(SENSECOVER)

        position += direction
        for i in range(strip.numPixels()):
            if i > (position - scanner_length) and i < (position + scanner_length):
                distance_from_position = position - i
                if distance_from_position < 0:
                    distance_from_position *= -1
                divide = ((scanner_length / 2) -
                          distance_from_position) / float(scanner_length / 2)

                red = int(float(red_fixed) * float(divide))
                green = int(float(green_fixed) * float(divide))
                blue = int(float(blue_fixed) * float(divide))

                if divide > 0:
                    strip.setPixelColor(i, Color(green, red, blue))
                else:
                    strip.setPixelColor(i, Color(0, 0, 0))

        if position >= strip.numPixels() or position <= 1:
            direction *= -1
        strip.show()
        time.sleep(wait_ms / 1000.0)

    menu.screensaver_is_running = False
    fastColorWipe(strip, True, ledsettings)
