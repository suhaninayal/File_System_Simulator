from storage import save_state, load_state
from datetime import datetime

disk_size = 100
disk = ['free'] * disk_size
file_directory = {}

saved_data = load_state()
if saved_data:
    disk = saved_data["disk"]
    file_directory = saved_data["file_directory"]

def get_disk():
    return disk

def get_free_block_count():
    return disk.count('free')

def get_free_blocks():
    return [i for i, b in enumerate(disk) if b == 'free']

def allocate_contiguous(file_name, size):
    for i in range(disk_size - size + 1):
        if all(disk[i + j] == 'free' for j in range(size)):
            for j in range(size):
                disk[i + j] = file_name
            return list(range(i, i + size))
    return []

def allocate_linked(file_name, size):
    free = get_free_blocks()
    if len(free) >= size:
        for b in free[:size]:
            disk[b] = file_name
        return free[:size]
    return []

def allocate_indexed(file_name, size):
    free = get_free_blocks()
    if len(free) >= size + 1:
        index_block = free[0]
        data_blocks = free[1:size + 1]
        disk[index_block] = file_name
        for b in data_blocks:
            disk[b] = file_name
        return index_block, data_blocks
    return None, []

def create_file(file_name, file_size, method, ftype, content, owner='admin'):
    if file_name in file_directory:
        return False

    blocks, index_block = [], None

    if method == 'Contiguous':
        blocks = allocate_contiguous(file_name, file_size)
    elif method == 'Linked':
        blocks = allocate_linked(file_name, file_size)
    elif method == 'Indexed':
        index_block, blocks = allocate_indexed(file_name, file_size)

    if not blocks:
        return False

    file_directory[file_name] = {
        'size': file_size,
        'method': method,
        'blocks': blocks,
        'type': ftype,
        'content': content,
        'index': index_block if method == 'Indexed' else None,
        'created_at': datetime.now(),
        'last_modified': datetime.now(),
        'owner': owner,
        'permissions': {
            'read': [owner],
            'write': [owner],
            'delete': [owner]
        }
    }

    save_state({"disk": disk, "file_directory": file_directory})
    return True

def delete_file(file_name):
    if file_name in file_directory:
        for block in file_directory[file_name]['blocks']:
            disk[block] = 'free'
        if file_directory[file_name]['method'] == 'Indexed':
            index_block = file_directory[file_name].get('index')
            if index_block is not None:
                disk[index_block] = 'free'
        del file_directory[file_name]
        save_state({"disk": disk, "file_directory": file_directory})

def get_all_files():
    return file_directory

def get_file_content(file_name):
    return file_directory[file_name]['content'] if file_name in file_directory else None

def update_file_content(file_name, new_content):
    if file_name in file_directory:
        file_directory[file_name]['content'] = new_content
        file_directory[file_name]['last_modified'] = datetime.now()
        save_state({"disk": disk, "file_directory": file_directory})
        return True
    return False

def check_permission(file_name, action, user):
    file = file_directory.get(file_name)
    if file:
        return user in file['permissions'].get(action, [])
    return False
