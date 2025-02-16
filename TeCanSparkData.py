import yaml 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def generate_cell_range(cell_range:str) -> list:
    cells = []
    not_expanded_cells = cell_range.split(';')
    for cell in not_expanded_cells:
        if '-' not in cell:
            cells.append(cell)
        else:
            cells.extend(expand_cell_range(cell))
    return cells


def expand_cell_range(cell_range: str) -> list:
    start_cell = cell_range.split('-')[0]
    end_cell = cell_range.split('-')[1]
    start_cell_letter = ord(start_cell[0])
    start_cell_number = int(start_cell[1:])
    end_cell_letter = ord(end_cell[0])
    end_cell_number = int(end_cell[1:])
    return [f'{chr(letter)}{number}' for letter in range(start_cell_letter, end_cell_letter+1) for number in range(start_cell_number, end_cell_number+1)]


def extract_data(filename):
    df = pd.read_excel(filename, header= None)
    
    wells = generate_cell_range(df[df[0]=='Plate area'].iloc[:, 4].to_string(index=False)) #read all well names
    with open('well_names.yaml', 'w') as wells_file:
            yaml.safe_dump(wells, wells_file)

    well_indexes = {well:df[df[0]==well].index for well in wells} #creates a dictionary with the indexes of the first row for each well
    try:
        difference = well_indexes[wells[1]][0] - well_indexes[wells[0]][0] #find table length
    except Exception as e:
         
        #  print(e)
        #  print(f'well indexes: {well_indexes}')
        #  return False
        difference = 47
        print ("there was only one well, so we assume that the length is 47")
    

    for well in wells:
        i=1
        metadata = {}
        metadata['well_name'] = well
        files = {}
        if not os.path.exists(well):
            os.makedirs(well)
        for well_index in well_indexes[well]:
            df_well= df.iloc[well_index:well_index+difference, :]
            df_well.to_csv(f'{well}/{well}_{i}.csv',header=False, index=False)
            files[i]= f'{well}_{i}.csv'
            i+=1
        metadata['series']=files
        print(metadata)
        with open(f'{well}/metadata.yaml', 'w') as metadata_file:
            yaml.safe_dump(metadata, metadata_file)

if __name__ == "__main__":
    filename = '7_20.xls'
    extract_data(filename) 
