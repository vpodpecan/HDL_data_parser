import tarfile
import os
import sys
import argparse
import pandas as pd



def process_HDL_data(dirname, storeFname):
    def group_files():
        print('Reading folder {}\n'.format(dirname))
        fnames = os.listdir(dirname)
        fnames = [x for x in fnames if x.endswith('.tar.bz2')]

        fdict = {}
        for fn in fnames:
            fullname = os.path.join(dirname, fn)
            if not os.path.isfile(fullname) or '_' not in fn:
                continue

            nick = fn.split('_')[1]

            # handle inconsistency in data
            if nick == 'DAISEY':
                nick = 'DAISY'
            elif nick == 'LILY':
                nick = 'LILLY'
            elif nick in ['DEFAULT', 'TESTCLIQ']:
                continue

            if nick not in fdict:
                fdict[nick] = [fullname]
            else:
                fdict[nick].append(fullname)

        for nick in fdict:
            fdict[nick].sort()
        return fdict
    #end


    def get_single_archive_data(tarname):
        archive = tarfile.open(tarname)
        fnames = archive.getnames()

        sensordata = {}
        for fullname in fnames:
            info = archive.getmember(fullname)
            fpath, fname = os.path.split(fullname)
            if not info.isfile() or fname.startswith('.') or not fname.endswith('.csv') or '_' not in fname:
                continue

            sensorname = fname.split('_')[1]
            if sensorname == 'meta':
                continue

            fp = archive.extractfile(fullname)
            try:
                data = pd.read_csv(fp, parse_dates=['time'])
            except:
                print('Error reading archive {}, file {}'.format(tarname, fname), file=sys.stderr)
                continue

            if sensorname not in sensordata:
                sensordata[sensorname] = [data]
            else:
                sensordata[sensorname].append(data)
        return sensordata
    #end


    # group files according to patient nickname
    groups = group_files()
    if not groups:
        return

    nicks = groups.keys()
    store = pd.HDFStore(storeFname)

    # collect data for all patients, all recording sessions
    for nick in nicks:
        print('Processing data for {}'.format(nick))
        data = {}
        for tarname in groups[nick]:
            sensordata = get_single_archive_data(tarname)
            for sensorname in sensordata:
                if sensorname not in data:
                    data[sensorname] = sensordata[sensorname]
                else:
                    data[sensorname].extend(sensordata[sensorname])

        # merge recording sessions, sort according to time, drop duplicates (in time)
        print('Storing data for {}'.format(nick))
        for sensorname in data:
            data[sensorname] = pd.concat(data[sensorname], ignore_index=True)
            data[sensorname].sort_values('time', inplace=True)

            # this is tricky: which measurement to keep when two (or more) have the same timestamp?
            # most likely the first candidate is the one to keep because
            # the second measurement typically has a very small 'diffSec' (time difference) from the first one
            data[sensorname] = data[sensorname].drop_duplicates('time', keep='first')
            data[sensorname].set_index('time', inplace=True)

            name = '/{}/{}'.format(nick, sensorname)
            store.put(name, data[sensorname])
            store.flush()
    store.close()
#end



if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--datadir', default='input', help='directory with the contents of mjff_text_files.zip')
    parser.add_argument('-s', '--store', default=os.path.join('output', 'hdl_data.h5'), help='file name for the HDF5 store')
    args = parser.parse_args()

    if not os.path.isdir(args.datadir):
        print('Error: "{}" is not a directory!'.format(args.datadir, file=sys.stderr))
        exit(1)
    if os.path.exists(args.store):
        print('Error: file "{}" already exists!'.format(args.store, file=sys.stderr))
        exit(1)


    process_HDL_data(args.datadir, args.store)
#end








