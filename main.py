import sys
import os
import shutil
import zipfile
import time
from io import BytesIO

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
        print("Wand library is required to run this script. Exiting.")
        sys.exit(1)

sizes = [440, 260, 128, 64]


def cleanDir(path):

    if os.path.exists(path):
        shutil.rmtree(path)


def add_files_to_zip_in_memory(file_paths: list[str]) -> bytes:
    in_memory_zip = BytesIO()

    with zipfile.ZipFile(in_memory_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in file_paths:
            arcname = os.path.basename(file_path)
            zf.write(file_path, arcname)

    in_memory_zip.seek(0)
    return in_memory_zip.read()


def create_online_json(dir):
    online_json_content = r"""{"avatarUrl":"http:\/\/static-resource.np.community.playstation.net\/avatar_xl\/WWS_E\/E0012_XL.png","firstName":"","lastName":"","pictureUrl":"https:\/\/image.api.np.km.playstation.net\/images\/?format=png&w=440&h=440&image=https%3A%2F%2Fkfscdn.api.np.km.playstation.net%2F00000000000008%2F000000000000003.png&sign=blablabla019501","trophySummary":"{\"level\":1,\"progress\":0,\"earnedTrophies\":{\"platinum\":0,\"gold\":0,\"silver\":0,\"bronze\":0}}","isOfficiallyVerified":"true"}"""
    with open(f"{dir}/online.json", "w") as f:
        f.write(online_json_content)


def copy_files(dir):

    create_online_json(dir)
    shutil.copy(f"{dir}/avatar.png", f"{dir}/picture.png")

    for size in sizes:
        outputdirection = f"{dir}/picture{size}.dds"
        inputdirection = f"{dir}/avatar{size}.dds"
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
            print("requests library is required to run this script. Exiting.")
            sys.exit(1)

    response = requests.get(link, stream=True)

    if response.status_code == 200:
        return response.content
    else:
        sys.exit(
            f"Failed to download image from the provided link.\nStatus code: {response.status_code}"
        )


def process_image(img, temp_dir):
    img.format = "png"
    img.resize(440, 440)

    img.save(filename=os.path.join(temp_dir, "avatar.png"))

    img.compression = "dxt5"

    for size in sizes:
        if img.width != size:
            img.resize(size, size)

        output_filename = os.path.join(temp_dir, f"avatar{size}.dds")
        img.save(filename=output_filename)


def convert_image(image_path: str, output_path: str, activated: bool = False):

    temp_dir = "temp"

    try:
        os.makedirs(temp_dir)
    except FileExistsError:
        sys.exit("Temporary directory already exists. Please remove it and try again.")

    start_time = time.time()

    if image_path.startswith("http://") or image_path.startswith("https://"):
        output_path = output_path.replace("://", "_").replace("/", "_")
        image_bytes = process_link(image_path)
        with WandImage(blob=image_bytes) as img:
            process_image(img, temp_dir)
    else:
        with WandImage(filename=image_path) as img:
            process_image(img, temp_dir)

    if activated:
        copy_files(temp_dir)

    file_paths = [os.path.join(temp_dir, filename) for filename in os.listdir(temp_dir)]

    archive_bytes = add_files_to_zip_in_memory(file_paths)

    with open(output_path, "wb") as f:
        f.write(archive_bytes)

    end_time = time.time()

    shutil.rmtree(temp_dir)

    print(f"Converted {image_path} to {output_path} successfully.")
    print(f"Time taken: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":

    arg_count = len(sys.argv)

    if arg_count == 2:
        input_file = sys.argv[1]
        output_file = input_file.rsplit(".", 1)[0] + ".xavatar"
    elif arg_count == 3:
        input_file = sys.argv[1]
        output_file = (
            sys.argv[2]
            if sys.argv[2].endswith(".xavatar")
            else sys.argv[2] + ".xavatar"
        )
    else:
        print("Usage: python main.py <input_image> [output_image]")
        sys.exit(1)

    choice = input("Is your account offile activated? (y/n): ")
    if choice.lower() == "y":
        convert_image(input_file, output_file, activated=True)
    else:
        convert_image(input_file, output_file)
