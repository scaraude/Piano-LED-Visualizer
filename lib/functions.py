import threading
from constants import *
from lib.ledanimations import *
from mappers.mappers import map_midi_note_to_literal_note
from neopixel import *
import mido
import datetime
import psutil
import time
import socket
import RPi.GPIO as GPIO

SENSECOVER = 12
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSECOVER, GPIO.IN, GPIO.PUD_UP)


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip


def find_between(s, start, end):
    try:
        return (s.split(start))[1].split(end)[0]
    except:
        return False


def find_value_of(value, message):
    return find_between(str(message), value + "=", " ")


def is_alternative_key(midi_note):
    return "#" in map_midi_note_to_literal_note(midi_note)


def get_s_color(hand_colorList, hand_color, is_alternative_key):
    red = int(hand_colorList[hand_color][0])
    green = int(hand_colorList[hand_color][1])
    blue = int(hand_colorList[hand_color][2])
    return Color(green, red, blue)


def clamp(val, val_min, val_max):
    return max(val_min, min(val, val_max))


def shift(l, n):
    return l[n:] + l[:n]


def play_midi(song_path, midiports, saving, menu, ledsettings, ledstrip):
    midiports.pending_queue.append(mido.Message('note_on'))

    if song_path in saving.is_playing_midi.keys():
        menu.render_message(song_path, "Already playing", 2000)
        return

    saving.is_playing_midi.clear()

    saving.is_playing_midi[song_path] = True
    menu.render_message("Playing: ", song_path, 2000)
    saving.t = threading.currentThread()

    try:
        mid = mido.MidiFile("Songs/" + song_path)
        fastColorWipe(ledstrip.strip, True, ledsettings)
        #length = mid.length
        t0 = False
        total_delay = 0
        delay = 0
        for message in mid:
            if song_path in saving.is_playing_midi.keys():
                if not t0:
                    t0 = time.time()

                total_delay += message.time
                current_time = (time.time() - t0) + message.time
                drift = total_delay - current_time

                if (drift < 0):
                    delay = message.time + drift
                else:
                    delay = message.time
                if(delay < 0):
                    delay = 0

                if delay > 0:
                    time.sleep(delay)
                if not message.is_meta:
                    midiports.playport.send(message)
                    midiports.pending_queue.append(message.copy(time=0))

            else:
                break
        print('play time: {:.2f} s (expected {:.2f})'.format(
            time.time() - t0, total_delay))
        #print('play time: {:.2f} s (expected {:.2f})'.format(time.time() - t0, length))
        # saving.is_playing_midi = False
    except:
        menu.render_message(song_path, "Can't play this file", 2000)
    saving.is_playing_midi.clear()


