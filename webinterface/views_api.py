from webinterface import webinterface
from flask import render_template, flash, redirect, request, url_for, jsonify
from lib.functions import find_between, theaterChase, theaterChaseRainbow, sound_of_da_police, scanner, breathing, \
    rainbow, rainbowCycle
import psutil
import threading
from neopixel import *
import webcolors as wc


@webinterface.route('/api/start_animation', methods=['GET'])
def start_animation():
    choice = request.args.get('name')
    speed = request.args.get('speed')
    if choice == "theaterchase":
        webinterface.menu.t = threading.Thread(target=theaterChase, args=(webinterface.ledstrip.strip,
                                                                          Color(127, 127, 127),
                                                                          webinterface.ledsettings,
                                                                          webinterface.menu))
        webinterface.menu.t.start()

    if choice == "theaterchaserainbow":
        webinterface.t = threading.Thread(target=theaterChaseRainbow, args=(webinterface.ledstrip.strip,
                                                                            webinterface.ledsettings,
                                                                            webinterface.menu, 5))
        webinterface.t.start()

    if choice == "soundofdapolice":
        webinterface.t = threading.Thread(target=sound_of_da_police, args=(webinterface.ledstrip.strip,
                                                                           webinterface.ledsettings,
                                                                           webinterface.menu, 1))
        webinterface.t.start()

    if choice == "scanner":
        webinterface.t = threading.Thread(target=scanner, args=(webinterface.ledstrip.strip,
                                                                webinterface.ledsettings,
                                                                webinterface.menu, 1))
        webinterface.t.start()

    if choice == "breathing":
        if speed == "fast":
            webinterface.t = threading.Thread(target=breathing, args=(webinterface.ledstrip.strip,
                                                                      webinterface.ledsettings,
                                                                      webinterface.menu, 5))
            webinterface.t.start()
        if speed == "medium":
            webinterface.t = threading.Thread(target=breathing, args=(webinterface.ledstrip.strip,
                                                                      webinterface.ledsettings,
                                                                      webinterface.menu, 10))
            webinterface.t.start()
        if speed == "slow":
            webinterface.t = threading.Thread(target=breathing, args=(webinterface.ledstrip.strip,
                                                                      webinterface.ledsettings,
                                                                      webinterface.menu, 25))
            webinterface.t.start()

    if choice == "rainbow":
        if speed == "fast":
            webinterface.t = threading.Thread(target=rainbow, args=(webinterface.ledstrip.strip,
                                                                    webinterface.ledsettings,
                                                                    webinterface.menu, 2))
            webinterface.t.start()
        if speed == "medium":
            webinterface.t = threading.Thread(target=rainbow, args=(webinterface.ledstrip.strip,
                                                                    webinterface.ledsettings,
                                                                    webinterface.menu, 20))
            webinterface.t.start()
        if speed == "slow":
            webinterface.t = threading.Thread(target=rainbow, args=(webinterface.ledstrip.strip,
                                                                    webinterface.ledsettings,
                                                                    webinterface.menu, 50))
            webinterface.t.start()

    if choice == "rainbowcycle":
        if speed == "fast":
            webinterface.t = threading.Thread(target=rainbowCycle, args=(webinterface.ledstrip.strip,
                                                                         webinterface.ledsettings,
                                                                         webinterface.menu, 1))
            webinterface.t.start()
        if speed == "medium":
            webinterface.t = threading.Thread(target=rainbowCycle, args=(webinterface.ledstrip.strip,
                                                                         webinterface.ledsettings,
                                                                         webinterface.menu, 20))
            webinterface.t.start()
        if speed == "slow":
            webinterface.t = threading.Thread(target=rainbowCycle, args=(webinterface.ledstrip.strip,
                                                                         webinterface.ledsettings,
                                                                         webinterface.menu, 50))
            webinterface.t.start()

    if choice == "stop":
        webinterface.menu.screensaver_is_running = False

    return jsonify(success=True)


@webinterface.route('/api/get_homepage_data')
def get_homepage_data():
    try:
        temp = find_between(str(psutil.sensors_temperatures()["cpu_thermal"]), "current=", ",")
    except:
        temp = find_between(str(psutil.sensors_temperatures()["cpu-thermal"]), "current=", ",")

    temp = round(float(temp), 1)

    upload = psutil.net_io_counters().bytes_sent
    download = psutil.net_io_counters().bytes_recv

    card_space = psutil.disk_usage('/')

    homepage_data = {
        'cpu_usage': psutil.cpu_percent(interval=0.1),
        'memory_usage_percent': psutil.virtual_memory()[2],
        'memory_usage_total': psutil.virtual_memory()[0],
        'memory_usage_used':  psutil.virtual_memory()[3],
        'cpu_temp': temp,
        'upload': upload,
        'download': download,
        'card_space_used': card_space.used,
        'card_space_total': card_space.total,
        'card_space_percent': card_space.percent
    }
    return jsonify(homepage_data)


@webinterface.route('/api/change_setting', methods=['GET'])
def change_setting():
    setting_name = request.args.get('setting_name')
    value = request.args.get('value')

    if setting_name == "led_color":
        rgb = wc.hex_to_rgb("#"+value)

        webinterface.ledsettings.color_mode = "Single"

        webinterface.ledsettings.red = rgb[0]
        webinterface.ledsettings.green = rgb[1]
        webinterface.ledsettings.blue = rgb[2]

        webinterface.usersettings.change_setting_value("color_mode", webinterface.ledsettings.color_mode)
        webinterface.usersettings.change_setting_value("red", rgb[0])
        webinterface.usersettings.change_setting_value("green", rgb[1])
        webinterface.usersettings.change_setting_value("blue", rgb[2])

    if setting_name == "light_mode":
        webinterface.ledsettings.mode = value
        webinterface.usersettings.change_setting_value("mode", value)

    if setting_name == "fading_speed" or setting_name == "velocity_speed":
        webinterface.ledsettings.fadingspeed = int(value)
        webinterface.usersettings.change_setting_value("fadingspeed", webinterface.ledsettings.fadingspeed)

    if setting_name == "brightness":
        webinterface.usersettings.change_setting_value("brightness_percent", int(value))
        webinterface.ledstrip.change_brightness(int(value), True)

    return jsonify(success=True)


@webinterface.route('/api/get_settings', methods=['GET'])
def get_settings():
    response = {}

    red = webinterface.usersettings.get_setting_value("red")
    green = webinterface.usersettings.get_setting_value("green")
    blue = webinterface.usersettings.get_setting_value("blue")
    led_color = wc.rgb_to_hex((int(red), int(green), int(blue)))

    light_mode = webinterface.usersettings.get_setting_value("mode")

    brightness = webinterface.usersettings.get_setting_value("brightness_percent")

    response["led_color"] = led_color
    response["light_mode"] = light_mode
    response["brightness"] = brightness

    return jsonify(response)
