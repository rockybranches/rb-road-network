import os, sys, time, subprocess
try:
    from termcolor import colored, cprint
except ModuleNotFoundError as e:
    print(e)
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'termcolor'])
    from termcolor import colored, cprint

usage = colored('\tUsage: ','red',attrs=['bold']) + colored('python3 test_poptable.py /absolute/path/to/input/poptable.tex\r\n', 'red')

root_dpath = os.environ['RB_DATA']

def load_input_table(input_fpath):
    fstr=''
    with open(input_fpath, 'r') as fp:
        fstr = fp.read()
    return fstr

def load_template(input_str=''):
    template_fpath = os.path.join(root_dpath, 'templates/PopTableTest.tex')
    template_str = ''
    with open(template_fpath, 'r') as fp:
        template_str = fp.read()
    if not input_str:
        return template_str
    return template_str.replace('%% INSERT_TEST_TABLE %%', input_str)

def create_ptex_doc(input_str, output_fpath=None, genpdf=True):
    default_fpath = os.path.join(root_dpath, 'tmp/PopTableTestRender')
    output_fpath = output_fpath if output_fpath else default_fpath
    template_str = load_template(input_str)
    output_fpath_tex = output_fpath + '.tex'
    print('generated table tex from template.')
    for old_files in [output_fpath + '.tex',
                      output_fpath + '.pdf']:
        if os.path.exists(old_files):
            backup_fpath = f'{old_files}.{int(time.time())}.bak'
            os.rename(old_files, backup_fpath)
            print(colored(f'( saved a backup of an existing test to: {backup_fpath} )', 'grey'))
    with open(output_fpath_tex, 'w') as fptex:
        fptex.write(template_str)
    print('rendering {}...'.format(output_fpath,))
    compile_cmd = [
        'xelatex',
        '--interaction=nonstopmode',
        f'-output-directory={os.path.join(root_dpath,"tmp/")}',
        output_fpath_tex
    ]
    proc = subprocess.run(compile_cmd)
    print('Rendered: {}.pdf .'.format(output_fpath,))
    os.popen(f'xpdf {output_fpath}.pdf')
    # return doc

if __name__=='__main__':
    if len(sys.argv) < 2:
        cprint(colored('Not enough arguments provided!\r\n','red',attrs=['bold']))
        print(usage)
        sys.exit()
    input_fpath = os.path.abspath(sys.argv[1])
    input_str = load_input_table(input_fpath)
    create_ptex_doc(input_str)
    print('done.')
