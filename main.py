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
import shutil
import sys
import time
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

try:
    import i18n
except ImportError:
    c = input("python-i18n library is not installed. Do you want to install it now? (y/n): ")
    if c.lower() == "y":
        import subprocess

        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-i18n"])
        import i18n
    else:
        sys.exit("python-i18n is required to run this utility.")

config_path = Path("config.json")
locales_dir = Path("locales")

if not locales_dir.exists():
    locales_dir.mkdir()
    en_data = {
        "wand_install": "Wand library is not installed. Do you want to install it now? (y/n): ",
        "wand_req": "Wand library is required to run this utility.",
        "req_install": "requests library is not installed. Do you want to install it now? (y/n): ",
        "req_req": "requests library is required to process images from URLs.",
        "dl_fail": "Failed to download image from the provided link.\nStatus code: %{status}",
        "success": "Converted %{input} to %{output} successfully.",
        "time": "Time taken: %{time} seconds",
        "input_path": "Enter the input image path or URL: ",
        "no_input": "No input provided."
    }
    ar_data = {
        "wand_install": "مكتبة Wand غير مثبتة. هل تريد تثبيتها الآن؟ (y/n): ",
        "wand_req": "مكتبة Wand مطلوبة لتشغيل هذه الأداة.",
        "req_install": "مكتبة requests غير مثبتة. هل تريد تثبيتها الآن؟ (y/n): ",
        "req_req": "مكتبة requests مطلوبة لمعالجة الصور من الروابط.",
        "dl_fail": "فشل تنزيل الصورة من الرابط.\nكود الحالة: %{status}",
        "success": "تم تحويل %{input} إلى %{output} بنجاح.",
        "time": "الوقت المستغرق: %{time} ثانية",
        "input_path": "أدخل مسار الصورة أو الرابط: ",
        "no_input": "لم يتم إدخال مسار أو رابط."
    }
    (locales_dir / "app.en.json").write_text(json.dumps(en_data, ensure_ascii=False), encoding="utf-8")
    (locales_dir / "app.ar.json").write_text(json.dumps(ar_data, ensure_ascii=False), encoding="utf-8")

i18n.load_path.append(str(locales_dir))

def load_lang():
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f).get("lang", "en")
    return None

def save_lang(lang):
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump({"lang": lang}, f)

current_lang = load_lang()

if current_lang is None:
    c = input("Choose language / اختر اللغة (1: English, 2: العربية): ")
    current_lang = "ar" if c == "2" else "en"
    save_lang(current_lang)
else:
    c = input("Press Enter to continue or 'L' to change language / اضغط انتر للاستمرار او L لتغيير اللغة: ")
    if c.lower() == 'l':
        c2 = input("Choose language / اختر اللغة (1: English, 2: العربية): ")
        current_lang = "ar" if c2 == "2" else "en"
        save_lang(current_lang)

i18n.set('locale', current_lang)
i18n.set('fallback', 'en')

try:
    from wand.image import Image as WandImage
except ImportError:
    choice = input(i18n.t('app.wand_install'))

    if choice.lower() == "y":
        import subprocess

        subprocess.check_call([sys.executable, "-m", "pip", "install", "Wand"])
        from wand.image import Image as WandImage
    else:
        sys.exit(i18n.t('app.wand_req'))

sizes = [440, 260, 128, 64]


def add_files_to_zip_in_memory(file_paths: list[Path]) -> bytes:
    in_memory_zip = BytesIO()

    with ZipFile(in_memory_zip, "w", ZIP_DEFLATED) as zf:
        for file_path in file_paths:
            zf.write(file_path, file_path.name)

    in_memory_zip.seek(0)
    return in_memory_zip.read()


def create_online_json(directory: Path) -> None:
    online_json_content = r"""{"avatarUrl":"http:\/\/static-resource.np.community.playstation.net\/avatar_xl\/WWS_E\/E0012_XL.png","firstName":"","lastName":"","pictureUrl":"https:\/\/image.api.np.km.playstation.net\/images\/?format=png&w=440&h=440&image=https%3A%2F%2Fkfscdn.api.np.km.playstation.net%2F00000000000008%2F000000000000003.png&sign=blablabla019501","trophySummary":"{\"level\":1,\"progress\":0,\"earnedTrophies\":{\"platinum\":0,\"gold\":0,\"silver\":0,\"bronze\":0}}","isOfficiallyVerified":"true"}"""

    (directory / "online.json").write_text(online_json_content, encoding="utf-8")


def copy_files(directory: Path) -> None:
    create_online_json(directory)
    shutil.copy(directory / "avatar.png", directory / "picture.png")

    for size in sizes:
        outputdirection = directory / f"picture{size}.dds"
        inputdirection = directory / f"avatar{size}.dds"
        shutil.copy(inputdirection, outputdirection)


def process_link(link: str) -> bytes:
    try:
        import requests
    except ImportError:
        choice = input(i18n.t('app.req_install'))

        if choice.lower() == "y":
            import subprocess

            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
            import requests
        else:
            sys.exit(i18n.t('app.req_req'))

    response = requests.get(link, stream=True)

    if response.status_code == 200:
        return response.content
    else:
        sys.exit(i18n.t('app.dl_fail', status=response.status_code))


def process_image(img: WandImage, temp_dir: Path) -> None:
    img.format = "png"
    img.resize(440, 440)

    img.save(filename=str(temp_dir / "avatar.png"))

    img.compression = "dxt5"

    for size in sizes:
        if img.width != size:
            img.resize(size, size)

        output_filename = temp_dir / f"avatar{size}.dds"
        img.save(filename=str(output_filename))


def convert_image(image_input: str, output_path_str: str) -> None:
    output_path = Path(output_path_str)

    with TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)

        if image_input.startswith(("http://", "https://")):
            image_bytes = process_link(image_input)
            start_time = time.time()
            with WandImage(blob=image_bytes) as img:
                process_image(img, temp_dir)
        else:
            start_time = time.time()
            with WandImage(filename=image_input) as img:
                process_image(img, temp_dir)

        copy_files(temp_dir)

        file_paths = [p for p in temp_dir.iterdir()]

        archive_bytes = add_files_to_zip_in_memory(file_paths)

    output_path.write_bytes(archive_bytes)

    end_time = time.time()

    print(i18n.t('app.success', input=image_input, output=output_path))
    print(i18n.t('app.time', time=f"{end_time - start_time:.2f}"))


if __name__ == "__main__":
    arg_count = len(sys.argv)

    input_str = (
        input(i18n.t('app.input_path')) if arg_count < 2 else sys.argv[1]
    )

    if not input_str:
        sys.exit(i18n.t('app.no_input'))

    if arg_count != 3:
        if input_str.startswith(("http://", "https://")):
            output_file_path = Path(
                input_str.replace("://", "_").replace("/", "_")
            ).with_suffix(".xavatar")
        else:
            output_file_path = Path(input_str).with_suffix(".xavatar")
    else:
        output_file_path = Path(sys.argv[2])
        if output_file_path.suffix != ".xavatar":
            output_file_path = output_file_path.with_suffix(".xavatar")

    convert_image(input_str, str(output_file_path))