def screensaver(menu, midiports, saving, ledstrip, ledsettings):
    KEY2 = 20
    GPIO.setup(KEY2, GPIO.IN, GPIO.PUD_UP)

    delay = 0.1
    interval = 3 / float(delay)
    i = 0
    cpu_history = [None] * int(interval)
    cpu_chart = [0] * 28
    cpu_average = 0

    upload = 0
    download = 0
    upload_start = 0
    download_start = 0
    local_ip = 0

    if menu.screensaver_settings["local_ip"] == "1":
        local_ip = get_ip_address()

    try:
        midiports.inport.poll()
    except:
        pass
    while True:
        if (time.time() - saving.start_time) > 3600 and delay < 0.5 and menu.screensaver_is_running == False:
            delay = 0.9
            interval = 5 / float(delay)
            cpu_history = [None] * int(interval)
            cpu_average = 0
            i = 0

        if int(menu.screen_off_delay) > 0 and ((time.time() - saving.start_time) > (int(menu.screen_off_delay) * 60)):
            menu.screen_status = 0
            GPIO.output(24, 0)

        if int(menu.led_animation_delay) > 0 and ((time.time() - saving.start_time) > (
                int(menu.led_animation_delay) * 60)) and menu.screensaver_is_running == False:
            menu.screensaver_is_running = True
            if menu.led_animation == "Theater Chase":
                menu.t = threading.Thread(target=theaterChase, args=(ledstrip.strip,
                                                                     Color(
                                                                         127, 127, 127),
                                                                     ledsettings,
                                                                     menu))
                menu.t.start()
            if menu.led_animation == "Breathing Slow":
                menu.t = threading.Thread(target=breathing, args=(ledstrip.strip,
                                                                  ledsettings,
                                                                  menu, 25))
                menu.t.start()
            if menu.led_animation == "Rainbow Slow":
                menu.t = threading.Thread(target=rainbow, args=(ledstrip.strip,
                                                                ledsettings,
                                                                menu, 50))
                menu.t.start()
            if menu.led_animation == "Rainbow Cycle Slow":
                menu.t = threading.Thread(target=rainbowCycle, args=(ledstrip.strip,
                                                                     ledsettings,
                                                                     menu, 50))
                menu.t.start()
            if menu.led_animation == "Theater Chase Rainbow":
                menu.t = threading.Thread(target=theaterChaseRainbow, args=(ledstrip.strip,
                                                                            ledsettings,
                                                                            menu, 5))
                menu.t.start()
            if menu.led_animation == "Sound of da police":
                menu.t = threading.Thread(target=sound_of_da_police, args=(ledstrip.strip,
                                                                           ledsettings,
                                                                           menu, 1))
                menu.t.start()
            if menu.led_animation == "Scanner":
                menu.t = threading.Thread(target=scanner, args=(ledstrip.strip,
                                                                ledsettings,
                                                                menu, 1))
                menu.t.start()

        hour = datetime.datetime.now().strftime("%H:%M:%S")
        date = datetime.datetime.now().strftime("%d-%m-%Y")
        cpu_usage = psutil.cpu_percent()
        cpu_history[i] = cpu_usage
        cpu_chart.append(cpu_chart.pop(0))
        cpu_chart[27] = cpu_usage

        if i >= (int(interval) - 1):
            i = 0
            try:
                cpu_average = sum(cpu_history) / (float(len(cpu_history) + 1))
                last_cpu_average = cpu_average
            except:
                cpu_average = last_cpu_average

        if menu.screensaver_settings["ram"] == "1":
            ram_usage = psutil.virtual_memory()[2]
        else:
            ram_usage = 0

        if menu.screensaver_settings["temp"] == "1":
            try:
                temp = find_between(str(psutil.sensors_temperatures()[
                                    "cpu_thermal"]), "current=", ",")
            except:
                temp = find_between(str(psutil.sensors_temperatures()[
                                    "cpu-thermal"]), "current=", ",")
            temp = round(float(temp), 1)
        else:
            temp = 0

        if menu.screensaver_settings["network_usage"] == "1":
            upload_end = psutil.net_io_counters().bytes_sent
            download_end = psutil.net_io_counters().bytes_recv

            if upload_start:
                upload = upload_end - upload_start
                upload = upload * (1 / delay)
                upload = upload / 1000000
                upload = round(upload, 2)

            if download_start:
                download = download_end - download_start
                download = download * (1 / delay)
                download = download / 1000000
                download = round(download, 2)

            upload_start = upload_end
            download_start = download_end
        else:
            upload = 0
            download = 0
        if menu.screensaver_settings["sd_card_space"] == "1":
            card_space = psutil.disk_usage('/')
        else:
            card_space = 0

        menu.render_screensaver(hour, date, cpu_usage, round(cpu_average, 1), ram_usage, temp, cpu_chart, upload,
                                download, card_space, local_ip)
        time.sleep(delay)
        i += 1
        try:
            if str(midiports.inport.poll()) != "None":
                menu.screensaver_is_running = False
                saving.start_time = time.time()
                menu.screen_status = 1
                GPIO.output(24, 1)
                midiports.reconnect_ports()
                midiports.last_activity = time.time()
                menu.show()
                break
        except:
            pass
        if GPIO.input(KEY2) == 0:
            menu.screensaver_is_running = False
            saving.start_time = time.time()
            menu.screen_status = 1
            GPIO.output(24, 1)
            midiports.reconnect_ports()
            menu.show()
            break


