
import os, glob, argparse, hashlib, time, sys

def hash_file(filename):
    """
        This function returns the SHA-1 hash
        of the file passed into it
        
        Source: https://www.programiz.com/python-programming/examples/hash-file

        Parameters:
        -----------
        filename - str - Relative path to file

        Returns:
        --------
        hexdigest - str - Hexadecimal digest of supplied file
    """
    # make a hash object
    h = hashlib.sha1()

    # open file for reading in binary mode
    with open(filename,'rb') as file:

        # loop till the end of the file
        chunk = 0
        while chunk != b'':
            # read only 1024 bytes at a time
            chunk = file.read(1024)
            h.update(chunk)

    # return the hex representation of digest
    return h.hexdigest()

def get_all_files(base_path, filetypes=['jpeg', 'JPG', 'jpg', 'gif', 'GIF', 'png', 'PNG', 'mov', 'MOV', 'mp4']):
    """
        Gets all images with the supplied filetypes, note that filetype checking is based on the file extension

        Parameters:
        -----------
        base_path - str - Absolute or relative path to the directory containing potential duplicates

        filetypes - list - File types to search for in the provided directory

        Returns:
        --------
        all_images - list - All files with the supplied filetypes
    """
    all_images = []
    for ftype in filetypes:
        all_images += glob.glob(os.path.join(base_path, f'*.{ftype}'))
    return all_images

def get_originals(all_images, indicator=' '):
    """
        Extracts the original files from all files based off of filename indicator

        Parameters:
        -----------
        all_images - list - All files from the originally supplied directory with file extensions supplied in get_all_files

        indicator - str - How to determine if the file is a duplicate, based off the automatic renaming scheme for duplicate filenames

        Returns:
        --------
        originals - list - Filepaths to all original files as determined by the indicator supplied
    """
    return [p for p in all_images if not indicator in p.split(os.path.sep)[-1]]

def get_dupes(base_path, originals, indicator=' ', verify_hashes=False):
    """
        Gets lists of duplicate files if an original exists for that file. Files without an original as determined by the indicator in get_originals are ignored.

        Parameters:
        -----------
        base_path - str - Absolute or relative path to directory containing potential duplicates

        originals - list - Original files as determined by the indicator in get_originals

        indicator - str - How to determine if the file is a duplicate, based off the automatic renaming scheme for duplicate filenames

        verify_hashes - bool - If duplicate files should be hashed to verify duplicity

        Returns:
        --------
        dupes - list - List of lists of duplicate files
    """
    dupes = []

    for pic_path in originals:
        # Get the name of the original image
        pic_name = pic_path.split(os.path.sep)[-1].split('.')[0]
        # Get the filetype of the image
        filetype = pic_path[pic_path.rfind('.')+1:]
        # Get the dupes
        cur_dupes = [p for p in glob.glob(os.path.join(base_path, f"{pic_name}*")) if indicator in p.split(os.path.sep)[-1] and p.endswith(filetype)]
        # Verify duplicate files have the same hash as the original, otherwise ignore
        if verify_hashes:
            original_hash = hash_file(pic_path)
            cur_dupes = [dupe for dupe in cur_dupes if hash_file(dupe) == original_hash]
        # Append duplicates if there exist any
        if len(cur_dupes):
            dupes.append(cur_dupes)
    
    return dupes

def remove_dupes(all_dupes, do_del):
    """
        Removes all duplicates as determined by get_dupes

        Parameters:
        -----------
        all_dupes - list - List of lists of duplicate files

        do_del - bool - If the file should be removed or not
    """
    for cur_dupeset in all_dupes:
        print("\tRemoving:")
        for cur_dupe in cur_dupeset:
            print(f"\t\t{cur_dupe}")
            if do_del:
                try:
                    os.remove(cur_dupe)
                except FileNotFoundError:
                    print(f"\t\t[!] Couldn't find duplicate file: {cur_dupe}")

def main(base_path, recursive=True, verify_hash=False, do_del=False):
    print("Checking:", base_path)
    root_images = get_all_files(base_path)
    originals = get_originals(root_images)
    dupes = get_dupes(base_path, originals, verify_hashes=verify_hash)
    if not len(dupes):
        print('\tNo duplicates found')
    remove_dupes(dupes, do_del)

    if recursive:
        dirs = [os.path.join(base_path, d) for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
        if len(dirs):
            for cd in dirs:
                main(cd, recursive=recursive, verify_hash=verify_hash, do_del=do_del)

def parse_cla():
    """
        Parses the command line arguments

        Returns:
        --------
        opt - argparse.Namespace - Object containing command line arguments
    """
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--base_path', type=str, required=True, help='Base directory to search for duplicates in')
    parser.add_argument('--recursive', action='store_true', default=False, help='Recursively search directories for files to remove')
    parser.add_argument('--verify', action='store_true', default=False, help='Verify file hashes between original file and duplicates')
    parser.add_argument('--run', action='store_true', default=False, help="Run the script and remove files, otherwise the script will only print potential removals to stdout")
    parser.add_argument('--skip_check', action='store_true', default=False, help='Flag to skip pause before continuing execution, useful during testing')

    return parser.parse_args()

def do_verify(do_del):
    """
        Verifies command line arguments are what were intended.

        Parameters:
        -----------
        do_del - bool - If the user intends to delete files or only view potential removals
    """
    if do_del:
        print('[!] Warning, you are about to remove files from your system, these files are irrecoverable by this program')
        print('[!] If you wish to only view potential removals, run the script again without the "--run" flag')
    else:
        print('[*] You are running the script in a mode which does not remove files, only prints them to stdout')
        print('[*] If you are sure you wish to remove files, run the script again with the "--run" flag')
    
    try:
        print('[*] Waiting 10 seconds before continuing execution, use CTRL+C to stop script')
        time.sleep(10)
    except KeyboardInterrupt:
        print('\nKeyboard Interrupt received, stopping script execution')
        sys.exit()

if __name__ == "__main__":
    opt = parse_cla()
    
    if not opt.skip_check:
        do_verify(opt.run)

    main(base_path=opt.base_path, recursive=opt.recursive, verify_hash=opt.verify, do_del=opt.run)
    