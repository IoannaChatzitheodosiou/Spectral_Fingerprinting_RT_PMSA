import TeCanSparkData
import WellTimeSeries
import yaml
import OutliarRemovalStrategy

if __name__ == "__main__":
    filename = input("Please enter the data path: ")
    TeCanSparkData.extract_data(filename)
    with open('well_names.yaml', 'r') as file:
        total_wells = yaml.safe_load(file)
    for well in total_wells:        
        well = WellTimeSeries.WellTimeSeries(f'./{well}', OutliarRemovalStrategy.remove_outliers_corner)
        well.plot_reading_heatmap()
        well.make_gif()
        well.plot_euclidean_heatmap()
