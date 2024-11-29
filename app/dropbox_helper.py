import dropbox
import dropbox.files
import os

with open('dropbox_token.txt', 'r') as f:
    dropbox_token = f.read()

dbx = dropbox.Dropbox(dropbox_token)

async def upload_files_to_drop_box(file_name: str):
    with open(file_name, 'rb') as f:
        data = f.read()
        dbx.files_upload(data, f"/{file_name}")

async def upload_data_to_drop_box(data: str, file_name: str):
    """This function takes in any format of data and uploads it to dropbox with title as the filename

    Args:
        data (str): data
        file_name (str): name of the file in dropbox
    """
    dbx.files_upload(data, f"/{file_name}")