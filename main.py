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

import shutil
import sys
import time
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

try:
    from wand.image import Image as WandImage
except ImportError:
    choice = input(
        "Wand library is not installed. Do you want to install it now? (y/n): "
    )

    if choice.lower() == "y":
        import subprocess

        subprocess.check_call([sys.executable, "-m", "pip", "install", "Wand"])
        from wand.image import Image as WandImage
    else:
        sys.exit("Wand library is required to run this utility.")

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
        choice = input(
            "requests library is not installed. Do you want to install it now? (y/n): "
        )

        if choice.lower() == "y":
            import subprocess

            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
            import requests
        else:
            sys.exit("requests library is required to process images from URLs.")

    response = requests.get(link, stream=True)

    if response.status_code == 200:
        return response.content
    else:
        sys.exit(
            f"Failed to download image from the provided link.\nStatus code: {response.status_code}"
        )


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

    print(f"Converted {image_input} to {output_path} successfully.")
    print(f"Time taken: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    arg_count = len(sys.argv)

    input_str = (
        input("Enter the input image path or URL: ") if arg_count < 2 else sys.argv[1]
    )

    if not input_str:
        sys.exit("No input provided.")

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
