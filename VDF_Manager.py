import os
import glob

class Game:
    def __init__(self) -> None:
        self.index = 0
        self.appid = 0
        self.AppName = "App Name",
        self.Exe = "PATH TO EXE",
        self.StartDir = "DIRECTORY TO START IN",
        self.icon = "",
        self.ShortcutPath = "",
        self.LaunchOptions = "",
        self.IsHidden = False,
        self.AllowDesktopConfig = True,
        self.AllowOverlay = True,
        self.OpenVR = "",
        self.Devkit = "",
        self.DevkitGameID = "",
        self.LastPlayTime = "",
        self.tags = []

    def quick_setup(self):
        self.index = input("Index: ")
        self.AppName = input("App Name: ")
        self.Exe = input("Exec file absolute path: ")
        self.StartDir = input("Directory exec file start in(with \ or / at the end): ")

    def quick_setup(self, index, AppName, Exe, StartDir):
        self.index = index
        self.AppName = AppName
        self.Exe = Exe
        self.StartDir = StartDir

    def export_to_bytes(self, offset: int = 0) -> bytes:
        data_comp: str = '\x00{}\x00'.format(self.index + offset)
        data_comp += '\x02appid\x00\x00\x00\x00\x00'
        data_comp += '\x01AppName\x00{}\x00'.format(self.AppName)
        data_comp += '\x01Exe\x00"{}"\x00'.format(self.Exe)
        data_comp += '\x01StartDir\x00"{}"\x00'.format(self.StartDir)
        data_comp += '\x01icon\x00"{}"\x00'.format(self.icon)
        data_comp += '\x01ShortcutPath\x00\x00'
        data_comp += '\x01LaunchOptions\x00\x00'
        data_comp += '\x02IsHidden\x00\x00\x00\x00\x00'
        data_comp += '\x02AllowDesktopConfig\x00\x01\x00\x00\x00'
        data_comp += '\x02AllowOverlay\x00\x01\x00\x00\x00'
        data_comp += '\x02OpenVR\x00\x00\x00\x00\x00'
        data_comp += '\x02Devkit\x00\x00\x00\x00\x00'
        data_comp += '\x01DevkitGameID\x00\x00'
        data_comp += '\x02LastPlayTime\x00\x00\x00\x00\x00'
        data_comp += '\x00tags\x00\x08\x08'

        return data_comp.encode('utf-8')

    
    def __str__(self) -> str:
        return 'Index: {}\nAppName: {}\nExec: {}\nExecDir: {}\n\n'.format(self.index, self.AppName, self.Exe, self.StartDir)


class ShortCuts:
    def __init__(self) -> None:
        self.short_cuts_number = 0
        self.short_cuts_list: list[Game] = list()

    def generate_profiles(self, path) -> int:
        with open(path, 'rb') as vdf:
            data = vdf.read()
            translated = bytearray(data)
            translated = translated[1:]
            translated = translated[(translated.find(0) + 1):]
            
            group = bytes(translated)
            chunks = group.split(b'\x08')

            try:
                while chunks.remove(b'') != ValueError:
                    continue
            except ValueError:
                None # This is expected behaviour
            except:
                print("Something else broken!")

            for i in range(len(chunks)):
                static_mapping = bytearray(chunks[i])

                # Isolate Unwanted Keys
                static_mapping = static_mapping[static_mapping.find(b'AppName\x00'):]

                # Find AppName
                static_mapping = static_mapping[static_mapping.find(b'\x00') + 1:]
                app_name = static_mapping[0: static_mapping.find(b'\x00')]
                static_mapping = static_mapping[static_mapping.find(b'\x00') + 1:]

                # Find Executable absolute path to file
                static_mapping = static_mapping[static_mapping.find(b'\x00') + 1:]
                exec_path = static_mapping[0: static_mapping.find(b'\x00')]
                static_mapping = static_mapping[static_mapping.find(b'\x00') + 1:]

                # Find Executable directory asolute path
                static_mapping = static_mapping[static_mapping.find(b'\x00') + 1:]
                exec_dir = static_mapping[0: static_mapping.find(b'\x00')]
                static_mapping = static_mapping[static_mapping.find(b'\x00') + 1:]

                game = Game()
                game.quick_setup(i, app_name.decode(), exec_path.decode()[1:-1], exec_dir.decode()[1:-1])
                self.short_cuts_list.append(game)
                self.short_cuts_number += 1

            return self.short_cuts_number
    
    def add_profile(self, game: Game):
        for game_s in self.short_cuts_list:
            if (game_s.AppName == game.AppName):
                return

        game.index = self.short_cuts_number
        self.short_cuts_list.append(game)
        self.short_cuts_number += 1


    def vdf_overwrite(self, des: str):
        with open(des, 'wb') as outter:
            default_msg = '\x00shortcuts\x00'
            composite: list[int] = [int(b) for b in default_msg.encode('utf-8')]
            for game in self.short_cuts_list:
                composite += ([int(b) for b in game.export_to_bytes()])
            
            composite.append(8)
            composite.append(8)

            outter.write(bytearray(composite))

    def test_reap_output(self, inpath, outpath):
        with open(inpath, 'rb') as in_file:
            data = in_file.read()
            mod = [int(b) for b in data]
            mod = mod[0:-2]
            mod +=([int(b) for b in self.short_cuts_list[0].export_to_bytes(self.short_cuts_number)])
            mod.append(8)
            mod.append(8)
            with open(outpath, 'wb') as out_file:
                out_file.write(bytearray(mod))
