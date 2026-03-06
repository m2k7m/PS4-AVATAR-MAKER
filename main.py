
#  Copyright (C) 2025-2026 m2k7m
#
#  The MIT License (MIT)
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import json
import os
import shutil
import sys
import time
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile

if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stdin.reconfigure(encoding='utf-8')

try:
    import i18n
    import arabic_reshaper
    from bidi.algorithm import get_display
except ImportError:
    user_choice = input("Missing essential libraries (i18n, arabic-reshaper, python-bidi). Install them now? (y/n): ").strip().lower()
    if user_choice == "y":
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "python-i18n", "arabic-reshaper", "python-bidi"])
            import i18n
            import arabic_reshaper
            from bidi.algorithm import get_display
        except Exception as e:
            sys.exit(f"Failed to install libraries. Please install manually: pip install python-i18n arabic-reshaper python-bidi. Error: {e}")
    else:
        sys.exit("Required libraries are missing.")

CONFIG_FILE_NAME = "config.json"
LOCALES_FOLDER = "locales"
AVATAR_IMAGE_SIZES = [440, 260, 128, 64]

if not os.path.exists(LOCALES_FOLDER):
    os.makedirs(LOCALES_FOLDER)

en_messages = {
    "prompt": "Press Space to continue or 'L' to change language: ",
    "choose": "Choose language (1: English, 2: Arabic): ",
    "wand_ask": "Wand library is missing. Install it now? (y/n): ",
    "wand_err": "Wand library is required.",
    "req_ask": "requests library is missing. Install it now? (y/n): ",
    "req_err": "requests library is required for URLs.",
    "fail_dl": "Download failed. Status: %{status}",
    "success": "Converted %{input} to %{output} successfully.",
    "timer": "Time taken: %{time} seconds",
    "enter_p": "Enter image path or URL: ",
    "no_in": "No input provided."
}

ar_messages = {
    "prompt": "اضغط مسطرة للاستمرار أو مفتاح L لتغيير اللغة: ",
    "choose": "اختر اللغة (1 للانجليزية، 2 للعربية): ",
    "wand_ask": "مكتبة Wand غير موجودة. هل تريد تثبيتها؟ (y/n): ",
    "wand_err": "المكتبة مطلوبة لتشغيل الأداة.",
    "req_ask": "مكتبة requests غير موجودة. هل تريد تثبيتها؟ (y/n): ",
    "req_err": "المكتبة مطلوبة لمعالجة الروابط.",
    "fail_dl": "فشل تنزيل الصورة. كود الحالة: %{status}",
    "success": "تم تحويل %{input} إلى %{output} بنجاح.",
    "timer": "الوقت المستغرق: %{time} ثانية",
    "enter_p": "أدخل مسار الصورة أو الرابط: ",
    "no_in": "لم يتم إدخال شيء."
}

with open(os.path.join(LOCALES_FOLDER, "app.en.json"), "w", encoding="utf-8") as f:
    json.dump({"en": en_messages}, f, ensure_ascii=False, indent=4)
with open(os.path.join(LOCALES_FOLDER, "app.ar.json"), "w", encoding="utf-8") as f:
    json.dump({"ar": ar_messages}, f, ensure_ascii=False, indent=4)

i18n.load_path.append(LOCALES_FOLDER)
i18n.set('file_format', 'json')
i18n.set('filename_format', '{namespace}.{locale}.{format}')

def get_localized_text(key, **kwargs):
    text = i18n.t(f"app.{key}", **kwargs)
    if i18n.get('locale') == 'ar':
        return get_display(arabic_reshaper.reshape(text))
    return text

current_language_setting = "en"
if os.path.exists(CONFIG_FILE_NAME):
    try:
        with open(CONFIG_FILE_NAME, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            current_language_setting = config_data.get("lang", "en")
    except (json.JSONDecodeError, Exception):
        pass

with open(CONFIG_FILE_NAME, "w", encoding="utf-8") as f:
    json.dump({"lang": current_language_setting}, f, indent=4, ensure_ascii=False)

i18n.set('locale', current_language_setting)
i18n.set('fallback', 'en')

print(get_localized_text('prompt'), end='', flush=True)

if os.name == 'nt':
    import msvcrt
    while True:
        key_pressed = msvcrt.getwch().lower()
        if key_pressed == ' ':
            print()
            break
        elif key_pressed == 'l':
            print()
            lang_choice = input(get_localized_text('choose')).strip()
            current_language_setting = "en" if lang_choice == "1" else "ar"
            with open(CONFIG_FILE_NAME, "w", encoding="utf-8") as f:
                json.dump({"lang": current_language_setting}, f, indent=4, ensure_ascii=False)
            i18n.set('locale', current_language_setting)
            break
else:
    user_response = input()
    if user_response.lower() == 'l':
        lang_choice = input(get_localized_text('choose')).strip()
        current_language_setting = "en" if lang_choice == "1" else "ar"
        with open(CONFIG_FILE_NAME, "w", encoding="utf-8") as f:
            json.dump({"lang": current_language_setting}, f, indent=4, ensure_ascii=False)
        i18n.set('locale', current_language_setting)

try:
    from wand.image import Image as WandImage
except ImportError:
    user_answer = input(get_localized_text('wand_ask')).strip().lower()
    if user_answer == "y":
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "Wand"])
            from wand.image import Image as WandImage
        except Exception as e:
            sys.exit(f"Failed to install Wand library. Please install manually: pip install Wand. Error: {e}")
    else:
        sys.exit(get_localized_text('wand_err'))

