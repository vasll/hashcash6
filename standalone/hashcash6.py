import os
import json
import multiprocessing as mp
from hashlib import sha3_384
from time import sleep
from typer import Option, Typer, Argument, Exit as cliExit
from typing import Optional
from hc6_utils import hex_to_bin, has_leading_zeros, clean_filename, rand_base64
from datetime import datetime
from math import floor
from rich import print as richprint


class Hashcash6:
    """ An hashcash implementation that that uses SHA3 384bit. I called it Hashcash6 because it sounds cool """
    def __init__(self, resource: str, zero_bits: int = 20, len_rand: int = 16, len_counter: int = 4):
        """
        :param resource: Email or IP of the sender
        :param zero_bits: How many zeros we want at the start of the hash (binary)
        :param len_rand: Length of the random base64 string that is generated once
        :param len_counter: Length of the random base64 counter
        """
        self.version = 6
        self.resource = resource
        self.zero_bits = zero_bits
        self.len_rand = len_rand
        self.len_counter = len_counter

    def generate(self) -> dict:
        """
        :return: Dict containing the hashcash header and its SHA3 384bit hash. The dict has a 'header' and a 'hash' key
        """
        date_now = datetime.now().strftime("%Y%m%d%H%M%S.%f")  # Timestamp of calculation start
        rand = rand_base64(self.len_rand)  # Random string in base-64
        while True:
            counter = rand_base64(self.len_counter)  # In each iteration the counter is a random base64 string
            hashcash = f'{self.version}:{self.zero_bits}:{date_now}:{self.resource}:{rand}:{counter}'
            hashcash_hash_hex = sha3_384(hashcash.encode()).digest().hex()
            hashcash_hash_bin = hex_to_bin(hashcash_hash_hex)

            # If the binary string has X leading zeros we return the hashcash string and the hash
            if has_leading_zeros(hashcash_hash_bin, self.zero_bits):
                return {'header': hashcash, 'hash': hashcash_hash_hex}

    def _update_dict(self, name, shared_dict):
        """ Looks for the right hash and when it's found it's assigned to the shared dict """
        shared_dict[name] = self.generate()

    def generate_multicore(self, process_count: int = floor(mp.cpu_count() / 2)) -> dict:
        """
        Uses multiple processes for calculating Hashcash6, because why not
        :param process_count: Count of processes that will be created. Default is half of the CPU cores
        :return: a dict containing the plaintext string of the hashcash and its hash value
        """
        shared_dict = mp.Manager().dict()
        processes = []

        for i in range(process_count):
            # Using Process instead of Thread because of global interpreter lock, CPython is weird
            process = mp.Process(
                target=self._update_dict,
                args=(f'process_{i}', shared_dict)
            )
            processes.append(process)
            process.start()

        while True:
            if bool(shared_dict):  # If dict is not empty it means that we have a return value from one of the processes
                for process in processes:  # Terminate all processes
                    process.terminate()
                return shared_dict.values()[0]
            sleep(0.10)  # Check every 0.10 seconds if one of the processes has found the hash


# CLI LOGIC STARTS HERE ¦ CLI LOGIC STARTS HERE ¦ CLI LOGIC STARTS HERE
cli = Typer(
    add_completion=False,
    rich_markup_mode="rich",
    pretty_exceptions_short=True,
)

# ASCII art because yes
ascart = r"""[purple]    __  __                    __                             __[/purple]     [yellow]_____
[purple]   / / / /  ____ _   _____   / /_   _____  ____ _   _____   / /_[/purple]   [yellow]/ ___/
[purple]  / /_/ /  / __ `/  / ___/  / __ \ / ___/ / __ `/  / ___/  / __ \ [/purple][yellow]/ __ \
[purple] / __  /  / /_/ /  (__  )  / / / // /__  / /_/ /  (__  )  / / / /[/purple][yellow]/ /_/ /
[purple]/_/ /_/   \__,_/  /____/  /_/ /_/ \___/  \__,_/  /____/  /_/ /_/[/purple] [yellow]\____/ [white]v1.0[/white]"""


# Callback for the --about Option
def about_callback(value: bool):
    if value:
        richprint(ascart, end="\n\n")
        richprint("An hashcash implementation that uses SHA3 384bit")
        richprint("Made by [cyan]vasll")
        richprint("Github: [cyan]https://github.com/vasll")
        richprint("Version: 1.0 standalone")
        raise cliExit()


# The main command
@cli.command(help="For more information on hashcash and the various fields visit: "
                  "https://en.wikipedia.org/wiki/Hashcash")
def generate(
        resource: str = Argument(..., help="Email or IP of the sender", show_default=False),
        zero_bits: Optional[int] = Option(20, help="How many 0 bits we want at the start of the Hashcash6 header hash"),
        len_rand: Optional[int] = Option(16, help="Length in chars of the 'rand' field"),
        len_counter: Optional[int] = Option(4, help="Length in chars of the 'counter' field"),
        threads: Optional[int] = Option(default=1, help="Number of threads to be used for hash generation", min=1),
        to_txt: Optional[bool] = Option(None, "--to-txt", help="Save the output to a .txt file"),
        to_json: Optional[bool] = Option(None, "--to-json", help="Save the output to a .json file"),
        about: Optional[bool] = Option(None, "--about", callback=about_callback, help="About Hashcash6")):
    if len(resource) > 254:  # If resource is longer than 254 chars, truncate it
        print("[italic]Resource is longer than 254 chars and will be truncated[/italic]")
        resource = resource[0:254]

    hashcash6 = Hashcash6(resource, zero_bits, len_rand, len_counter)
    values: dict

    calc_start_time = datetime.now()

    if threads > 1:
        richprint(f'\nGenerating Hashcash6 for resource "{resource}" with [dark_green]{zero_bits}[/dark_green] zero '
                  f'bits using {threads} threads...', end='')
        values = hashcash6.generate_multicore(threads)
    else:
        richprint(
            f'\nGenerating Hashcash6 for resource "{resource}" with [dark_green]{zero_bits}[/dark_green] zero bits '
            f'using 1 thread...', end='')
        values = hashcash6.generate()

    calc_end_time = datetime.now() - calc_start_time

    richprint(" [green]Done![/green]")

    binary_hash = hex_to_bin(values['hash'])

    print(f"\n====================== Hashcash header =======================\nX-Hashcash: {values['header']}\n")
    print(f"====================== Hexadecimal hash ======================\n{values['hash']}\n")
    print(f"======================== Binary hash =========================")

    richprint(f'[bold]{binary_hash[0:zero_bits]}[/bold]', end='')
    print(binary_hash[zero_bits:])

    if to_txt:
        filename = clean_filename(f"{values['header'].split(':')[2]}_{resource}.txt")
        filepath = f"output/{filename}"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as FILE:
            FILE.write(
                f"Hashcash6 header : \"X-Hashcash: {values['header']}\" \n"
                f"Header hash (hex): \"{values['hash']}\"\n"
                f"Header hash (bin): \"{binary_hash}\"\n")
        richprint(f"\nFile written to [italic]{filepath}[/italic]")

    if to_json:
        filepath = "output/" + clean_filename(f"{values['header'].split(':')[2]}_{resource}.json")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as FILE:
            data = {'header': values['header'], 'hash': values['hash']}
            FILE.write(json.dumps(data, indent=4))
        print(f"\nFile written to {filepath}")

    if not to_txt and not to_json:
        print()  # Print a newline for formatting

    richprint(f"Completed in [green]{calc_end_time}[/green]")


if __name__ == "__main__":
    cli()  # Start the typer CLI
