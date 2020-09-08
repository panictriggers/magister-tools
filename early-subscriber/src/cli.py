from colorama import Fore
import sys

def print_info(msg):
    sys.stdout.write(f"[{Fore.CYAN}i{Fore.RESET}] {msg}")
    sys.stdout.flush()
def print_error(msg):
    sys.stdout.write(f"{Fore.RED}[E] {msg} {Fore.RESET}")
    sys.stdout.flush()
def print_warning(msg):
    sys.stdout.write(f"[{Fore.MAGENTA}!{Fore.RESET}] {msg}")
    sys.stdout.flush()
def print_success(msg):
    sys.stdout.write(f"[{Fore.GREEN}+{Fore.RESET}] {msg}")
    sys.stdout.flush()
def add_to_print(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()