def create_avatar_zip(files_to_add, output_zip_path):
    with ZipFile(output_zip_path, "w", ZIP_DEFLATED) as zf:
        for f_path in files_to_add:
            zf.write(f_path, os.path.basename(f_path))

def download_image_from_web(image_url):
    try:
        import requests
    except ImportError:
        user_answer = input(get_localized_text('req_ask')).strip().lower()
        if user_answer == "y":
            import subprocess
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
                import requests
            except Exception as e:
                sys.exit(f"Failed to install requests library. Please install manually: pip install requests. Error: {e}")
        else:
            sys.exit(get_localized_text('req_err'))

    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        sys.exit(get_localized_text('fail_dl', status=e))

def process_and_save_image(image_object, temp_output_folder):
    image_object.format = "png"
    image_object.resize(440, 440)
    image_object.save(filename=os.path.join(temp_output_folder, "avatar.png"))

    image_object.compression = "dxt5"
    for size in AVATAR_IMAGE_SIZES:
        if image_object.width != size:
            image_object.resize(size, size)
        image_object.save(filename=os.path.join(temp_output_folder, f"avatar{size}.dds"))

def make_ps4_avatar_file(input_source, final_output_file):
    temp_working_dir = tempfile.mkdtemp()
    start_time = time.time()

    try:
        if input_source.startswith(("http://", "https://")):
            image_bytes = download_image_from_web(input_source)
            with WandImage(blob=image_bytes) as img:
                process_and_save_image(img, temp_working_dir)
        else:
            with WandImage(filename=input_source) as img:
                process_and_save_image(img, temp_working_dir)

        json_data_content = '''{
    "avatarUrl":"http:\/\/static-resource.np.community.playstation.net\/avatar_xl\/WWS_E\/E0012_XL.png",
    "firstName":"",
    "lastName":"",
    "pictureUrl":"https:\/\/image.api.np.km.playstation.net\/images\/?format=png&w=440&h=440&image=https%3A%2F%2Fkfscdn.api.np.km.playstation.net%2F00000000000008%2F000000000000003.png&sign=blablabla019501",
    "trophySummary":"{\"level\":1,\"progress\":0,\"earnedTrophies\":{\"platinum\":0,\"gold\":0,\"silver\":0,\"bronze\":0}}",
    "isOfficiallyVerified":"true"
}'''
        with open(os.path.join(temp_working_dir, "online.json"), "w", encoding="utf-8") as f:
            f.write(json_data_content)

        shutil.copy(os.path.join(temp_working_dir, "avatar.png"), os.path.join(temp_working_dir, "picture.png"))
        for size in AVATAR_IMAGE_SIZES:
            shutil.copy(os.path.join(temp_working_dir, f"avatar{size}.dds"), os.path.join(temp_working_dir, f"picture{size}.dds"))

        all_temp_files = [os.path.join(temp_working_dir, f) for f in os.listdir(temp_working_dir)]
        
        create_avatar_zip(all_temp_files, final_output_file)

    finally:
        shutil.rmtree(temp_working_dir)

    end_time = time.time()

    print(get_localized_text('success', input=input_source, output=final_output_file))
    print(get_localized_text('timer', time=f"{end_time - start_time:.2f}"))

if __name__ == "__main__":
    cmd_args = sys.argv
    user_input_path = input(get_localized_text('enter_p')).strip() if len(cmd_args) < 2 else cmd_args[1]

    if not user_input_path:
        sys.exit(get_localized_text('no_in'))

    output_file_name = None
    if len(cmd_args) < 3:
        if user_input_path.startswith(("http://", "https://")):
            safe_name = user_input_path.replace("://", "_").replace("/", "_").replace(".", "_")
            output_file_name = safe_name + ".xavatar"
        else:
            base_name, _ = os.path.splitext(user_input_path)
            output_file_name = base_name + ".xavatar"
    else:
        output_file_name = cmd_args[2]
        if not output_file_name.endswith(".xavatar"):
            output_file_name += ".xavatar"

    make_ps4_avatar_file(user_input_path, output_file_name)
    
