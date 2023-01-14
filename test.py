import os
import shutil


def mk_dir(out_dir):
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    pass


def get_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size


def copy_dir(dir1, dir2, bkeepstruct=False):
    size = get_size(dir1)
    if size > 200 * 1024 * 1024:
        for fi in os.listdir(dir1):
            fi = fi.split("-")[0]
            ori_dir = dir1 + "\\" + fi
            new_dir = dir2 + "\\" + fi
            if os.path.isdir(ori_dir):
                mk_dir(new_dir)
                copy_dir(ori_dir, new_dir)
    else:
        for root, dirs, files in os.walk(dir1):
            for file in files:
                segs = file.split("-")
                fix = file.split(".")[1]
                fname = segs[1].split("_")
                if fname[0] == "ui":
                    fname = "_".join(fname[2:])
                else:
                    fname = segs[1]
                name = fname + "." + fix
                src_file = os.path.join(root, file)
                shutil.copy(src_file, dir2 +"\\" +name)
            # print(src_file)
    pass
in_dir = "F:\\Genshin\\TextureOut\\Sprite_in\\"
out_dir = "F:\\Genshin\\TextureOut\\Sprite\\"
#origin_dir = "F:\\Genshin\\Texture2D\\Extract\\Origin\\"
mk_dir(out_dir)
#mk_dir(origin_dir)
for fi in os.listdir(in_dir):
    ori_dir = in_dir + fi
    new_dir = out_dir + fi
    if os.path.isdir(ori_dir):
        mk_dir(new_dir)
        copy_dir(ori_dir, new_dir)