import ReadFiles
import WellTimeSeries
import yaml

if __name__ == "__main__":
    filename = input("Please enter the data path: ")
    ReadFiles.extract_data(filename)
    with open('well_names.yaml', 'r') as file:
        total_wells = yaml.safe_load(file)
    for well in total_wells:        
        well = WellTimeSeries.WellTimeSeries(f'./{well}')
        well.plot_heatmaps()
        well.make_gif()