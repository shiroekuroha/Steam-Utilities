from VDF_Manager import Game, ShortCuts
import os
import glob


def get_executables_in_folders(target_dir):
    # Get a list of all subdirectories in the target directory
    subdirs = [os.path.join(target_dir, d) for d in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, d))]

    # Find all executable files in the subdirectories
    result = []
    for subdir in subdirs:
        executable: str = ''

        if os.name == 'posix':  # Linux
            files = glob.glob(os.path.join(subdir, '*'))
            if len(files) > 1:
                print('Subfolder have more than one executable! Require input from user...')
                for i in range(len(files)):
                    print('\t' + str(i) + ' ==> ' + files[i].split('\\')[-1] + ' || OS Access: ' + str(os.access(files[i], os.X_OK)))
                choice = int(input("\tEnter the execute index to be assign as the executable: "))
                executable = files[choice]

            else:
                executable = files[0]

        elif os.name == 'nt':  # Windows
            files = glob.glob(os.path.join(subdir, '*.exe'))
            if len(files) > 1:
                print('Subfolder have more than one executable! Require input from user...')
                for i in range(len(files)):
                    print('\t' + str(i) + ' ==> ' + files[i].split('\\')[-1])
                choice = int(input("\tEnter the execute index to be assign as the executable: "))
                executable = files[choice]

            else:
                executable = files[0]

        # Add the directory name and executable files to the result list
        folder_name = os.path.basename(subdir)
        result.append((subdir, folder_name, executable))

    return result

def write_shortcuts_to_steam():
    os_pathway = ''

    print("Default Steam userdata:")
    print("\tWindows: C:\\Program Files (x86)\\Steam\\userdata")
    print("\tLinux/UNIX: ~/.steam/steam/userdata")

    if (int(input("Specify Steam userdata folder?(1 for Yes/0 for No): "))):
        os_pathway = input('Enter Path to userdata folder: ')

    else:
        if os.name == 'posix':  # Linux
            os_pathway = "~/.steam/steam/userdata"

        elif os.name == 'nt':  # Windows
            os_pathway = "C:\\Program Files (x86)\\Steam\\userdata"

    folders = []

    for item in os.listdir(os_pathway):
        item_path = os.path.join(os_pathway, item)
        if os.path.isdir(item_path):
            folders.append(item_path)

    if len(folders) > 1:
        print("More than one profile detected! This feature is not ready, exitting...")
        return
    
    if len(folders) == 0:
        print("No Profile detected! Exitting...")
        return
    
    profile_path = folders[0]

    if os.name == 'posix':  # Linux
        shortcuts_vdf_path = os.path.join(profile_path, 'config/shortcuts.vdf')
    elif os.name == 'nt':  # Windows
        shortcuts_vdf_path = os.path.join(profile_path, 'config\\shortcuts.vdf')
    
    shortcut = ShortCuts()
    shortcut.generate_profiles(shortcuts_vdf_path)
    executable = get_executables_in_folders(input('Enter target directory to get executable from(Steam Require ABSOLUTE path not relative path): '))

    for index in range(len(executable)):
        game = Game()
        game.quick_setup(index, executable[index][1], executable[index][2], executable[index][0])
        shortcut.add_profile(game)
    
    shortcut.vdf_overwrite(shortcuts_vdf_path)

write_shortcuts_to_steam()