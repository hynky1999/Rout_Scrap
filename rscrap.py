import re
import csv
import os
import click


def load_routers(f,expressions,functions):
    counter = 0
    length = 0
    discard = 1
    routers = []
    act_router = {}
    while True:
        lines = f.readline()
        if not lines:
            break
        if counter:
            if counter == 2:
                match = re.match('\S*',lines[length:])
                if match:
                    act_router['SW Version'] = match.group(0)
                    
                counter = 0
            else:
                counter += 1
            continue
        
        for e_index in range(len(expressions)):
            for expression in expressions[e_index]:
                match = re.search(expression,lines)
                if match:
                    if e_index == 0:
                        if not discard:
                            routers.append(act_router)
                            print('Router added: {}'.format(act_router['Name']))
                        else:
                            try:
                                print('Unreadable router: {}'.format(act_router['Name']))
                            except KeyError:
                                pass
                        prefix = match.group(1)[:3]
                        name = re.match('[a-zA-Z]*',match.group(1)[3:]).group(0)
                        func = functions.get(name.upper(),0)
                        if func:
                            act_router = {'Name':match.group(1).upper(),'Building-Block':prefix.upper(),'Function':func}
                            discard = 0
                        else:
                            act_router = {'Name':match.group(1).upper()}
                            discard = 1
                    elif e_index == 1:
                        act_router['System Serial Number'] = match.group(1)
                    elif e_index == 2:
                        act_router['Model Number'] = match.group(1)
                    elif e_index == 3:
                        act_router['SW Version'] = match.group(1)
                    elif e_index == 4:
                        counter = 1
                        length = match.start(1)
                    elif e_index == 5:
                        discard = 1
    if not discard:
        routers.append(act_router)
        print('Router added: {}'.format(act_router['Name']))
    else:
        try:
            print('Unreadable router: {}'.format(act_router['Name']))
        except KeyError:
            pass
    return routers
def routers_to_csv(routers,output,separator):
    
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, output)
    try:
        os.makedirs(os.path.dirname(filename))
    except (FileNotFoundError,FileExistsError):
        pass
        
    with open(filename,'w+') as f:
        writer = csv.DictWriter(f,fieldnames=['Name','Building-Block','Function','System Serial Number','Model Number','SW Version'],delimiter=separator,lineterminator='\n')
        writer.writeheader()
        for router in routers:
            writer.writerow(router)


@click.command()
@click.argument('output', nargs=1, type=click.Path())
@click.argument('source', nargs=-1, type=click.Path(exists=True))
@click.option('--folder/--file', help='determines whether source are files or folders', default=True)
@click.option('--separator', help='separator for csv', default=',')
def start(source,output,folder,separator):
    '''This program is used to scrap data from routers.
    There are 2 positional arguments that are needed to run this program:
    --source
    This argument defines source folders/files, where routers logs are located
    --output
    This argument defines output file of program

    There are 2 optional arguments:
    --folder/--file
    This argument defines whether sources are files or folders
    --separator
    This arguments defines separator for csv output file
    '''
    routers = []
    expressions = (('spawn ssh -x -l rancid (\S*)',),('[Ss]ystem [Ss]erial [Nn]umber\s*: ([-A-Z0-9]*)',),('Model [nN]umber\s*: ([-A-Z0-9]*)',),('Software.*Version ([A-Za-z0-9().]*)',),('(SW Version)',),('Error: EOF received',))
    functions = {'CPLA':'CPLA','OPLA':'OPLA','LTAP':'LTAP','DUT':'DUT','MLA':'DISTRIBUTION','MLB':'DISTRIBUTION','MLS':'CORE'}
    if folder:
        for fold in source:
            for file in os.listdir(fold):
                with open(os.path.join(fold,file)) as f:
                    routers+= load_routers(f,expressions,functions)
    else:
        for file in source:
            with open(file) as f:
                    routers+= load_routers(f,expressions,functions)
            
        
    routers_to_csv(routers,output,separator)
start()
    
                             

    
    