# Get note position on the strip
def get_note_position(note, ledstrip, ledsettings):
    note_offsets = ledsettings.note_offsets
    note_offset = 0
    for i in range(0, len(note_offsets)):
        if note > note_offsets[i][0]:
            note_offset = note_offsets[i][1]
            break
    note_offset -= ledstrip.shift
    note_pos_raw = 2 * (note - 20) - note_offset
    if ledstrip.reverse:
        return max(0, ledstrip.led_number - note_pos_raw)
    else:
        return max(0, note_pos_raw)

# scale: 1 means in C, scale: 2 means in C#, scale: 3 means in D, etc...


def get_scale_color(scale, note_position, ledsettings):
    notes_in_scale = [0, 2, 4, 5, 7, 9, 11]
    scale = int(scale)
    note_position = (note_position - scale) % 12

    if note_position in notes_in_scale:
        return list(ledsettings.key_in_scale.values())
    else:
        return list(ledsettings.key_not_in_scale.values())


def get_rainbow_colors(pos, color):
    pos = int(pos)
    if pos < 85:
        if color == "green":
            return pos * 3
        elif color == "red":
            return 255 - pos * 3
        elif color == "blue":
            return 0
    elif pos < 170:
        pos -= 85
        if color == "green":
            return 255 - pos * 3
        elif color == "red":
            return 0
        elif color == "blue":
            return pos * 3
    else:
        pos -= 170
        if color == "green":
            return 0
        elif color == "red":
            return pos * 3
        elif color == "blue":
            return 255 - pos * 3


def handle_GPIO_interface(midiports, menu, ledstrip, ledsettings, usersettings):
    if GPIO.input(KEYUP) == 0:
        midiports.last_activity = time.time()
        menu.change_pointer(0)
        while GPIO.input(KEYUP) == 0:
            time.sleep(0.001)
    if GPIO.input(KEYDOWN) == 0:
        midiports.last_activity = time.time()
        menu.change_pointer(1)
        while GPIO.input(KEYDOWN) == 0:
            time.sleep(0.001)
    if GPIO.input(KEY1) == 0:
        midiports.last_activity = time.time()
        menu.enter_menu()
        while GPIO.input(KEY1) == 0:
            time.sleep(0.001)
    if GPIO.input(KEY2) == 0:
        midiports.last_activity = time.time()
        menu.go_back()
        if not menu.screensaver_is_running:
            fastColorWipe(ledstrip.strip, True, ledsettings)
        while GPIO.input(KEY2) == 0:
            time.sleep(0.01)
    if GPIO.input(KEY3) == 0:
        midiports.last_activity = time.time()
        if ledsettings.sequence_active == True:
            ledsettings.set_sequence(0, 1)
        else:
            active_input = usersettings.get_setting_value("input_port")
            secondary_input = usersettings.get_setting_value(
                "secondary_input_port")
            midiports.change_port("inport", secondary_input)
            usersettings.change_setting_value(
                "secondary_input_port", active_input)
            usersettings.change_setting_value("input_port", secondary_input)
            fastColorWipe(ledstrip.strip, True, ledsettings)

        while GPIO.input(KEY3) == 0:
            time.sleep(0.01)
    if GPIO.input(KEYLEFT) == 0:
        midiports.last_activity = time.time()
        menu.change_value("LEFT")
        time.sleep(0.1)
    if GPIO.input(KEYRIGHT) == 0:
        midiports.last_activity = time.time()
        menu.change_value("RIGHT")
        time.sleep(0.1)
    if GPIO.input(JPRESS) == 0:
        midiports.last_activity = time.time()
        menu.speed_change()
        while GPIO.input(JPRESS) == 0:
            time.sleep(0.01)
