# PS4-AVATAR-MAKER

A Python utility to automatically convert images (local files or URLs) into the `.xavatar` format. This tool handles resizing, and directory structure generation required for custom avatars (typically for Jailbroken PlayStation 4/5).

## ⚠️ Disclaimer

This tool is provided for educational and customization purposes. Please ensure you have the right to use and modify the images you convert. The author is not responsible for any issues arising from the use of generated files on modified hardware.

## 🚀 Features

* **Dual Input Support:** Accepts local image paths or direct web URLs.
* **Automatic Resizing:** Automatically scales images to required dimensions.
* **Dependency Management:** auto-detects missing Python libraries and offers to install them.

## 📋 Prerequisites

Before running the utility, ensure you have the following installed:

### 1. Python
You need Python 3.x installed on your system. [Download](https://www.python.org/downloads/)

### 2. ImageMagick (Important)
This utility uses the **Wand** library, which is a binding for ImageMagick. You must have the ImageMagick binary installed on your operating system for **Wand** to work.

* **Windows:** [Download ImageMagick](https://imagemagick.org/script/download.php#windows).
* **Linux:** `sudo apt-get install libmagickwand-dev`
* **macOS:** `brew install imagemagick`

Check [docs.wand-py.org](https://docs.wand-py.org/en/0.6.12/guide/install.html) for more.

## 📦 Installation

1.  Clone this repository or download as zip .
2.  (Optional) Install the required Python packages **manually**:

```bash
pip install Wand requests
````

> [\!NOTE]
> The utility includes an auto-installer feature that will ask to install these if they are missing.

## 💻 Usage

Open your terminal or command prompt in the utility's directory.

### Basic Usage

Convert a local image. The output filename will default to the input name with the `.xavatar` extension.

```bash
python main.py my_image.jpg
```

### Specify Output Name

You can define a custom name for the output file.

```bash
python main.py my_image.jpg custom_name
```

### From a URL

Directly download and convert an image from the web.

```bash
python main.py https://example.com/cool_avatar.png
```

## 🤖 Telegram Bot Alternative

If you don't have a PC, I am hosting this utility on Telegram. You can use it directly via the link below:

[**@PS4AVATARSBOT**](https://t.me/PS4AVATARSBOT)

## 🌐 Where can I get avatars?

You can find high-quality avatars to convert at the following websites:

  * [PS Prices](https://psprices.com/region-us/collection/avatars)
  * [PSN Tools](https://www.psntools.com/avatars?page=1)

## 🎮 How to Apply the Avatar

Once you have generated your `.xavatar` file, transfer it to your console via FTP or USB. You can apply it using one of the following methods:

### Method 1: PSX-Xplorer

1.  Navigate to the file location using **[PS4-Xplorer 2.0](https://pkg-zone.com/details/LAPY20009)** (or **[PS5-Xplorer](https://pkg-zone.com/details/LAPY20011)**).
2. Simply press the <img src="https://raw.githubusercontent.com/bucanero/pkgi-ps3/master/data/CROSS.png" width="20" height="20" style="vertical-align: middle;"> button on the `.xavatar` file to install it.

### Method 2: Avatar Changer App

1.  Move the `.xavatar` file to the following path on your console: `/data/AVATARS/`
2.  Open **[Avatar Changer](https://pkg-zone.com/details/LAPY20015)** (or **[Avatar Changer PS5](https://pkg-zone.com/details/LAPY20016)**).
3.  Select and apply the image from within the application.

## 🏆 Credits

  * **[LAPY](https://x.com/Lapy05575948):** For creating the `.xavatar` format.
  * **[m2k7m](https://github.com/m2k7m):** For creating this Python utility.

## Contributing

Pull requests are welcome.

## 📄 License

[MIT License](https://github.com/m2k7m/PS4-AVATAR-MAKER/blob/main/LICENSE)