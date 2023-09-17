import os
import urllib.request

# TODO use shutil to copy files

arch = "x86_64-linux-gnu"

answers = {}

answers["modular"] = input("Do you already have modular installed? (y/n) ").lower() == "y"
answers["global"] = input("Do you want to install the libraries globally (for all users)? (y/n) ").lower() == "y"
answers["venv"] = input(
    "Do you want to automatically use a venv when running modular install/update? (y/n) ").lower() == "y"
if answers["venv"]:
    answers["path"] = input("Where do you want to create the venv and temporary files. (the venv is needed for "
                            "installation anyways) ")
answers["token"] = input("Please enter your Modular auth token. You can also type 'manual' to run "
                         "modular manually when requested ")

if answers["venv"]:
    if answers["path"].split("/")[1] == "tmp":
        print("You can't use a tmp dir when you want to automatically use a venv. Please choose a different path")
        exit(1)

WORKING_DIR = answers["path"]

if WORKING_DIR == "":
    WORKING_DIR = "/tmp/arch-mojo/"
elif WORKING_DIR[-1] != "/":
    WORKING_DIR += "/"

# install modular if not installed
if answers["modular"]:
    # download PKGBUILD
    urllib.request.urlretrieve("https://raw.githubusercontent.com/Sharktheone/arch-mojo/main/PKGBUILD",
                               f"{WORKING_DIR}PKGBUILD")
    os.system(f"cd {WORKING_DIR} && makepkg -si")

# authenticate in modular
if answers["token"] != "manual":
    os.system(f"modular auth {answers['token']}")
else:
    print("Please run 'modular auth <token>' to authenticate yourself")
    input("Press enter to continue")

# download ncurses lib

urllib.request.urlretrieve("http://ftp.debian.org/debian/pool/main/n/ncurses/libncurses6_6.4-4_amd64.deb",
                           f"{WORKING_DIR}libncurses.deb")

os.system(f"cd {WORKING_DIR} && ar -vx libncurses.deb && tar -xf data.tar.xz")

# copy libs
if answers["global"]:
    os.system(f"sudo cp {WORKING_DIR}lib/{arch}/* /lib/")
    os.system(f"sudo cp {WORKING_DIR}usr/lib/{arch}/* /usr/lib/")
    os.system(f"sudo cp {WORKING_DIR}lib/{arch}/* /usr/lib/")


else:
    mojo_lib_path = "/home/$USER/.local/lib/mojo"

    os.system(f"mkdir -p {mojo_lib_path}")

    os.system(f"cp {WORKING_DIR}lib/{arch}/libncurses.so.6.4 {mojo_lib_path}/libncurses.so.6")
    os.system(f"cp {WORKING_DIR}lib/{arch}/libform.so.6.4 {mojo_lib_path}/libform.so.6")
    os.system(f"cp {WORKING_DIR}lib/{arch}/libpanel.so.6.4 {mojo_lib_path}/libncurses.so.6.4")

# install mojo

os.system(f"python3 -m venv {WORKING_DIR}venv")
os.system(f"source {WORKING_DIR}venv/bin/activate")
os.system("modular install mojo")

rc_path = ""

match os.environ["SHELL"].split("/")[-1]:
    case "bash":
        rc_path.join("~/.bashrc")
    case "zsh":
        rc_path.join("~/.zshrc")
    case _:
        path = input("Please enter the path to your shell rc file (e.g. ~/.bashrc for bash) ")
        rc_path.join(path)

rc_file = open(rc_path, "a")

if answers["venv"]:
    os.system(f"python3 -m venv {WORKING_DIR}venv")
    urllib.request.urlretrieve("https://raw.githubusercontent.com/Sharktheone/arch-mojo/main/shell.sh",
                               f"{WORKING_DIR}shell.sh")
    shell_file = open(f"{WORKING_DIR}shell.sh", "a")
    shell = shell_file.read()

    shell.replace("{{venv-path}}", f"{WORKING_DIR}venv")

    rc_file.write(shell)

exports = \
    """
export PATH=$PATH:~/.modular/pkg/packages.modular.com_mojo/bin/
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/.local/lib/mojo
"""

rc_file.write(exports)

rc_file.close()

# delete temp files
# maybe here a check would make sense if the WORKING_DIR is already existing

if WORKING_DIR.split("/")[1] == "tmp":
    exit(0)

created_files = [
    "PKGBUILD",
    "libncurses.deb",
    "data.tar.xz",
    "control.tar.xz",
    "shell.sh",
    "venv",
    f"lib/{arch}/*",
    f"usr/lib/{arch}/*",
    "usr/share/doc/*",
]

if answers["venv"]:
    created_files.append("venv")

for file in created_files:
    os.system(f"rm {WORKING_DIR}{file}")
