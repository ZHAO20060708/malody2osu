import os
import json
import sys
import zipfile
from shutil import rmtree
import traceback
from datetime import datetime
import platform
import urllib.request
import urllib.error

# 跨平台 getch 实现
def getch():
    """跨平台获取单个按键输入"""
    if platform.system() == 'Windows':
        import msvcrt
        return msvcrt.getch()
    else:
        # Unix/Linux/macOS
        import sys
        # 检查 stdin 是否是终端
        if not sys.stdin.isatty():
            # 非终端环境（如管道、IDE），直接读取一行并返回第一个字符
            line = sys.stdin.readline()
            return line[0].encode() if line else b'\n'
        try:
            import tty
            import termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch.encode()
        except (termios.error, AttributeError):
            # 如果 termios 失败，回退到普通输入
            return input()[0].encode() if input() else b'\n'

lastfile = "N/A"
version = "2"
date = "January 1, 2026"

try:
    # 设置控制台标题（仅Windows）
    if platform.system() == 'Windows':
        import ctypes
        ctypes.windll.kernel32.SetConsoleTitleW(f"Malody to osu!mania Converter v{version}")
    
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
        #https://codeday.me/ko/qa/20190316/78831.html
        
    print(f"Malody to osu!mania Converter v{version}")
    print(date)
    print("original by Jakads")
    print("modified by Eric Zhao using Claude Opus 4.5")
    
    # 版本检测
    print("\n(i) Checking for updates...")
    try:
        with urllib.request.urlopen(
            'https://raw.githubusercontent.com/ZHAO20060708/malody2osu/master/version.txt',
            timeout=5
        ) as response:
            latest = response.read().decode('utf-8').strip()
        if latest != version:
            print(f"[!] New version available: v{latest} (current: v{version})")
            print("[!] Please visit the repository to download the latest version.")
            print("[!] Repository: https://github.com/ZHAO20060708/malody2osu")
        else:
            print("[O] You are using the latest version.")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"[!] Could not check for updates: {e}")
    except Exception as e:
        print(f"[!] Update check failed: {e}")
    print()
    
    def choose():
        choice = getch().decode()
        while choice not in 'yYnN':
            choice = getch().decode()
        
        if choice in 'nN':
            return 0
        
        else:
            return 1
        
    def recursive_file_gen(mydir):
        for root, dirs, files in os.walk(mydir):
            for file in files:
                yield os.path.join(root, file)
                #https://stackoverflow.com/questions/2865278
    
    def convert(i, bgtmp, soundtmp):
        lastfile = f'{i} (Crashed while reading)'

        try:
            with open(f'{i}',encoding='utf-8') as mc:
                mcFile = json.loads(mc.read())
            mcFile['meta']['mode']
        except:
            print(f"[!] FileWarning: {os.path.basename(i)} is not a valid .mc file. Ignoring...")
            return 1
    
        if not mcFile['meta']['mode'] == 0:
            print(f"[!] KeyWarning: {os.path.basename(i)} is not a Key difficulty. Ignoring...")
            return 1

        ms = lambda beats, bpm, offset: 1000*(60/bpm)*beats+offset
        beat = lambda beat: beat[0] + beat[1]/beat[2] #beats = [measure, nth beat, divisor]
        col = lambda column, keys: int(512*(2*column+1)/(2*keys))

        SVMap = False
            
        line = mcFile['time']
        meta = mcFile['meta']
        note = mcFile['note']
        if 'effect' in mcFile and len(mcFile['effect'])>0:
            sv = mcFile['effect']
            SVMap = True
        soundnote = {}
    
        keys = meta["mode_ext"]["column"]
    
        for x in note:
            if x.get('type',0):
                soundnote = x
    
        bpm = [line[0]['bpm']]
        bpmoffset = [-soundnote.get('offset',0)]
    
        if len(line)>1:
            j=0
            lastbeat=line[0]['beat']
            for x in line[1:]:
                bpm.append(x['bpm'])
                bpmoffset.append(ms(beat(x['beat'])-beat(lastbeat),line[j]['bpm'],bpmoffset[j]))
                j+=1
                lastbeat=x['beat']
    
        global title, artist #I know using global is a bad practice but c'mon
        title = meta["song"]["title"]
        artist = meta["song"]["artist"]
    
        preview = meta.get('preview',-1)
        titleorg = meta['song'].get('titleorg',title)
        artistorg = meta['song'].get('artistorg',artist)
    
        background = meta["background"]
        if not background=="": bgtmp.append(os.path.join(os.path.dirname(i), background))
        sound = soundnote["sound"]
        if not sound=="": soundtmp.append(os.path.join(os.path.dirname(i), sound))
        creator = meta["creator"]
        version = meta["version"]

        lastfile = f'{i} (Crashed while converting)'
    
        with open(f'{os.path.splitext(i)[0]}.osu',mode='w',encoding='utf-8') as osu:
            osuformat = ['osu file format v14',
                         '',
                         '[General]',
                         f'AudioFilename: {sound}',
                         'AudioLeadIn: 0',
                         f'PreviewTime: {preview}',
                         'Countdown: 0',
                         'SampleSet: Soft',
                         'StackLeniency: 0.7',
                         'Mode: 3',
                         'LetterboxInBreaks: 0',
                         'SpecialStyle: 0',
                         'WidescreenStoryboard: 0',
                         '',
                         '[Editor]',
                         'DistanceSpacing: 1.2',
                         'BeatDivisor: 4',
                         'GridSize: 8',
                         'TimelineZoom: 2.4',
                         '',
                         '[Metadata]',
                         f'Title:{title}',
                         f'TitleUnicode:{titleorg}',
                         f'Artist:{artist}',
                         f'ArtistUnicode:{artistorg}',
                         f'Creator:{creator}',
                         f'Version:{version}',
                         'Source:Malody',
                         'Tags:Malody Convert by Jakads',
                         'BeatmapID:0',
                         'BeatmapSetID:-1',
                         '',
                         '[Difficulty]',
                         'HPDrainRate:8',
                         f'CircleSize:{keys}',
                         'OverallDifficulty:8',
                         'ApproachRate:5',
                         'SliderMultiplier:1.4',
                         'SliderTickRate:1',
                         '',
                         '[Events]',
                         '//Background and Video events',
                         f'0,0,\"{background}\",0,0',
                         '',
                         '[TimingPoints]\n']
            osu.write('\n'.join(osuformat))
            #https://thrillfighter.tistory.com/310
    
            bpmcount = len(bpm)
            for x in range(bpmcount):
                osu.write(f'{bpmoffset[x]},{60000/bpm[x]},{int(line[x].get("sign",4))},1,0,0,1,0\n')

            if SVMap:
                for n in sv:
                    j=0
    
                    for b in line:
                        if beat(b['beat']) > beat(n['beat']):
                            j+=1
                        else:
                            continue
    
                    j=bpmcount-j-1
    
                    if int(ms(beat(n["beat"]), bpm[j], bpmoffset[j])) >= bpmoffset[0]:
                        osu.write(f'{ms(beat(n["beat"])-beat(line[j]["beat"]), bpm[j], bpmoffset[j])},-{100/abs(n["scroll"]) if n["scroll"]!=0 else "1E+308"},{int(line[j].get("sign",4))},1,0,0,0,0\n')
    
            osu.write('\n\n[HitObjects]')
    
            for n in note:
                if not n.get('type',0) == 0:
                    continue
                
                j=0
                k=0
    
                for b in line:
                    if beat(b['beat']) > beat(n['beat']):
                        j+=1
                    else:
                        continue
    
                if not n.get('endbeat') == None:
                    for b in line:
                        if beat(b['beat']) > beat(n['endbeat']):
                            k+=1
                        else:
                            continue
    
                j=bpmcount-j-1
                k=bpmcount-k-1
    
                if int(ms(beat(n["beat"]), bpm[j], bpmoffset[j])) >= 0:
                    osu.write(f'\n{col(n["column"], keys)},192,{int(ms(beat(n["beat"])-beat(line[j]["beat"]), bpm[j], bpmoffset[j]))}')

                    if n.get('endbeat') == None:  #Regular Note
                        osu.write(',1,0,0:0:0:')
                    else:  #Long Note
                        osu.write(f',128,0,{int(ms(beat(n["endbeat"])-beat(line[k]["beat"]), bpm[k], bpmoffset[k]))}:0:0:0:')
                        
                    if n.get('sound') == None:
                        osu.write('0:')
                    else:  #Hitsound Note
                        osu.write('{0}:{1}'.format(n['vol'],n['sound'].replace('"','')))
        return 0
    
    def sanitize_filename(filename):
        """移除或替换文件名中的非法字符"""
        # Linux和Windows都不允许的字符
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\0']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        # 移除首尾空格和点
        filename = filename.strip(' .')
        return filename if filename else "unknown"
    
    def compress(compressname, name, bglist, soundlist):
        # 分离目录和文件名，只清理文件名部分
        dir_part = os.path.dirname(compressname)
        name_part = os.path.basename(compressname)
        name_part = sanitize_filename(name_part)
        if dir_part:
            compressname = os.path.join(dir_part, name_part)
        else:
            compressname = name_part
        
        # 检查文件是否已存在，如果存在则添加后缀
        original_name = compressname
        suffix = 1
        while os.path.isfile(f'{compressname}.osz'):
            compressname = f'{original_name} ({suffix})'
            suffix += 1
        if compressname != original_name:
            print(f'[!] {os.path.basename(original_name)}.osz already exists, saving as {os.path.basename(compressname)}.osz')
        
        osz = zipfile.ZipFile(f'{compressname}.osz','w')
    
        for i in name:
            lastfile = f'{i} (Crashed while compressing)'
            osz.write(f'{os.path.splitext(i)[0]}.osu', f'{os.path.basename(i)}.osu')
            os.remove(f'{os.path.splitext(i)[0]}.osu')
            print(f'[O] Compressed: {os.path.splitext(i)[0]}.osu')
        if not len(bglist)==0:
            for i in bglist:
                lastfile = f'{i} (Crashed while compressing)'
                if os.path.isfile(i):
                    osz.write(i, os.path.basename(i))
                    print(f'[O] Compressed: {os.path.basename(i)}')
                else:
                    print(f'[!] {os.path.basename(i)} is not found and thus not compressed.')
        if not len(soundlist)==0:
            for i in soundlist:
                lastfile = f'{i} (Crashed while compressing)'
                if os.path.isfile(i):
                    osz.write(i, os.path.basename(i))
                    print(f'[O] Compressed: {os.path.basename(i)}')
                else:
                    print(f'[!] {os.path.basename(i)} is not found and thus not compressed.')
        osz.close()
        oszname.append(f'{compressname}.osz')
    
    if len(sys.argv)<=1:
        print("(i) Usage: python3 convert.py <file1.mc> [file2.mcz] [file3.zip] ...")
        print("(i) Press any key to exit.")
        getch()
        sys.exit()
    
    MCDragged = False
    MCValid = False
    ZIPDragged = False
    #FolderDragged = False
    mcname = []
    zipname = []
    foldername = []
    oszname = []
    
    mctmp = []
    print('(i) Checking file validity . . .')
    for x in sys.argv[1:]:
        lastfile = f'{x} (Crashed while checking)'
        isMCZ = False
        if os.path.isdir(x):
            #zipname.append(os.path.splitext(x)[0])
            #FolderDragged = True
            print(f"[!] FileWarning: {os.path.basename(x)} is a directory, not a file. Ignoring...")
        elif not os.path.isfile(x):
            print(f"[!] FileWarning: {os.path.basename(x)} is not found. You normally aren't supposed to see this message. Ignoring...")
        elif os.path.splitext(x)[1].lower() == ".mc":
            mctmp.append(x)
            MCDragged = True
        elif os.path.splitext(x)[1].lower() in [".mcz", ".zip"]:
            if os.path.splitext(x)[1].lower() == ".mcz":
                isMCZ = True
                os.rename(x, f'{os.path.splitext(x)[0]}.zip')
                x = f'{os.path.splitext(x)[0]}.zip'
            mcz = zipfile.ZipFile(x)
            mcz.extractall(os.path.splitext(x)[0])
            mcz.close()
            if isMCZ:
                os.rename(x, f'{os.path.splitext(x)[0]}.mcz')
            zipname.append(os.path.splitext(x)[0])
            ZIPDragged = True
        else:
            print(f"[!] FileWarning: The file type of {os.path.basename(x)} is not supported. Ignoring...")
    
    if MCDragged:
        mcname.append(mctmp)
    
    if not MCDragged and not ZIPDragged:
        #print("\n[X] FILEERROR: None of the files you've dragged in are supported. This program only accepts .mc, .mcz, .zip files, or folders with them.")
        print("\n[X] FILEERROR: None of the files you've dragged in are supported. This program only accepts .mc, .mcz, or .zip files.")
        print("(i) Press any key to exit.")
        getch()
        sys.exit()
    
    title = ""
    artist = ""
    mctitle = ""
    mcartist = ""
    bglist = []
    soundlist = []
    
    print("\n(i) Converting . . .")
    
    #Converting to .osu (dragged .mc files)
    if MCDragged:
        bgtmp = []
        soundtmp = []
        for i in mcname[0][:]: #https://stackoverflow.com/questions/7210578
            if not convert(i, bgtmp, soundtmp):
                print(f'[O] Converted: {os.path.basename(i)}')
                MCValid = True
            else:
                mcname[0].remove(i)
        mctitle = title
        mcartist = artist
        bglist.append(bgtmp)
        soundlist.append(soundtmp)
    
    
    #Converting to .osu (dragged .mcz/.zip files)
    if ZIPDragged:
        for folder in zipname:
            print(f'\n(i) Converting {os.path.basename(folder)} . . .')
            c=0
            bgtmp = []
            soundtmp = []
            mctmp = []
            filelist = list(recursive_file_gen(folder))
            for files in filelist:
                if os.path.splitext(files)[1] == ".mc":
                    if not convert(files, bgtmp, soundtmp):
                        print(f'[O] Converted: {os.path.basename(files)}')
                        c+=1
                        MCValid = True
                        mctmp.append(files)
            if c>0:
                foldername.append(folder)
                bglist.append(bgtmp)
                soundlist.append(soundtmp)
                mcname.append(mctmp)
    
    if not MCValid:
        print("\n[X] FILEERROR: None of the files you've dragged are supported.")
        print("(i) Press any key to exit.")
        getch()
        sys.exit()
    
    print('\n(i) All the supported .mc files have been converted to .osu!')
    print('(i) Either close the program now and move the files manually,')
    print('(i) or press Enter to compress all into .osz.')
    getch()
    
    print('\n(i) Compressing . . .')
    #Compress to .osz (dragged .mc files as single mapset)
    if MCDragged:
        # 输出到第一个 mc 文件所在的目录
        output_dir = os.path.dirname(mcname[0][0]) if mcname[0] else '.'
        output_path = os.path.join(output_dir, f'{mcartist} - {mctitle}')
        compress(output_path, mcname[0], set(bglist[0]), set(soundlist[0]))
    
    if ZIPDragged:
        i = 1 if MCDragged else 0
        for folder in zipname:
            print(f'\n(i) Compressing {os.path.basename(folder)} . . .')
            # 输出到原始 mcz/zip 文件所在的目录（即解压目录的父目录）
            output_dir = os.path.dirname(folder)
            output_path = os.path.join(output_dir, os.path.basename(folder))
            compress(output_path, mcname[i], set(bglist[i]), set(soundlist[i]))
            i+=1
            rmtree(folder)
    
    print('\n(i) The following .osz files have been created! Run the files to add the maps to osu! automatically.')
    for i in oszname:
        print(f'* {i}')
    print('(i) Press any key to exit.')
    getch()
    
except Exception as e:
    print(f'\n\n\n[X] FATAL ERROR : {repr(e)}\n')
    traceback.print_exc()
    crashlog = f'CrashLog_{datetime.now().strftime("%Y%m%d%H%M%S")}.log'
    with open(crashlog,mode='w',encoding='utf-8') as crash:
        crash.write('lol rip xd\n\n')
        crash.write(f"Target File: {lastfile}\n")
        crash.write("If you would like to tell the dev about this issue, please attach the file above if available (and the whole folder too if possible) with this crash report.\n")
        crash.write('DO NOT EDIT ANYTHING WRITTEN HERE.\n\n')
        crash.write(traceback.format_exc())
    print(f'\n[X] The crash log has been saved as {crashlog}.')
    print('[X] Please tell the dev about this!')
    print('(i) Press any key to exit.')
    getch()
    exit()
