import os
import subprocess
import time
import click
import aria2p
import zipfile
import shutil

rb_src = os.path.abspath(os.path.dirname(__file__))

from dotenv import load_dotenv


def setup_environment():
    env_is_loaded = False
    while True:
        env_is_loaded = load_dotenv(os.path.join(rb_src, ".envrc"))
        env_is_loaded = load_dotenv(os.path.join(rb_src, ".env"))
        if not env_is_loaded:
            raise RuntimeError("Failed to load .env (or .envrc)")
    os.getenv("RB_SRC")
    os.getenv("RB_DATA")


def unzip_and_overwrite(zip_path, extract_to):
    """
    Unzips the specified zip file to the target directory, overwriting existing files.
    """
    if os.path.exists(extract_to):
        shutil.rmtree(extract_to)
    os.makedirs(extract_to, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"Extracted {zip_path} to {extract_to}")


# Function to start aria2c daemon
def start_aria2c_daemon():
    # Check if aria2c is already running
    try:
        subprocess.check_output(['pgrep', 'aria2c'])
        print("aria2c daemon is already running.")
    except subprocess.CalledProcessError:
        # Start aria2c with RPC enabled
        subprocess.Popen(['aria2c', '--enable-rpc', '--rpc-listen-all=false', '--rpc-allow-origin-all'])
        print("Started aria2c daemon with RPC enabled.")
        # Give aria2c some time to start
        time.sleep(2)

        
# Function to download shapefiles for specified states
def download_shapefiles(states):
    # Initialize aria2p API
    aria2 = aria2p.API(
        aria2p.Client(
            host="http://localhost",
            port=6800,
            secret=""
        )
    )

    # ensure download directory exists
    download_dir = os.path.normpath(os.path.join(os.getenv("RB_DATA"), "gis_osm_roads_downloads"))

    # Base URL and referer
    base_url = "https://download.geofabrik.de/north-america/us/{state}-latest-free.shp.zip"
    referer = "https://download.geofabrik.de/north-america/us.html"

    # Iterate over each state and add download
    for state in states:
        url = base_url.format(state=state.lower())
        options = {
            "referer": referer,
            "out": f"{state}-latest-free.shp.zip",
            "dir": download_dir,
            "continue": "true"  # Ensure downloads can be resumed
        }
        try:
            download = aria2.add_uris([url], options=options)
            print(f"Added download for {state}: {url}")
        except Exception as e:
            print(f"Failed to add download for {state}: {e}")

    # Wait for downloads to complete
    while True:
        downloads = aria2.get_downloads()
        active_downloads = [d for d in downloads if d.is_active]
        if not active_downloads:
            print("All downloads completed.")
            break
        for download in active_downloads:
            print(f"Downloading {download.name}: {download.progress_string()} at {download.download_speed_string()}")
        time.sleep(5)

    # Unzip each downloaded file to the specified directory
    rb_data_dir = os.path.normpath(os.getenv("RB_DATA"))
    for state in states:
        zip_filename = f"{state}-latest-free.shp.zip"
        zip_path = os.path.join(download_dir, zip_filename)
        if os.path.exists(zip_path):
            extract_to = os.path.join(rb_data_dir, f"gis_osm_roads_extra/{state}_geom")
            unzip_and_overwrite(zip_path, extract_to)
        else:
            print(f"Zip file for {state} not found at {zip_path}")


# Click command-line interface
@click.command()
@click.argument('states', nargs=-1)
def main(states):
    """
    Download shapefiles for specified STATES using aria2.
    """
    if not states:
        print("Please specify at least one state.")
        return

    # Start aria2c daemon
    start_aria2c_daemon()

    # Download shapefiles
    download_shapefiles(states)

if __name__ == '__main__':
    main()
